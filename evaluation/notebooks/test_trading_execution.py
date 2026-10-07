"""A known-value fixture for delayed execution; not project performance."""

from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime_vendor"))
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from trading_execution import delayed_backtest


class ExecutionTests(unittest.TestCase):
    def test_first_order_waits_and_uses_next_close_with_fees(self):
        dates = pd.bdate_range("2024-01-02", periods=3)
        rows = []
        for day, (a, b) in enumerate([(10, 20), (11, 22), (9, 18)]):
            for ticker, price in [("A", a), ("B", b)]:
                rows.append({"date": str(dates[day].date()), "tic": ticker,
                             "close": float(price), "macd": 0.25, "day": day})
        frame = pd.DataFrame(rows).set_index("day")
        kwargs = {"hmax": 1, "initial_amount": 100, "num_stock_shares": [0, 0],
                  "buy_cost_pct": [0.01, 0.01], "sell_cost_pct": [0.01, 0.01],
                  "state_space": 7, "stock_dim": 2, "tech_indicator_list": ["macd"],
                  "action_space": 2, "reward_scaling": 1.0}
        class BuyOneShare:
            def __init__(self):
                self.observations = []
            def predict(self, observation, deterministic=True):
                self.observations.append(observation.copy())
                return np.ones((1, 2), dtype=np.float32), None
        policy = BuyOneShare()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "normalizer.pkl"
            env = DummyVecEnv([lambda: StockTradingEnv(df=frame, **kwargs)])
            training_normalizer = VecNormalize(env, norm_obs=False, norm_reward=False)
            training_normalizer.save(str(path))
            accounts, summary = delayed_backtest(policy, path, frame, kwargs)
        # No t0 purchases. The t0 order buys at t1: 11 + 22 + 0.33 fees.
        # At t2: cash 66.67 plus marked-to-market shares 9 + 18 = 93.67.
        np.testing.assert_allclose(accounts.account_value, [100, 100, 93.67])
        self.assertAlmostEqual(summary["total_transaction_cost_usd"], 0.33)
        self.assertEqual(summary["environment_trade_counter"], 2)
        self.assertEqual(summary["nonzero_filled_order_events"], 2)
        self.assertEqual(summary["filled_buy_events"], 2)
        self.assertEqual(summary["filled_sell_events"], 0)
        self.assertEqual(summary["dates_with_filled_orders"], 1)
        np.testing.assert_allclose(policy.observations[0][0, 1:3], [10, 20])
        np.testing.assert_allclose(policy.observations[1][0, 1:3], [11, 22])


if __name__ == "__main__":
    unittest.main()
