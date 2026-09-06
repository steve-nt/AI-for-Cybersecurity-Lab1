# SCAFFOLD.md - The Blueprint

This file describes **what the project looks like** and contains **every line of code you need**.

It is a reference. It does not tell you what order to do things in - that is [GUIDE.md](GUIDE.md).
Read GUIDE.md first; come back here to copy code.

---

## 1. What we are building, in plain English

A program that looks at records of network connections and decides: **normal, or attack?**

We are not writing rules like "if more than 100 connections per second, alarm". Instead we show a
computer program thousands of examples of normal traffic and thousands of examples of attack
traffic, and it works out the difference by itself. That is machine learning.

We build it twice:

- **Binary**: normal vs. attack (a yes/no answer).
- **Multiclass**: which *kind* of attack (port scan, denial-of-service, brute force, ...).

---

## 2. Folder layout

Everything lives inside `AI-for-Cybersecurity-Lab1/`.

```
AI-for-Cybersecurity-Lab1/
├── README.md                 <- how to run it (you write this at the end)
├── GUIDE.md                  <- step-by-step instructions (do this first)
├── SCAFFOLD.md               <- this file: layout + all the code
├── requirements.txt          <- list of libraries to install (Python 3.11)
├── .gitignore                <- stops huge data files being uploaded to git
├── run_all.py                <- runs the whole pipeline start to finish
│
├── data/
│   ├── raw/                  <- the CSV you download goes here (never edited)
│   └── processed/            <- cleaned data the scripts create (auto-created)
│
├── src/                      <- all the code
│   ├── config.py             <- settings: random seed, file paths, split sizes
│   ├── metrics.py            <- calculates accuracy, macro-F1, recall, ROC-AUC, FAR
│   ├── explore.py            <- Lab Step 1: load and look
│   ├── clean.py              <- Lab Step 2: clean
│   ├── prepare.py            <- Lab Steps 3 + 4: split and scale
│   ├── train_binary.py       <- Lab Steps 5 + 6: classical models + neural network
│   ├── ablation.py           <- Lab Step 7: change one thing
│   ├── multiclass.py         <- the "which attack is it" version
│   └── compare.py            <- Lab Step 8: final results table
│
├── results/
│   ├── figures/              <- .png charts for your report (auto-created)
│   ├── tables/               <- .csv results tables (auto-created)
│   └── models/               <- trained models saved to disk (auto-created)
│
└── report/
    └── report.md             <- your 2-3 page write-up
```

**Why split into many small files instead of one big one?** The grading rubric gives 30% for
"reasonably tidy" code that "runs start-to-finish". Small files each doing one job is what tidy
means. It also means when something breaks, you know exactly which file broke.

---

## 3. How data flows through the pipeline

Each script reads a file, does one job, and writes a file. The next script picks it up.

```
  data/raw/Wednesday-workingHours.pcap_ISCX.csv      (you download this)
                    |
                    v
            src/explore.py      -> prints shape/columns, saves class_balance.png
                    |
                    v
            src/clean.py        -> data/processed/clean.csv
                    |
                    v
            src/prepare.py      -> data/processed/splits.joblib
                    |                (train/val/test, scaled + unscaled)
                    |
        +-----------+-----------+--------------------+
        v           v           v                    v
  train_binary  ablation   multiclass          (all read splits.joblib)
        |           |           |
        v           v           v
     results/tables/*.csv  +  results/figures/*.png
                    |
                    v
            src/compare.py      -> results/tables/final_comparison.csv
                                   results/figures/model_comparison.png
```

**The important rule this enforces:** `prepare.py` splits the data into train / validation / test
*once*, and saves it. Every later script loads that same split. This is how you guarantee you never
accidentally train on your test data - which is the single fastest way to fail this lab.

---

## 4. The files

Create each of these exactly as written. GUIDE.md tells you when.

---

### 4.1 `requirements.txt`

The list of libraries the project needs.

