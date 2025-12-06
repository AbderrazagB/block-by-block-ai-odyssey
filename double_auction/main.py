"""
Complete training and backtesting pipeline for Continuous Double Auction PPO agents.
Train agents on simulated environment, then test them on real market data.
"""
import os
import sys
import glob
import time
import warnings

# Suppress warnings
os.environ['RAY_DEBUG_DISABLE_MEMORY_MONITOR'] = "True"
os.environ['PYTHONWARNINGS'] = "ignore::DeprecationWarning"
os.environ['RAY_DISABLE_MEMORY_MONITOR'] = "1"
os.environ['RAY_DEDUP_LOGS'] = "0"
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Add paths
sys.path.append('./')
sys.path.append('./gym_continuousDoubleAuction')

import numpy as np
import gymnasium as gym
from typing import Dict
from collections import defaultdict

import ray
from ray.tune.registry import register_env
from ray.rllib.models import ModelCatalog
from ray.rllib.policy.policy import PolicySpec
from ray.rllib.algorithms.ppo import PPO, PPOConfig
from ray.rllib.env import BaseEnv
from ray.rllib.policy import Policy
from ray.rllib.algorithms.callbacks import DefaultCallbacks

import gym_continuousDoubleAuction
from gym_continuousDoubleAuction.envs import continuousDoubleAuctionEnv
from gym_continuousDoubleAuction.train.logger.log_handler import *
from gym_continuousDoubleAuction.train.storage.store_handler import storage
from gym_continuousDoubleAuction.train.policy.policy_handler import gen_policy, set_agents_policies
from gym_continuousDoubleAuction.train.model.model_handler import CustomModel_1
from gym_continuousDoubleAuction.train.callbk.callbk_handler import store_eps_hist_data
from gym_continuousDoubleAuction.train.weight.weight_handler import get_trained_policies_name, get_max_reward_ind, cp_weight

import matplotlib.pyplot as plt
from gym_continuousDoubleAuction.train.plotter.plot_handler import plot_storage

# Import backtesting functions
from gym_continuousDoubleAuction.test_on_real_data import (
    fetch_market_data,
    simulate_order_book_from_market_data,
    RealMarketBacktester,
    plot_results
)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Environment parameters
num_of_traders = 8
num_agents = num_of_traders
init_cash = 10000
tick_size = 1
tape_display_length = 10
max_step = 128
render_mode = None

# Training parameters
num_trained_agent = 2
num_iters = 150  # IMPROVED FOR BETTER LEARNING (increased from 100)

# Ray resources
num_gpus = 0
num_workers = 1
num_envs_per_worker = 2

# Paths
log_base_dir = os.path.join(os.getcwd(), "gym_continuousDoubleAuction/results/")
log_dir = os.path.join(log_base_dir, "ray_results/")
local_dir = os.path.join(log_base_dir, "chkpt/")
log_g_store_dir = os.path.join(log_base_dir, "log_g_store/")

# Checkpoint settings
chkpt_freq = 10  # IMPROVED: Save every 25 iterations (was 10)
is_restore = False

# Create directories
create_dir(log_base_dir)
create_dir(log_g_store_dir)


# ============================================================================
# CALLBACKS
# ============================================================================

