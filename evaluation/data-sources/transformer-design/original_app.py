import os
import asyncio
import requests # Added for manual API calls
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import warnings

# Force CPU-only execution for TensorFlow to avoid CUDA errors
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow import keras
from keras import layers

# Suppress warnings
warnings.filterwarnings("ignore")

# -------------------------
# Global Variables
# -------------------------
MODEL = None
SCALERS = None
FEATURE_COLS = None
TIME_STEPS = 10
N_FEATURES = None

# ThreadPoolExecutor for running synchronous tasks asynchronously
executor = ThreadPoolExecutor(max_workers=4)

# -------------------------
# Transformer Model
# -------------------------
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = x + inputs
    return x + res

def build_model(input_shape, head_size, num_heads, ff_dim, 
                num_transformer_blocks, mlp_units, 
                dropout=0, mlp_dropout=0):
    inputs = keras.Input(shape=input_shape)
    x = inputs
    
    for _ in range(num_transformer_blocks):
        x = transformer_encoder(x, head_size, num_heads, ff_dim, dropout)
    
    x = layers.GlobalAveragePooling1D(data_format="channels_first")(x)
    
    for dim in mlp_units:
        x = layers.Dense(dim, activation="elu")(x)
        x = layers.Dropout(mlp_dropout)(x)
    
    outputs = layers.Dense(1, activation="linear")(x)
    
    return keras.Model(inputs, outputs)

# -------------------------
# Feature Engineering
# -------------------------
def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Rename Adj Close if it exists (though our manual fetcher returns 'Close')
    if "Adj Close" in df.columns:
        df = df.rename(columns={"Adj Close": "Close"})

    # Simple Features
    df["Returns"] = df["Close"].pct_change()
    df["MA_5"] = df["Close"].rolling(5).mean()
    df["MA_10"] = df["Close"].rolling(10).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["Volatility"] = df["Returns"].rolling(10).std()
    df["Momentum"] = df["Close"] - df["Close"].shift(5)

    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))
        df["RSI"] = df["RSI"].fillna(100).replace([np.inf, -np.inf], 100)

    # MACD
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df["BB_Middle"] = df["Close"].rolling(20).mean()
    df["BB_Std"] = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Middle"] + 2 * df["BB_Std"]
    df["BB_Lower"] = df["BB_Middle"] - 2 * df["BB_Std"]
    
    # Volume Features
    df["Volume_MA"] = df["Volume"].rolling(5).mean()
    with np.errstate(divide='ignore', invalid='ignore'):
        df["Volume_Ratio"] = df["Volume"] / df["Volume_MA"]
        df["Volume_Ratio"] = df["Volume_Ratio"].replace([np.inf, -np.inf], 1).fillna(1)
    
    # High-Low Features
    df["High_Low_Diff"] = df["High"] - df["Low"]
    with np.errstate(divide='ignore', invalid='ignore'):
        df["High_Low_Pct"] = (df["High"] - df["Low"]) / df["Low"]
        df["High_Low_Pct"] = df["High_Low_Pct"].replace([np.inf, -np.inf], 0).fillna(0)
    
    return df.dropna()

# -------------------------
# Recursive Forecast
# -------------------------
def recursive_forecast(ticker_data, model, scaler, feature_cols, timesteps, n_features, forecast_days=7):
    df_prepared = add_technical_features(ticker_data)

    if len(df_prepared) < timesteps:
        raise ValueError("Not enough historical data after feature engineering.")

    last_seq = df_prepared.tail(timesteps)
    scaled_input = scaler.transform(last_seq[feature_cols].values)
    X = scaled_input.reshape(1, timesteps, n_features)
    
    preds = []
    for _ in range(forecast_days):
        next_scaled = model.predict(X, verbose=0)
        new_step = X[0, -1, :].copy()
        new_step[0] = next_scaled[0, 0]
        
        X = np.roll(X, -1, axis=1)
        X[0, -1, :] = new_step
        
        temp = np.zeros((1, n_features))
        temp[0, 0] = next_scaled[0, 0]
        pred = scaler.inverse_transform(temp)[0, 0]
        preds.append(round(pred, 4))
        
    return preds