```
# Python 3.11
tensorflow>=2.15.0,<2.18.0
torch>=2.1.0
scikit-learn>=1.3.0
pandas>=2.0.0
matplotlib>=3.7.0
joblib>=1.4.0
tabulate>=0.9.0
```

**This project requires Python 3.11.** Not the system 3.13. GUIDE.md 1.3 covers installing it, and
GUIDE.md Appendix A lists every available method. The `tensorflow<2.18` bound is what makes the
whole set resolve together; it also pins `numpy` to 1.26.x, which is expected and fine.

`joblib` and `tabulate` are not optional extras - every script in section 5 imports `joblib` to
save and load `splits.joblib`, and `compare.py` calls `df.to_markdown()`, which needs `tabulate`.

**Note on the neural network:** the lab lets you use Keras/TensorFlow, PyTorch, **or**
scikit-learn's `MLPClassifier` ("the easiest to start with"). All three are installed, so any of
them is available to you. The code below uses **`MLPClassifier`**. It is a real neural network (a
multi-layer perceptron), it counts for full marks, it trains in seconds rather than minutes on this
data, and it needs no GPU. TensorFlow and PyTorch are installed alongside it so you can swap in a
Keras or torch model later without redoing setup. Using `MLPClassifier` is the right choice, not a
shortcut.

---

### 4.2 `.gitignore`

Stops you accidentally uploading a 500 MB dataset - or a whole Python interpreter - to GitHub.
The `python/`, `Python-3.11.*/` and `py311.tar.gz` entries only matter if you installed 3.11 with
method A2 or A6 from GUIDE.md Appendix A, but they are harmless otherwise.

```
.venv/
python/
Python-3.11.*/
py311.tar.gz
__pycache__/
*.pyc
data/raw/*
data/processed/*
results/models/*
!data/raw/.gitkeep
!data/processed/.gitkeep
```

---

### 4.3 `src/config.py`

Every setting lives here. If you want to change something, change it here, not in six other files.

```python
"""Central settings for the whole lab.

Change things HERE, not in the other files. That way there is one place to look
when you are asked "what settings did you use?" for the report.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
# A "seed" fixes the randomness. Splitting data and training models both involve
# random choices. With a fixed seed, you get the SAME numbers every time you run.
# The lab requires this. Write this number in your README and report.
SEED = 42

# ---------------------------------------------------------------------------
# Where things live
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS = PROJECT_ROOT / "results"
FIGURES = RESULTS / "figures"
TABLES = RESULTS / "tables"
MODELS = RESULTS / "models"

# The file you downloaded. CHANGE THIS LINE to match your actual filename.
RAW_FILE = DATA_RAW / "Wednesday-workingHours.pcap_ISCX.csv"

CLEAN_FILE = DATA_PROCESSED / "clean.csv"
SPLITS_FILE = DATA_PROCESSED / "splits.joblib"

# ---------------------------------------------------------------------------
# Data settings
# ---------------------------------------------------------------------------
# Use only this fraction of the rows so everything runs in minutes, not hours.
# Set to 1.0 once everything works and you want the full-size final run.
SAMPLE_FRACTION = 0.20

LABEL_COLUMN = "Label"      # the column holding "BENIGN" / "DoS Hulk" / etc.
BENIGN_LABEL = "BENIGN"     # the value that means "normal traffic"

# Attack types with fewer than this many rows get dropped. Too few examples to
# learn from, and they break a stratified split. Mention this in your report.
MIN_CLASS_COUNT = 10

# ---------------------------------------------------------------------------
# Train / validation / test split -> 60% / 20% / 20%
# ---------------------------------------------------------------------------
TEST_SIZE = 0.20            # 20% held back for the final test
VAL_SIZE_OF_REMAINDER = 0.25  # 25% of the remaining 80% = 20% of the total

# ---------------------------------------------------------------------------
# Columns to delete
# ---------------------------------------------------------------------------
# WHY: these are "name tags". An IP address or a timestamp does not describe
# attack BEHAVIOUR, it identifies WHO or WHEN. A model given them will memorise
# "traffic from 192.168.10.50 is an attack" and score brilliantly on your test
# set while being completely useless on real traffic. This is called leakage.
#
# Not every dataset file uses all these names, so the code only drops the ones
# it actually finds.
ID_COLUMNS = [
    "Flow ID",
    "Source IP", "Src IP",
    "Destination IP", "Dst IP",
    "Source Port", "Src Port",
    "Destination Port", "Dst Port",
    "Timestamp",
    "Protocol",
    "Fwd Header Length.1",   # a known duplicated column in CICIDS2017
]

# ---------------------------------------------------------------------------
# Make sure the folders exist so nothing crashes later
# ---------------------------------------------------------------------------
for _folder in (DATA_RAW, DATA_PROCESSED, RESULTS, FIGURES, TABLES, MODELS):
    _folder.mkdir(parents=True, exist_ok=True)
```

