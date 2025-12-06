"""
Train PPO agents directly on real market data (AAPL, NVDA).
Creates a custom environment wrapper that uses historical stock prices.
"""
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import gymnasium as gym
from gymnasium import spaces

sys.path.append('./')
sys.path.append('./gym_continuousDoubleAuction')

from gym_continuousDoubleAuction.test_on_real_data import fetch_market_data, simulate_order_book_from_market_data


class RealMarketCDAEnv(gym.Env):
    """
    Custom Continuous Double Auction environment using real market data.
    Wraps real stock prices into the CDA observation format.
    """
    
    # Class-level cache to avoid re-fetching data
    _data_cache = {}
    _cache_lock = False
    
    def __init__(self, tickers=["AAPL", "NVDA"], tape_display_length=10, init_cash=10000, max_steps=250, use_cached_data=None):
        super().__init__()
        
        self.tickers = tickers
        self.tape_display_length = tape_display_length
        self.init_cash = init_cash
        self.max_steps = max_steps
        
        # Observation space: (4, 10) - same as original CDA
        # Row 0: bid_sizes, Row 1: bid_prices, Row 2: ask_sizes, Row 3: ask_prices
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(4, tape_display_length),
            dtype=np.float32
        )
        
        # Action space: same as original CDA
        # (action_type, order_type, price_adjustment, quantity_ratio, tick_size_multiplier)
        self.action_space = spaces.Tuple([
            spaces.Discrete(3),      # 0=no_action, 1=buy, 2=sell
            spaces.Discrete(4),      # 0=market, 1=limit, 2=cancel, 3=modify
            spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32),  # price adjustment
            spaces.Box(0.0, 1.0, shape=(1,), dtype=np.float32),   # quantity ratio
            spaces.Discrete(12)      # tick size multiplier
        ])
        
        # Load market data (use cache if provided)
        if use_cached_data is not None:
            self.market_data = use_cached_data
            print(f"✓ Using cached data with {len(self.market_data)} points")
        else:
            cache_key = tuple(sorted(tickers))
            if cache_key in RealMarketCDAEnv._data_cache:
                self.market_data = RealMarketCDAEnv._data_cache[cache_key]
                print(f"✓ Using cached data with {len(self.market_data)} points")
            else:
                print("🔄 Loading real market data...")
                self.market_data = self._load_all_market_data()
                RealMarketCDAEnv._data_cache[cache_key] = self.market_data
        
        self.order_book_snapshots = self._create_order_book_snapshots()
        
        # Episode state
        self.current_step = 0
        self.current_snapshot_idx = 0
        self.cash = init_cash
        self.position = 0  # Number of shares held
        self.nav_history = []
        self.trade_history = []
        
        print(f"✓ Environment initialized with {len(self.order_book_snapshots)} market snapshots")
    
    def _load_all_market_data(self) -> pd.DataFrame:
        """Load market data from AlphaVantage API."""
        import requests
        import time
        
        all_data = []
        api_key = "SYYJKD7RMAXAAR1J"
        
        for ticker in self.tickers:
            print(f"  Loading {ticker} from AlphaVantage...")
            
            try:
                # Fetch daily data from AlphaVantage
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": ticker,
                    "outputsize": "compact",  # Last 100 days (free tier)
                    "apikey": api_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Debug: print response keys
                print(f"  Response keys: {list(data.keys())}")
                
                # Check for errors
                if "Error Message" in data:
                    print(f"  ❌ API Error: {data['Error Message']}")
                    continue
                
                if "Note" in data:
                    print(f"  ⚠️ Rate limit warning: {data['Note']}")
                    time.sleep(15)  # Wait before next request
                    continue
                
                if "Information" in data:
                    print(f"  ℹ️ API Info: {data['Information']}")
                    continue
                
                # Extract time series
                time_series = data.get("Time Series (Daily)", {})
                
                if not time_series:
                    print(f"  ⚠️ No data returned for {ticker}")
                    continue
                
                # Convert to DataFrame
                records = []
                for date_str, values in time_series.items():
                    records.append({
                        'date': pd.to_datetime(date_str),
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
                
                df = pd.DataFrame(records)
                df = df.sort_values('date').reset_index(drop=True)
                df['ticker'] = ticker
                
                all_data.append(df)
                print(f"  ✓ Loaded {len(df)} data points for {ticker}")
                print(f"    Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"    Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
                
                # Rate limiting - wait between API calls
                time.sleep(12)  # AlphaVantage free tier: 5 calls/minute
                
            except Exception as e:
                print(f"  ❌ Error loading {ticker} from AlphaVantage: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not all_data:
            raise ValueError("❌ Failed to load any market data from AlphaVantage!")
        
        # Combine all tickers
        combined = pd.concat(all_data, ignore_index=True)
        
        # Shuffle to mix different stocks (if multiple)
        if len(all_data) > 1:
            combined = combined.sample(frac=1.0, random_state=42).reset_index(drop=True)
        
        print(f"✓ Total data points: {len(combined)}")
        return combined
    
    def _create_order_book_snapshots(self) -> List[Dict]:
        """Convert market data to order book snapshots."""
        return simulate_order_book_from_market_data(
            self.market_data,
            depth=self.tape_display_length
        )
    
    def reset(self, seed=None, options=None):
        """Reset environment for new episode."""
        super().reset(seed=seed)
        
        # Reset state
        self.current_step = 0
        self.cash = self.init_cash
        self.position = 0
        self.nav_history = [self.init_cash]
        self.trade_history = []
        
        # Randomly start from different point in data
        max_start = len(self.order_book_snapshots) - self.max_steps
        if max_start > 0:
            self.current_snapshot_idx = np.random.randint(0, max_start)
        else:
            self.current_snapshot_idx = 0
        
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current order book observation in (4, 10) format."""
        if self.current_snapshot_idx >= len(self.order_book_snapshots):
            # Return zeros if out of data
            return np.zeros((4, self.tape_display_length), dtype=np.float32)
        
        snapshot = self.order_book_snapshots[self.current_snapshot_idx]
        
        # Extract order book data
        bid_sizes = np.array(snapshot['bid_sizes'][:self.tape_display_length], dtype=np.float32)
        bid_prices = np.array(snapshot['bid_prices'][:self.tape_display_length], dtype=np.float32)
        ask_sizes = np.array(snapshot['ask_sizes'][:self.tape_display_length], dtype=np.float32)
        ask_prices = np.array(snapshot['ask_prices'][:self.tape_display_length], dtype=np.float32)
        
        # Pad if needed
        if len(bid_sizes) < self.tape_display_length:
            pad_length = self.tape_display_length - len(bid_sizes)
            bid_sizes = np.pad(bid_sizes, (0, pad_length), constant_values=0)
            bid_prices = np.pad(bid_prices, (0, pad_length), constant_values=0)
            ask_sizes = np.pad(ask_sizes, (0, pad_length), constant_values=0)
            ask_prices = np.pad(ask_prices, (0, pad_length), constant_values=0)
        
        # Stack into (4, 10) format
        obs = np.vstack([bid_sizes, bid_prices, ask_sizes, ask_prices])
        
        return obs.astype(np.float32)
    
    def step(self, action):
        """Execute one time step."""
        self.current_step += 1
        
        # Parse action
        action_type = action[0] if isinstance(action, (tuple, list)) else 0
        order_type = action[1] if isinstance(action, (tuple, list)) and len(action) > 1 else 0
        
        # Get current market price
        snapshot = self.order_book_snapshots[self.current_snapshot_idx]
        current_price = (snapshot['bid_prices'][0] + snapshot['ask_prices'][0]) / 2 if snapshot['bid_prices'] and snapshot['ask_prices'] else 0
        
        # Execute trade
        reward = 0.0
        trade_executed = False
        
        if action_type == 1 and current_price > 0:  # Buy
            # IMPROVED: More conservative position sizing (5% instead of 10%)
            shares_to_buy = int(self.cash * 0.05 / current_price)
            cost = shares_to_buy * current_price
            
            # Don't buy if it would exceed reasonable position size
            max_position_value = self.init_cash * 0.5  # Max 50% of initial capital in stocks
            current_position_value = self.position * current_price
            
            if cost <= self.cash and shares_to_buy > 0 and (current_position_value + cost) <= max_position_value:
                self.cash -= cost
                self.position += shares_to_buy
                trade_executed = True
                self.trade_history.append({
                    'step': self.current_step,
                    'type': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'cost': cost
                })
        
        elif action_type == 2 and self.position > 0:  # Sell
            # IMPROVED: More flexible selling (25-50% of position)
            sell_pct = 0.3  # Sell 30% by default
            shares_to_sell = int(self.position * sell_pct)
            proceeds = shares_to_sell * current_price
            
            if shares_to_sell > 0:
                self.cash += proceeds
                self.position -= shares_to_sell
                trade_executed = True
                self.trade_history.append({
                    'step': self.current_step,
                    'type': 'SELL',
                    'price': current_price,
                    'shares': shares_to_sell,
                    'proceeds': proceeds
                })
        
        # Move to next snapshot
        self.current_snapshot_idx += 1
        
        # Calculate NAV
        nav = self.cash + (self.position * current_price)
        self.nav_history.append(nav)
        
        # Check if episode is done
        done = (
            self.current_step >= self.max_steps or
            self.current_snapshot_idx >= len(self.order_book_snapshots) or
            nav <= self.init_cash * 0.2  # Stop if lost 80%
        )
        
        truncated = self.current_snapshot_idx >= len(self.order_book_snapshots)
        
        # CRITICAL FIX: Force position closure at episode end
        if done or truncated:
            if self.position > 0:
                # Liquidate all positions at current price
                proceeds = self.position * current_price
                self.cash += proceeds
                self.position = 0
                nav = self.cash  # Update NAV after liquidation
                self.nav_history[-1] = nav  # Update last NAV entry
        
        # IMPROVED REWARD FUNCTION
        # Focus on final outcome, not intermediate steps
        if done or truncated:
            # Episode ending - reward based on final PnL (after liquidation)
            total_return = (nav - self.init_cash) / self.init_cash
            reward = total_return * 100  # Scale up for learning
            
            # Strong penalty for large losses
            if nav < self.init_cash * 0.5:
                reward -= 50.0  # Massive penalty for losing >50%
            elif nav < self.init_cash * 0.8:
                reward -= 10.0  # Penalty for losing >20%
            
            # Bonus for profit
            if nav > self.init_cash:
                reward += 10.0  # Extra reward for any profit
                
        else:
            # During episode - small incremental rewards
            if len(self.nav_history) > 1:
                nav_change = nav - self.nav_history[-2]
                reward = nav_change / self.init_cash * 0.1  # Much smaller intermediate rewards
                
                # Penalize excessive trading (overtrading)
                if trade_executed and len(self.trade_history) > 30:
                    reward -= 0.05  # Discourage too many trades
                
                # Small penalty for holding losing positions
                if nav < self.nav_history[0]:  # Below starting NAV
                    reward -= 0.01
        
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, reward, done, truncated, info
    
    def _get_info(self) -> Dict:
        """Get episode info."""
        current_price = 0
        if self.current_snapshot_idx < len(self.order_book_snapshots):
            snapshot = self.order_book_snapshots[self.current_snapshot_idx]
            if snapshot['bid_prices'] and snapshot['ask_prices']:
                current_price = (snapshot['bid_prices'][0] + snapshot['ask_prices'][0]) / 2
        
        nav = self.cash + (self.position * current_price)
        
        return {
            'step': self.current_step,
            'cash': self.cash,
            'position': self.position,
            'NAV': nav,
            'num_trades': len(self.trade_history),
            'reward': (nav - self.init_cash) / self.init_cash if self.init_cash > 0 else 0
        }


def create_real_market_env(env_config):
    """Environment creator for RLlib."""
    return RealMarketCDAEnv(
        tickers=env_config.get('tickers', ['AAPL', 'NVDA']),
        tape_display_length=env_config.get('tape_display_length', 10),
        init_cash=env_config.get('init_cash', 10000),
        max_steps=env_config.get('max_steps', 250)
    )
