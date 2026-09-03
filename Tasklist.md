# Tasklist.md — The Work, In Order

Two people. Every entry below is actual implementation work — no meetings, no sign-offs, no
process steps.

- **[GUIDE.md](GUIDE.md)** = how to do things (explanations, commands, concepts)
- **[SCAFFOLD.md](SCAFFOLD.md)** = the code to copy
- **Tasklist.md** (this file) = what to build, who builds it, and what blocks what

---

## How the work splits

Every file has exactly one owner, so you never edit the same file at the same time.

| Person A — Data & Pipeline | Person B — Models & Evaluation |
|---|---|
| `src/config.py` | `src/metrics.py` |
| `src/explore.py` | `src/make_dummy_splits.py` |
| `src/clean.py` | `src/train_binary.py` |
| `src/prepare.py` | `src/ablation.py` |
| `README.md` | `src/multiclass.py` |
| Report §1 Problem, §2 What we did | `src/compare.py`, `run_all.py` |
| | Report §3 Results, §4 Discussion |

**Why B can start immediately instead of waiting for A.** A's pipeline ends by saving one file,
`data/processed/splits.joblib`, holding a dictionary. B's code only ever reads that dictionary — it
does not care where it came from. So B's first job (T11) is a short script that generates a **fake**
`splits.joblib` full of random numbers with the same keys, and B builds and tests the entire
modelling half against it from hour one. When A's real pipeline lands, delete the fake file and
rerun. No code changes.

The keys both sides rely on:

| Key | What it holds |
|---|---|
| `X_train`, `X_val`, `X_test` | feature tables, **unscaled** (for tree models) |
| `X_train_s`, `X_val_s`, `X_test_s` | the same rows, **scaled** (for LR / neural net) |
| `yb_train`, `yb_val`, `yb_test` | binary answers: `0` = normal, `1` = attack |
| `ym_train`, `ym_val`, `ym_test` | multiclass answers: `"BENIGN"`, `"DoS Hulk"`, ... |
| `feature_names`, `scaler`, `seed` | column names, the fitted scaler, the random seed |

---

## Master table

| Num | Title | Owner | What To Do | Depends On |
|---|---|---|---|---|
| T01 | Download the dataset | Both | Register at UNB, get CICIDS2017, unzip; start this first | — |
| T02 | Install tools and libraries | Both | apt install, venv, pip install, verify imports | — |
| T03 | Create the project skeleton | A | Folders, `requirements.txt`, `.gitignore` | T02 |
| T04 | Create `config.py` | A | Seed, paths, split sizes, ID columns to drop | T03 |
| T05 | Put the dataset in place | Both | Move CSV to `data/raw/`, make `RAW_FILE` match exactly | T01, T04 |
| T06 | Build `explore.py` | A | Lab Step 1: load, print shape/columns/balance, bar chart | T05 |
| T07 | Build `clean.py` | A | Lab Step 2: drop IDs, fix inf/NaN, dedupe, sample 20% | T06 |
| T08 | Record the cleaning numbers | A | Write down every before/after count while on screen | T07 |
| T09 | Build `prepare.py` | A | Lab Steps 3–4: stratified 60/20/20, scale on train only | T07 |
| T10 | Build `metrics.py` | B | Accuracy, macro-F1, recall, ROC-AUC, hand-written FAR | T04 |
| T11 | Build `make_dummy_splits.py` | B | Fake `splits.joblib` so B can build without waiting | T04 |
| T12 | Build `train_binary.py` | B | Lab Steps 5–6: LR + Random Forest + neural network | T10, T11 |
| T13 | Build `ablation.py` | B | Lab Step 7: scaling on vs. off, one thing changed | T12 |
| T14 | Build `multiclass.py` | B | Which attack type, plus confusion matrix | T10, T11 |
| T15 | Build `compare.py` | B | Lab Step 8: one final table + comparison chart | T12 |
| T16 | Build `run_all.py` | B | Whole pipeline in one command | T13, T14, T15 |
| T17 | Delete the fake data, run for real | Both | Wipe `data/processed/` + `results/`, run on the real CSV | T05, T09, T16 |
| T18 | Write `README.md` | A | How to run, libraries, the seed | T17 |
| T19 | Report §1 — the problem | A | What an IDS is, binary vs. multiclass | — |
| T20 | Report §2 — what we did | A | Cleaning, split, models, settings, limitations | T08, T17 |
| T21 | Report §3 — results | B | The table + 2 captioned figures + ablation numbers | T17 |
| T22 | Report §4 — discussion | B | Which model wins, what FAR means in practice | T21 |
| T23 | Sanity-check every number | B | Confirm nothing came from a fake-data run | T21 |
| T24 | Assemble the report | Both | Four sections + who-did-what + AI disclosure | T19, T20, T22 |
| T25 | Reproducibility test | Either | Run from scratch in a clean folder, README only | T18, T24 |
| T26 | Export and submit | Both | Report to PDF, build the zip, upload to Canvas | T25 |
| T27 | *(Optional)* Full-size run | Either | `SAMPLE_FRACTION = 1.0`, rerun, update numbers | T26 |