class MyCallbacks(DefaultCallbacks):
    def on_episode_start(self, worker, base_env: BaseEnv,
                         policies: Dict[str, Policy],
                         episode, **kwargs):
        prefix = "agt_"
        for i in range(num_agents):
            episode.user_data[f"{prefix}{i}_obs"] = []
            episode.user_data[f"{prefix}{i}_act"] = []
            episode.user_data[f"{prefix}{i}_reward"] = []
            episode.user_data[f"{prefix}{i}_NAV"] = []
            episode.user_data[f"{prefix}{i}_num_trades"] = []
            
            episode.hist_data[f"{prefix}{i}_reward"] = []
            episode.hist_data[f"{prefix}{i}_NAV"] = []
            episode.hist_data[f"{prefix}{i}_num_trades"] = []

    def on_episode_step(self, worker, base_env: BaseEnv,
                        episode, **kwargs):
        prefix = "agt_"
        for i in range(num_agents):
            try:
                obs = episode.last_observation_for(i)
            except (AttributeError, KeyError):
                continue
            
            try:
                act = episode.last_action_for(i)
            except (AttributeError, KeyError):
                continue
            
            info = episode.last_info_for(i)
            if info is None or not info:
                continue
                
            reward = info.get("reward")
            if reward is None:
                continue
                
            NAV = info.get("NAV")
            NAV = None if NAV is None else float(NAV)
            num_trades = info.get("num_trades")
            
            episode.user_data[f"{prefix}{i}_obs"].append(obs)
            episode.user_data[f"{prefix}{i}_act"].append(act)
            episode.user_data[f"{prefix}{i}_reward"].append(reward)
            episode.user_data[f"{prefix}{i}_NAV"].append(NAV)
            episode.user_data[f"{prefix}{i}_num_trades"].append(num_trades)

    def on_episode_end(self, worker, base_env: BaseEnv,
                       policies: Dict[str, Policy], episode, **kwargs):
        g_store = ray.get_actor("g_store")
        prefix = "agt_"
        
        for agt_id in range(num_agents):
            obs_key = f"{prefix}{agt_id}_obs"
            act_key = f"{prefix}{agt_id}_act"
            reward_key = f"{prefix}{agt_id}_reward"
            NAV_key = f"{prefix}{agt_id}_NAV"
            num_trades_key = f"{prefix}{agt_id}_num_trades"
            
            store_eps_hist_data(episode, reward_key)
            store_eps_hist_data(episode, NAV_key)
            store_eps_hist_data(episode, num_trades_key)
            
            obs = episode.user_data.get(obs_key, [])
            act = episode.user_data.get(act_key, [])
            reward = episode.user_data.get(reward_key, [])
            NAV = episode.user_data.get(NAV_key, [])
            num_trades = episode.user_data.get(num_trades_key, [])
            
            if obs:
                ray.get(g_store.store_agt_step.remote(agt_id, obs, act, reward, NAV, num_trades))
            
            if reward:
                eps_reward = np.sum(reward)
                eps_NAV = np.sum([n for n in NAV if n is not None])
                eps_num_trades = np.sum([n for n in num_trades if n is not None])
                ray.get(g_store.store_agt_eps.remote(agt_id, eps_reward, eps_NAV, eps_num_trades))
        
        ray.get(g_store.inc_eps_counter.remote())

    def on_train_result(self, algorithm, result: dict, **kwargs):
        result["callback_ok"] = True
        
        train_policies_name = get_trained_policies_name(policies, num_trained_agent)
        
        policy_rewards = []
        for policy_name in train_policies_name:
            reward = 0.0
            if "env_runners" in result:
                if "policy_reward_mean" in result["env_runners"]:
                    policy_stats = result["env_runners"]["policy_reward_mean"]
                    reward = policy_stats.get(policy_name, 0.0)
                elif "episode_reward_mean" in result["env_runners"]:
                    reward = result["env_runners"].get("episode_reward_mean", 0.0)
            
            policy_rewards.append(reward)
        
        if policy_rewards:
            max_reward_ind = np.argmax(policy_rewards)
            max_reward_policy_name = train_policies_name[max_reward_ind]
            cp_weight(algorithm, train_policies_name, max_reward_policy_name)
        
        g_store = ray.get_actor("g_store")
        for agt_id, reward in enumerate(policy_rewards):
            if agt_id < num_agents:
                ray.get(g_store.store_agt_train.remote(agt_id, reward))


# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def get_config(policies):
    """Create PPO configuration with improved learning rate."""
    improved_lr = 5e-5  # IMPROVED: Increased from 5e-5 for faster learning with 500 iterations
    
    for policy_name, policy_spec in policies.items():
        if hasattr(policy_spec, 'config') and policy_spec.config is not None:
            policy_spec.config["lr"] = improved_lr
    
    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=False,
            enable_env_runner_and_connector_v2=False,
        )
        .environment(env="continuousDoubleAuction-v0")
        .framework("torch")
        .multi_agent(
            policies=policies,
            policy_mapping_fn=lambda agent_id, episode=None, worker=None, **kwargs: f"policy_{agent_id}",
            policies_to_train=[f"policy_{i}" for i in range(num_trained_agent)],
        )
        .resources(num_gpus=num_gpus)
        .env_runners(
            num_env_runners=num_workers,
            num_envs_per_env_runner=num_envs_per_worker,
            batch_mode="complete_episodes",
        )
        .training(
            train_batch_size_per_learner=2048,
            minibatch_size=128,  # IMPROVED: Reduced from 256 for more granular updates
            lr=improved_lr,  # IMPROVED: 3e-4 (was 5e-5)
            gamma=0.99,
            lambda_=0.95,
            clip_param=0.2,
            vf_clip_param=10.0,
            entropy_coeff=0.01,
            num_sgd_iter=10,  # Number of SGD iterations per training batch
        )
        .callbacks(MyCallbacks)
        .debugging(log_level="WARN")
        .reporting(min_sample_timesteps_per_iteration=1000)
    )
    
    return config


