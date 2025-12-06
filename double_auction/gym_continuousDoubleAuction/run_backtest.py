"""
Quick test script for backtesting on real Yahoo Finance data.
Run this after training completes.
"""
import os
import sys
import glob

# Add paths
sys.path.append('./')
sys.path.append('../')

# Import everything from test module
from test_on_real_data import (
    fetch_market_data,
    simulate_order_book_from_market_data,
    RealMarketBacktester,
    plot_results
)

# Import training components
from gym_continuousDoubleAuction.train.policy.policy_handler import gen_policy, set_agents_policies
from ray.rllib.algorithms.ppo import PPOConfig
import ray

# Configuration (match your training settings)
num_agents = 8
num_trained_agent = 2
init_cash = 10000
tape_display_length = 10
local_dir = "./results/chkpt/"

# Fetch real market data
print("Step 1: Fetching market data...")
market_data = fetch_market_data(ticker="AAPL", period="5d", interval="1m")

if market_data is None:
    print("Failed to fetch data!")
    sys.exit(1)

# Simulate order book
print("\nStep 2: Simulating order book...")
order_book_data = simulate_order_book_from_market_data(market_data, depth=tape_display_length)
print(f"✓ Generated {len(order_book_data)} snapshots")

# Find checkpoint
print("\nStep 3: Loading trained model...")
checkpoints = glob.glob(os.path.join(local_dir, "checkpoint_*"))

if not checkpoints:
    print(f"❌ No checkpoints found in {local_dir}")
    print("Train your model first!")
    sys.exit(1)

latest_checkpoint = sorted(checkpoints, key=lambda x: int(x.split('_')[-1]))[-1]
checkpoint_num = latest_checkpoint.split('_')[-1]
checkpoint_path = os.path.join(latest_checkpoint, f"checkpoint-{checkpoint_num}")

print(f"Loading: {checkpoint_path}")

# You need to recreate the config - this is a simplified version
# For full functionality, run from the notebook after training
print("\n" + "="*80)
print("NOTE: For best results, run the backtest cells in the notebook")
print("This script is a simplified standalone version")
print("="*80)

print(f"\nMarket data loaded: {len(order_book_data)} snapshots")
print(f"Checkpoint ready: {checkpoint_path}")
print("\nTo run full backtest, use the notebook cells after training!")