---

# The tasks in detail

---

### T01 — Download the dataset
**Owner:** Both · **Depends on:** —

**What to do.** Start this **before anything else** and let it run in the background — it is the
one genuine bottleneck in the project.

Go to https://www.unb.ca/cic/datasets/ids-2017.html, fill in the short free form, download
`MachineLearningCSV.zip`, unzip it. You want **`Wednesday-workingHours.pcap_ISCX.csv`** — several
denial-of-service attacks plus normal traffic, good size, sensible balance.

Do **not** use `Monday-WorkingHours.pcap_ISCX.csv` — it is normal traffic only, with no attacks to
learn from.

Both of you need your own copy: the file is gitignored (far too big for git), and having it on both
machines means either person can run the whole pipeline alone.

Alternatives and details: GUIDE.md Part 3.

**Done when:** the CSV is on disk on both machines.

---

### T02 — Install tools and libraries
**Owner:** Both, each on their own machine · **Depends on:** —

**What to do.** Follow GUIDE.md Part 1:

```bash
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt        # once T03 has created it
python -c "import pandas, sklearn, matplotlib; print('All libraries OK')"
```

**Done when:** both machines print `All libraries OK`.

> This machine has Python 3.13.7 with **no pip and no ensurepip installed**, so the `apt` line is
> not optional — skip it and every later step fails.
>
> The `(.venv)` in your prompt vanishes when you close the terminal. Every new terminal needs
> `source .venv/bin/activate` again. A `ModuleNotFoundError` almost always means you forgot.

---

### T03 — Create the project skeleton
**Owner:** A · **Depends on:** T02

**What to do.**

```bash
mkdir -p src data/raw data/processed results/figures results/tables results/models report
```

Then create `requirements.txt` (SCAFFOLD.md section 4.1) and `.gitignore` (section 4.2).

**Done when:** `ls` shows `data`, `report`, `results`, `src`, and `pip install -r requirements.txt`
succeeds.

---

### T04 — Create `config.py`
**Owner:** A · **Depends on:** T03

**What to do.** Copy SCAFFOLD.md section 4.3 into `src/config.py`.

Every setting in the project lives here: the random seed (42), all file paths, the 60/20/20 split
sizes, the sample fraction, and the list of ID columns to drop.

B reads this file constantly but never edits it. If B needs a setting changed, A changes it.

**Done when:** `python -c "import sys; sys.path.insert(0,'src'); import config; print(config.SEED)"`
prints `42`.

---

### T05 — Put the dataset in place
**Owner:** Both · **Depends on:** T01, T04

**What to do.**

```bash
mv ~/Downloads/Wednesday-workingHours.pcap_ISCX.csv data/raw/
ls data/raw/
```

