"""
Model loading and prediction utilities.
"""

import os
import numpy as np
import pandas as pd
from stable_baselines3 import PPO

try:
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
    FINRL_AVAILABLE = True
except ImportError:
    FINRL_AVAILABLE = False
    from environments import SimpleStockEnv


def load_trading_model(model_path):
    """Load the trained PPO model."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)
    print("✓ Model loaded successfully")
    return model


def test_model_on_data(model, df, env_kwargs, ticker_list):
    """Test the model on given data and return predictions."""
    
    # ALWAYS use SimpleStockEnv for reliability - FinRL has issues with mismatched dimensions
    print("Creating SimpleStockEnv for testing...")
    from environments import SimpleStockEnv
    
    env_instance = SimpleStockEnv(df=df, **env_kwargs)
    test_obs = env_instance.reset()
    
    account_values = []
    actions_history = []
    states_history = []
    portfolio_positions = []
    
    unique_dates = df['date'].unique()
    
    for date_idx in range(len(unique_dates)):
        obs_reshaped = test_obs.reshape(1, -1)
        action, _states = model.predict(obs_reshaped, deterministic=True)
        test_obs, reward, done, info = env_instance.step(action[0])
        
        account_values.append(env_instance.asset_memory[-1])
        actions_history.append(action[0].tolist())
        states_history.append(test_obs.tolist())
        portfolio_positions.append(env_instance.shares[:len(ticker_list)])
        
        if done:
            break
    
    dates = [str(d) for d in unique_dates[:len(account_values)]]
    
    # Get stock prices for each date
    stock_prices = {}
    for ticker in ticker_list:
        ticker_data = df[df['tic'] == ticker].sort_values('date')
        stock_prices[ticker] = ticker_data['close'].values.tolist()
    
    # Calculate per-stock performance metrics
    stock_metrics = {}
    for idx, ticker in enumerate(ticker_list):
        # Get actions for this stock over time
        stock_actions = [action[idx] if idx < len(action) else 0 for action in actions_history]
        
        # Calculate ACTUAL trades by tracking position changes
        buy_count = 0
        sell_count = 0
        if len(portfolio_positions) > 1:
            for i in range(1, len(portfolio_positions)):
                prev_shares = portfolio_positions[i-1][idx] if idx < len(portfolio_positions[i-1]) else 0
                curr_shares = portfolio_positions[i][idx] if idx < len(portfolio_positions[i]) else 0
                
                if curr_shares > prev_shares:
                    buy_count += 1  # Position increased = buy
                elif curr_shares < prev_shares:
                    sell_count += 1  # Position decreased = sell
        
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
        'tickers': ticker_list,
        'initial_value': float(account_values[0]) if account_values else float(env_kwargs.get('initial_amount', 100000)),
        'final_value': float(account_values[-1]) if account_values else float(env_kwargs.get('initial_amount', 100000)),
        'total_return': float(((account_values[-1] / account_values[0]) - 1) * 100) if account_values else 0.0,
        'sharpe_ratio': float(sharpe_ratio),
        'max_drawdown': float(max_drawdown),
        'volatility': float(volatility),
        'win_rate': float(win_rate),
        'total_trades': int(sum(m['total_trades'] for m in stock_metrics.values()))
    }
    
    return results


def calculate_risk_score(indicators):
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
