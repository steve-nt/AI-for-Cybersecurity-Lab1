"""LAB STEP 8: Put everything in one table and one chart.

This produces the table that goes straight into our report.

Run:  python src/compare.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import config


def main():
    parts = []
    for filename in ["binary_results.csv", "ablation_results.csv"]:
        path = config.TABLES / filename
        if path.exists():
            parts.append(pd.read_csv(path))
    if not parts:
        raise SystemExit("No results found. Run train_binary.py first.")

    df = pd.concat(parts, ignore_index=True)
    cols = ["model", "accuracy", "macro_f1", "recall_attack", "roc_auc", "FAR", "notes"]
    df = df[cols].round(4)

    out = config.TABLES / "final_comparison.csv"
    df.to_csv(out, index=False)

    print("=" * 70)
    print("STEP 8: FINAL COMPARISON")
    print("=" * 70)
    print(df.to_markdown(index=False))

    # A chart comparing the main models on the two metrics that matter.
    main_models = df[~df["model"].str.contains(r"\[", regex=True)]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].barh(main_models["model"], main_models["macro_f1"], color="#4C72B0")
    axes[0].set_title("macro-F1 (higher is better)")
    axes[0].set_xlim(0, 1)
    axes[1].barh(main_models["model"], main_models["FAR"], color="#C44E52")
    axes[1].set_title("False Alarm Rate (LOWER is better)")
    plt.tight_layout()
    fig_out = config.FIGURES / "model_comparison.png"
    plt.savefig(fig_out, dpi=150)
    print(f"\nSaved -> {out}\nSaved -> {fig_out}")


if __name__ == "__main__":
    main()
