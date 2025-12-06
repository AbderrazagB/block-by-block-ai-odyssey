from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow import keras
from keras import layers
import yfinance as yf
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
import asyncio
warnings.filterwarnings("ignore")

# Disable yfinance's problematic features
os.environ['YF_ENABLE_REQUESTS_CACHE'] = '0'

# --- Global Artifacts and Configuration ---
MODEL = None
SCALERS = None
FEATURE_COLS = None
TIME_STEPS = 10
N_FEATURES = None

# --- Model Architecture (Must match training exactly) ---
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    """Transformer encoder block - must match training definition"""
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = x + inputs
    return x + res

def build_model(
    input_shape,
    head_size,
    num_heads,
    ff_dim,
    num_transformer_blocks,
    mlp_units,
    dropout=0,
    mlp_dropout=0,
):
    """Build the complete transformer model - must match training"""
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

# --- Feature Engineering Function (Must be identical to training script) ---
def add_technical_features(df):
    """Add technical indicators to the dataframe. Adjusted for live data."""
    df = df.copy()
    
    # Must use 'Close' price for all calculations
    if 'Adj Close' in df.columns:
        df = df.rename(columns={'Adj Close': 'Close'})
    
    df['Returns'] = df['Close'].pct_change()
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['Volatility'] = df['Returns'].rolling(window=10).std()
    df['Momentum'] = df['Close'] - df['Close'].shift(5)
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    
    df['Volume_MA'] = df['Volume'].rolling(window=5).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    
    df['High_Low_Diff'] = df['High'] - df['Low']
    df['High_Low_Pct'] = (df['High'] - df['Low']) / df['Low']
    
    df = df.dropna()
    return df

# --- Prediction Function (Identical to notebook) ---
def recursive_forecast(ticker_data, model, scaler, feature_cols, timesteps, n_features, forecast_days=7):
    # 1. Prepare the historical data and features
    df_prepared = add_technical_features(ticker_data)
    
    # Need at least 'timesteps' days of clean data to start prediction
    if len(df_prepared) < timesteps:
        raise ValueError(f"Not enough historical data ({len(df_prepared)} days) to create a starting sequence of {timesteps} days.")

    # Get the last 'timesteps' days of data for the starting sequence
    last_sequence_df = df_prepared.tail(timesteps)
    
    # Scale the last sequence
    X_input_scaled = scaler.transform(last_sequence_df[feature_cols].values)
    X_input_scaled = X_input_scaled.reshape(1, timesteps, n_features)
    
    predicted_prices = []
    
    # 2. Recursive Loop
    for _ in range(forecast_days):
        next_step_scaled = model.predict(X_input_scaled, verbose=0)
        
        # Create the new timestep features vector (Copy last feature set)
        new_timestep = X_input_scaled[0, -1, :].copy() 
        
        # Inject the predicted Close price into the first feature slot (index 0)
        new_timestep[0] = next_step_scaled[0, 0] 

        # Update the sequence: Drop the oldest day, append the new prediction
        X_input_scaled = np.roll(X_input_scaled, -1, axis=1)
        X_input_scaled[0, -1, :] = new_timestep

        # Inverse transform the predicted Close price for output
        temp_full = np.zeros((1, n_features))
        temp_full[0, 0] = next_step_scaled[0, 0]
        predicted_price = scaler.inverse_transform(temp_full)[0, 0]
        
        predicted_prices.append(round(predicted_price, 4)) # Round to 4 decimals
        
    return predicted_prices

