"""Creates a FAKE splits.joblib so the modelling scripts can be built and tested
before the real cleaning pipeline is finished.

Run:  python src/make_dummy_splits.py
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import config

N_ROWS = 6000
N_FEATURES = 20


def main():
    print("!" * 70)
    print("!!  WARNING: GENERATING FAKE DATA FOR TESTING ONLY")
    print("!!  Any results produced from this are MEANINGLESS.")
    print("!!  Delete data/processed/ and run the real pipeline before")
    print("!!  putting ANY number in your report.")
    print("!" * 70)

    X, yb = make_classification(
        n_samples=N_ROWS,
        n_features=N_FEATURES,
        n_informative=10,
        n_redundant=4,
        weights=[0.8, 0.2],      # same imbalance shape as the real data
        class_sep=1.2,
        random_state=config.SEED,
    )
    X = pd.DataFrame(X, columns=[f"fake_feature_{i}" for i in range(N_FEATURES)])
    yb = pd.Series(yb, name=config.LABEL_COLUMN)

    rng = np.random.default_rng(config.SEED)
    fake_attacks = rng.choice(["FakeDoS", "FakePortScan", "FakeBruteForce"], size=len(yb))
    ym = pd.Series(np.where(yb == 0, config.BENIGN_LABEL, fake_attacks))

    X_tmp, X_test, yb_tmp, yb_test, ym_tmp, ym_test = train_test_split(
        X, yb, ym, test_size=config.TEST_SIZE, stratify=ym, random_state=config.SEED)
    X_train, X_val, yb_train, yb_val, ym_train, ym_val = train_test_split(
        X_tmp, yb_tmp, ym_tmp, test_size=config.VAL_SIZE_OF_REMAINDER,
        stratify=ym_tmp, random_state=config.SEED)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    bundle = {
        "X_train": X_train, "X_val": X_val, "X_test": X_test,
        "X_train_s": X_train_s, "X_val_s": X_val_s, "X_test_s": X_test_s,
        "yb_train": yb_train, "yb_val": yb_val, "yb_test": yb_test,
        "ym_train": ym_train, "ym_val": ym_val, "ym_test": ym_test,
        "feature_names": list(X.columns),
        "scaler": scaler,
        "seed": config.SEED,
        "source": "DUMMY - NOT REAL DATA",
    }
    joblib.dump(bundle, config.SPLITS_FILE)
    print(f"\nWrote FAKE splits ({N_ROWS} rows, {N_FEATURES} features) -> {config.SPLITS_FILE}")
    print("Real data will have ~140,000 rows and ~70 features. If you see 6000, it is fake.")


if __name__ == "__main__":
    main()
