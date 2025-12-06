"""
Test trained PPO agents on real market data from AlphaVantage.
"""
import os
import sys
import glob
import time
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Optional

import ray
from ray.rllib.algorithms.ppo import PPOConfig


def fetch_market_data(ticker="AAPL", period="compact", interval="daily"):
    """
    Fetch real market data from AlphaVantage.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL", "MSFT", "GOOGL")
        period: "compact" (last 100 points) or "full" (full history)
        interval: "daily", "weekly", "monthly", or "1min", "5min", "15min", "30min", "60min" for intraday
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
    print(f"📥 Fetching {ticker} data from AlphaVantage...")
    
    try:
        # AlphaVantage API key (free tier: 25 requests/day, 5 requests/minute)
        api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "5VDIO7T7X83CHOA8")
        base_url = "https://www.alphavantage.co/query"
        
        # Map interval to function
        if interval in ["1min", "5min", "15min", "30min", "60min"]:
            function = "TIME_SERIES_INTRADAY"
            params = {
                "function": function,
                "symbol": ticker,
                "interval": interval,
                "outputsize": period,
                "apikey": api_key
            }
        elif interval == "daily":
            function = "TIME_SERIES_DAILY"
            params = {
                "function": function,
                "symbol": ticker,
                "outputsize": period,
                "apikey": api_key
            }
        elif interval == "weekly":
            function = "TIME_SERIES_WEEKLY"
            params = {
                "function": function,
                "symbol": ticker,
                "apikey": api_key
            }
        elif interval == "monthly":
            function = "TIME_SERIES_MONTHLY"
            params = {
                "function": function,
                "symbol": ticker,
                "apikey": api_key
            }
        else:
            raise ValueError(f"Unsupported interval: {interval}")
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            print(f"❌ API Error: {data['Error Message']}")
            return None
        
        if "Note" in data:
            print(f"⚠️ API Note: {data['Note']}")
            print("Rate limit reached. Using smaller dataset or try again later.")
            return None
        
        # Extract time series data
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break
        
        if time_series_key is None:
            print(f"❌ No time series data found in response")
            return None
        
        time_series = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = [col.split('. ')[1] if '. ' in col else col for col in df.columns]
        df.columns = [col.lower() for col in df.columns]
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Reset index to make date a column
        df = df.reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        
        print(f"✓ Retrieved {len(df)} data points")
        print(f"  Time range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
        print(f"  Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        return None


def simulate_order_book_from_market_data(df, depth=10):
    """
    Simulate order book levels from market data.
    
    Args:
        df: DataFrame with market data (open, high, low, close, volume)
        depth: Number of levels in the order book
    
    Returns:
        List of order book snapshots
    """
    observations = []
    
    # Determine timestamp column name
    time_col = 'date' if 'date' in df.columns else 'datetime'
    
    for idx, row in df.iterrows():
        mid_price = (row['high'] + row['low']) / 2
        spread = (row['high'] - row['low']) / 2
        
        if spread == 0:
            spread = row['close'] * 0.001  # 0.1% default spread
        
        # Simulate bid side
        bid_prices = []
        bid_sizes = []
        for i in range(depth):
            price_offset = spread * (i + 1) * 0.5
            bid_price = mid_price - price_offset
            bid_size = row['volume'] / (depth * 100) * (depth - i)
            
            bid_prices.append(max(0, bid_price))
            bid_sizes.append(max(1, int(bid_size)))
        
        # Simulate ask side
        ask_prices = []
        ask_sizes = []
        for i in range(depth):
            price_offset = spread * (i + 1) * 0.5
            ask_price = mid_price + price_offset
            ask_size = row['volume'] / (depth * 100) * (depth - i)
            
            ask_prices.append(ask_price)
            ask_sizes.append(max(1, int(ask_size)))
        
        obs = {
            'timestamp': row[time_col],
            'bid_prices': bid_prices,
            'bid_sizes': bid_sizes,
            'ask_prices': ask_prices,
            'ask_sizes': ask_sizes,
            'last_price': row['close'],
            'volume': row['volume'],
            'spread': spread
        }
        
        observations.append(obs)
    
    return observations


class RealMarketBacktester:
    """Backtest trained agents on real market data."""
    
    def __init__(self, trainer, num_agents, init_cash, tape_display_length):
        self.trainer = trainer
        self.num_agents = num_agents
        self.init_cash = init_cash
        self.tape_display_length = tape_display_length
        
        self.portfolios = {
            i: {
                'cash': init_cash,
                'position': 0,
                'nav': init_cash,
                'trades': [],
                'nav_history': [],
                'pnl_history': []
            }
            for i in range(num_agents)
        }
    
    def format_observation(self, order_book_snapshot, agent_id):
        """Convert order book snapshot to observation format matching (4, 10) shape."""
        portfolio = self.portfolios[agent_id]
        
        # Match the CDA environment observation format: (4, 10) array
        # Row 0: bid sizes (padded to 10)
        # Row 1: bid prices (padded to 10) 
        # Row 2: ask sizes (padded to 10)
        # Row 3: ask prices (padded to 10)
        
        obs = np.zeros((4, 10), dtype=np.float32)
        
        # Fill in bid data
        bid_sizes = order_book_snapshot['bid_sizes'][:10]
        bid_prices = order_book_snapshot['bid_prices'][:10]
        obs[0, :len(bid_sizes)] = bid_sizes
        obs[1, :len(bid_prices)] = bid_prices
        
        # Fill in ask data
        ask_sizes = order_book_snapshot['ask_sizes'][:10]
        ask_prices = order_book_snapshot['ask_prices'][:10]
        obs[2, :len(ask_sizes)] = ask_sizes
        obs[3, :len(ask_prices)] = ask_prices
        
        return obs
    
    def execute_action(self, agent_id, action, order_book_snapshot):
        """Execute agent's action."""
        portfolio = self.portfolios[agent_id]
        action_type, order_type, limit_price, quantity, duration = action
        
        best_bid = order_book_snapshot['bid_prices'][0]
        best_ask = order_book_snapshot['ask_prices'][0]
        last_price = order_book_snapshot['last_price']
        
        execution = {'executed': False, 'action': 'HOLD', 'quantity': 0, 'price': 0}
        
        if action_type == 1:  # Buy
            price = best_ask if order_type == 1 else limit_price
            quantity = int(quantity)
            cost = price * quantity
            
            if portfolio['cash'] >= cost and quantity > 0:
                portfolio['cash'] -= cost
                portfolio['position'] += quantity
                execution = {
                    'executed': True,
                    'action': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'cost': cost
                }
                portfolio['trades'].append(execution)
        
        elif action_type == 2:  # Sell
            price = best_bid if order_type == 1 else limit_price
            quantity = int(quantity)
            
            if portfolio['position'] >= quantity and quantity > 0:
                portfolio['cash'] += price * quantity
                portfolio['position'] -= quantity
                execution = {
                    'executed': True,
                    'action': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'revenue': price * quantity
                }
                portfolio['trades'].append(execution)
        
        portfolio['nav'] = portfolio['cash'] + portfolio['position'] * last_price
        portfolio['nav_history'].append(portfolio['nav'])
        portfolio['pnl_history'].append(portfolio['nav'] - self.init_cash)
        
        return execution
    
    def run_backtest(self, order_book_data, num_trained_agents, verbose=True):
        """Run backtest."""
        print(f"\n{'='*80}")
        print(f"🎯 Running Backtest on {len(order_book_data)} Market Snapshots")
        print(f"{'='*80}\n")
        
        for step, snapshot in enumerate(order_book_data):
            if verbose and step % 100 == 0:
                print(f"Step {step}/{len(order_book_data)}...")
            
            for agent_id in range(self.num_agents):
                obs = self.format_observation(snapshot, agent_id)
                policy_id = f"policy_{agent_id}"
                policy = self.trainer.get_policy(policy_id)
                action = policy.compute_single_action(obs)[0]
                self.execute_action(agent_id, action, snapshot)
        
        results = self.calculate_results(num_trained_agents)
        self.print_results(results)
        return results
    
    def calculate_results(self, num_trained_agents):
        """Calculate performance metrics."""
        results = {'agents': [], 'summary': {}}
        
        for agent_id in range(self.num_agents):
            portfolio = self.portfolios[agent_id]
            
            final_nav = float(portfolio['nav'])
            total_pnl = final_nav - self.init_cash
            return_pct = (total_pnl / self.init_cash) * 100
            num_trades = len(portfolio['trades'])
            
            if len(portfolio['pnl_history']) > 1:
                # Convert to numpy array of floats to ensure homogeneous data
                pnl_array = np.array([float(x) for x in portfolio['pnl_history']], dtype=np.float64)
                returns = np.diff(pnl_array)
                sharpe = np.mean(returns) / (np.std(returns) + 1e-9) * np.sqrt(252)
            else:
                sharpe = 0
            
            agent_type = "PPO (trained)" if agent_id < num_trained_agents else "Random"
            
            # Convert nav_history to proper numpy array
            nav_history = [float(x) for x in portfolio['nav_history']] if portfolio['nav_history'] else [self.init_cash]
            
            agent_result = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'final_nav': final_nav,
                'total_pnl': total_pnl,
                'return_pct': return_pct,
                'num_trades': num_trades,
                'sharpe_ratio': sharpe,
                'nav_history': nav_history,
                'trades': portfolio['trades']
            }
            
            results['agents'].append(agent_result)
        
        ppo_results = [r for r in results['agents'] if r['agent_type'] == "PPO (trained)"]
        random_results = [r for r in results['agents'] if r['agent_type'] == "Random"]
        
        results['summary'] = {
            'avg_ppo_return': np.mean([r['return_pct'] for r in ppo_results]) if ppo_results else 0,
            'avg_random_return': np.mean([r['return_pct'] for r in random_results]) if random_results else 0,
            'best_agent': max(results['agents'], key=lambda x: x['final_nav']),
            'worst_agent': min(results['agents'], key=lambda x: x['final_nav'])
        }
        
        return results
    
    def print_results(self, results):
        """Print results."""
        print(f"\n{'='*80}")
        print(f"📊 Backtest Results Summary")
        print(f"{'='*80}\n")
        
        print(f"Initial Capital: ${self.init_cash:,.2f}\n")
        
        print(f"{'Agent':<15} {'Type':<20} {'Final NAV':<15} {'PnL':<15} {'Return %':<12} {'Trades':<10} {'Sharpe':<10}")
        print(f"{'-'*105}")
        
        for agent in results['agents']:
            print(f"Agent {agent['agent_id']:<8} "
                  f"{agent['agent_type']:<20} "
                  f"${agent['final_nav']:>13,.2f} "
                  f"${agent['total_pnl']:>13,.2f} "
                  f"{agent['return_pct']:>10.2f}% "
                  f"{agent['num_trades']:>9} "
                  f"{agent['sharpe_ratio']:>9.2f}")
        
        print(f"\n{'-'*105}")
        print(f"\n🏆 Best Agent: Agent {results['summary']['best_agent']['agent_id']} "
              f"({results['summary']['best_agent']['agent_type']}) - "
              f"${results['summary']['best_agent']['final_nav']:,.2f}")
        
        print(f"\n📈 Average Returns:")
        print(f"  PPO Agents: {results['summary']['avg_ppo_return']:.2f}%")
        print(f"  Random Agents: {results['summary']['avg_random_return']:.2f}%")
        
        if results['summary']['avg_ppo_return'] > results['summary']['avg_random_return']:
            diff = results['summary']['avg_ppo_return'] - results['summary']['avg_random_return']
            print(f"\n✅ PPO agents outperformed random agents by {diff:.2f}%!")
        else:
            diff = results['summary']['avg_random_return'] - results['summary']['avg_ppo_return']
            print(f"\n⚠️ Random agents outperformed PPO agents by {diff:.2f}%")


