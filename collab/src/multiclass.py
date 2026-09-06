"""THE MULTICLASS TASK: not just "is it an attack" but "WHICH attack".

Same data, same split. The only difference is that the answer we train against
is the full attack name instead of a 0/1.

Run:  python src/multiclass.py
"""
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, f1_score

import config
import metrics


def main():
    d = joblib.load(config.SPLITS_FILE)
    print("=" * 70)
    print("MULTICLASS: which kind of attack is it?")
    print("=" * 70)

    model = RandomForestClassifier(
        n_estimators=200, random_state=config.SEED, n_jobs=-1)
    model.fit(d["X_train"], d["ym_train"])
    y_pred = model.predict(d["X_test"])

    print("\nPer-attack-type scores on the test set:\n")
    print(classification_report(d["ym_test"], y_pred, zero_division=0))

    labels = sorted(d["ym_train"].unique())
    print(f"macro-F1  : {f1_score(d['ym_test'], y_pred, average='macro'):.4f}")
    print(f"macro-FAR : {metrics.macro_false_alarm_rate(d['ym_test'], y_pred, labels):.4f}")

    fig, ax = plt.subplots(figsize=(9, 8))
    ConfusionMatrixDisplay.from_predictions(
        d["ym_test"], y_pred, labels=labels, cmap="Blues",
        xticks_rotation=45, normalize="true", values_format=".2f", ax=ax)
    ax.set_title("Multiclass confusion matrix (row-normalised)")
    plt.tight_layout()
    out = config.FIGURES / "confusion_multiclass.png"
    plt.savefig(out, dpi=150)
    print(f"\nSaved -> {out}")

    joblib.dump(model, config.MODELS / "RandomForest_multiclass.joblib")


if __name__ == "__main__":
    main()