# --- FastAPI Initialization ---
app = FastAPI(title="Stock Transformer Prediction Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Thread pool for running blocking yfinance calls
executor = ThreadPoolExecutor(max_workers=4)

def fetch_stock_data_sync(ticker: str):
    """Synchronous function to fetch stock data - runs in thread pool"""
    try:
        # Method 1: Try using Ticker with simpler approach
        print(f"Attempting to download {ticker} data using Ticker.history()...")
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period="2mo")
        
        if not data.empty and len(data) >= 30:
            print(f"✅ Successfully downloaded {len(data)} days of data for {ticker}")
            return data
        
        # Method 2: Try download without session parameter
        print(f"Trying yf.download for {ticker}...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        data = yf.download(
            ticker, 
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if not data.empty and len(data) >= 30:
            print(f"✅ Successfully downloaded {len(data)} days of data for {ticker}")
            return data
        
        print(f"❌ No data returned for {ticker}")
        return None
        
    except Exception as e:
        print(f"Error in fetch_stock_data_sync: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.on_event("startup")
async def startup_event():
    """Load the model and scalers once when the server starts."""
    global MODEL, SCALERS, FEATURE_COLS, N_FEATURES
    
    try:
        # Load Feature Columns first to determine architecture
        FEATURE_COLS = joblib.load("./model/feature_cols.pkl")
        N_FEATURES = len(FEATURE_COLS)
        print(f"✅ Feature columns loaded. N_FEATURES: {N_FEATURES}")
        
        # Load Scalers
        SCALERS = joblib.load("./model/all_scalers.pkl")
        print("✅ Scalers loaded successfully.")
        
        # Rebuild the model architecture (must match training exactly)
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
        
        # Compile the model
        MODEL.compile(
            loss="mean_squared_error",
            optimizer=keras.optimizers.Adam(learning_rate=1e-4),
            metrics=["mean_squared_error"],
        )
        print("✅ Model architecture rebuilt successfully.")
        
        # Load the trained weights
        MODEL.load_weights("./model/transformer_stock.weights.h5")
        print("✅ Model weights loaded successfully.")
        
    except FileNotFoundError as e:
        print(f"ERROR: Model artifacts not found: {e}")
        print("Please save model weights in the notebook using:")
        print("  model.save_weights('../server/model/transformer_stock_weights.h5')")
        raise
    except Exception as e:
        print(f"ERROR loading model: {e}")
        import traceback
        traceback.print_exc()
        raise

# --- API Endpoint ---
@app.get("/predict/{ticker}", summary="Get 7-day price forecast for a given stock ticker.")
async def predict_price(ticker: str):
    """
    Accepts a stock ticker (e.g., AAPL) and returns the predicted closing prices 
    for the next 7 market days.
    """
    
    if ticker not in SCALERS:
        # Ticker not in the list the model was trained on
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not in the trained list. Scaler missing.")

    try:
        # Run yfinance in a thread pool to avoid async issues
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, fetch_stock_data_sync, ticker)
        
        # Check if we got data
        if data is None or data.empty:
            raise HTTPException(
                status_code=400, 
                detail=f"No data available for ticker '{ticker}'. The ticker may be invalid or data unavailable."
            )
        
        # Reset index to make Date a column and handle timezone-aware datetimes
        data = data.reset_index()
        
        # Convert timezone-aware datetime to timezone-naive if needed
        if 'Date' in data.columns and hasattr(data['Date'].iloc[0], 'tz'):
            data['Date'] = data['Date'].dt.tz_localize(None)
        
        # Verify we have enough data
        if len(data) < 30:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for ticker '{ticker}'. Got {len(data)} days, need at least 30."
            )

        # 2. Get the specific scaler for this ticker
        scaler = SCALERS[ticker]
        
        # 3. Generate the recursive forecast
        predictions = recursive_forecast(
            ticker_data=data,
            model=MODEL,
            scaler=scaler,
            feature_cols=FEATURE_COLS,
            timesteps=TIME_STEPS,
            n_features=N_FEATURES,
            forecast_days=7
        )
        
        # 4. Prepare dates for the response
        last_date_actual = pd.to_datetime(data['Date'].iloc[-1])
        # Generate 7 market days starting *after* the last known actual date
        forecast_dates = pd.date_range(start=last_date_actual, periods=8, inclusive='right', freq='B').strftime('%Y-%m-%d').tolist()

        return {
            "ticker": ticker,
            "predictions_7d": predictions,
            "forecast_dates": forecast_dates,
            "unit": "USD Close Price",
            "last_actual_date": last_date_actual.strftime('%Y-%m-%d'),
            "data_points_used": len(data)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"An error occurred during prediction for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Check if the service is running and model is loaded."""
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None,
        "scalers_loaded": SCALERS is not None,
        "features": N_FEATURES
    }

# --- Run the Server ---
# To run this file, save it as 'app.py' and execute the command:
# uvicorn app:app --reload