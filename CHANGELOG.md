# CHANGELOG.md - What has been done, and what remains

Working document for Lab 1 (Building Your First Intrusion Detector).
Branch: `Implementation`. Last updated: 2026-09-06.

Task IDs refer to [TASKLIST.md](TASKLIST.md).

---

## Status at a glance

| Phase | State |
|---|---|
| Setup (T01-T05) | **Done** |
| Code (T06-T16) | **Done** - all 11 files written and executed |
| Real pipeline run (T17) | **Done** - 29.5 min, exit 0 |
| Number sanity checks (T23) | **Done** - all pass |
| README (T18) | **Done** |
| **Report (T19-T22, T24)** | **Not started** - this is the remaining work |
| Reproducibility test (T25) | Not started |
| Submission (T26) | Not started |

**The code is finished and the numbers are real. What is left is almost entirely writing.**

---

## Part 1 - Done

### Environment (T02)

Python **3.11.16**, installed with `uv`, in `.venv/`.

`sudo apt install python3.11` does **not** work on this machine and never will - Ubuntu 25.10
("questing") ships only `python3.13` and `python3.14`, and the deadsnakes PPA has no questing
series. GUIDE.md **Appendix A** documents all eleven install methods, which work and which do not.

Libraries per `requirements.txt`: tensorflow 2.17.1, torch 2.14.0, scikit-learn, pandas,
matplotlib, joblib, tabulate. **Note:** no script actually imports tensorflow or torch - the
neural network is scikit-learn's `MLPClassifier`. They are installed because the lab brief offers
all three and having them present means the model could be swapped without redoing setup.

### Dataset (T01, T05)

`Wednesday-workingHours.pcap_ISCX.csv` (225 MB) in `data/raw/`, from the `MachineLearningCVE/`
download. Filename matches `RAW_FILE` in `src/config.py` exactly. Gitignored.

### Code (T04, T06-T16)

Eleven files, all written and all executed:

| File | Task | Purpose |
|---|---|---|
| `src/config.py` | T04 | every setting: seed 42, paths, split sizes, columns to drop |
| `src/metrics.py` | T10 | accuracy, macro-F1, recall, ROC-AUC, hand-written FAR |
| `src/explore.py` | T06 | Lab Step 1 - load, describe, class-balance chart |
| `src/clean.py` | T07 | Lab Step 2 - drop IDs, fix inf/NaN, dedupe, sample |
| `src/prepare.py` | T09 | Lab Steps 3-4 - stratified 60/20/20, scale on train only |
| `src/train_binary.py` | T12 | Lab Steps 5-6 - LR, Random Forest, MLP |
| `src/ablation.py` | T13 | Lab Step 7 - scaling on vs off |
| `src/multiclass.py` | T14 | which attack type + confusion matrix |
| `src/compare.py` | T15 | Lab Step 8 - final table and chart |
| `src/make_dummy_splits.py` | T11 | fake splits so B is never blocked |
| `run_all.py` | T16 | whole pipeline in one command |

Every file matches its SCAFFOLD.md code block byte-for-byte. A verification script checks all 11
blocks against the files on disk, so the docs cannot silently drift from the code.

### Cleaning numbers (T08)

Captured from the final run. **These are the numbers for report section 2.**

| Stage | Value |
|---|---|
| Raw | 692,703 rows x 79 columns |
| ID columns dropped | 2 - `Destination Port`, `Fwd Header Length.1` |
| Infinity values found | 1,586 |
| Missing values found | 2,594 |
| Rows dropped for inf/NaN | 1,297 |
| Duplicate rows dropped | 106,415 |
| Constant columns dropped | 10 |
| Classes dropped (< 10 rows) | none |
| Classes **protected** (< 20 rows) | Heartbleed, all 11 rows kept |
| After 20% sample | **117,007 rows x 67 columns** |
| Features after label removal | 66 |

Raw class balance: BENIGN 440,031 (63.52%), DoS Hulk 231,073 (33.36%), DoS GoldenEye 10,293
(1.49%), DoS slowloris 5,796 (0.84%), DoS Slowhttptest 5,499 (0.79%), Heartbleed 11 (0.00%).

