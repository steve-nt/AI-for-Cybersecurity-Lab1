# Tasklist.md - Who Does What, In What Order

For **two people**, designed so you spend as little time as possible waiting for each other.

- **[GUIDE.md](GUIDE.md)** = how to do things (explanations, commands, concepts)
- **[SCAFFOLD.md](SCAFFOLD.md)** = the code to copy
- **Tasklist.md** (this file) = who does which bit, and what blocks what

---

## The strategy for working independently

The pipeline is naturally sequential - you cannot train a model until the data is cleaned, and you
cannot clean it until it is downloaded. If you simply worked in order, **one person would sit idle
for hours.**

We break that with two decisions:

**1. Disjoint file ownership.** Every file has exactly one owner. Nobody ever edits a file they do
not own. This means git can never produce a merge conflict, which for two people new to git saves
more time than anything else on this page.

**2. A fixed data contract plus fake data.** Person A's pipeline ends by saving one file,
`splits.joblib`, containing a dictionary with agreed key names. Person B's code only ever touches
that dictionary - it does not care where it came from. So B writes a 60-line script that generates a
**fake** `splits.joblib` full of random numbers in the same shape, and builds and tests the entire
modelling half against it, **starting immediately, without waiting for A at all.**

When A's real pipeline lands, B deletes the fake file, reruns, and gets real numbers. No code
changes.

This is genuinely how software teams decouple work, and it is worth one sentence in your report.

### Ownership map

| Person A - "Data & Pipeline" | Person B - "Models & Evaluation" |
|---|---|
| `src/config.py` | `src/metrics.py` |
| `src/explore.py` | `src/make_dummy_splits.py` |
| `src/clean.py` | `src/train_binary.py` |
| `src/prepare.py` | `src/ablation.py` |
| `README.md` | `src/multiclass.py` |
| Report §1 Problem, §2 What we did | `src/compare.py`, `run_all.py` |
| | Report §3 Results, §4 Discussion |

> **Is this fair?** B has more files, but A owns the data work - and downloading, filename
> mismatches, encoding errors and memory problems are where the hidden hours actually go. It
> balances out. Swap the columns if you both prefer; just decide once and stick to it.

### Git rules (three of them)

1. Never edit a file you do not own.
2. Always `git pull --rebase` **before** `git push`.
3. Commit small and often, with a message saying what you did.

Because ownership is disjoint, rule 1 makes conflicts essentially impossible.

---

## Master table

