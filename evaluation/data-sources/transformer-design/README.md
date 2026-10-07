# Shared Transformer goal and verified scope

The original training notebook combines sequences from all 37 stocks into one
Transformer model (`X_train_combined`/`y_train_combined`). The user confirms that
generalization to tickers absent from training was a project goal. The CV now
states that goal explicitly alongside the actual checkpoint evaluation.

The notebook uses a per-ticker chronological split: before 2024 for training and
2024 onward for testing. Every listed ticker contributes to the shared training
pool. Its test therefore evaluates later observations of known tickers, not
held-out stocks. The current prediction API rejects tickers absent from its saved
scaler dictionary with HTTP 404. This shows that arbitrary new-ticker inference
is not implemented by that endpoint.

Our completed audit evaluated 16,872 time-held-out windows across those 37 stocks.
It did not retrain the Transformer or evaluate unseen-ticker generalization.
Checkpoint training/model-selection provenance remains uncertain; the original
code is evidence of the pipeline design, not a new proof about training history.

A future unseen-ticker study would hold out complete stocks before any model
training, fit new-stock normalization using only available past observations,
freeze development choices, and compare with simple baselines on those held-out
stocks. Successful transfer has not yet been demonstrated.

See source-manifest.json for pinned original code references and hashes.
