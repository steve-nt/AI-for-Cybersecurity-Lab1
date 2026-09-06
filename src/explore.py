"""LAB STEP 1: Load the data and look at it.

Prints the shape, the columns, and how many rows are normal vs. attack.
Saves one bar chart of the class balance for your report.

Run:  python src/explore.py
"""
import matplotlib
matplotlib.use("Agg")   # draw to a file instead of opening a window
import matplotlib.pyplot as plt
import pandas as pd

import config


def load_raw(path=config.RAW_FILE):
    """Load the CSV and tidy up the text.

    The CICIDS files have leading spaces in their column names (' Label' rather
    than 'Label') and sometimes trailing spaces in the label values. If you skip
    this, everything downstream fails with confusing KeyError messages.
    """
    if not path.exists():
        raise SystemExit(
            f"\nCannot find the data file:\n  {path}\n\n"
            "Download it (GUIDE.md section 3), put it in data/raw/, and make sure\n"
            "RAW_FILE in src/config.py matches the filename exactly.\n"
        )
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()
    df[config.LABEL_COLUMN] = df[config.LABEL_COLUMN].astype(str).str.strip()
    return df


def main():
    df = load_raw()

    print("=" * 70)
    print("STEP 1: LOAD AND LOOK")
    print("=" * 70)
    print(f"\nShape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    print(f"\nFirst 15 column names:")
    for name in df.columns[:15]:
        print(f"  - {name}")
    print(f"  ... and {len(df.columns) - 15} more")

    print("\nHow many rows of each type?")
    counts = df[config.LABEL_COLUMN].value_counts()
    for label, n in counts.items():
        print(f"  {label:<30} {n:>10,}  ({n / len(df) * 100:5.2f}%)")

    n_attack = (df[config.LABEL_COLUMN] != config.BENIGN_LABEL).sum()
    n_normal = len(df) - n_attack
    print(f"\nBinary view:  normal={n_normal:,}   attack={n_attack:,}")
    print(f"Attacks are {n_attack / len(df) * 100:.2f}% of the data.")
    print("\nThis is called an IMBALANCED dataset. It is why accuracy alone is")
    print("a misleading score - see GUIDE.md section 5.")

    # ---- the bar chart the lab asks for ----
    fig, ax = plt.subplots(figsize=(10, 5))
    counts.plot(kind="bar", ax=ax, color="#4C72B0")
    ax.set_title("Class balance: how many rows of each traffic type")
    ax.set_xlabel("Label")
    ax.set_ylabel("Number of rows (log scale)")
    ax.set_yscale("log")   # log scale, or the tiny attack classes are invisible
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out = config.FIGURES / "class_balance.png"
    plt.savefig(out, dpi=150)
    print(f"\nSaved chart -> {out}")


if __name__ == "__main__":
    main()