| Num | Title | Owner | What To Do | Depends On |
|---|---|---|---|---|
| **PHASE 1 - JOINT KICKOFF (~45 min, do this together)** ||||
| T01 | Split the roles | Both | Decide who is A and who is B; write it down | - |
| T02 | Set up the shared repo | Both | One GitHub repo, both have push access | T01 |
| T03 | Start the dataset download | Both | Register at UNB, download CICIDS2017, leave it running | - |
| T04 | Install tools and libraries | Both | apt install, venv, pip install - each on own machine | - |
| T05 | Create the shared skeleton | A (B pulls) | Folders, `requirements.txt`, `.gitignore`, `config.py`; push | T02, T04 |
| T06 | Lock the data contract | Both | Agree the key names in `splits.joblib` out loud | T05 |
| **PHASE 2 - INDEPENDENT BUILD (~3 hrs, no waiting)** ||||
| T07 | Put the dataset in place | Both | Move CSV to `data/raw/`, make `RAW_FILE` match | T03, T05 |
| T08 | Build `explore.py` | A | Lab Step 1: load, print, class balance chart | T07 |
| T09 | Build `clean.py` | A | Lab Step 2: drop IDs, fix inf/NaN, dedupe, sample | T08 |
| T10 | Record the cleaning numbers | A | Write down every before/after count for the report | T09 |
| T11 | Build `prepare.py` | A | Lab Steps 3–4: stratified 60/20/20, scale on train only | T09 |
| T12 | Push the pipeline | A | Commit and push A's four files | T11 |
| T13 | Build `metrics.py` | B | All five scores incl. hand-written FAR | T05 |
| T14 | Build `make_dummy_splits.py` | B | Fake `splits.joblib` so B can start now | T06 |
| T15 | Build `train_binary.py` | B | Lab Steps 5–6: LR + RF + neural net, tested on fake data | T13, T14 |
| T16 | Build `ablation.py` | B | Lab Step 7: scaling on vs. off | T15 |
| T17 | Build `multiclass.py` | B | Which attack type is it | T13, T14 |
| T18 | Build `compare.py` | B | Lab Step 8: one final table + comparison chart | T15 |
| T19 | Build `run_all.py` | B | Whole pipeline in one command | T18 |
| T20 | Push the modelling code | B | Commit and push B's six files | T19 |
| **PHASE 3 - INTEGRATION (~30 min, together)** ||||
| T21 | Sync both machines | Both | Pull each other's work, confirm all 10 files present | T12, T20 |
| T22 | Delete the fake data, run for real | Both | Wipe `data/processed/`, run `run_all.py` on real CSV | T21, T07 |
| T23 | Cross-check the numbers | Both | Confirm both machines print identical results | T22 |
| **PHASE 4 - WRITE-UP (~2 hrs, independent again)** ||||
| T24 | Write `README.md` | A | How to run, libraries, seed | T23 |
| T25 | Write report §1 - the problem | A | What an IDS is, binary vs. multiclass | T23 |
| T26 | Write report §2 - what we did | A | Cleaning, split, models, settings | T10, T23 |
| T27 | Write report §3 - results | B | The table + 2 captioned figures + ablation numbers | T23 |
| T28 | Write report §4 - discussion | B | Which model wins, what FAR means in practice | T27 |
| T29 | Sanity-check every number | B | Confirm nothing was copied from a fake-data run | T27 |
| **PHASE 5 - JOINT FINISH (~1 hr, together)** ||||
| T30 | Merge the report | Both | Combine into one document, add who-did-what + AI disclosure | T26, T28 |
| T31 | Fresh-clone reproducibility test | The person who did NOT write the code being tested | Clone into an empty folder, run from scratch | T30 |
| T32 | Export and submit | Both | Report to PDF, build the zip, upload to Canvas | T31 |
| T33 | *(Optional)* Full-size run | Either | Set `SAMPLE_FRACTION = 1.0`, rerun, update numbers | T32 |

---

# The tasks in detail

---

## PHASE 1 - JOINT KICKOFF

Do this part **in the same room or on one call.** It is short, and it buys you total independence
afterwards.

---

### T01 - Split the roles
**Owner:** Both · **Depends on:** -

**What to do.** Decide who is **Person A (Data & Pipeline)** and who is **Person B (Models &
Evaluation)**. Write the decision in a note - you will need it for the "who did what" line in the
report, which the lab explicitly requires.

Read the ownership map at the top of this file together so you both know which files are yours.

**Done when:** you can both say, without looking, which files you own.

---

### T02 - Set up the shared repo
**Owner:** Both · **Depends on:** T01

