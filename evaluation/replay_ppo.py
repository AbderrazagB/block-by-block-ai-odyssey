"""Reproduce saved PPO evaluation without training another million steps.

Loads the matched policy/VecNormalize pair, verifies the original dated account
series, and audits a one-observation execution delay. No source artifacts or
original training outputs are overwritten.
"""

import json
import os
from pathlib import Path
import sys

import nbformat
import numpy as np
import pandas as pd


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root / "notebooks")
    sys.path.insert(0, str(root / "notebooks"))
    notebook = nbformat.read(root.parent / "RL_model/FinRL_BlockByBlock.ipynb", as_version=4)
    scope = {}
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        if "TOTAL_TIMESTEPS =" in cell.source:
            break
        exec(compile(cell.source, "FinRL_BlockByBlock.ipynb", "exec"), scope)
    source = root / "runs" / "ppo"
    destination = root / "runs" / "ppo-replay"
    destination.mkdir(exist_ok=True)
    scope["PROJECT_PATH"] = str(destination)
    scope["model"] = scope["PPO"].load(source / "trained_ppo_trading_model.zip", device="cuda")
    scope["normalization_path"] = str(source / "trained_ppo_vecnormalize.pkl")
    backtest_cell = next(c.source for c in notebook.cells if c.cell_type == "code"
                         and "test_env = StockTradingEnv" in c.source)
    exec(compile(backtest_cell, "FinRL_Backtest", "exec"), scope)
    comparison_cell = next(c.source for c in notebook.cells if c.cell_type == "code"
                           and "comparison = trading_comparison" in c.source)
    exec(compile(comparison_cell, "FinRL_Comparison", "exec"), scope)
    original = pd.read_csv(source / "dated_backtest.csv", index_col="date", parse_dates=True)
    comparison = scope["comparison"]
    assert original.index.equals(comparison.index)
    np.testing.assert_allclose(original.to_numpy(), comparison.to_numpy(), rtol=1e-9, atol=1e-6)
    from trading_execution import delayed_backtest
    lagged_account, execution = delayed_backtest(scope["model"], scope["normalization_path"],
                                               scope["test_df"], scope["env_kwargs"])
    delayed = scope["trading_comparison"](lagged_account, scope["price_frame"],
                                         scope["INITIAL_AMOUNT"], scope["TRANSACTION_COST_PCT"])
    comparison["PPO: one-observation delay"] = delayed["PPO"]
    metrics = scope["trading_metrics"](comparison, scope["INITIAL_AMOUNT"])
    comparison.to_csv(destination / "execution_sensitivity_accounts.csv", index_label="date")
    metrics.to_csv(destination / "execution_sensitivity_metrics.csv")
    execution["saved_policy_replay_matches_original"] = True
    execution["metrics"] = metrics.to_dict(orient="index")
    (destination / "execution_audit.json").write_text(json.dumps(execution, indent=2) + "\n")
    print("PASS: saved policy and normalization reproduce original held-out accounts.")
    print(metrics.round(3).to_string())


if __name__ == "__main__":
    main()