The filename that prints must match the `RAW_FILE` line in `src/config.py` **exactly** — capitals,
hyphens, dots and all. If it does not, A edits `config.py` to match.

**Done when:** `ls data/raw/` shows the CSV and the name matches `config.py`.

---

## PERSON A's TRACK

---

### T06 — Build `explore.py` (Lab Step 1)
**Owner:** A · **Depends on:** T05

**What to do.** Copy SCAFFOLD.md section 4.5 into `src/explore.py`, then:

```bash
python src/explore.py
xdg-open results/figures/class_balance.png
```

**Done when:** it prints the row and column counts and the label breakdown, and
`class_balance.png` exists. **Keep that chart — the lab requires it in Step 1.**

**Watch out:** `KeyError: 'Label'` means you dropped the `.str.strip()` lines. The CICIDS column
names have leading spaces in them.

---

### T07 — Build `clean.py` (Lab Step 2)
**Owner:** A · **Depends on:** T06

**What to do.** Copy SCAFFOLD.md section 4.6 into `src/clean.py`, then `python src/clean.py`.

It drops ID columns, fixes infinity and NaN, removes duplicate rows and dead columns, drops
ultra-rare classes, and takes a 20% stratified sample.

**Done when:** `data/processed/clean.csv` exists and six numbered report lines printed.

**Understand before moving on:** why dropping IP addresses, ports and timestamps matters. They are
name tags — they say *who* and *when*, not *what an attack looks like*. Leave them in and the model
memorises "traffic from 192.168.10.50 is bad", scoring brilliantly on your test set and uselessly on
real traffic. That is **data leakage**, and explaining it is the single best way to show
understanding in the report. GUIDE.md Part 4 Step 2.

---

### T08 — Record the cleaning numbers
**Owner:** A · **Depends on:** T07

**What to do.** Copy the T07 output into a note. You need:

- rows and columns before cleaning
- how many ID columns dropped, and which
- how many infinity and NaN values found, and rows lost to them
- how many duplicate rows dropped
- how many constant columns dropped
- which rare classes were dropped, and their counts
- final rows and columns

**Done when:** the note exists. **Do it now, not later** — the output scrolls away and re-running
costs minutes.

---

### T09 — Build `prepare.py` (Lab Steps 3–4)
**Owner:** A · **Depends on:** T07

**What to do.** Copy SCAFFOLD.md section 4.7 into `src/prepare.py`, then `python src/prepare.py`.

**Done when:** `data/processed/splits.joblib` exists, the splits print at roughly 60/20/20, and the
three attack rates are nearly identical.

**Check two things — they carry 25% of the grade:**
1. The three attack rates match → stratification worked.
2. The output confirms the scaler was fitted on **training data only**. Fitting it on everything
   leaks information about the test set into training.

Then confirm the keys B's code expects are all present:

```bash
python -c "import joblib; d = joblib.load('data/processed/splits.joblib'); print(sorted(d.keys()))"
```

Compare against the key table at the top of this file. A missing key breaks B's scripts at T17.

---

## PERSON B's TRACK — runs at the same time as A's

---

### T10 — Build `metrics.py`
**Owner:** B · **Depends on:** T04

**What to do.** Copy SCAFFOLD.md section 4.4 into `src/metrics.py`.

Computes accuracy, macro-F1, recall, ROC-AUC and FAR. **FAR is hand-written** — scikit-learn has no
built-in for it. It is `FP / (FP + TN)`, pulled out of the confusion matrix.

Read GUIDE.md Part 5 properly while you do this. You own the results and discussion sections, so
you need to understand these five numbers, not just print them. The two that matter are **macro-F1**
(higher is better) and **FAR** (lower is better).

**Done when:** `python -c "import sys; sys.path.insert(0,'src'); import metrics; print('ok')"` runs
clean.

---

### T11 — Build `make_dummy_splits.py`
**Owner:** B · **Depends on:** T04

**What to do.** This is the file that lets you build everything else today instead of waiting for A.
Create `src/make_dummy_splits.py`:

```python
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
```

```bash
python src/make_dummy_splits.py
```

It writes to the same path and with the same keys A's real pipeline uses, so your scripts cannot
tell the difference. It is also tiny, so your test cycle is seconds rather than minutes.

**Done when:** `data/processed/splits.joblib` exists and the warning banner printed.

> **The one danger is forgetting the numbers are fake.** They are deliberately absurd — 6,000 rows,
> 20 features, attack names starting with "Fake". T17 wipes them and T23 double-checks. Never copy
> a number into the report before T17.

---

### T12 — Build `train_binary.py` (Lab Steps 5–6)
**Owner:** B · **Depends on:** T10, T11

**What to do.** Copy SCAFFOLD.md section 4.8 into `src/train_binary.py`, then
`python src/train_binary.py`.

Three model families:
- **Logistic Regression** — draws one straight boundary. Fast, easy to explain.
- **Random Forest** — hundreds of decision trees voting. Usually strongest here.
- **MLP** — the neural network the lab requires.

For each: try a few settings, pick the winner **on the validation set**, then score that winner
**once** on the test set.

**Done when:** it runs on the fake data and writes `results/tables/binary_results.csv`.

**Do not be impressed by the fake scores** — the synthetic problem is easy on purpose. You are
testing that the code runs, nothing more.

**Understand:** why the winner is chosen on validation, never on test. Using the test set to make
choices means it is no longer unseen, and your reported score becomes a lie. That is the
"no test-set peeking" rule, and it is a graded criterion.

---

### T13 — Build `ablation.py` (Lab Step 7)
**Owner:** B · **Depends on:** T12

**What to do.** Copy SCAFFOLD.md section 4.9 into `src/ablation.py`, then `python src/ablation.py`.

Trains each model twice — once without scaling, once with — changing **exactly one thing** and
holding everything else identical.

**Done when:** `results/tables/ablation_results.csv` exists with two rows per model.

**Note:** the fake data comes out already roughly scaled, so the effect looks small here. That is an
artefact of the fake data, not a bug — the real effect shows up after T17.

---

### T14 — Build `multiclass.py`
**Owner:** B · **Depends on:** T10, T11

**What to do.** Copy SCAFFOLD.md section 4.10 into `src/multiclass.py`, then
`python src/multiclass.py`.

Same data and same split as the binary task; the only difference is that the answer being learned is
the full attack name rather than 0/1.

**Done when:** a per-class report prints and `results/figures/confusion_multiclass.png` exists.

**How to read the confusion matrix:** rows are what the traffic actually was, columns are what the
model guessed. The diagonal is where it got things right. A bright square off the diagonal means the
model systematically mistakes one attack for another — a genuinely interesting thing to write about.

---

### T15 — Build `compare.py` (Lab Step 8)
**Owner:** B · **Depends on:** T12

**What to do.** Copy SCAFFOLD.md section 4.11 into `src/compare.py`, then `python src/compare.py`.

**Done when:** a formatted table prints and `results/tables/final_comparison.csv` exists.

If `to_markdown()` errors, `pip install tabulate` (already in `requirements.txt`).

---

### T16 — Build `run_all.py`
**Owner:** B · **Depends on:** T13, T14, T15

**What to do.** Copy SCAFFOLD.md section 4.12 into `run_all.py` — top level, **not** in `src/`.

You cannot fully test it until A's scripts exist. Check the syntax now:

```bash
python -c "import ast; ast.parse(open('run_all.py').read()); print('syntax OK')"
```

**Done when:** syntax check passes. Real test is T17.

---

## BOTH TRACKS MEET HERE

---

### T17 — Delete the fake data and run for real
**Owner:** Both · **Depends on:** T05, T09, T16

**What to do.** **The most important task in this file.** Destroy every trace of the fake data and
everything computed from it, then run the real pipeline:

```bash
rm -f data/processed/*
rm -f results/tables/* results/figures/* results/models/*
python run_all.py
```