Split: train 70,203 / val 23,402 / test 23,402. Attack rate 0.3313 in all three - stratification
confirmed. Scaler fitted on training data only.

### Results (T17)

Full `run_all.py`, exit 0, 29.5 minutes. Binary test-set results:

| Model | accuracy | macro-F1 | recall | ROC-AUC | FAR |
|---|---|---|---|---|---|
| LogisticRegression | 0.9804 | 0.9779 | 0.9768 | 0.9978 | 0.0178 |
| **RandomForest** | **0.9984** | **0.9982** | **0.9977** | 0.9999 | **0.0012** |
| MLP (neural network) | 0.9943 | 0.9935 | 0.9914 | 0.9998 | 0.0043 |

Winning settings: LR `{'C': 1.0}`, RF `{'n_estimators': 100, 'max_depth': None}`,
MLP `{'hidden_layer_sizes': (64, 32)}`. All chosen on validation, scored once on test.

Ablation (scaling off -> on):

| Model | macro-F1 | FAR |
|---|---|---|
| LogisticRegression | 0.9091 -> 0.9779 | 0.0570 -> 0.0178 |
| MLP | 0.9675 -> 0.9935 | 0.0103 -> 0.0043 |
| RandomForest | 0.9982 -> 0.9984 | 0.0012 -> 0.0010 |

Multiclass: macro-F1 0.9937, macro-FAR 0.0006. Per-class F1 at or above 0.97 for every class.

Artifacts in `results/`: 6 figures, 3 tables, 4 saved models.

### Sanity checks (T23)

All pass: 117,007 rows (not 6,000), 66 features (not 20), no `source` key in the splits, no label
containing "Fake", all metrics within 0-1, all five metrics present in the table.

### README (T18)

Written, with the 3.11 requirement, setup commands, verification commands, data instructions, run
commands, and the seed.

---

## Part 2 - Changes made beyond the original plan

### Migrated all documentation from Python 3.13 to 3.11

GUIDE.md, TASKLIST.md, SCAFFOLD.md and README.md were written assuming the system Python 3.13.
All four now target 3.11 via uv. Added **GUIDE.md Appendix A**, documenting every way to install
3.11 on this machine - uv, standalone tarball, Docker, conda, pyenv, source build, mise/asdf - plus
the four that look plausible but do not work here (apt, deadsnakes, deadsnakes pinned to noble,
snap).

### Rare-class protection - `PROTECT_CLASS_BELOW`

**The problem.** Heartbleed has 11 raw rows. It cleared `MIN_CLASS_COUNT = 10` by one row, then the
20% sample cut it to 2, which landed **2 in train and 0 in test**. The class was in the training
data but absent from the test set - a phantom. `classification_report` silently omitted it, but the
confusion matrix reserved an all-zero row for it and `macro_false_alarm_rate` averaged over 6
classes when only 5 existed.

**The fix.** `PROTECT_CLASS_BELOW = 20` in `config.py`. Classes that survive `MIN_CLASS_COUNT` but
are smaller than this skip the sampling step and are kept whole. The policy is now three tiers:

> **drop below 10, keep whole below 20, sample normally at 20 and above.**

**The result.** Heartbleed keeps all 11 rows, splitting 7/2/2, so it appears in the test set.
The phantom row is gone and macro-FAR now averages six classes that all genuinely exist. Cost to
the headline number: macro-F1 moved from 0.9936 to 0.9937.

**The caveat that must reach the report.** Heartbleed's per-class scores rest on **2 test rows**.
The 1.00 it earns is not evidence of anything. State the support and say so explicitly - as an
owned limitation it earns marks; unqualified it reads as naive. Also note that a protected class is
deliberately over-represented relative to a true 20% sample.

Docs updated to match: SCAFFOLD.md 4.3 and 4.6 (code regenerated from source), SCAFFOLD.md section 5
decision table, GUIDE.md Part 4 Step 2, TASKLIST.md T07 and T08.

### Documentation corrections

- `make_dummy_splits.py` existed only in TASKLIST T11 - absent from SCAFFOLD's folder diagram, its
  numbered sections, and GUIDE's file table. Added as **SCAFFOLD.md section 4.13** and to both docs.