---

### 4.4 `src/metrics.py`

One place that computes every score the lab asks for. Written once, used by every training script,
so the numbers in your final table are guaranteed to be calculated the same way.

```python
"""Every score the lab asks for, computed in one place.

Read section 5 of GUIDE.md for what these numbers actually mean.
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
    roc_auc_score,
)


def false_alarm_rate(y_true, y_pred):
    """FAR: of all the traffic that was genuinely NORMAL, what fraction did we
    wrongly scream about?

        FAR = FP / (FP + TN)

    This is the number a real security team cares about most. A detector with a
    5% FAR on a network carrying a million normal connections a day generates
    50,000 false alarms a day, and the humans stop reading them.

    scikit-learn has no built-in function for this, so we compute it from the
    confusion matrix ourselves.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    denominator = fp + tn
    return float(fp / denominator) if denominator > 0 else 0.0


def evaluate_binary(model_name, y_true, y_pred, y_score=None, notes=""):
    """Return one row of the results table for a normal-vs-attack model.

    y_pred  = the model's yes/no decision  (0 = normal, 1 = attack)
    y_score = the model's confidence, 0.0 to 1.0. Needed for ROC-AUC.
    """
    row = {
        "model": model_name,
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "recall_attack": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_score) if y_score is not None else np.nan,
        "FAR": false_alarm_rate(y_true, y_pred),
        "notes": notes,
    }
    return row


def macro_false_alarm_rate(y_true, y_pred, labels):
    """The multiclass version of FAR: work out the false alarm rate separately
    for every attack type, then average them.
    """
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    total = cm.sum()
    per_class = []
    for i in range(len(labels)):
        fp = cm[:, i].sum() - cm[i, i]
        tn = total - cm[i, :].sum() - cm[:, i].sum() + cm[i, i]
        per_class.append(fp / (fp + tn) if (fp + tn) > 0 else 0.0)
    return float(np.mean(per_class))


def print_row(row):
    """Print one result line in a readable way."""
    print(
        f"  {row['model']:<28} "
        f"acc={row['accuracy']:.4f}  "
        f"macroF1={row['macro_f1']:.4f}  "
        f"recall={row['recall_attack']:.4f}  "
        f"AUC={row['roc_auc']:.4f}  "
        f"FAR={row['FAR']:.4f}"
    )
```

---

### 4.5 `src/explore.py` - Lab Step 1: Load and look

```python
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
```

---

### 4.6 `src/clean.py` - Lab Step 2: Clean

```python
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
```

---

### 4.7 `src/prepare.py` - Lab Steps 3 + 4: Split and scale

```python
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
    print("  (these three should be nearly identical - that is what stratify does)")

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
```

---

### 4.8 `src/train_binary.py` - Lab Steps 5 + 6: The models

```python
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
```

Note: `metrics.f1_score` works because `metrics.py` imports `f1_score` from scikit-learn at the
top, which makes it reachable as `metrics.f1_score`.

---

### 4.9 `src/ablation.py` - Lab Step 7: Change one thing

```python
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
    print("\nPut the before/after numbers in your report and say what changed.")


if __name__ == "__main__":
    main()
```

---