# -------------------------
# Manual Data Fetching (Bypassing yfinance)
# -------------------------
def fetch_stock_data_sync(ticker: str):
    """
    Synchronous function to fetch data directly from Yahoo JSON API.
    Bypasses yfinance library issues.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # Yahoo Finance Chart API (returns JSON) - 2 months range
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2mo"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        # Validation
        if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
            print(f"No data found for {ticker}")
            return None
        
        result = data["chart"]["result"][0]
        
        # Extract columns
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        
        df = pd.DataFrame({
            "Date": pd.to_datetime(timestamps, unit="s"),
            "Open": quote["open"],
            "High": quote["high"],
            "Low": quote["low"],
            "Close": quote["close"],
            "Volume": quote["volume"]
        })

        # Drop any failed rows (Yahoo sometimes returns nulls)
        df = df.dropna()
        return df

    except Exception as e:
        print(f"Error manually fetching data for {ticker}: {e}")
        return None

async def fetch_stock_data(ticker: str) -> pd.DataFrame | None:
    """Wrapper to run the sync fetch in a thread."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, lambda: fetch_stock_data_sync(ticker))

# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(title="Stock Transformer Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
async def startup_event():
    global MODEL, SCALERS, FEATURE_COLS, N_FEATURES

    try:
        FEATURE_COLS = joblib.load("./model/feature_cols.pkl")
        SCALERS = joblib.load("./model/all_scalers.pkl")
        N_FEATURES = len(FEATURE_COLS)
        
        input_shape = (TIME_STEPS, N_FEATURES)
        
        MODEL = build_model(
            input_shape,
            head_size=46,
            num_heads=60,
            ff_dim=55,
            num_transformer_blocks=1,
            mlp_units=[256],
            mlp_dropout=0.4,
            dropout=0.14,
        )

        MODEL.compile(loss="mse", optimizer=keras.optimizers.Adam(learning_rate=1e-4), metrics=["mse"])
        MODEL.load_weights("./model/transformer_stock.weights.h5")
        
        print("✅ Model and scalers loaded successfully.")

    except Exception as e:
        print(f"❌ Error during startup loading: {e}")
        MODEL = None
        SCALERS = None

# -------------------------
# Prediction Endpoint (Updated)
# -------------------------
@app.get("/predict/{ticker}")
async def predict(ticker: str):
    if MODEL is None or SCALERS is None:
        raise HTTPException(status_code=503, detail="Model service is not fully initialized.")
        
    if ticker not in SCALERS:
        raise HTTPException(status_code=404, detail=f"Scaler not found for ticker '{ticker}'")

    data = await fetch_stock_data(ticker)

    MIN_DATA_POINTS = 30
    if data is None or len(data) < MIN_DATA_POINTS:
        raise HTTPException(status_code=400, detail=f"Insufficient data for '{ticker}'. Need >{MIN_DATA_POINTS} points.")

    # --- 1. Extract Historical Data (New) ---
    historical_data = data.tail(7)[["Date", "Close"]].copy()
    
    # Format and rename columns for clarity in the response
    historical_data["Date"] = historical_data["Date"].dt.strftime("%Y-%m-%d")
    historical_data = historical_data.rename(columns={"Date": "date", "Close": "price"})
    
    # Convert to a list of dictionaries
    historical_list = historical_data.to_dict("records")

    try:
        preds = recursive_forecast(
            ticker_data=data,
            model=MODEL,
            scaler=SCALERS[ticker],
            feature_cols=FEATURE_COLS,
            timesteps=TIME_STEPS,
            n_features=N_FEATURES,
            forecast_days=7,
        )
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
         print(f"Logic error for {ticker}: {e}")
         raise HTTPException(status_code=500, detail="Prediction failed due to calculation error.")

    last_date = pd.to_datetime(data["Date"].iloc[-1])
    forecast_dates = pd.date_range(
        start=last_date, 
        periods=7, 
        freq="B", 
        inclusive="right"
    ).strftime("%Y-%m-%d").tolist()
    
    # --- 2. Update Return Structure (New) ---
    return {
        "ticker": ticker,
        "historical_7d": historical_list, # Added
        "predictions_7d": preds,
        "forecast_dates": forecast_dates,
        "last_actual_date": last_date.strftime("%Y-%m-%d"),
        "data_points_used": len(data)
    }
# -------------------------
# Health Check
# -------------------------
@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "model_loaded": MODEL is not None, 
        "scalers_loaded": SCALERS is not None, 
        "features": N_FEATURES
    }