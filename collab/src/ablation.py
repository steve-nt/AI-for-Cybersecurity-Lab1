"""LAB STEP 7: The ablation.

An ablation means: change EXACTLY ONE THING, keep everything else identical,
and see what happens to the scores. It proves which choices actually matter.

Our one thing: FEATURE SCALING, on vs. off.

We expect Logistic Regression and the neural network to get noticeably worse 
without it, and Random Forest to barely notice - because trees ask questions
like "is this value above 500?", and that question means the same thing
whatever units the column is in.

Run:  python src/ablation.py
"""
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

import config
import metrics


def main():
    d = joblib.load(config.SPLITS_FILE)
    print("=" * 70)
    print("STEP 7: ABLATION - with vs. without feature scaling")
    print("=" * 70)

    models = {
        "LogisticRegression": lambda: LogisticRegression(
            max_iter=1000, random_state=config.SEED),
        "RandomForest": lambda: RandomForestClassifier(
            n_estimators=100, random_state=config.SEED, n_jobs=-1),
        "MLP (neural network)": lambda: MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=100,
            early_stopping=True, random_state=config.SEED),
    }

    rows = []
    for name, make in models.items():
        print(f"\n--- {name} " + "-" * (60 - len(name)))
        for setting, Xtr, Xte in [
            ("WITHOUT scaling", d["X_train"], d["X_test"]),
            ("WITH scaling", d["X_train_s"], d["X_test_s"]),
        ]:
            model = make()                      # a fresh, identical model
            model.fit(Xtr, d["yb_train"])
            y_pred = model.predict(Xte)
            y_score = model.predict_proba(Xte)[:, 1]
            row = metrics.evaluate_binary(
                f"{name} [{setting}]", d["yb_test"], y_pred, y_score,
                notes="ablation: scaling")
            rows.append(row)
            metrics.print_row(row)

    out = config.TABLES / "ablation_results.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved -> {out}")

if __name__ == "__main__":
    main()