def plot_results(backtest_results, init_cash):
    """Plot backtest results."""
    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    
    # Plot 1: NAV History
    ax1 = axes[0, 0]
    for agent in backtest_results['agents']:
        label = f"Agent {agent['agent_id']} ({agent['agent_type']})"
        color = 'blue' if 'PPO' in agent['agent_type'] else 'gray'
        linewidth = 2 if 'PPO' in agent['agent_type'] else 1
        alpha = 0.8 if 'PPO' in agent['agent_type'] else 0.5
        
        ax1.plot(agent['nav_history'], label=label, color=color, linewidth=linewidth, alpha=alpha)
    
    ax1.axhline(y=init_cash, color='red', linestyle='--', label='Initial Capital', linewidth=2)
    ax1.set_xlabel('Time Steps')
    ax1.set_ylabel('Net Asset Value ($)')
    ax1.set_title('NAV History - All Agents')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Final Returns
    ax2 = axes[0, 1]
    agent_ids = [a['agent_id'] for a in backtest_results['agents']]
    returns = [a['return_pct'] for a in backtest_results['agents']]
    colors = ['blue' if a['agent_type'] == 'PPO (trained)' else 'gray' for a in backtest_results['agents']]
    
    bars = ax2.bar(agent_ids, returns, color=colors, alpha=0.7)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax2.set_xlabel('Agent ID')
    ax2.set_ylabel('Return (%)')
    ax2.set_title('Final Returns by Agent')
    ax2.set_xticks(agent_ids)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, ret in zip(bars, returns):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{ret:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
    
    # Plot 3: Number of Trades
    ax3 = axes[1, 0]
    num_trades = [a['num_trades'] for a in backtest_results['agents']]
    bars = ax3.bar(agent_ids, num_trades, color=colors, alpha=0.7)
    ax3.set_xlabel('Agent ID')
    ax3.set_ylabel('Number of Trades')
    ax3.set_title('Trading Activity by Agent')
    ax3.set_xticks(agent_ids)
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, trades in zip(bars, num_trades):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{trades}', ha='center', va='bottom', fontsize=9)
    
    # Plot 4: Sharpe Ratios
    ax4 = axes[1, 1]
    sharpe_ratios = [a['sharpe_ratio'] for a in backtest_results['agents']]
    bars = ax4.bar(agent_ids, sharpe_ratios, color=colors, alpha=0.7)
    ax4.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax4.set_xlabel('Agent ID')
    ax4.set_ylabel('Sharpe Ratio')
    ax4.set_title('Risk-Adjusted Returns (Sharpe Ratio)')
    ax4.set_xticks(agent_ids)
    ax4.grid(True, alpha=0.3, axis='y')
    
    for bar, sharpe in zip(bars, sharpe_ratios):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{sharpe:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    return fig

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST MODULE - Import this in your notebook instead of running directly")
    print("="*80)
    print("\nExample usage:")
    print("""
    from test_on_real_data import *
    
    # Fetch data
    market_data = fetch_market_data("AAPL", "5d", "1m")
    order_book_data = simulate_order_book_from_market_data(market_data, tape_display_length)
    
    # Load your trained model
    checkpoints = glob.glob(os.path.join(local_dir, "checkpoint_*"))
    if checkpoints:
        latest = sorted(checkpoints, key=lambda x: int(x.split('_')[-1]))[-1]
        checkpoint_num = latest.split('_')[-1]
        checkpoint_path = os.path.join(latest, f"checkpoint-{checkpoint_num}")
        
        test_config = get_config()
        test_trainer = test_config.build()
        test_trainer.restore(checkpoint_path)
        
        # Run backtest
        backtester = RealMarketBacktester(test_trainer, num_agents, init_cash, tape_display_length)
        results = backtester.run_backtest(order_book_data, num_trained_agent)
        plot_results(results, init_cash)
    else:
        print("No checkpoints found. Train your model first!")
    """)