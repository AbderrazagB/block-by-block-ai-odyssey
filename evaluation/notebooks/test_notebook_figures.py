"""Chart/data checks on synthetic fixtures; no project performance measured."""

import tempfile
import json
from pathlib import Path
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from notebook_figures import (finrl_feature_names, forecast_diagnostics,
                              plot_classification, plot_forecast_examples,
                              plot_shap_action, plot_trading, trading_comparison,
                              trading_metrics)


class FigureTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.dates = pd.bdate_range("2024-01-02", periods=3)
        self.accounts = pd.DataFrame({"date": self.dates, "account_value": [100, 105, 90]})
        self.prices = pd.DataFrame({"A": [10, 11, 9], "B": [20, 22, 18]}, index=self.dates)

    def tearDown(self):
        plt.close("all")

    def test_dated_benchmark_and_drawdown(self):
        comparison = trading_comparison(self.accounts, self.prices, 100)
        np.testing.assert_allclose(comparison["Equal-weight hold"], [100, 110, 90])
        metrics = trading_metrics(comparison, 100)
        self.assertAlmostEqual(metrics.loc["PPO", "return_pct"], -10)
        self.assertAlmostEqual(metrics.loc["PPO", "max_drawdown_pct"], (90 / 105 - 1) * 100)
        fig = plot_trading(comparison, 100, self.root / "trading.png")
        self.assertEqual(len(fig.axes), 2)
        self.assertTrue((self.root / "trading.png").exists())

    def test_misaligned_and_duplicate_dates_fail(self):
        with self.assertRaisesRegex(ValueError, "date sets differ"):
            trading_comparison(self.accounts, self.prices.iloc[1:], 100)
        duplicate = pd.concat([self.accounts, self.accounts.iloc[:1]])
        with self.assertRaisesRegex(ValueError, "Duplicate account dates"):
            trading_comparison(duplicate, self.prices, 100)

    def test_benchmark_entry_fee(self):
        comparison = trading_comparison(self.accounts, self.prices, 100, buy_cost=0.01)
        self.assertAlmostEqual(comparison.iloc[0]["Equal-weight hold"], 100)
        self.assertAlmostEqual(comparison.iloc[1]["Equal-weight hold"], 110 / 1.01)

    def test_binary_diagnostic_counts_and_prevalence(self):
        summary, report, fig = plot_classification([0, 0, 1, 1], [0.1, 0.8, 0.7, 0.2],
                                                  self.root / "classification.png", "fraud")
        self.assertEqual(summary["held_out_rows"], 4)
        self.assertEqual(summary["positive_prevalence"], 0.5)
        self.assertEqual(summary["accuracy"], 0.5)
        self.assertEqual(report.loc["1", "support"], 2)
        np.testing.assert_array_equal(fig.axes[1].images[0].get_array(), [[1, 1], [1, 1]])
        with self.assertRaisesRegex(ValueError, "both original binary classes"):
            plot_classification([0, 0], [0.1, 0.2], self.root / "bad.png", "fraud")

    def test_state_labels_and_scalar_shap_dimensions(self):
        names = finrl_feature_names(["A", "B"], ["rsi", "macd"])
        self.assertEqual(names, ["cash", "A: close", "B: close", "A: shares", "B: shares",
                                 "A: rsi", "B: rsi", "A: macd", "B: macd"])
        fig = plot_shap_action(np.ones((3, 9)), names, "A", self.root / "shap.png")
        self.assertEqual(len(fig.axes), 1)
        with self.assertRaisesRegex(ValueError, "ONE stock action"):
            plot_shap_action(np.ones((3, 9, 2)), names, "A", self.root / "bad.png")

    def test_forecast_baseline_and_representative_cases(self):
        predictions = {}
        for ticker, error in [("A", 0), ("B", 1), ("C", 2)]:
            predictions[ticker] = pd.DataFrame({"actual": [10, 11, 12],
                                                "predicted": np.array([10, 11, 12]) + error,
                                                "previous_close": [9, 10, 11]}, index=self.dates)
        metrics = forecast_diagnostics(predictions)
        self.assertEqual(metrics.loc["A", "mae_improvement_pct"], 100)
        self.assertEqual(metrics.loc["B", "mae_improvement_pct"], 0)
        self.assertEqual(metrics.loc["C", "mae_improvement_pct"], -100)
        fig = plot_forecast_examples(predictions, metrics, self.root / "forecasts.png")
        self.assertEqual(len(fig.axes), 3)
        self.assertTrue(fig.axes[0].get_title().startswith("C:"))

    def test_finrl_notebook_comparison_cell_executes(self):
        path = Path(__file__).resolve().parents[2] / "RL_model/FinRL_BlockByBlock.ipynb"
        notebook = json.loads(path.read_text())
        source = next("".join(cell["source"]) for cell in notebook["cells"]
                      if cell["cell_type"] == "code" and "comparison = trading_comparison" in "".join(cell["source"]))
        long_prices = self.prices.rename_axis("date").reset_index().melt(
            id_vars="date", var_name="tic", value_name="close")
        scope = {"account_frame": self.accounts, "test_df": long_prices,
                 "INITIAL_AMOUNT": 100, "TRANSACTION_COST_PCT": 0.01,
                 "PROJECT_PATH": str(self.root), "display": lambda value: None, "plt": plt}
        exec(source, scope)
        self.assertEqual(len(scope["comparison"]), 3)
        self.assertTrue((self.root / "dated_backtest.csv").exists())

    def test_transformer_notebook_evaluation_cell_executes(self):
        path = Path(__file__).resolve().parents[2] / "stock_transformer/Model_training/Transformer.ipynb"
        notebook = json.loads(path.read_text())
        source = next("".join(cell["source"]) for cell in notebook["cells"]
                      if cell["cell_type"] == "code" and "forecast_metrics = forecast_diagnostics" in "".join(cell["source"]))
        dates = pd.bdate_range("2024-01-02", periods=13)
        frame = pd.DataFrame({"Date": dates, "Close": np.arange(10, 23),
                              "Volume": np.arange(100, 113)})
        scaler = MinMaxScaler().fit(frame[["Close", "Volume"]].to_numpy())
        scaled = scaler.transform(frame[["Close", "Volume"]].to_numpy())
        windows = np.array([scaled[i - 10:i] for i in range(10, 13)])
        class PersistenceModel:
            def predict(self, values, batch_size=None, verbose=0):
                return values[:, -1, :1]
        scope = {"feature_cols": ["Close", "Volume"], "stockList": ["A"],
                 "model": PersistenceModel(), "testset": {"A": {"X": windows, "y": scaled[10:, 0]}},
                 "transform_test": {"A": scaled}, "scaler": {"A": scaler},
                 "df_new": {"A": {"Test": frame}}, "np": np, "pd": pd,
                 "display": lambda value: None, "RUN_DIR": self.root}
        source = source.replace("price_pred_plots/held_out_forecast_metrics.csv",
                                str(self.root / "forecast_metrics.csv"))
        exec(source, scope)
        self.assertEqual(scope["forecast_metrics"].loc["A", "mae_improvement_pct"], 0)
        self.assertEqual(len(scope["pred_result"]["A"]), 3)



if __name__ == "__main__":
    unittest.main()
