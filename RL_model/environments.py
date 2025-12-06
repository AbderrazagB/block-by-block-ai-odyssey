"""
Trading environment implementations.
"""

import numpy as np
import pandas as pd

try:
    from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
    FINRL_AVAILABLE = True
except ImportError:
    FINRL_AVAILABLE = False


class SimpleStockEnv:
    """Simplified stock trading environment compatible with trained model."""
    
    def __init__(self, df, **kwargs):
        self.df = df
        self.stock_dim = kwargs.get('stock_dim', 28)
        self.hmax = kwargs.get('hmax', 100)
        self.initial_amount = kwargs.get('initial_amount', 100000)
        self.transaction_cost_pct = kwargs.get('buy_cost_pct', [0.001])[0]
        self.tech_indicator_list = kwargs.get('tech_indicator_list', [])
        self.state_space = kwargs.get('state_space', 1 + 2 * self.stock_dim + len(self.tech_indicator_list) * self.stock_dim)
        
        self.data = self.df.copy()
        self.unique_dates = self.data['date'].unique()
        
        # Get list of available tickers in the data (may be less than stock_dim)
        self.available_tickers = sorted(self.data['tic'].unique())
        print(f"SimpleStockEnv: stock_dim={self.stock_dim}, available_tickers={len(self.available_tickers)}")
        
        self.day = 0
        self.terminal = False
        
        # Portfolio state
        self.balance = self.initial_amount
        self.shares = [0] * self.stock_dim
        self.asset_memory = [self.initial_amount]
        self.state = self._get_state()
        
    def reset(self):
        self.day = 0
        self.balance = self.initial_amount
        self.shares = [0] * self.stock_dim
        self.asset_memory = [self.initial_amount]
        self.terminal = False
        self.state = self._get_state()
        return self.state
    
    def _get_state(self):
        if self.day >= len(self.unique_dates):
            return self.state
        
        current_date = self.unique_dates[self.day]
        day_data = self.data[self.data['date'] == current_date]
        
        # State: [balance, shares..., prices..., indicators...]
        state = [self.balance]
        
        # Add shares held (always stock_dim length, padded with 0s if needed)
        state.extend(self.shares)
        
        # Add current prices (pad to stock_dim with 0s for missing tickers)
        prices = [0] * self.stock_dim
        for idx, ticker in enumerate(self.available_tickers[:self.stock_dim]):
            ticker_data = day_data[day_data['tic'] == ticker]
            if len(ticker_data) > 0:
                prices[idx] = ticker_data.iloc[0]['close']
        state.extend(prices)
        
        # Add technical indicators (pad to stock_dim for each indicator)
        for indicator in self.tech_indicator_list:
            indicator_values = [0] * self.stock_dim
            for idx, ticker in enumerate(self.available_tickers[:self.stock_dim]):
                ticker_data = day_data[day_data['tic'] == ticker]
                if len(ticker_data) > 0 and indicator in ticker_data.columns:
                    indicator_values[idx] = ticker_data.iloc[0][indicator]
            state.extend(indicator_values)
        
        # Ensure we match state_space exactly
        while len(state) < self.state_space:
            state.append(0)
        state = state[:self.state_space]
        
        return np.array(state)
    
    def step(self, actions):
        if self.terminal:
            return self.state, 0, True, {}
        
        # Get current prices
        current_date = self.unique_dates[self.day]
        day_data = self.data[self.data['date'] == current_date]
        
        prices = [0] * self.stock_dim
        for idx, ticker in enumerate(self.available_tickers[:self.stock_dim]):
            ticker_data = day_data[day_data['tic'] == ticker]
            if len(ticker_data) > 0:
                prices[idx] = ticker_data.iloc[0]['close']
        
        # Execute trades based on actions (only for available tickers with valid prices)
        for i in range(min(len(actions), len(self.available_tickers))):
            action = actions[i]
            if prices[i] > 0:  # Only trade if we have a valid price
                if action > 0:  # Buy
                    shares_to_buy = min(int(action * self.hmax), int(self.balance / (prices[i] * (1 + self.transaction_cost_pct))))
                    if shares_to_buy > 0:
                        cost = shares_to_buy * prices[i] * (1 + self.transaction_cost_pct)
                        self.balance -= cost
                        self.shares[i] += shares_to_buy
                elif action < 0:  # Sell
                    shares_to_sell = min(int(-action * self.hmax), self.shares[i])
                    if shares_to_sell > 0:
                        revenue = shares_to_sell * prices[i] * (1 - self.transaction_cost_pct)
                        self.balance += revenue
                        self.shares[i] -= shares_to_sell
        
        # Calculate portfolio value
        portfolio_value = self.balance
        for i, shares in enumerate(self.shares):
            if i < len(prices) and prices[i] > 0:
                portfolio_value += shares * prices[i]
        
        self.asset_memory.append(portfolio_value)
        
        # Move to next day
        self.day += 1
        if self.day >= len(self.unique_dates):
            self.terminal = True
        
        self.state = self._get_state()
        reward = portfolio_value - self.asset_memory[-2]
        
        return self.state, reward, self.terminal, {}
