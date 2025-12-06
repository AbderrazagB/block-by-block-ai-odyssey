"""
Train PPO agents on real market data (AAPL + NVDA).
This script trains agents directly on historical stock prices.
"""
import os
import sys
import warnings

# Suppress warnings
os.environ['RAY_DEBUG_DISABLE_MEMORY_MONITOR'] = "True"
os.environ['PYTHONWARNINGS'] = "ignore::DeprecationWarning"
os.environ['RAY_DISABLE_MEMORY_MONITOR'] = "1"
os.environ['RAY_DEDUP_LOGS'] = "0"
warnings.filterwarnings('ignore', category=DeprecationWarning)

sys.path.append('./')
sys.path.append('./gym_continuousDoubleAuction')

import numpy as np
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig

from gym_continuousDoubleAuction.train_on_real_data import create_real_market_env


# ============================================================================
# CONFIGURATION
# ============================================================================

# Stocks to train on
TRAIN_TICKERS = ["AAPL", "NEE"]  # Training on AAPL and NEE 6-month data

# Training parameters
num_iters = 100  # IMPROVED: Reduced to prevent overfitting (was 200)
chkpt_freq = 20
init_cash = 10000
tape_display_length = 10
max_steps = 250  # Steps per episode

# Ray resources
num_gpus = 0
num_workers = 2  # Parallel environments
num_envs_per_worker = 2

# Paths
log_base_dir = os.path.join(os.getcwd(), "gym_continuousDoubleAuction/results/")
real_data_dir = os.path.join(log_base_dir, "real_data_training/")
checkpoint_dir = os.path.join(real_data_dir, "checkpoints/")

# Create directories
os.makedirs(real_data_dir, exist_ok=True)
os.makedirs(checkpoint_dir, exist_ok=True)


# ============================================================================
# TRAINING
# ============================================================================

def train_on_real_market_data():
    """Train PPO agent on real market data."""
    print("\n" + "="*80)
    print(f"TRAINING PPO ON REAL MARKET DATA: {', '.join(TRAIN_TICKERS)}")
    print("="*80 + "\n")
    
    # Initialize Ray
    ray.init(
        ignore_reinit_error=True,
        log_to_driver=True,
        num_cpus=num_workers + 2,
        num_gpus=num_gpus,
        include_dashboard=False,
    )
    
    # Register environment
    register_env("real_market_cda", create_real_market_env)
    
    # Configure PPO
    config = (
        PPOConfig()
        .api_stack(
            enable_rl_module_and_learner=False,
            enable_env_runner_and_connector_v2=False,
        )
        .environment(
            env="real_market_cda",
            env_config={
                'tickers': TRAIN_TICKERS,
                'tape_display_length': tape_display_length,
                'init_cash': init_cash,
                'max_steps': max_steps,
            }
        )
        .framework("torch")
        .resources(num_gpus=num_gpus)
        .env_runners(
            num_env_runners=num_workers,
            num_envs_per_env_runner=num_envs_per_worker,
            batch_mode="complete_episodes",
        )
        .training(
            train_batch_size_per_learner=4096,  # Larger batch for stability
            minibatch_size=256,
            lr=1e-4,  # IMPROVED: Lower LR to prevent overfitting (was 3e-4)
            gamma=0.95,  # IMPROVED: Lower gamma for shorter-term focus (was 0.99)
            lambda_=0.95,
            clip_param=0.2,
            vf_clip_param=10.0,
            entropy_coeff=0.05,  # IMPROVED: Higher entropy to encourage exploration (was 0.01)
            num_sgd_iter=5,  # IMPROVED: Fewer updates to prevent overfitting (was 10)
        )
        .debugging(log_level="WARN")
        .reporting(min_sample_timesteps_per_iteration=2000)
    )
    
    # Build trainer
    print("Building PPO trainer...")
    trainer = config.build()
    
    # Training loop
    reward_history = []
    best_reward = float('-inf')
    
    print(f"\nStarting training for {num_iters} iterations...")
    print("="*80 + "\n")
    
    for i in range(num_iters):
        print(f"{'='*80}")
        print(f"Iteration {i+1}/{num_iters}")
        print(f"{'='*80}")
        
        result = trainer.train()
        
        # Extract metrics
        episode_reward_mean = result.get('env_runners', {}).get('episode_reward_mean', 0)
        episode_len_mean = result.get('env_runners', {}).get('episode_len_mean', 0)
        
        reward_history.append(episode_reward_mean)
        
        if episode_reward_mean > best_reward:
            best_reward = episode_reward_mean
            print(f"🎉 New best reward: {best_reward:,.4f}")
        
        # Print metrics
        print(f"\n📊 Metrics:")
        print(f"  Episode reward mean: {episode_reward_mean:,.4f}")
        print(f"  Episode length mean: {episode_len_mean:.1f}")
        print(f"  Best reward so far: {best_reward:,.4f}")
        
        if len(reward_history) >= 10:
            recent_avg = np.mean(reward_history[-10:])
            print(f"  Recent avg (last 10): {recent_avg:,.4f}")
        
        # Save checkpoint
        if (i + 1) % chkpt_freq == 0:
            checkpoint_path = trainer.save(checkpoint_dir)
            print(f"\n✓ Checkpoint saved at iteration {i+1}")
            print(f"  Path: {checkpoint_path.checkpoint.path}")
        
        print()
    
    # Final checkpoint
    final_checkpoint = trainer.save(checkpoint_dir)
    print(f"\n{'='*80}")
    print("✅ TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"\n📈 Training Summary:")
    print(f"  Total iterations: {num_iters}")
    print(f"  Initial reward: {reward_history[0]:,.4f}")
    print(f"  Final reward: {reward_history[-1]:,.4f}")
    print(f"  Best reward: {best_reward:,.4f}")
    print(f"  Improvement: {reward_history[-1] - reward_history[0]:,.4f}")
    print(f"\n💾 Final checkpoint: {final_checkpoint.checkpoint.path}")
    print(f"{'='*80}\n")
    
    trainer.stop()
    ray.shutdown()
    
    return final_checkpoint.checkpoint.path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train PPO on real market data")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "NVDA"],
                        help="Stock tickers to train on")
    parser.add_argument("--iterations", type=int, default=200,
                        help="Number of training iterations")
    args = parser.parse_args()
    
    TRAIN_TICKERS = args.tickers
    num_iters = args.iterations
    
    try:
        checkpoint_path = train_on_real_market_data()
        print(f"\n🎯 Use this checkpoint for testing:")
        print(f"   python test_real_trained_model.py --checkpoint {checkpoint_path}")
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ray.is_initialized():
            ray.shutdown()