**What to do.** You already have a git repository here. Create an empty repo on GitHub, then from
this folder:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Add the other person as a collaborator (GitHub: Settings → Collaborators). They then clone it:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
```

**Done when:** both of you can `git push` a trivial change and the other can `git pull` it. Test
this now - do not discover a permissions problem at 2am.

---

### T03 - Start the dataset download
**Owner:** Both · **Depends on:** -

**What to do.** Start this **first**, before anything else, and let it run in the background while
you do T04 and T05. It is large.

Go to https://www.unb.ca/cic/datasets/ids-2017.html, fill in the short free form, download
`MachineLearningCSV.zip`. Unzip it. You want
**`Wednesday-workingHours.pcap_ISCX.csv`**.

**Both of you download it.** It is gitignored (far too big for git), so each machine needs its own
copy. This is also what lets either of you run the whole pipeline alone later.

Details and alternatives: GUIDE.md Part 3.

**Done when:** both of you have the CSV on disk.

---

### T04 - Install tools and libraries
**Owner:** Both, independently · **Depends on:** -

**What to do.** Each person on their own machine, following **GUIDE.md Part 1**:

```bash
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt     # after T05 creates it
python -c "import pandas, sklearn, matplotlib; print('All libraries OK')"
```

**Done when:** both machines print `All libraries OK`.

> This machine has Python 3.13.7 with **no pip and no ensurepip**, so the `apt` line is not
> optional - without it every later step fails.

---

### T05 - Create the shared skeleton
**Owner:** A creates and pushes; B pulls · **Depends on:** T02, T04

**What to do.** Person A only, so these files have a single author and cannot conflict:

```bash
mkdir -p src data/raw data/processed results/figures results/tables results/models report
```

Then create, from SCAFFOLD.md:
- `requirements.txt` (section 4.1)
- `.gitignore` (section 4.2)
- `src/config.py` (section 4.3)

```bash
git add -A && git commit -m "Add project skeleton and config" && git push
```

Person B then runs `git pull`.

**Why A owns `config.py`:** B reads it constantly but never edits it. One author, no conflicts. If B
needs a setting changed, B asks A.

**Done when:** both machines have identical `src/config.py` and `ls src/` shows it.

---

### T06 - Lock the data contract
**Owner:** Both · **Depends on:** T05

**What to do.** This 10-minute conversation is what makes the rest of the project parallel. Sit
together and agree out loud that `src/prepare.py` will save a dictionary containing **exactly**
these keys, and that nothing else will change:

| Key | What it holds |
|---|---|
| `X_train`, `X_val`, `X_test` | feature tables, **unscaled** (for tree models) |
| `X_train_s`, `X_val_s`, `X_test_s` | the same rows, **scaled** (for LR / SVM / neural net) |
| `yb_train`, `yb_val`, `yb_test` | binary answers: `0` = normal, `1` = attack |
| `ym_train`, `ym_val`, `ym_test` | multiclass answers: `"BENIGN"`, `"DoS Hulk"`, ... |
| `feature_names` | list of column names |
| `scaler` | the fitted StandardScaler |
| `seed` | the random seed used |

From this moment: **A guarantees they will produce this. B assumes it exists.** Neither of you
needs to talk to the other again until Phase 3.

**Done when:** you have both read the list and agreed. Do not skip this because it looks like
nothing - if you get the key names wrong, Phase 3 breaks and you will not know whose fault it is.

---

## PHASE 2 - INDEPENDENT BUILD

**Stop coordinating now.** A works down the left column, B works down the right. You will not need
each other until T21.

---

### T07 - Put the dataset in place
**Owner:** Both · **Depends on:** T03, T05

**What to do.**

```bash
mv ~/Downloads/Wednesday-workingHours.pcap_ISCX.csv data/raw/
ls data/raw/
```

The filename that prints must match the `RAW_FILE` line in `src/config.py` **exactly** -
capitals, hyphens, dots and all. If it does not, **B asks A to change it** (A owns `config.py`).

**Done when:** `ls data/raw/` shows the CSV and the name matches `config.py`.

---

## PERSON A's TRACK

---

### T08 - Build `explore.py` (Lab Step 1)
**Owner:** A · **Depends on:** T07

**What to do.** Copy SCAFFOLD.md section 4.5 into `src/explore.py`, then:

```bash
python src/explore.py
xdg-open results/figures/class_balance.png
```

**Done when:** it prints the row/column counts and the label breakdown, and `class_balance.png`
exists. **Keep that chart - the lab requires it.**

**Watch out:** if you get `KeyError: 'Label'`, you dropped the `.str.strip()` lines. The CICIDS
column names have leading spaces.

---

### T09 - Build `clean.py` (Lab Step 2)
**Owner:** A · **Depends on:** T08

**What to do.** Copy SCAFFOLD.md section 4.6 into `src/clean.py`, then `python src/clean.py`.

It removes ID columns, fixes infinity/NaN, drops duplicates and dead columns, drops ultra-rare
classes, and takes a 20% stratified sample.

**Done when:** `data/processed/clean.csv` exists and six numbered report lines printed.

**Understand before moving on:** why dropping IP addresses and timestamps matters. GUIDE.md Part 4
Step 2 explains it - this is the leakage argument, and it is the single best thing you can
demonstrate understanding of in the report.

---

### T10 - Record the cleaning numbers
**Owner:** A · **Depends on:** T09

**What to do.** Copy the output of T09 into a scratch note. You need:

- rows and columns before cleaning
- how many ID columns dropped, and which
- how many infinity and NaN values found; rows lost
- how many duplicate rows dropped
- how many constant columns dropped
- which rare classes were dropped, and their counts
- final rows and columns

**Done when:** the note exists. **Do this now, not later** - the numbers scroll off the terminal
and re-running takes minutes.

---

### T11 - Build `prepare.py` (Lab Steps 3–4)
**Owner:** A · **Depends on:** T09

**What to do.** Copy SCAFFOLD.md section 4.7 into `src/prepare.py`, then `python src/prepare.py`.

**Done when:** `data/processed/splits.joblib` exists, the three splits print at roughly 60/20/20,
and the three attack rates are nearly identical.

**Check two things carefully - they are worth 25% of the grade:**
1. The three attack rates match → stratification worked.
2. The output confirms the scaler was fitted on **training data only**.

**Then verify the contract from T06:**

```bash
python -c "import joblib; d = joblib.load('data/processed/splits.joblib'); print(sorted(d.keys()))"
```

Every key from the T06 table must be there. If one is missing, B's code will break in Phase 3 and
it will be your fault, not theirs.

---

### T12 - Push the pipeline
**Owner:** A · **Depends on:** T11

**What to do.**

```bash
git pull --rebase
git add src/explore.py src/clean.py src/prepare.py
git commit -m "Add data pipeline: explore, clean, prepare"
git push
```

Message B: *"pipeline pushed, contract verified."*

**Done when:** pushed. A is now free - go start T25.

---

## PERSON B's TRACK - runs at the same time as A's

---

### T13 - Build `metrics.py`
**Owner:** B · **Depends on:** T05

**What to do.** Copy SCAFFOLD.md section 4.4 into `src/metrics.py`.

This computes accuracy, macro-F1, recall, ROC-AUC and FAR. **FAR is hand-written** because
scikit-learn has no built-in for it - `FP / (FP + TN)`, taken from the confusion matrix.

Read GUIDE.md Part 5 now, properly. You own the results and discussion sections, so you need to
actually understand these five numbers, not just print them.

**Done when:** `python -c "import sys; sys.path.insert(0,'src'); import metrics; print('ok')"` runs
without error.

---

### T14 - Build `make_dummy_splits.py`
**Owner:** B · **Depends on:** T06

**What to do.** This is the file that frees you from waiting for A. Create
`src/make_dummy_splits.py`:

```python
"""Creates a FAKE splits.joblib so the modelling scripts can be built and tested
before the real cleaning pipeline is finished.

This lets Person B work without waiting for Person A.

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
```

Run it:

```bash
python src/make_dummy_splits.py
```

It writes to the **same path** A's real pipeline uses, with the **same keys** agreed in T06. Your
scripts cannot tell the difference - which is exactly the point. It is small and fast, so your
train/test cycle is seconds instead of minutes.

**Done when:** `data/processed/splits.joblib` exists and the warning banner printed.

> **The one danger:** forgetting the numbers are fake. They are deliberately absurd - 6,000 rows,
> 20 features, attack names starting with "Fake". T22 wipes them; T29 double-checks. Never copy a
> number into the report before T22.

---

### T15 - Build `train_binary.py` (Lab Steps 5–6)
**Owner:** B · **Depends on:** T13, T14

**What to do.** Copy SCAFFOLD.md section 4.8 into `src/train_binary.py`, then
`python src/train_binary.py`.

Three model families - Logistic Regression, Random Forest, and an MLP neural network. For each: try
a few settings, pick the winner **on the validation set**, then score that winner **once** on the
test set.

**Done when:** it runs on the fake data and writes `results/tables/binary_results.csv`. On fake data
this takes seconds.

**Do not be impressed by the fake scores.** The synthetic problem is easy on purpose. You are
testing that the code runs, nothing else.

**Understand:** why the winner is picked on validation and not test. That is the "no test-set
peeking" rule, and it is a graded criterion. GUIDE.md Part 4 Step 3.

---

### T16 - Build `ablation.py` (Lab Step 7)
**Owner:** B · **Depends on:** T15

**What to do.** Copy SCAFFOLD.md section 4.9 into `src/ablation.py`, then `python src/ablation.py`.

Trains each model twice - once without scaling, once with - changing **exactly one thing**.

**Done when:** `results/tables/ablation_results.csv` exists with two rows per model.

**Note:** the fake data is generated already roughly scaled, so the effect will look small here.
That is an artefact of the fake data, not a bug. The real effect appears after T22.

---

### T17 - Build `multiclass.py`
**Owner:** B · **Depends on:** T13, T14

**What to do.** Copy SCAFFOLD.md section 4.10 into `src/multiclass.py`, then
`python src/multiclass.py`.

**Done when:** a per-class report prints and `results/figures/confusion_multiclass.png` exists.

---

### T18 - Build `compare.py` (Lab Step 8)
**Owner:** B · **Depends on:** T15

**What to do.** Copy SCAFFOLD.md section 4.11 into `src/compare.py`, then `python src/compare.py`.

**Done when:** a formatted table prints and `results/tables/final_comparison.csv` exists.

If `to_markdown()` errors, run `pip install tabulate` (it is already in `requirements.txt`).

---

### T19 - Build `run_all.py`
**Owner:** B · **Depends on:** T18

**What to do.** Copy SCAFFOLD.md section 4.12 into `run_all.py` (top level, **not** in `src/`).

You cannot fully test it yet - it starts with A's `explore.py`, which you may not have. Check the
syntax at least:

```bash
python -c "import ast; ast.parse(open('run_all.py').read()); print('syntax OK')"
```

**Done when:** syntax check passes. Real test is T22.

---

### T20 - Push the modelling code
**Owner:** B · **Depends on:** T19

**What to do.**

```bash
git pull --rebase
git add src/metrics.py src/make_dummy_splits.py src/train_binary.py \
        src/ablation.py src/multiclass.py src/compare.py run_all.py
git commit -m "Add modelling: metrics, training, ablation, multiclass, comparison"
git push
```

**Done when:** pushed. B is now free - go start T27's structure (headings and captions), even
without real numbers.

---

## PHASE 3 - INTEGRATION

Short, and worth doing together.

---

### T21 - Sync both machines
**Owner:** Both · **Depends on:** T12, T20

**What to do.**

```bash
git pull --rebase
ls src/
```

**Done when:** both machines show all 10 files: `config.py`, `metrics.py`, `explore.py`,
`clean.py`, `prepare.py`, `train_binary.py`, `ablation.py`, `multiclass.py`, `compare.py`,
`make_dummy_splits.py`, plus `run_all.py` at the top level.

---

### T22 - Delete the fake data and run for real
**Owner:** Both · **Depends on:** T21, T07

**What to do.** **This is the most important task in the file.** Destroy every trace of the fake
data and its results, then run the real thing:

```bash
rm -f data/processed/*
rm -f results/tables/* results/figures/* results/models/*
python run_all.py
```

Takes 5–15 minutes.

**Done when:** it completes with no errors **and** the printed row count is around **140,000, not
6,000**, with roughly **70 features, not 20**. If you see 6,000, you are still on fake data - the
`rm` did not happen.

**From this moment, every number is real.** Nothing that came before it goes anywhere near the
report.

---

### T23 - Cross-check the numbers
**Owner:** Both · **Depends on:** T22

**What to do.** Both of you run `python src/compare.py` and compare the printed tables.

**They should be identical**, because the seed is fixed at 42.

**Done when:** the numbers match on both machines. If they do not, someone has a different CSV file,
a different `SAMPLE_FRACTION`, or a different library version - find out which before writing
anything. Matching numbers on two machines is your proof of reproducibility, which is a graded item.

---

## PHASE 4 - WRITE-UP

Independent again. A and B write different sections of the same report; merge at T30.

Agree one thing first: **where the document lives.** Google Docs is easiest for two people. If you
prefer to keep it in git, use `report/report_A.md` and `report/report_B.md` so ownership stays
disjoint, and merge at T30.

---

### T24 - Write `README.md`
**Owner:** A · **Depends on:** T23

**What to do.** Follow the template in GUIDE.md Part 6. Must cover: what it is, setup commands, how
to get the data, how to run, **the random seed (42)**, the libraries, where the output lands.

**Done when:** someone who has never seen the project could run it from your README alone.

---

### T25 - Write report §1 - the problem
**Owner:** A · **Depends on:** T23 *(can be drafted from T12 onwards)*

**What to do.** One short paragraph: what an IDS is, binary vs. multiclass, and why machine learning
instead of hand-written rules. Source material is GUIDE.md Part 0 - put it in your own words.

**Done when:** roughly a third of a page.

---

### T26 - Write report §2 - what we did
**Owner:** A · **Depends on:** T10, T23

**What to do.** Use your T10 notes. Cover:

- Which dataset file, rows before → after cleaning
- What was removed and **why** - especially the leakage argument for IPs, ports and timestamps
- The 60/20/20 stratified split, and the seed
- That the scaler was fitted on training data only, and why that matters
- Which models and which settings were tried
- That rare classes under 10 rows were dropped *(state it - an owned limitation earns marks)*

**Done when:** roughly three-quarters of a page, and every claim traces back to a real number.

---

### T27 - Write report §3 - results
**Owner:** B · **Depends on:** T23

**What to do.**

- **One table**, from `results/tables/final_comparison.csv`. Columns: accuracy, macro-F1, recall,
  ROC-AUC, FAR.
- **One or two figures.** Best picks: `model_comparison.png` and `confusion_multiclass.png`
  (or `class_balance.png` if you want to show the imbalance visually).
- **The ablation before/after numbers**, with one line on what changed.
- **Caption everything, then refer to each caption in the text** - "as Table 1 shows...",
  "Figure 2 shows that...". The rubric rewards figures the writing actually uses. **An uncaptioned
  figure nobody mentions earns nothing.**

**Done when:** table and figures are in, each has a caption, and each caption is referenced in a
sentence.

---

### T28 - Write report §4 - discussion
**Owner:** B · **Depends on:** T27

**What to do.** The section carrying the most marks. Cover:

- **Which model you would deploy, and why** - argue from macro-F1 **and** FAR together. Use the
  worked example in GUIDE.md section 5.3 as a shape, with your own numbers.
- **What FAR means in practice** - multiply your FAR by a million connections a day and state the
  number of daily false alarms. That single sentence shows you understand what the metric is *for*.
- **Why accuracy alone misleads here** - the always-say-normal argument.
- **What the ablation proved** - and why Random Forest barely moved (it asks threshold questions,
  which are unit-independent).
- **Limitations, honestly:** one day of one synthetic dataset; a 20% sample; rare classes dropped; a
  lab network is not a real one; 2017 attacks may not resemble today's.

**Done when:** roughly a page, and it reaches an actual recommendation rather than trailing off.

---

### T29 - Sanity-check every number
**Owner:** B · **Depends on:** T27

**What to do.** Ten minutes that protect the whole grade.

- [ ] Every number in the report came from a run **after** T22
- [ ] No attack name in any figure starts with "Fake"
- [ ] Row counts in §2 are in the ~140,000 range, not 6,000
- [ ] FAR values are **low** for good models - you have not accidentally reported it as if higher
      were better
- [ ] The table has **all five** metrics; the lab is explicit that accuracy alone is not enough
- [ ] macro-F1, recall and ROC-AUC all sit between 0 and 1

**Done when:** all six boxes ticked.

---

## PHASE 5 - JOINT FINISH

---

### T30 - Merge the report
**Owner:** Both · **Depends on:** T26, T28

**What to do.** Combine the four sections into one document, in order. Then add:

- **§5 Who did what** - one or two lines. The lab is explicit: *"If one person does everything, that
  shows up in individual grades."* Say honestly who owned the data pipeline and who owned the
  modelling.
- **AI disclosure** - required. The lab says *"If you use an AI assistant, say so in the report."*
  Wording is in GUIDE.md section 7.6.

Read each other's sections. B checks A's §2 matches what the code actually does; A checks B's §4
does not overstate what the numbers show.

**Done when:** one document, 2–3 pages, all six parts present, both of you have read all of it.

---

### T31 - Fresh-clone reproducibility test
**Owner:** Whoever did **not** write most of the code being tested · **Depends on:** T30

**What to do.** The rubric asks that the code *"runs start-to-finish and reproduces your numbers."*
Prove it, in a clean folder, following only your own README:

```bash
cd ~/Desktop
git clone https://github.com/<user>/<repo>.git fresh-test
cd fresh-test
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/raw && cp ~/Desktop/AI-for-Cybersecurity-Lab1/data/raw/*.csv data/raw/
python run_all.py
```

**Done when:** it runs to completion and the numbers match the report. If it does not, the README is
wrong - fix the README, not the report.

> Have the *other* person do this. The author unconsciously fills in missing steps from memory; a
> second pair of eyes finds them.

---

### T32 - Export and submit
**Owner:** Both · **Depends on:** T31

**What to do.**

1. Export the report as **PDF**.
2. Build the zip:

```bash
cd ~/Desktop
zip -r Lab1_submission.zip AI-for-Cybersecurity-Lab1 \
  -x "*/.venv/*" "*/data/*" "*/.git/*" "*/__pycache__/*" "*/fresh-test/*"
```

3. Check the size - should be well under 5 MB. If it is hundreds of MB, an exclusion did not apply.
4. Upload **both** the zip (or repo link) **and** the report PDF to Canvas.

**Done when:** both files are uploaded and you have gone through the checklist at the end of
GUIDE.md.

> The lab says late submissions are not accepted in general, and that if a lab does not reach grade
> 3 you may resubmit once before the final reporting date.

---

### T33 - *(Optional)* Full-size run
**Owner:** Either · **Depends on:** T32

**What to do.** Only if you have time to spare **after** submitting something that works. Ask A to
set `SAMPLE_FRACTION = 1.0` in `config.py`, then `python run_all.py`. Expect 30–90 minutes and much
more memory use.

If it finishes and the numbers improve, update the report and resubmit. If your machine runs out of
memory, revert to `0.20` - **the sampled version is explicitly what the lab asked for**, so this is
a bonus, never a requirement.

---

## Critical path

The shortest possible route from nothing to a submission:

```
T01 -> T02 -> T05 -> T06 -> T07 -> T08 -> T09 -> T11 -> T12
                                                          \
                                                           T21 -> T22 -> T23 -> T26/T28 -> T30 -> T31 -> T32
                                                          /
T13 -> T14 -> T15 -> T18 -> T19 -> T20 ------------------
```

Everything on **B's branch (T13–T20) is free** - it happens entirely in parallel with A's work and
adds nothing to the total time. That is what the dummy-data trick bought you.

**The genuine bottleneck is T03, the download.** Start it first, before you do anything else.

## If one of you falls behind

Because the dummy contract exists, either person can run the whole project alone if they have to.
If A stalls, B can run A's scripts themselves (they are in git). If B stalls, A can do the same.
Nobody is ever fully blocked - but say so early rather than at the deadline, and be honest in the
"who did what" line either way.
