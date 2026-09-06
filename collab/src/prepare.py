"""LAB STEPS 3 AND 4: Split into train/validation/test, then scale.

This is the most important file for your grade. It splits the data ONCE and
saves the result, so every later script uses the identical split and nobody
can accidentally peek at the test set.

Run:  python src/prepare.py
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import config


def main():
    df = pd.read_csv(config.CLEAN_FILE)
    print("=" * 70)
    print("STEPS 3 & 4: SPLIT AND SCALE")
    print("=" * 70)

    # --- 3a. Separate the features from the answers -----------------------
    y_multi = df[config.LABEL_COLUMN]                       # "DoS Hulk", ...
    y_binary = (y_multi != config.BENIGN_LABEL).astype(int)  # 0 normal, 1 attack
    X = df.drop(columns=[config.LABEL_COLUMN])
    X = X.select_dtypes(include=[np.number])   # models only accept numbers
    print(f"\nFeatures: {X.shape[1]} columns, {X.shape[0]:,} rows")

    # --- 3b. Split 60 / 20 / 20 -------------------------------------------
    # Done in two moves: first chop off the test set, then chop the validation
    # set out of what remains.  0.80 x 0.25 = 0.20 of the original.
    #
    # We stratify on the MULTICLASS label so every attack type keeps its
    # proportion in all three parts, not just "attack" as a whole.
    X_tmp, X_test, yb_tmp, yb_test, ym_tmp, ym_test = train_test_split(
        X, y_binary, y_multi,
        test_size=config.TEST_SIZE,
        stratify=y_multi,
        random_state=config.SEED,
    )
    X_train, X_val, yb_train, yb_val, ym_train, ym_val = train_test_split(
        X_tmp, yb_tmp, ym_tmp,
        test_size=config.VAL_SIZE_OF_REMAINDER,
        stratify=ym_tmp,
        random_state=config.SEED,
    )
    total = len(X)
    print(f"  train: {len(X_train):>8,} rows ({len(X_train)/total:.0%})")
    print(f"  val:   {len(X_val):>8,} rows ({len(X_val)/total:.0%})")
    print(f"  test:  {len(X_test):>8,} rows ({len(X_test)/total:.0%})")
    print(f"\n  attack rate  train={yb_train.mean():.4f}  "
          f"val={yb_val.mean():.4f}  test={yb_test.mean():.4f}")
    

    # --- 4. Scale ----------------------------------------------------------
    # StandardScaler rewrites every column so it has average 0 and spread 1.
    # WHY: one column might be "duration in microseconds" (millions) and another
    # "number of flags" (0-8). Logistic Regression, SVM and neural networks all
    # treat the big-numbered column as more important purely because the numbers
    # are bigger. Scaling removes that unfair advantage.
    #
    # CRITICAL: .fit_transform() on TRAIN, but only .transform() on val/test.
    # The scaler learns the average and spread from the training data alone.
    # Letting it see the test data first is a subtle form of cheating.
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)
    print("\nScaler fitted on TRAINING data only, then applied to val and test.")

    bundle = {
        "X_train": X_train, "X_val": X_val, "X_test": X_test,
        "X_train_s": X_train_s, "X_val_s": X_val_s, "X_test_s": X_test_s,
        "yb_train": yb_train, "yb_val": yb_val, "yb_test": yb_test,
        "ym_train": ym_train, "ym_val": ym_val, "ym_test": ym_test,
        "feature_names": list(X.columns),
        "scaler": scaler,
        "seed": config.SEED,
    }
    joblib.dump(bundle, config.SPLITS_FILE)
    print(f"Saved -> {config.SPLITS_FILE}")


if __name__ == "__main__":
    main()