Takes 5–15 minutes.

**Done when:** it completes with no errors **and** the printed row count is around **140,000, not
6,000**, with roughly **70 features, not 20**. If you see 6,000, the `rm` did not happen.

Run it on both machines. The numbers should be identical because the seed is fixed at 42 — matching
results on two machines is your proof of reproducibility, which is graded.

**From this moment every number is real.** Nothing produced before it goes near the report.

---

## WRITE-UP

A and B write different sections; they get combined at T24. Google Docs is easiest for two people;
if you would rather keep it in git, use `report/report_A.md` and `report/report_B.md` so you are
never editing the same file.

---

### T18 — Write `README.md`
**Owner:** A · **Depends on:** T17

**What to do.** Follow the template in GUIDE.md Part 6. Must cover: what the project is, setup
commands, how to get the data, how to run it, **the random seed (42)**, the libraries used, and
where the output lands.

**Done when:** someone who has never seen the project could run it from your README alone.

---

### T19 — Report §1 — the problem
**Owner:** A · **Depends on:** —

**What to do.** One short paragraph: what an IDS is, binary vs. multiclass detection, and why
machine learning instead of hand-written rules. Source material is GUIDE.md Part 0 — put it in your
own words.

This needs no results, so it is the natural thing to write while a model is training.

**Done when:** roughly a third of a page.

---

### T20 — Report §2 — what we did
**Owner:** A · **Depends on:** T08, T17

**What to do.** Built from your T08 notes. Cover:

- Which dataset file, and rows before → after cleaning
- What was removed and **why** — especially the leakage argument for IPs, ports and timestamps
- The 60/20/20 stratified split, and the fixed seed
- That the scaler was fitted on training data only, and why that matters
- Which models, and which settings were tried
- That rare classes under 10 rows were dropped — **state it plainly; an owned limitation earns
  marks rather than losing them**

**Done when:** roughly three-quarters of a page, and every claim traces to a real number.

---

### T21 — Report §3 — results
**Owner:** B · **Depends on:** T17

**What to do.**

- **One table**, from `results/tables/final_comparison.csv`. Columns: accuracy, macro-F1, recall,
  ROC-AUC, FAR.
- **One or two figures.** Best picks: `model_comparison.png` and `confusion_multiclass.png`, or
  `class_balance.png` to show the imbalance.
- **The ablation before/after numbers**, with a line on what changed.
- **Caption everything, then refer to each caption in the text** — "as Table 1 shows…", "Figure 2
  shows that…". The rubric rewards figures the writing actually uses. **A figure nobody mentions
  earns nothing.**

**Done when:** table and figures are in, each captioned, each caption referenced in a sentence.

---

### T22 — Report §4 — discussion
**Owner:** B · **Depends on:** T21

**What to do.** The section carrying the most marks. Cover:

- **Which model you would deploy, and why** — argue from macro-F1 **and** FAR together. The worked
  example in GUIDE.md section 5.3 shows the shape; use your own numbers.
- **What FAR means in practice** — multiply your FAR by a million connections a day and state the
  resulting number of daily false alarms. That one sentence shows you understand what the metric is
  *for*.
- **Why accuracy alone misleads here** — a model that always answers "normal" scores ~80% accuracy
  on this data and catches zero attacks.
- **What the ablation proved** — and why Random Forest barely moved: it asks threshold questions
  like "is this above 500?", which mean the same thing in any units.
- **Limitations, honestly:** one day of one synthetic dataset; a 20% sample; rare classes dropped; a
  lab network is not a real one; 2017 attacks may not resemble today's.

**Done when:** roughly a page, ending in an actual recommendation rather than trailing off.

---

### T23 — Sanity-check every number
**Owner:** B · **Depends on:** T21

**What to do.** Ten minutes that protect the whole grade.