### 4.10 `src/multiclass.py` - Naming the attack

```python
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
    print("\nLook at this chart: which attack types get mixed up with each")
    print("other? That is an excellent thing to discuss in your report.")

    joblib.dump(model, config.MODELS / "RandomForest_multiclass.joblib")


if __name__ == "__main__":
    main()
```

---

### 4.11 `src/compare.py` - Lab Step 8: The final table

```python
"""LAB STEP 8: Put everything in one table and one chart.

This produces the table that goes straight into your report.

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
    print("\nCopy this table into your report:\n")
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
```

`to_markdown()` needs the `tabulate` package. If you get an error there, either
`pip install tabulate` or change that line to `print(df.to_string(index=False))`.

---

### 4.12 `run_all.py` - the whole pipeline in one command

The rubric asks that your code "runs start-to-finish and reproduces your numbers". This is that.

```python
"""Run the entire lab from raw CSV to final table.

Run:  python run_all.py
"""
import subprocess
import sys
from pathlib import Path

STEPS = [
    ("Step 1  - explore",    "src/explore.py"),
    ("Step 2  - clean",      "src/clean.py"),
    ("Steps 3&4 - prepare",  "src/prepare.py"),
    ("Steps 5&6 - train",    "src/train_binary.py"),
    ("Step 7  - ablation",   "src/ablation.py"),
    ("Multiclass",           "src/multiclass.py"),
    ("Step 8  - compare",    "src/compare.py"),
]

root = Path(__file__).resolve().parent
for title, script in STEPS:
    print(f"\n{'#' * 70}\n### {title}\n{'#' * 70}")
    result = subprocess.run([sys.executable, str(root / script)])
    if result.returncode != 0:
        print(f"\nFAILED at {script}. Fix the error above, then re-run.")
        sys.exit(1)

print("\nAll steps finished. Look in results/ for your tables and figures.")
```

---

## 5. Design decisions you should defend in your report

Markers give credit for knowing *why* you did things. These are the choices baked into this
scaffold, with the reasoning:

| Decision | Why | 
|---|---|
| Dropped IPs, ports, timestamps, Flow ID | They identify *who/when*, not *how an attack behaves*. Keeping them lets the model memorise addresses and score fake-high. |
| Dropped `Protocol` and `Destination Port` too | Debatable, and worth a sentence in your report. Port 80 vs 22 is genuinely informative, but in a lab dataset the attack traffic sits on fixed ports, so the model can shortcut. We drop them to be safe. |
| Fitted the scaler on training data only | Fitting on everything leaks information about the test set into training. |
| Stratified on the multiclass label, not binary | Keeps rare attack *types* proportionally present in all three splits. |
| Dropped classes with < 10 rows | Cannot be split three ways or learned from. Say so in the report - it is a limitation, not a secret. |
| Chose the winner on validation, scored once on test | This is what "no test-set peeking" means, and it is 25% of your grade. |
| Used `MLPClassifier` as the neural network | Explicitly permitted by the lab brief, trains in seconds, needs no GPU. TensorFlow and PyTorch are installed too, so swapping it out later costs nothing. |
| Judged by macro-F1 and FAR, not accuracy | The data is ~80% normal traffic, so a model that says "normal" every single time scores ~80% accuracy while catching zero attacks. |

---

## 6. What you end up with

After `python run_all.py` finishes:

**Tables** (`results/tables/`)
- `binary_results.csv` - the main comparison
- `ablation_results.csv` - the scaling on/off experiment
- `final_comparison.csv` - everything merged, ready for the report

**Figures** (`results/figures/`)
- `class_balance.png` - Lab Step 1's required bar chart
- `confusion_LogisticRegression.png`, `confusion_RandomForest.png`, `confusion_MLP.png`
- `confusion_multiclass.png` - which attacks get confused with which
- `model_comparison.png` - macro-F1 and FAR side by side

Pick **one table and one or two figures** for the report, and make sure you actually refer to each
one in the text. The rubric specifically rewards captions that the writing uses.
