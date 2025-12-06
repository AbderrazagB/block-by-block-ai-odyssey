"""
Trading Model Server
====================
Flask server that loads the trained PPO model and provides endpoints
for testing on recent data and forecasting prices/actions.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stockstats import StockDataFrame
import os
import json

# Import FinRL components with detailed error reporting
FINRL_AVAILABLE = False
FINRL_ERROR = None

try:
    print("Attempting to import FinRL components...")
    from finrl.meta.preprocessor.yahoodownloader import YahooDownloader
    print("  ✓ YahooDownloader imported")
    from finrl.meta.preprocessor.preprocessors import FeatureEngineer, data_split
    print("  ✓ FeatureEngineer imported")
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
    print("  ✓ StockTradingEnv imported")
    FINRL_AVAILABLE = True
    print("✓ All FinRL components imported successfully")
except ImportError as e:
    FINRL_ERROR = str(e)
    print(f"✗ FinRL import failed with error:")
    print(f"  {e}")
    print("\nPossible solutions:")
    print("  1. Install FinRL: pip install finrl")
    print("  2. Install FinRL from source: pip install git+https://github.com/AI4Finance-Foundation/FinRL.git")
    print("  3. Check if you're using the correct Python environment")
    print("  4. Try: pip install --upgrade finrl")
except Exception as e:
    FINRL_ERROR = str(e)
    print(f"✗ Unexpected error during FinRL import:")
    print(f"  {e}")
    import traceback
    traceback.print_exc()

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

app = Flask(__name__)
app.json.ensure_ascii = False

# Set custom JSON encoder
try:
    app.json_encoder = NumpyEncoder  # Flask < 2.2
except AttributeError:
    # Flask 2.2+ uses a different approach
    from flask.json.provider import DefaultJSONProvider
    
    class NumpyJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            return super().default(obj)
    
    app.json = NumpyJSONProvider(app)

CORS(app)  # Enable CORS for frontend

# Configuration
PROJECT_PATH = './FinRL_Trading_Results'
MODEL_PATH = f'{PROJECT_PATH}/trained_ppo_trading_model.zip'

TRAIN_END_DATE = '2023-01-01'
TICKER_LIST = [
    # Green Energy
    "NEE", "FSLR", "BEP", "PLUG",
    # Oil & Gas
    "XOM", "CVX", "COP", "SLB",
    # Banking & Finance
    "JPM", "BAC", "WFC", "GS", "MS",
    # Utilities / General Energy
    "DUK", "SO", "PCG", "EIX",
    # IT / Tech
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "ORCL", "IBM"
]

INDICATORS_LIST = ['macd', 'rsi_30', 'cci_30', 'dx_30', 'close_30_sma', 'close_60_sma']
INITIAL_AMOUNT = 100000
TRANSACTION_COST_PCT = 0.001
REWARD_SCALING = 1e-4

# Global variables for model and environment
model = None
env_kwargs = None


def safe_fetch_data(self):
    """Custom Yahoo downloader to handle multi-ticker data."""
    data = yf.download(
        tickers=self.ticker_list,
        start=self.start_date,
        end=self.end_date,
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join([str(c) for c in col]).strip() for col in data.columns.values]
    
    allowed = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    data = data[[col for col in data.columns if any(a in col for a in allowed)]]
    data.reset_index(inplace=True)
    return data


def make_finrl_ready(df, tickers):
    """Convert raw Yahoo data to FinRL long-format DataFrame."""
    df = df.copy()
    
    # Handle different column formats
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join([str(c) for c in col if c]).strip() for col in df.columns.values]
        df = df.reset_index()
    else:
        if 'Date' not in df.columns and 'date' not in df.columns:
            df = df.reset_index()
    
    # Ensure we have a date column
    if 'Date' in df.columns:
        df.rename(columns={'Date': 'date'}, inplace=True)
    elif 'index' in df.columns:
        df.rename(columns={'index': 'date'}, inplace=True)
    
    if 'date' not in df.columns:
        raise ValueError(f"No date column found. Available columns: {df.columns.tolist()}")
    
    df['date'] = pd.to_datetime(df['date'])
    
    if len(tickers) == 1:
        ticker = tickers[0]
        # Try to find ticker columns
        col_mapping = {}
        for base_col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            possible_names = [f'{base_col}_{ticker}', base_col]
            for name in possible_names:
                if name in df.columns:
                    col_mapping[name] = base_col.lower().replace(' ', '_')
                    break
        
        df_long = df.rename(columns=col_mapping)
        df_long['tic'] = ticker
    else:
        df_long = pd.DataFrame()
        for ticker in tickers:
            ticker_cols = [c for c in df.columns if c.endswith(f'_{ticker}')]
            if not ticker_cols:
                print(f"Warning: No columns found for {ticker}")
                continue
                
            temp = df[['date'] + ticker_cols].copy()
            col_map = {c: c.replace(f'_{ticker}','').lower().replace(' ','_') for c in ticker_cols}
            temp.rename(columns=col_map, inplace=True)
            temp['tic'] = ticker
            df_long = pd.concat([df_long, temp], ignore_index=True)
    
    required_cols = ['date', 'tic', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    
    # Check if all required columns exist
    missing_cols = [col for col in required_cols if col not in df_long.columns]
    if missing_cols:
        print(f"Warning: Missing columns {missing_cols}. Available: {df_long.columns.tolist()}")
        # Try to fill missing columns
        for col in missing_cols:
            if col not in ['date', 'tic']:
                df_long[col] = 0
    
    return df_long[required_cols]


def load_model():
    """Load the trained PPO model."""
    global model, env_kwargs
    
    if not FINRL_AVAILABLE:
        raise RuntimeError("FinRL is not available. Cannot load model without FinRL.")
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    
    print(f"Loading model from {MODEL_PATH}...")
    model = PPO.load(MODEL_PATH)
    
    # Setup environment kwargs
    stock_dimension = len(TICKER_LIST)
    state_space = 1 + 2*stock_dimension + len(INDICATORS_LIST)*stock_dimension
    
    env_kwargs = {
        "hmax": 100,
        "initial_amount": INITIAL_AMOUNT,
        "num_stock_shares": [0] * stock_dimension,
        "buy_cost_pct": [TRANSACTION_COST_PCT] * stock_dimension,
        "sell_cost_pct": [TRANSACTION_COST_PCT] * stock_dimension,
        "state_space": state_space,
        "stock_dim": stock_dimension,
        "tech_indicator_list": INDICATORS_LIST,
        "action_space": stock_dimension,
        "reward_scaling": REWARD_SCALING
    }
    
    print("✓ Model loaded successfully")


def fetch_recent_data(start_date, end_date):
    """Fetch and process recent stock data using FinRL."""
    if not FINRL_AVAILABLE:
        raise RuntimeError("FinRL is not available. Cannot fetch data.")
    
    print(f"Fetching data from {start_date} to {end_date}...")
    
    # Use FinRL's YahooDownloader
    YahooDownloader.fetch_data = safe_fetch_data
    df = YahooDownloader(
        start_date=start_date,
        end_date=end_date,
        ticker_list=TICKER_LIST
    ).fetch_data()
    
    # Convert to FinRL format
    df_finrl = make_finrl_ready(df, TICKER_LIST)
    
    # Sort by date and ticker
    df_finrl = df_finrl.sort_values(['date', 'tic']).reset_index(drop=True)
    
    # Add technical indicators using FinRL's FeatureEngineer
    fe = FeatureEngineer(
        use_technical_indicator=True,
        tech_indicator_list=INDICATORS_LIST,
        use_vix=False,
        use_turbulence=False,
        user_defined_feature=False
    )
    processed_df = fe.preprocess_data(df_finrl)
    
    # Clean the data
    processed_df = processed_df.dropna().reset_index(drop=True)
    
    # Ensure all required columns exist and are properly typed
    for col in ['open', 'high', 'low', 'close', 'adj_close', 'volume'] + INDICATORS_LIST:
        if col in processed_df.columns:
            processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
    
    # Remove any remaining NaN values
    processed_df = processed_df.dropna().reset_index(drop=True)
    
    # Verify we have data for all tickers on each date
    dates = processed_df['date'].unique()
    tickers_per_date = processed_df.groupby('date')['tic'].nunique()
    incomplete_dates = tickers_per_date[tickers_per_date < len(TICKER_LIST)]
    
    if len(incomplete_dates) > 0:
        print(f"Warning: {len(incomplete_dates)} dates have incomplete ticker data")
        # Remove dates with incomplete data
        complete_dates = tickers_per_date[tickers_per_date == len(TICKER_LIST)].index
        processed_df = processed_df[processed_df['date'].isin(complete_dates)].reset_index(drop=True)
    
    print(f"✓ Fetched {len(processed_df)} rows across {processed_df['date'].nunique()} dates")
    
    return processed_df


def test_model_on_data(df, custom_env_kwargs=None):
    """Test the model on given data using FinRL's StockTradingEnv."""
    global model, env_kwargs
    
    if not FINRL_AVAILABLE:
        raise RuntimeError("FinRL is not available. Cannot test model.")
    
    # Use custom env_kwargs if provided, otherwise use global
    env_config = custom_env_kwargs if custom_env_kwargs is not None else env_kwargs.copy()
    
    # Ensure data is sorted and properly formatted for FinRL
    df = df.sort_values(['date', 'tic']).reset_index(drop=True)
    
    # Verify data structure
    print(f"Data date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Unique dates: {df['date'].nunique()}")
    print(f"Unique tickers: {df['tic'].nunique()}")
    print(f"Total rows: {len(df)}")
    
    # CRITICAL: Remove turbulence and day from env_config if they exist
    # These can cause issues with state initialization
    env_config.pop('turbulence_threshold', None)
    env_config.pop('day', None)
    
    # Create test environment using FinRL's StockTradingEnv
    print("Creating FinRL StockTradingEnv for testing...")
    try:
        test_env = StockTradingEnv(df=df, **env_config)
    except Exception as e:
        print(f"Error creating environment: {e}")
        print(f"Environment config: {env_config}")
        print(f"DataFrame info:")
        print(f"  Columns: {df.columns.tolist()}")
        print(f"  Shape: {df.shape}")
        print(f"  First few rows:")
        print(df.head())
        raise
    
    # Reset environment and get initial observation
    reset_result = test_env.reset()
    
    # Handle different gym API versions
    if isinstance(reset_result, tuple):
        test_obs, info = reset_result
    else:
        test_obs = reset_result
        info = {}
    
    account_values = []
    actions_history = []
    states_history = []
    
    done = False
    step_count = 0
    
    print("Running model predictions...")
    while not done:
        # Get model prediction
        action, _states = model.predict(test_obs, deterministic=True)
        
        # Take step in environment
        step_result = test_env.step(action)
        
        # Handle both old and new gym API
        if len(step_result) == 5:
            test_obs, rewards, terminated, truncated, info = step_result
            done = terminated or truncated
        else:
            test_obs, rewards, done, info = step_result
        
        # Record history
        account_values.append(test_env.asset_memory[-1])
        actions_history.append(action.tolist() if hasattr(action, 'tolist') else action)
        states_history.append(test_obs.tolist() if hasattr(test_obs, 'tolist') else test_obs)
        
        step_count += 1
        if step_count % 50 == 0:
            print(f"  Step {step_count}, Portfolio: ${account_values[-1]:,.2f}")
    
    print(f"✓ Completed {step_count} steps")
    
    # Get dates from the dataframe
    unique_dates = df['date'].unique()
    dates = [str(d) for d in unique_dates[:len(account_values)]]
    
    # Get portfolio positions from states
    # State structure: [balance, shares..., prices..., indicators...]
    portfolio_positions = []
    for state in states_history:
        shares = state[1:len(TICKER_LIST)+1] if len(state) > len(TICKER_LIST) else [0] * len(TICKER_LIST)
        portfolio_positions.append(shares)
    
    # Get stock prices for each date
    stock_prices = {}
    for ticker in TICKER_LIST:
        ticker_data = df[df['tic'] == ticker].sort_values('date')
        stock_prices[ticker] = ticker_data['close'].values.tolist()
    
    # Calculate per-stock performance metrics
    stock_metrics = {}
    for idx, ticker in enumerate(TICKER_LIST):
        # Get actions for this stock over time
        stock_actions = [action[idx] if idx < len(action) else 0 for action in actions_history]
        
        # Calculate trades
        buy_count = sum(1 for a in stock_actions if a > 0.1)
        sell_count = sum(1 for a in stock_actions if a < -0.1)
        
        # Get final position
        final_shares = portfolio_positions[-1][idx] if len(portfolio_positions) > 0 and idx < len(portfolio_positions[-1]) else 0
        
        # Calculate average action
        avg_action = np.mean([abs(a) for a in stock_actions]) if stock_actions else 0
        
        # Get latest price and indicators
        ticker_data = df[df['tic'] == ticker]
        if len(ticker_data) > 0:
            latest = ticker_data.iloc[-1]
            first = ticker_data.iloc[0]
            
            # Convert all values to native Python types
            stock_metrics[ticker] = {
                'final_shares': int(final_shares),
                'total_trades': int(buy_count + sell_count),
                'buy_trades': int(buy_count),
                'sell_trades': int(sell_count),
                'avg_action_strength': float(avg_action),
                'final_price': float(latest['close']),
                'price_change': float((latest['close'] / first['close'] - 1) * 100) if float(first['close']) > 0 else 0.0,
                'position_value': float(final_shares * latest['close']),
                'indicators': {
                    'rsi_30': float(latest.get('rsi_30', 50)),
                    'macd': float(latest.get('macd', 0)),
                    'cci_30': float(latest.get('cci_30', 0)),
                    'dx_30': float(latest.get('dx_30', 0))
                }
            }
    
    # Calculate overall performance metrics
    if len(account_values) > 1:
        returns = pd.Series(account_values).pct_change().dropna()
        sharpe_ratio = float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0
        cumulative = pd.Series(account_values)
        max_drawdown = float(((cumulative - cumulative.cummax()) / cumulative.cummax()).min() * 100)
        volatility = float(returns.std() * np.sqrt(252) * 100)
        win_rate = float((returns > 0).sum() / len(returns) * 100) if len(returns) > 0 else 0
    else:
        sharpe_ratio = 0
        max_drawdown = 0
        volatility = 0
        win_rate = 0
    
    results = {
        'dates': dates,
        'account_values': [float(v) for v in account_values],
        'actions': [[float(a) for a in action] for action in actions_history],
        'states': [[float(s) for s in state] for state in states_history],
        'portfolio_positions': [[float(p) for p in pos] for pos in portfolio_positions],
        'stock_prices': {k: [float(p) for p in v] for k, v in stock_prices.items()},
        'stock_metrics': stock_metrics,
        'tickers': TICKER_LIST,
        'initial_value': float(account_values[0]) if account_values else float(env_config.get('initial_amount', INITIAL_AMOUNT)),
        'final_value': float(account_values[-1]) if account_values else float(env_config.get('initial_amount', INITIAL_AMOUNT)),
        'total_return': float(((account_values[-1] / account_values[0]) - 1) * 100) if account_values else 0.0,
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown': float(max_drawdown),
        'volatility': float(volatility),
        'win_rate': float(win_rate),
        'total_trades': int(sum(m['total_trades'] for m in stock_metrics.values()))
    }
    
    return results


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'finrl_available': FINRL_AVAILABLE,
        'finrl_error': FINRL_ERROR if not FINRL_AVAILABLE else None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get model configuration information."""
    return jsonify({
        'tickers': TICKER_LIST,
        'indicators': INDICATORS_LIST,
        'initial_amount': INITIAL_AMOUNT,
        'transaction_cost': TRANSACTION_COST_PCT,
        'train_end_date': TRAIN_END_DATE,
        'model_path': MODEL_PATH,
        'stock_count': len(TICKER_LIST),
        'finrl_available': FINRL_AVAILABLE
    })


@app.route('/api/test', methods=['POST'])
def test_model():
    """
    Test the model on recent data using FinRL environment.
    Request body: {
        "start_date": "2023-01-01",      // optional
        "end_date": "2024-12-04",        // optional (defaults to 2 days ago)
        "initial_amount": 100000,        // optional (portfolio starting capital)
        "hmax": 100,                     // optional (max shares per trade)
        "transaction_cost": 0.001        // optional (transaction cost as decimal)
    }
    """
    if not FINRL_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'FinRL is not available. Please install FinRL to use this endpoint.'
        }), 503
    
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please check server logs.'
        }), 503
    
    try:
        data = request.get_json() or {}
        
        # Default: from training end to 2 days ago
        end_date = data.get('end_date', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
        start_date = data.get('start_date', TRAIN_END_DATE)
        initial_amount = data.get('initial_amount', INITIAL_AMOUNT)
        hmax = data.get('hmax', 100)
        transaction_cost = data.get('transaction_cost', TRANSACTION_COST_PCT)
        
        print(f"Testing model from {start_date} to {end_date}")
        print(f"Initial portfolio value: ${initial_amount:,.2f}")
        print(f"Max shares per trade: {hmax}")
        print(f"Transaction cost: {transaction_cost*100:.2f}%")
        
        # Update env_kwargs with custom parameters
        global env_kwargs
        test_env_kwargs = env_kwargs.copy()
        test_env_kwargs['initial_amount'] = initial_amount
        test_env_kwargs['hmax'] = hmax
        test_env_kwargs['buy_cost_pct'] = [transaction_cost] * len(TICKER_LIST)
        test_env_kwargs['sell_cost_pct'] = [transaction_cost] * len(TICKER_LIST)
        
        # Fetch and process data
        df = fetch_recent_data(start_date, end_date)
        
        if len(df) == 0:
            return jsonify({'error': 'No data available for the specified date range'}), 400
        
        print(f"Data columns: {df.columns.tolist()}")
        print(f"Data shape: {df.shape}")
        
        # Test model with FinRL environment
        results = test_model_on_data(df, test_env_kwargs)
        
        return jsonify({
            'success': True,
            'start_date': start_date,
            'end_date': end_date,
            'initial_amount': initial_amount,
            'results': results
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in test_model: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict_next_actions():
    """
    Predict actions for the most recent market state using FinRL environment.
    Request body: {
        "date": "2024-12-04"  // optional (defaults to 2 days ago)
    }
    """
    if not FINRL_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'FinRL is not available. Please install FinRL to use this endpoint.'
        }), 503
    
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please check server logs.'
        }), 503
    
    try:
        data = request.get_json() or {}
        target_date = data.get('date', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
        
        # Fetch recent data (need historical context for indicators)
        # We need MORE data because FinRL needs to step through to reach the target date
        start_date = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')
        df = fetch_recent_data(start_date, target_date)
        
        if len(df) == 0:
            return jsonify({'error': 'No data available'}), 400
        
        # Verify data format and completeness
        print(f"Data shape before env creation: {df.shape}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Unique dates: {df['date'].nunique()}")
        print(f"Expected tickers per date: {len(TICKER_LIST)}")
        
        # Ensure we have complete data for all tickers on each date
        dates_with_all_tickers = df.groupby('date')['tic'].nunique()
        complete_dates = dates_with_all_tickers[dates_with_all_tickers == len(TICKER_LIST)].index
        df = df[df['date'].isin(complete_dates)].copy()
        
        # Sort by date and ticker (critical for FinRL)
        df = df.sort_values(['date', 'tic']).reset_index(drop=True)
        
        print(f"After filtering - Shape: {df.shape}, Dates: {df['date'].nunique()}")
        
        if len(df) == 0:
            return jsonify({'error': 'No complete data available after filtering'}), 400
        
        # Get the most recent date for reporting
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        # Verify we have all tickers for the latest date
        if len(latest_data) != len(TICKER_LIST):
            return jsonify({
                'error': f'Incomplete data for latest date. Expected {len(TICKER_LIST)} tickers, got {len(latest_data)}'
            }), 400
        
        # Create FinRL environment - it will iterate through ALL the data
        print("Creating FinRL environment for prediction...")
        
        # Use a copy of env_kwargs and remove problematic keys
        predict_env_kwargs = env_kwargs.copy()
        predict_env_kwargs.pop('turbulence_threshold', None)
        predict_env_kwargs.pop('day', None)
        
        try:
            test_env = StockTradingEnv(df=df, **predict_env_kwargs)
        except Exception as env_error:
            print(f"Environment creation error: {env_error}")
            print(f"DataFrame sample:")
            print(df.head(30))
            print(f"\nDataFrame info:")
            print(df.info())
            print(f"\nDataFrame dtypes:")
            print(df.dtypes)
            
            # Try to diagnose the issue
            print(f"\nChecking first date data structure:")
            first_date = df['date'].min()
            first_date_data = df[df['date'] == first_date]
            print(f"First date: {first_date}")
            print(f"Rows for first date: {len(first_date_data)}")
            print(f"Tickers in first date: {first_date_data['tic'].tolist()}")
            
            raise
        
        # Reset and step through to get to the last state
        reset_result = test_env.reset()
        if isinstance(reset_result, tuple):
            obs, info = reset_result
        else:
            obs = reset_result
        
        print(f"Initial observation shape: {obs.shape if hasattr(obs, 'shape') else len(obs)}")
        
        # Step through the environment to reach the final state
        done = False
        step_count = 0
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            step_result = test_env.step(action)
            
            if len(step_result) == 5:
                obs, rewards, terminated, truncated, info = step_result
                done = terminated or truncated
            else:
                obs, rewards, done, info = step_result
            
            step_count += 1
        
        print(f"Stepped through {step_count} timesteps to reach final state")
        
        # Now get the final prediction for the last state
        action, _states = model.predict(obs, deterministic=True)
        
        print(f"Final action shape: {action.shape if hasattr(action, 'shape') else len(action)}")
        
        # Calculate total absolute action for portfolio allocation
        total_action = np.sum(np.abs(action))
        
        # Format the prediction with enhanced details
        predictions = {}
        for idx, ticker in enumerate(TICKER_LIST):
            ticker_info = latest_data[latest_data['tic'] == ticker]
            if len(ticker_info) > 0:
                ticker_info = ticker_info.iloc[0]
                action_value = float(action[idx])
                
                # Calculate portfolio allocation percentage
                allocation = (abs(action_value) / total_action * 100) if total_action > 0 else 0
                
                # Get technical indicators for this stock
                indicators = {
                    'macd': float(ticker_info.get('macd', 0)),
                    'rsi_30': float(ticker_info.get('rsi_30', 50)),
                    'cci_30': float(ticker_info.get('cci_30', 0)),
                    'dx_30': float(ticker_info.get('dx_30', 0)),
                    'sma_30': float(ticker_info.get('close_30_sma', 0)),
                    'sma_60': float(ticker_info.get('close_60_sma', 0))
                }
                
                # Calculate risk score based on indicators
                risk_score = calculate_risk_score(indicators, ticker_info['close'])
                
                # Determine confidence level
                confidence = abs(action_value)
                if confidence > 0.7:
                    confidence_level = "Very High"
                elif confidence > 0.4:
                    confidence_level = "High"
                elif confidence > 0.2:
                    confidence_level = "Medium"
                elif confidence > 0.1:
                    confidence_level = "Low"
                else:
                    confidence_level = "Very Low"
                
                predictions[ticker] = {
                    'action': float(action_value),
                    'current_price': float(ticker_info['close']),
                    'recommendation': 'BUY' if action_value > 0 else 'SELL' if action_value < 0 else 'HOLD',
                    'confidence': float(confidence),
                    'confidence_level': confidence_level,
                    'portfolio_allocation': float(allocation),
                    'estimated_shares': int(abs(action_value) * env_kwargs.get('hmax', 100)),
                    'risk_score': float(risk_score),
                    'indicators': indicators
                }
        
        return jsonify({
            'success': True,
            'date': str(latest_date),
            'predictions': predictions,
            'market_summary': {
                'total_stocks': int(len(TICKER_LIST)),
                'buy_signals': int(sum(1 for p in predictions.values() if p['action'] > 0.1)),
                'sell_signals': int(sum(1 for p in predictions.values() if p['action'] < -0.1)),
                'hold_signals': int(sum(1 for p in predictions.values() if abs(p['action']) <= 0.1))
            }
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in predict: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 500


def calculate_risk_score(indicators, current_price):
    """Calculate risk score based on technical indicators."""
    risk = 50  # Base risk
    
    # RSI risk (overbought/oversold)
    rsi = indicators.get('rsi_30', 50)
    if rsi > 70:
        risk += 15  # Overbought - higher risk
    elif rsi < 30:
        risk += 10  # Oversold - moderate risk
    
    # CCI risk (extreme values)
    cci = abs(indicators.get('cci_30', 0))
    if cci > 200:
        risk += 10
    elif cci > 100:
        risk += 5
    
    # DX (trend strength - higher DX = more confident trend)
    dx = indicators.get('dx_30', 0)
    if dx < 20:
        risk += 10  # Weak trend
    elif dx > 40:
        risk -= 10  # Strong trend - lower risk
    
    # Price vs Moving Averages
    sma_30 = indicators.get('sma_30', 0)
    sma_60 = indicators.get('sma_60', 0)
    
    if sma_30 > 0 and sma_60 > 0:
        if sma_30 < sma_60:
            risk += 5  # Death cross territory
        else:
            risk -= 5  # Golden cross territory
    
    # Cap risk between 0-100
    return max(0, min(100, risk))


@app.route('/api/backtest/summary', methods=['GET'])
def backtest_summary():
    """Get summary of the saved backtest results."""
    try:
        results_path = f'{PROJECT_PATH}/backtest_results.csv'
        if not os.path.exists(results_path):
            return jsonify({'error': 'Backtest results not found'}), 404
        
        df = pd.read_csv(results_path)
        summary = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*60)
    print("Trading Model Server (FinRL-based)")
    print("="*60)
    
    # Check FinRL availability
    if not FINRL_AVAILABLE:
        print("\n❌ ERROR: FinRL is not installed!")
        print("Please install FinRL to run this server:")
        print("  pip install finrl")
        print("\nServer will start but all endpoints will fail.")
        print("="*60)
    else:
        # Load the model on startup
        try:
            load_model()
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Server will start but model endpoints will fail until model is loaded.")
    
    print("\nStarting server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/model/info          - Model configuration")
    print("  POST /api/test                - Test model on recent data")
    print("  POST /api/predict             - Predict next actions")
    print("  GET  /api/backtest/summary    - Get backtest summary")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)