- [ ] Every number in the report came from a run **after** T17
- [ ] No attack name in any figure starts with "Fake"
- [ ] Row counts in §2 are in the ~140,000 range, not 6,000
- [ ] FAR values are **low** for the good models — you have not reported it as if higher were better
- [ ] The table has **all five** metrics; accuracy alone is explicitly not enough
- [ ] macro-F1, recall and ROC-AUC all sit between 0 and 1

**Done when:** all six ticked.

---

### T24 — Assemble the report
**Owner:** Both · **Depends on:** T19, T20, T22

**What to do.** Combine the four sections into one 2–3 page document, then add:

- **Who did what** — one or two lines. The lab is explicit that if one person does everything, it
  shows up in individual grades. Say honestly who owned the data pipeline and who owned the
  modelling.
- **AI disclosure** — required by the lab: *"If you use an AI assistant, say so in the report."*
  Wording is in GUIDE.md section 7.6.

Read each other's sections while you are here: B checks A's §2 matches what the code actually does;
A checks B's §4 does not claim more than the numbers support.

**Done when:** one document, all six parts present, both of you have read all of it.

---

### T25 — Reproducibility test
**Owner:** Whichever of you did **not** write most of the code · **Depends on:** T18, T24

**What to do.** The rubric asks that the code *"runs start-to-finish and reproduces your numbers."*
Prove it in a clean folder, following only the README:

```bash
cd ~/Desktop
git clone <your repo> fresh-test
cd fresh-test
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/raw && cp ~/Desktop/AI-for-Cybersecurity-Lab1/data/raw/*.csv data/raw/
python run_all.py
```

**Done when:** it runs to completion and the numbers match the report. If it does not, the README is
wrong — **fix the README, not the report.**

> Have the person who did *not* write the code do this. Authors unconsciously fill in missing steps
> from memory; a second pair of eyes finds them.

---

### T26 — Export and submit
**Owner:** Both · **Depends on:** T25

**What to do.**

1. Export the report as **PDF**.
2. Build the zip:

```bash
cd ~/Desktop
zip -r Lab1_submission.zip AI-for-Cybersecurity-Lab1 \
  -x "*/.venv/*" "*/data/*" "*/.git/*" "*/__pycache__/*" "*/fresh-test/*"
```

3. Check the size — should be well under 5 MB. Hundreds of MB means an exclusion did not apply.
4. Upload **both** the zip (or a repository link) **and** the report PDF to Canvas.

**Done when:** both uploaded, and the checklist at the end of GUIDE.md is fully ticked.

> Late submissions are not accepted in general. If a lab does not reach grade 3 you may resubmit it
> once, before the final reporting date.

---

### T27 — *(Optional)* Full-size run
**Owner:** Either · **Depends on:** T26

**What to do.** Only after you have submitted something that works. A sets `SAMPLE_FRACTION = 1.0`
in `config.py`, then `python run_all.py`. Expect 30–90 minutes and much heavier memory use.

If it finishes and the numbers improve, update the report and resubmit. If the machine runs out of
memory, revert to `0.20` — **the sampled version is explicitly what the lab asked for**, so this is
a bonus and never a requirement.

---

## Critical path

```
T01 -> T05 -> T06 -> T07 -> T09 ----\
                                     T17 -> T20/T21 -> T22 -> T24 -> T25 -> T26
T04 -> T10/T11 -> T12 -> T15 -> T16 -/
```

**B's entire track (T10–T16) is free** — it runs in parallel with A's and adds nothing to the total
time. That is what the fake-splits file at T11 buys you.

**The real bottleneck is T01, the download.** Start it before anything else.

Two natural waiting windows: while the dataset downloads (T01) and while models train (T12, T17).
T19 — writing the problem statement — needs no results and fits either gap.

## If one of you gets stuck

Both machines have the dataset and all the code, so either person can run the whole project alone.
If A stalls, B can run A's scripts; if B stalls, A can run B's. Nobody is ever fully blocked — but
raise it early rather than at the deadline, and either way be honest in the who-did-what line.
