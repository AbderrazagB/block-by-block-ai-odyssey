"""A one-observation execution-delay sensitivity check for a fixed policy."""

import numpy as np
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv


def delayed_backtest(model, normalization_path, test_df, env_kwargs):
    """Decide at close t, execute that fixed action at close t+1.

    The first step executes zero orders. The decision uses only the current raw
    observation and frozen training normalization. No future observation enters
    model.predict. This changes execution at evaluation, not policy training.
    """
    environment = StockTradingEnv(df=test_df, **env_kwargs)
    wrapper = DummyVecEnv([lambda: environment])
    normalizer = VecNormalize.load(str(normalization_path), wrapper)
    normalizer.training = False
    normalizer.norm_reward = False
    obs, _ = environment.reset()
    pending = np.zeros(env_kwargs["stock_dim"], dtype=np.float32)
    done = False
    while not done:
        normalized = normalizer.normalize_obs(np.asarray(obs, dtype=np.float32).reshape(1, -1))
        next_order, _ = model.predict(normalized, deterministic=True)
        result = environment.step(pending)
        obs, _, terminated, truncated, _ = result
        done = terminated or truncated
        pending = next_order[0]
    fills = np.asarray(environment.actions_memory)
    return environment.save_asset_memory().copy(), {
        "execution": "Decision at close t; order executes at next observation close",
        "initial_action": "Zero orders; capital remains cash on first step",
        "total_transaction_cost_usd": float(environment.cost),
        "environment_trade_counter": int(environment.trades),
        "nonzero_filled_order_events": int(np.count_nonzero(fills)),
        "filled_buy_events": int(np.count_nonzero(fills > 0)),
        "filled_sell_events": int(np.count_nonzero(fills < 0)),
        "dates_with_filled_orders": int(np.count_nonzero(np.any(fills != 0, axis=1))),
        "counter_note": "Upstream trade counter may include attempted orders with zero fill; nonzero action-memory entries count filled symbol/day orders.",
        "limitations": "Policy was trained with same-close execution; delay is a sensitivity check, not retraining. Ignores slippage/dividend cash flows and uses the same selected universe.",
    }
