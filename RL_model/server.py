"""
Trading Model Server - Refactored
==================================
Flask server for PPO trading model inference and backtesting.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from config import *
from data_utils import fetch_recent_data, FINRL_AVAILABLE
from environments import SimpleStockEnv
from model_utils import load_trading_model, test_model_on_data, calculate_risk_score

try:
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
except ImportError:
    StockTradingEnv = None

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


# Initialize Flask app
app = Flask(__name__)
app.json.ensure_ascii = False

# Set custom JSON encoder
try:
    app.json_encoder = NumpyEncoder
except AttributeError:
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

# Global variables
model = None
env_kwargs = None
active_ticker_list = TICKER_LIST.copy()  # Track which tickers are actually available


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat(),
        'active_tickers': len(active_ticker_list)
    })


@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get model configuration information."""
    return jsonify({
        'tickers': active_ticker_list,
        'all_tickers': TICKER_LIST,
        'indicators': INDICATORS_LIST,
        'initial_amount': INITIAL_AMOUNT,
        'transaction_cost': TRANSACTION_COST_PCT,
        'train_end_date': TRAIN_END_DATE,
        'model_path': MODEL_PATH,
        'stock_count': len(active_ticker_list),
        'finrl_available': FINRL_AVAILABLE
    })


@app.route('/api/test', methods=['POST'])
def test_model():
    """
    Test the model on recent data.
    Request body: {
        "start_date": "2023-01-01",
        "end_date": "2024-12-04",
        "initial_amount": 100000,
        "hmax": 100,
        "transaction_cost": 0.001
    }
    """
    global active_ticker_list
    
    try:
        data = request.get_json() or {}
        
        # Parse parameters
        end_date = data.get('end_date', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
        start_date = data.get('start_date', TRAIN_END_DATE)
        initial_amount = data.get('initial_amount', INITIAL_AMOUNT)
        hmax = data.get('hmax', DEFAULT_HMAX)
        transaction_cost = data.get('transaction_cost', TRANSACTION_COST_PCT)
        
        print(f"\n{'='*60}")
        print(f"Testing model from {start_date} to {end_date}")
        print(f"Initial portfolio value: ${initial_amount:,.2f}")
        print(f"Max shares per trade: {hmax}")
        print(f"Transaction cost: {transaction_cost*100:.2f}%")
        print(f"{'='*60}\n")
        
        # Fetch and process data
        df, valid_tickers = fetch_recent_data(start_date, end_date, TICKER_LIST, INDICATORS_LIST)
        active_ticker_list = valid_tickers  # Update active tickers
        
        if len(df) == 0:
            return jsonify({'error': 'No data available for the specified date range'}), 400
        
        # IMPORTANT: Keep environment at ORIGINAL 28 dimensions to match trained model
        # The model was trained on 28 stocks, changing dimensions will cause issues
        test_env_kwargs = get_env_kwargs(initial_amount, hmax, transaction_cost)
        test_env_kwargs['stock_dim'] = len(TICKER_LIST)  # Use 28, not len(valid_tickers)
        test_env_kwargs['action_space'] = len(TICKER_LIST)
        test_env_kwargs['state_space'] = 1 + 2*len(TICKER_LIST) + len(INDICATORS_LIST)*len(TICKER_LIST)
        test_env_kwargs['buy_cost_pct'] = [transaction_cost] * len(TICKER_LIST)
        test_env_kwargs['sell_cost_pct'] = [transaction_cost] * len(TICKER_LIST)
        test_env_kwargs['num_stock_shares'] = [0] * len(TICKER_LIST)
        
        print(f"Environment state space: {test_env_kwargs['state_space']} (model trained on 28 stocks)")
        print(f"Environment action space: {test_env_kwargs['action_space']}")
        print(f"Valid tickers available: {len(valid_tickers)}\n")
        
        # Test model
        results = test_model_on_data(model, df, test_env_kwargs, valid_tickers)
        
        return jsonify({
            'success': True,
            'start_date': start_date,
            'end_date': end_date,
            'initial_amount': initial_amount,
            'active_tickers': valid_tickers,
            'results': results
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ Error in test_model:\n{error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': error_trace
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict_next_actions():
    """
    Predict actions for the most recent market state.
    Request body: {
        "date": "2024-12-04"
    }
    """
    global active_ticker_list
    
    try:
        data = request.get_json() or {}
        target_date = data.get('date', (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
        
        print(f"\n{'='*60}")
        print(f"Predicting for date: {target_date}")
        print(f"{'='*60}\n")
        
        # Fetch recent data (need historical context for indicators)
        start_date = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')
        df, valid_tickers = fetch_recent_data(start_date, target_date, TICKER_LIST, INDICATORS_LIST)
        active_ticker_list = valid_tickers
        
        if len(df) == 0:
            return jsonify({'error': 'No data available'}), 400
        
        # Get the most recent date
        latest_date = df['date'].max()
        latest_data = df[df['date'] == latest_date]
        
        print(f"Latest date: {latest_date}")
        print(f"Available tickers: {len(valid_tickers)}")
        print(f"Data rows for prediction: {len(latest_data)}\n")
        
        # Verify we have all tickers for the latest date
        if len(latest_data) != len(valid_tickers):
            return jsonify({
                'error': f'Incomplete data for latest date. Expected {len(valid_tickers)} tickers, got {len(latest_data)}'
            }), 400
        
        # Map valid tickers to their original indices in TICKER_LIST
        ticker_to_index = {ticker: idx for idx, ticker in enumerate(TICKER_LIST)}
        valid_ticker_indices = [ticker_to_index[ticker] for ticker in valid_tickers if ticker in ticker_to_index]
        
        print(f"Valid ticker indices: {valid_ticker_indices}\n")
        
        # Create environment for prediction using ORIGINAL dimensions (28 tickers)
        # The model was trained on 28 stocks, so we need to maintain that state space
        predict_env_kwargs = get_env_kwargs()
        predict_env_kwargs['stock_dim'] = len(TICKER_LIST)  # Use 28, not 25
        predict_env_kwargs['action_space'] = len(TICKER_LIST)
        predict_env_kwargs['state_space'] = 1 + 2*len(TICKER_LIST) + len(INDICATORS_LIST)*len(TICKER_LIST)
        predict_env_kwargs['num_stock_shares'] = [0] * len(TICKER_LIST)
        
        # Build a state manually with the available data
        # State: [balance, shares (28), prices (28), indicators (28*6)]
        state = [predict_env_kwargs['initial_amount']]  # balance
        state.extend([0] * len(TICKER_LIST))  # shares (all 0 for prediction)
        
        # Add prices - use 0 for missing tickers
        prices = [0] * len(TICKER_LIST)
        for ticker in valid_tickers:
            ticker_info = latest_data[latest_data['tic'] == ticker]
            if len(ticker_info) > 0 and ticker in ticker_to_index:
                prices[ticker_to_index[ticker]] = float(ticker_info.iloc[0]['close'])
        state.extend(prices)
        
        # Add indicators - use 0 for missing tickers
        for indicator in INDICATORS_LIST:
            indicator_values = [0] * len(TICKER_LIST)
            for ticker in valid_tickers:
                ticker_info = latest_data[latest_data['tic'] == ticker]
                if len(ticker_info) > 0 and ticker in ticker_to_index:
                    indicator_values[ticker_to_index[ticker]] = float(ticker_info.iloc[0].get(indicator, 0))
            state.extend(indicator_values)
        
        # Convert to numpy array and get prediction
        obs = np.array(state).reshape(1, -1)
        print(f"State shape: {obs.shape}, Expected: (1, {predict_env_kwargs['state_space']})")
        
        action, _states = model.predict(obs, deterministic=True)
        
        # Calculate total absolute action for portfolio allocation (only for valid tickers)
        valid_actions = [action[0][ticker_to_index[ticker]] for ticker in valid_tickers if ticker in ticker_to_index]
        total_action = np.sum(np.abs(valid_actions))
        
        print(f"Model output shape: {action[0].shape}")
        print(f"Valid actions: {len(valid_actions)}\n")
        
        # Format predictions - only for valid tickers
        predictions = {}
        for ticker in valid_tickers:
            if ticker not in ticker_to_index:
                continue
                
            ticker_idx = ticker_to_index[ticker]
            ticker_info = latest_data[latest_data['tic'] == ticker]
            if len(ticker_info) > 0:
                ticker_info = ticker_info.iloc[0]
                action_value = float(action[0][ticker_idx])  # Use ticker_idx instead of idx
                
                # Calculate portfolio allocation percentage
                allocation = (abs(action_value) / total_action * 100) if total_action > 0 else 0
                
                # Get technical indicators
                indicators = {
                    'macd': float(ticker_info.get('macd', 0)),
                    'rsi_30': float(ticker_info.get('rsi_30', 50)),
                    'cci_30': float(ticker_info.get('cci_30', 0)),
                    'dx_30': float(ticker_info.get('dx_30', 0)),
                    'sma_30': float(ticker_info.get('close_30_sma', 0)),
                    'sma_60': float(ticker_info.get('close_60_sma', 0))
                }
                
                # Calculate risk score
                risk_score = calculate_risk_score(indicators)
                
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
                    'recommendation': 'BUY' if action_value > 0.1 else 'SELL' if action_value < -0.1 else 'HOLD',
                    'confidence': float(confidence),
                    'confidence_level': confidence_level,
                    'portfolio_allocation': float(allocation),
                    'estimated_shares': int(abs(action_value) * predict_env_kwargs.get('hmax', 100)),
                    'risk_score': float(risk_score),
                    'indicators': indicators
                }
        
        return jsonify({
            'success': True,
            'date': str(latest_date),
            'predictions': predictions,
            'active_tickers': valid_tickers,
            'market_summary': {
                'total_stocks': int(len(valid_tickers)),
                'buy_signals': int(sum(1 for p in predictions.values() if p['action'] > 0.1)),
                'sell_signals': int(sum(1 for p in predictions.values() if p['action'] < -0.1)),
                'hold_signals': int(sum(1 for p in predictions.values() if abs(p['action']) <= 0.1))
            }
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ Error in predict:\n{error_trace}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
    print("Trading Model Server - Refactored Edition")
    print("="*60)
    
    # Load the model on startup
    try:
        model = load_trading_model(MODEL_PATH)
        env_kwargs = get_env_kwargs()
        print(f"✓ Model configuration loaded")
        print(f"✓ Tracking {len(TICKER_LIST)} tickers")
        print(f"✓ Using {len(INDICATORS_LIST)} technical indicators")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Server will start but endpoints will fail until model is loaded.")
    
    print("\n" + "="*60)
    print("Starting server on http://localhost:5000")
    print("="*60)
    print("\nAvailable endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/model/info          - Model configuration")
    print("  POST /api/test                - Test model on recent data")
    print("  POST /api/predict             - Predict next actions")
    print("  GET  /api/backtest/summary    - Get backtest summary")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
