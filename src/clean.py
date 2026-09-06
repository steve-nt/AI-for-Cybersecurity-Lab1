"""LAB STEP 2: Clean the data.

Removes ID columns, fixes infinity/NaN, drops duplicates and dead columns,
then takes a manageable sample.

Run:  python src/clean.py
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import config
from explore import load_raw


def main():
    df = load_raw()
    print("=" * 70)
    print("STEP 2: CLEAN")
    print("=" * 70)
    print(f"\nStarting with {df.shape[0]:,} rows x {df.shape[1]} columns")

    # --- 2a. Drop the ID columns ------------------------------------------
    # See the comment in config.py for WHY. Only drop ones that exist.
    to_drop = [c for c in config.ID_COLUMNS if c in df.columns]
    df = df.drop(columns=to_drop)
    print(f"\n[1] Dropped {len(to_drop)} ID columns: {to_drop}")

    # --- 2b. Fix broken numbers -------------------------------------------
    # Some speed features are computed as "bytes divided by duration". When the
    # duration is zero the answer is infinity, which no model can handle.
    numeric = df.select_dtypes(include=[np.number]).columns
    n_inf = int(np.isinf(df[numeric]).sum().sum())
    df[numeric] = df[numeric].replace([np.inf, -np.inf], np.nan)
    n_nan = int(df.isna().sum().sum())
    before = len(df)
    df = df.dropna()
    print(f"[2] Found {n_inf:,} infinity values and {n_nan:,} missing values")
    print(f"    Dropped {before - len(df):,} rows containing them")

    # --- 2c. Drop exact duplicate rows ------------------------------------
    # Duplicates let the same row appear in BOTH training and test data, which
    # inflates your scores dishonestly.
    before = len(df)
    df = df.drop_duplicates()
    print(f"[3] Dropped {before - len(df):,} duplicate rows")

    # --- 2d. Drop dead columns --------------------------------------------
    # A column with the same value in every row teaches the model nothing.
    numeric = df.select_dtypes(include=[np.number]).columns
    dead = [c for c in numeric if df[c].nunique() <= 1]
    df = df.drop(columns=dead)
    print(f"[4] Dropped {len(dead)} constant (zero-variance) columns")

    # --- 2e. Drop attack types with too few examples ----------------------
    counts = df[config.LABEL_COLUMN].value_counts()
    rare = counts[counts < config.MIN_CLASS_COUNT]
    if len(rare) > 0:
        print(f"[5] Dropping {len(rare)} very rare classes (< "
              f"{config.MIN_CLASS_COUNT} rows). MENTION THIS IN YOUR REPORT:")
        for label, n in rare.items():
            print(f"      {label}: {n} rows")
        df = df[~df[config.LABEL_COLUMN].isin(rare.index)]
    else:
        print(f"[5] No classes below {config.MIN_CLASS_COUNT} rows")

    # --- 2f. Take a sample -------------------------------------------------
    # "stratify" means: keep the same mix of normal/attack in the sample as in
    # the full data. A plain random sample could miss a rare attack entirely.
    if config.SAMPLE_FRACTION < 1.0:
        df, _ = train_test_split(
            df,
            train_size=config.SAMPLE_FRACTION,
            stratify=df[config.LABEL_COLUMN],
            random_state=config.SEED,
        )
        print(f"[6] Sampled {config.SAMPLE_FRACTION:.0%} -> {len(df):,} rows")
    else:
        print("[6] Using 100% of the rows")

    df.to_csv(config.CLEAN_FILE, index=False)
    print(f"\nFinal: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Saved -> {config.CLEAN_FILE}")


if __name__ == "__main__":
    main()