def train_agents():
    """Train PPO agents."""
    print("\n" + "="*80)
    print("TRAINING PPO AGENTS")
    print("="*80)
    
    # Setup environment
    single_CDA_env = continuousDoubleAuctionEnv(
        num_of_traders, init_cash, tick_size, 
        tape_display_length, max_step, render_mode
    )
    obs_space = single_CDA_env.observation_space
    act_space = single_CDA_env.action_space
    
    def env_creator(env_config):
        return continuousDoubleAuctionEnv(
            num_of_traders, init_cash, tick_size,
            tape_display_length, max_step - 1, render_mode
        )
    
    register_env("continuousDoubleAuction-v0", env_creator)
    ModelCatalog.register_custom_model("model_disc", CustomModel_1)
    
    # Initialize Ray
    ray.init(
        ignore_reinit_error=True,
        log_to_driver=True,
        num_cpus=4,
        num_gpus=num_gpus,
        include_dashboard=False,
        _metrics_export_port=None,
    )
    
    # Initialize storage
    try:
        g_store = ray.get_actor("g_store")
        print("Using existing g_store actor")
    except ValueError:
        g_store = storage.options(name="g_store", lifetime="detached").remote(num_agents)
        print("Created new g_store actor")
    
    # Generate policies
    global policies
    policies = {f"policy_{i}": gen_policy(i, obs_space, act_space) for i in range(num_agents)}
    set_agents_policies(policies, obs_space, act_space, num_agents, num_trained_agent)
    
    # Build trainer
    config = get_config(policies)
    trainer = config.build()
    
    # Training loop
    reward_history = []
    best_reward = float('-inf')
    
    for i in range(num_iters):
        print(f"\n{'='*80}")
        print(f"Training iteration {i+1}/{num_iters}")
        print(f"{'='*80}\n")
        
        result = trainer.train()
        
        episode_reward_mean = result.get('env_runners', {}).get('episode_reward_mean', 0)
        episodes_sampled = ray.get(g_store.get_eps_counter.remote())
        
        reward_history.append(episode_reward_mean)
        if episode_reward_mean > best_reward:
            best_reward = episode_reward_mean
            print(f"🎉 New best reward: {best_reward:,.2f}")
        
        print(f"\n📊 Metrics:")
        print(f"  Episodes sampled: {episodes_sampled}")
        print(f"  Episode reward mean: {episode_reward_mean:,.2f}")
        print(f"  Best reward so far: {best_reward:,.2f}")
        
        if len(reward_history) >= 5:
            recent_avg = np.mean(reward_history[-5:])
            print(f"  Recent avg (last 5): {recent_avg:,.2f}")
        
        if "env_runners" in result and "policy_reward_mean" in result["env_runners"]:
            policy_rewards = result["env_runners"]["policy_reward_mean"]
            print(f"\n  Policy rewards:")
            for policy_name, reward in policy_rewards.items():
                print(f"    {policy_name}: {reward:,.2f}")
        
        if (i + 1) % chkpt_freq == 0:
            checkpoint_path = trainer.save(local_dir)
            print(f"\n✓ Checkpoint saved at iteration {i+1}")
    
    # Final checkpoint
    checkpoint_path = trainer.save(local_dir)
    print(f"\n✓ Final checkpoint saved at: {checkpoint_path.checkpoint.path}")
    
    print(f"\n{'='*80}")
    print(f"📈 Training Summary:")
    print(f"  Total iterations: {num_iters}")
    print(f"  Total episodes: {episodes_sampled}")
    print(f"  Initial reward: {reward_history[0]:,.2f}")
    print(f"  Final reward: {reward_history[-1]:,.2f}")
    print(f"  Best reward: {best_reward:,.2f}")
    print(f"  Improvement: {reward_history[-1] - reward_history[0]:,.2f}")
    print(f"{'='*80}\n")
    
    # Generate plots
    print("\nGenerating training plots...")
    import importlib
    from gym_continuousDoubleAuction.train.plotter import plot_handler
    importlib.reload(plot_handler)
    from gym_continuousDoubleAuction.train.plotter.plot_handler import plot_storage
    
    plot_storage(num_agents, init_cash, "eps", "reward")
    plot_storage(num_agents, init_cash, "eps", "NAV")
    plot_storage(num_agents, init_cash, "eps", "num_trades")
    
    trainer.stop()
    return checkpoint_path.checkpoint.path