- File counts in GUIDE were wrong and self-contradictory ("eight files in `src/`" two lines above a
  table listing nine). Corrected to ten in `src/`, eleven including `run_all.py`.

### Google Colab package - `~/Desktop/collab/`

A self-contained copy that runs the same pipeline on Colab. `src/` is byte-identical to this
project, so results are directly comparable; everything Colab-specific lives in the notebook.

Contents: `Lab1_IDS_Colab.ipynb` (29 cells), `README.md`, `requirements-colab.txt`, `run_all.py`,
`src/`, and the CSV. 215 MB total. A 28 KB code-only zip is at `~/Desktop/collab-code-only.zip`.

**Important:** do not install this project's `requirements.txt` on Colab. It pins
`tensorflow<2.18`, which forces a numpy downgrade and a runtime restart for libraries the pipeline
never imports. `requirements-colab.txt` installs only what is used.

---

## Part 3 - What remains

### Blocking submission

| Task | Owner | What it needs |
|---|---|---|
| **T19** Report section 1 - the problem | A | ~1/3 page. What an IDS is, binary vs multiclass, why ML over hand-written rules. Source: GUIDE.md Part 0, in your own words. Needs no results. |
| **T20** Report section 2 - what we did | A | ~3/4 page. Built from the cleaning-numbers table above. Must cover the leakage argument for dropping IPs/ports/timestamps, the 60/20/20 stratified split, seed 42, scaler fitted on train only, and the Heartbleed protection with its 2-row caveat. |
| **T21** Report section 3 - results | B | The table from `results/tables/final_comparison.csv`, one or two captioned figures, and the ablation before/after numbers. **Every figure must be referred to in the text** - an unmentioned figure earns nothing. |
| **T22** Report section 4 - discussion | B | ~1 page, carries the most marks. Which model to deploy and why, arguing from macro-F1 **and** FAR together. Multiply FAR by a million connections and state the daily false-alarm count. Why accuracy alone misleads. What the ablation proved and why Random Forest was unaffected. Limitations, honestly. |
| **T24** Assemble the report | Both | Combine the four sections, add who-did-what, add the AI disclosure (required - wording in GUIDE.md 7.6). |
| **T25** Reproducibility test | Whoever wrote less of the code | Clean clone, follow only the README, confirm the numbers match. Fix the README if it fails, not the report. |
| **T26** Export and submit | Both | Report to PDF, build the zip excluding `.venv/` and `data/`, upload both to Canvas. |

### Optional

- **T27** Full-size run at `SAMPLE_FRACTION = 1.0`. Only after a working submission exists.
  Expect 30-90 minutes and much heavier memory use.

### Known issues, not blocking

- **GUIDE.md line ~830** attributes `ConvergenceWarning` to the neural network. In the real run it
  comes from Logistic Regression (`lbfgs failed to converge after 1000 iterations`). Harmless, and
  worth a sentence in the report either way, but the troubleshooting row is inaccurate.
- **ROC-AUC displays as `1` for Random Forest** in the final table. That is `.round(4)` on
  approximately 0.99993, not a literal perfect score. Do not write "perfect AUC".
- **`results/` is untracked.** `results/models/*` is gitignored; figures and tables are not. Decide
  whether the report figures belong in the repo.

### Points to defend in the report

Markers give credit for knowing *why*. The full list is SCAFFOLD.md section 5. The three that carry
the most weight:

1. **Dropping IPs, ports and timestamps** - they identify who and when, not how an attack behaves.
   Keeping them lets the model memorise addresses and score fake-high. This is data leakage.
2. **Winner chosen on validation, scored once on test** - 25% of the grade.
3. **Judged on macro-F1 and FAR, not accuracy** - the data is ~64% BENIGN, so an always-normal
   model scores well on accuracy while catching nothing.

---

## Commit history on this branch

```
13124ff  Modified gitignore, and added the .py files
0c20290  Updated Guide
d607468  Merge pull request #1 from steve-nt/dev
ceb75b1  Dataset Downloaded and .gitignored added
a48301a  TASKLIST.md
```

**Uncommitted at the time of writing:** `src/config.py`, `src/clean.py`, `GUIDE.md`,
`SCAFFOLD.md`, `TASKLIST.md` (modified), and `results/` (untracked).
