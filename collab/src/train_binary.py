"""LAB STEPS 5 AND 6: Train the classical models and the neural network.

Trains three model families on the normal-vs-attack task:
  - Logistic Regression   (classical, needs scaling)
  - Random Forest         (classical, no scaling needed)
  - MLPClassifier         (the neural network, needs scaling)

For each family it tries a few settings, picks the best ON THE VALIDATION SET,
then scores that single winner ONCE on the test set.

Run:  python src/train_binary.py
"""
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.neural_network import MLPClassifier

import config
import metrics

# Which settings to try for each model. "scaled" says whether this model wants
# the scaled version of the data.
CANDIDATES = {
    "LogisticRegression": {
        "scaled": True,
        "grid": [
            {"C": 0.1},
            {"C": 1.0},
            {"C": 1.0, "class_weight": "balanced"},
        ],
    },
    "RandomForest": {
        "scaled": False,
        "grid": [
            {"n_estimators": 100, "max_depth": None},
            {"n_estimators": 300, "max_depth": 20},
        ],
    },
    "MLP (neural network)": {
        "scaled": True,
        "grid": [
            {"hidden_layer_sizes": (32,)},
            {"hidden_layer_sizes": (64, 32)},
        ],
    },
}


def build(name, params):
    """Create an untrained model of the given family with the given settings."""
    if name == "LogisticRegression":
        return LogisticRegression(max_iter=1000, random_state=config.SEED, **params)
    if name == "RandomForest":
        return RandomForestClassifier(random_state=config.SEED, n_jobs=-1, **params)
    if name == "MLP (neural network)":
        return MLPClassifier(
            max_iter=100, early_stopping=True, random_state=config.SEED, **params
        )
    raise ValueError(name)


def main():
    d = joblib.load(config.SPLITS_FILE)
    print("=" * 70)
    print("STEPS 5 & 6: TRAIN BINARY MODELS")
    print("=" * 70)

    rows = []
    for name, spec in CANDIDATES.items():
        Xtr = d["X_train_s"] if spec["scaled"] else d["X_train"]
        Xva = d["X_val_s"] if spec["scaled"] else d["X_val"]
        Xte = d["X_test_s"] if spec["scaled"] else d["X_test"]

        print(f"\n--- {name} " + "-" * (60 - len(name)))
        best = None
        for params in spec["grid"]:
            model = build(name, params)
            model.fit(Xtr, d["yb_train"])
            # Choose using the VALIDATION set. The test set stays sealed.
            val_f1 = metrics.f1_score(
                d["yb_val"], model.predict(Xva), average="macro"
            )
            print(f"  tried {params}  ->  validation macro-F1 = {val_f1:.4f}")
            if best is None or val_f1 > best[0]:
                best = (val_f1, params, model)

        val_f1, params, model = best
        print(f"  WINNER: {params}  (validation macro-F1 {val_f1:.4f})")

        # Now, and only now, touch the test set.
        y_pred = model.predict(Xte)
        y_score = model.predict_proba(Xte)[:, 1]
        row = metrics.evaluate_binary(name, d["yb_test"], y_pred, y_score,
                                      notes=str(params))
        rows.append(row)
        metrics.print_row(row)

        joblib.dump(model, config.MODELS / f"{name.split()[0]}_binary.joblib")

        fig, ax = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay.from_predictions(
            d["yb_test"], y_pred,
            display_labels=["normal", "attack"], cmap="Blues", ax=ax,
        )
        ax.set_title(f"{name} - test set")
        plt.tight_layout()
        plt.savefig(config.FIGURES / f"confusion_{name.split()[0]}.png", dpi=150)
        plt.close()

    out = config.TABLES / "binary_results.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved results -> {out}")


if __name__ == "__main__":
    main()