def backtest_on_real_data(checkpoint_path, ticker="NVDA"):
    """Backtest trained agents on real market data."""
    print("\n" + "="*80)
    print(f"BACKTESTING ON REAL MARKET DATA - {ticker}")
    print("="*80)
    
    # Fetch real market data from AlphaVantage
    market_data = None
    
    # Try different data sources in order of preference
    options = [
        ("full", "daily", "Full year+ data (daily)"),
        ("compact", "daily", "Last 100 days (daily)"),
        ("compact", "weekly", "Last 100 weeks (weekly)"),
    ]
    
    print(f"\n💡 Using AlphaVantage API (free tier: 25 requests/day)")
    print(f"   Set ALPHAVANTAGE_API_KEY env variable for your own key\n")
    
    for period, interval, desc in options:
        print(f"\nAttempting: {desc}...")
        market_data = fetch_market_data(ticker=ticker, period=period, interval=interval)
        if market_data is not None and len(market_data) > 0:
            print(f"✓ Successfully fetched {len(market_data)} data points")
            break
        print(f"  Failed, trying next option...")
        time.sleep(1)  # Rate limiting
    
    if market_data is None or len(market_data) == 0:
        print("\n❌ Failed to fetch market data from all sources")
        print("Possible issues:")
        print("  - Network connectivity")
        print("  - AlphaVantage API rate limit reached (25 requests/day)")
        print("  - Invalid API key")
        print("\nSolutions:")
        print("  - Get free API key at: https://www.alphavantage.co/support/#api-key")
        print("  - Set environment variable: export ALPHAVANTAGE_API_KEY=your_key")
        print("  - Wait a few minutes and try again")
        return
    
    # Simulate order book
    order_book_data = simulate_order_book_from_market_data(market_data, depth=tape_display_length)
    print(f"✓ Generated {len(order_book_data)} order book snapshots\n")
    
    # Setup environment for loading checkpoint
    single_CDA_env = continuousDoubleAuctionEnv(
        num_of_traders, init_cash, tick_size,
        tape_display_length, max_step, render_mode
    )
    obs_space = single_CDA_env.observation_space
    act_space = single_CDA_env.action_space
    
    def env_creator(env_config):
        return continuousDoubleAuctionEnv(
            num_of_traders, init_cash, tick_size,
            tape_display_length, max_step - 1, render_mode
        )
    
    register_env("continuousDoubleAuction-v0", env_creator)
    
    # Generate policies
    test_policies = {f"policy_{i}": gen_policy(i, obs_space, act_space) for i in range(num_agents)}
    set_agents_policies(test_policies, obs_space, act_space, num_agents, num_trained_agent)
    
    # Build and restore trainer
    config = get_config(test_policies)
    test_trainer = config.build()
    
    print(f"Loading checkpoint: {checkpoint_path}")
    test_trainer.restore(checkpoint_path)
    print("✓ Checkpoint restored!\n")
    
    # Run backtest
    backtester = RealMarketBacktester(
        trainer=test_trainer,
        num_agents=num_agents,
        init_cash=init_cash,
        tape_display_length=tape_display_length
    )
    
    backtest_results = backtester.run_backtest(
        order_book_data,
        num_trained_agents=num_trained_agent,
        verbose=True
    )
    
    # Plot results
    print("\n📊 Generating backtest visualizations...")
    plot_results(backtest_results, init_cash)
    
    test_trainer.stop()
    print("\n✓ Backtest complete!")
    
    return backtest_results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train and backtest PPO trading agents")
    parser.add_argument("--skip-training", action="store_true", help="Skip training and only run backtest")
    parser.add_argument("--checkpoint", type=str, help="Path to checkpoint for backtest")
    args = parser.parse_args()
    
    try:
        if args.skip_training:
            # Only run backtest
            if args.checkpoint:
                # Convert to absolute path if relative
                checkpoint_path = os.path.abspath(args.checkpoint)
            else:
                # Find latest checkpoint
                checkpoints = glob.glob(os.path.join(local_dir, "checkpoint_*"))
                if not checkpoints:
                    print("❌ No checkpoints found. Train first or specify --checkpoint")
                    sys.exit(1)
                
                latest = sorted(checkpoints, key=lambda x: int(x.split('_')[-1]))[-1]
                checkpoint_num = latest.split('_')[-1]
                checkpoint_path = os.path.join(latest, f"checkpoint-{checkpoint_num}")
            
            backtest_on_real_data(checkpoint_path)
        else:
            # Full pipeline: train then backtest
            print("Starting full training and backtesting pipeline...")
            checkpoint_path = train_agents()
            
            print("\n" + "="*80)
            print("Training complete! Starting backtest...")
            print("="*80)
            
            backtest_on_real_data(checkpoint_path)
        
        print("\n" + "="*80)
        print("✅ ALL DONE!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ray.is_initialized():
            ray.shutdown()