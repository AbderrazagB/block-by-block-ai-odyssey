"""
Test PPO agent trained on real market data.
Load checkpoint and backtest on new stock data.
"""
import os
import sys
import warnings
import argparse

os.environ['RAY_DEBUG_DISABLE_MEMORY_MONITOR'] = "True"
os.environ['PYTHONWARNINGS'] = "ignore::DeprecationWarning"
warnings.filterwarnings('ignore', category=DeprecationWarning)

sys.path.append('./')
sys.path.append('./gym_continuousDoubleAuction')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPO

from gym_continuousDoubleAuction.train_on_real_data import create_real_market_env, RealMarketCDAEnv


def test_trained_agent(checkpoint_path, test_ticker="AAPL", num_episodes=5):
    """Test trained agent on new stock data."""
    print("\n" + "="*80)
    print(f"TESTING TRAINED AGENT ON {test_ticker}")
    print("="*80 + "\n")
    
    # Initialize Ray
    ray.init(ignore_reinit_error=True, log_to_driver=False)
    
    # Register environment
    register_env("real_market_cda", create_real_market_env)
    
    # Create test environment (will fetch from AlphaVantage)
    print(f"Loading {test_ticker} data from AlphaVantage...")
    test_env = RealMarketCDAEnv(
        tickers=[test_ticker],
        tape_display_length=10,
        init_cash=10000,
        max_steps=250,
        use_cached_data=None  # Force fresh fetch from AlphaVantage
    )
    
    # Load trained agent
    print(f"\nLoading checkpoint: {checkpoint_path}")
    agent = PPO.from_checkpoint(checkpoint_path)
    print("✓ Agent loaded!\n")
    
    # Run test episodes
    all_results = []
    
    for episode in range(num_episodes):
        print(f"{'='*80}")
        print(f"Episode {episode + 1}/{num_episodes}")
        print(f"{'='*80}")
        
        # Use different seed for each episode to vary starting conditions
        obs, info = test_env.reset(seed=episode + 42)
        done = False
        truncated = False
        episode_reward = 0
        step = 0
        
        while not (done or truncated):
            # Get action from trained agent (with exploration for variety)
            action = agent.compute_single_action(obs, explore=True)
            
            # Take step
            obs, reward, done, truncated, info = test_env.step(action)
            episode_reward += reward
            step += 1
            
            if step % 50 == 0:
                print(f"  Step {step}: NAV=${info['NAV']:,.2f}, Trades={info['num_trades']}")
        
        # Episode results
        final_nav = info['NAV']
        num_trades = info['num_trades']
        pnl = final_nav - 10000
        return_pct = (pnl / 10000) * 100
        
        print(f"\n📊 Episode {episode + 1} Results:")
        print(f"  Final NAV: ${final_nav:,.2f}")
        print(f"  PnL: ${pnl:,.2f}")
        print(f"  Return: {return_pct:.2f}%")
        print(f"  Total Trades: {num_trades}")
        print()
        
        all_results.append({
            'episode': episode + 1,
            'final_nav': final_nav,
            'pnl': pnl,
            'return_pct': return_pct,
            'num_trades': num_trades,
            'nav_history': test_env.nav_history.copy(),
            'trade_history': test_env.trade_history.copy()
        })
    
    # Summary
    print(f"{'='*80}")
    print("📈 OVERALL RESULTS")
    print(f"{'='*80}\n")
    
    avg_return = np.mean([r['return_pct'] for r in all_results])
    avg_trades = np.mean([r['num_trades'] for r in all_results])
    best_return = max([r['return_pct'] for r in all_results])
    worst_return = min([r['return_pct'] for r in all_results])
    
    print(f"Test Stock: {test_ticker}")
    print(f"Episodes: {num_episodes}")
    print(f"\nAverage Return: {avg_return:.2f}%")
    print(f"Best Return: {best_return:.2f}%")
    print(f"Worst Return: {worst_return:.2f}%")
    print(f"Average Trades per Episode: {avg_trades:.1f}")
    print()
    
    # Plot results
    plot_test_results(all_results, test_ticker)
    
    agent.stop()
    ray.shutdown()
    
    return all_results


def plot_test_results(results, ticker):
    """Plot test episode results."""
    num_episodes = len(results)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'PPO Agent Test Results on {ticker}', fontsize=16, fontweight='bold')
    
    # 1. NAV over time for all episodes
    ax1 = axes[0, 0]
    for i, result in enumerate(results):
        nav_history = result['nav_history']
        ax1.plot(nav_history, label=f"Episode {i+1}", alpha=0.7)
    ax1.axhline(y=10000, color='red', linestyle='--', alpha=0.5, label='Initial Capital')
    ax1.set_title('NAV Over Time')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('NAV ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Returns per episode
    ax2 = axes[0, 1]
    returns = [r['return_pct'] for r in results]
    colors = ['green' if r > 0 else 'red' for r in returns]
    ax2.bar(range(1, num_episodes + 1), returns, color=colors, alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_title('Returns by Episode')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Return (%)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Number of trades per episode
    ax3 = axes[1, 0]
    trades = [r['num_trades'] for r in results]
    ax3.bar(range(1, num_episodes + 1), trades, color='blue', alpha=0.7)
    ax3.set_title('Trades per Episode')
    ax3.set_xlabel('Episode')
    ax3.set_ylabel('Number of Trades')
    ax3.grid(True, alpha=0.3)
    
    # 4. Final NAV distribution
    ax4 = axes[1, 1]
    final_navs = [r['final_nav'] for r in results]
    ax4.hist(final_navs, bins=min(10, num_episodes), color='purple', alpha=0.7, edgecolor='black')
    ax4.axvline(x=10000, color='red', linestyle='--', linewidth=2, label='Initial Capital')
    ax4.set_title('Final NAV Distribution')
    ax4.set_xlabel('Final NAV ($)')
    ax4.set_ylabel('Frequency')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = "gym_continuousDoubleAuction/results/real_data_training/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"test_results_{ticker}.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"📊 Results plot saved: {output_file}")
    
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test trained PPO agent on real market data")
    parser.add_argument("--checkpoint", type=str, required=True,
                        help="Path to checkpoint directory")
    parser.add_argument("--ticker", type=str, default="AAPL",
                        help="Stock ticker to test on")
    parser.add_argument("--episodes", type=int, default=5,
                        help="Number of test episodes")
    args = parser.parse_args()
    
    try:
        checkpoint_path = os.path.abspath(args.checkpoint)
        results = test_trained_agent(
            checkpoint_path=checkpoint_path,
            test_ticker=args.ticker,
            num_episodes=args.episodes
        )
        
        print("\n✅ Testing complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ray.is_initialized():
            ray.shutdown()
