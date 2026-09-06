# Lab 1: Building Your First Intrusion Detector - portable runner

A machine-learning intrusion detector trained on CICIDS2017. It classifies network connections as
normal or attack (**binary**) and identifies which attack family (**multiclass**).

This folder is a **self-contained copy** of the pipeline that runs two ways: **locally** or on
**Google Colab**. The code in `src/` is the same in both cases, so results are directly comparable.

**Jump to:** [Running locally](#running-locally) · [Running on Google Colab](#running-on-google-colab)
· [Configuration](#configuration) · [Troubleshooting](#troubleshooting)

---

## What is here

```
collab/
├── Lab1_IDS_Colab.ipynb     <- the Colab notebook (26 cells, with a COMPLETE saved run)
├── README.md                <- this file
├── requirements-colab.txt   <- dependency list (works locally too)
├── run_all.py               <- whole pipeline in one command
├── src/                     <- 10 Python files
└── data/, results/          <- empty folders the scripts write into
```

> **The dataset is NOT included.** `data/raw/` is empty. See
> [Getting the dataset](#getting-the-dataset).

### The pipeline

Each script does one job and hands a file to the next.

| # | Script | Lab step | What it does | Writes |
|---|---|---|---|---|
| 1 | `src/explore.py` | Step 1 | Load, print shape and class balance | `results/figures/class_balance.png` |
| 2 | `src/clean.py` | Step 2 | Drop ID columns, fix inf/NaN, dedupe, sample | `data/processed/clean.csv` |
| 3 | `src/prepare.py` | Steps 3-4 | Stratified 60/20/20 split, scale on train only | `data/processed/splits.joblib` |
| 4 | `src/train_binary.py` | Steps 5-6 | Logistic Regression, Random Forest, MLP | `results/tables/binary_results.csv` |
| 5 | `src/ablation.py` | Step 7 | Scaling on vs. off | `results/tables/ablation_results.csv` |
| 6 | `src/multiclass.py` | - | Which attack type + confusion matrix | `results/figures/confusion_multiclass.png` |
| 7 | `src/compare.py` | Step 8 | Final results table and chart | `results/tables/final_comparison.csv` |

Supporting files: `src/config.py` holds every setting; `src/metrics.py` computes accuracy, macro-F1,
recall, ROC-AUC and FAR; `src/make_dummy_splits.py` generates fake data for smoke-testing.

`run_all.py` runs 1-7 in order and stops at the first failure.

---

## Getting the dataset

You need **`Wednesday-workingHours.pcap_ISCX.csv`** (~225 MB) in `data/raw/`.

Download `MachineLearningCSV.zip` from https://www.unb.ca/cic/datasets/ids-2017.html (short free
form), or search Kaggle for "CICIDS2017". Unzip and take the Wednesday file.

Do **not** use `Monday-WorkingHours.pcap_ISCX.csv` on its own - it is normal traffic only, with no
attacks to learn from.

> **The filename must match `RAW_FILE` in `src/config.py` (line 29) exactly** - capitals, hyphens
> and dots. The dataset is inconsistent about this: Wednesday uses a lowercase `w` in
> `workingHours`, the other days an uppercase `W` in `WorkingHours`. Rename the file, or edit
> `config.py` to match.

---

## Running locally

### 1. Python

The project targets **Python 3.11**, though anything from 3.9 to 3.13 runs this code - it uses only
scikit-learn, pandas, numpy, matplotlib and joblib, none version-sensitive here.

On Ubuntu 25.10 or newer, `sudo apt install python3.11` **will not work** (the archive has only 3.13
and 3.14, and the deadsnakes PPA has no `questing` release). Use [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.11
```

### 2. Virtual environment

```bash
cd <path-to>/collab
uv venv --python 3.11 .venv
source .venv/bin/activate
```

Your prompt should now start with `(.venv)`.

> **The most common source of errors.** `(.venv)` disappears whenever you close the terminal. Every
> new terminal needs `source .venv/bin/activate` again. A `ModuleNotFoundError` almost always means
> you forgot.

### 3. Libraries

```bash
uv pip install -r requirements-colab.txt
```

Roughly 100 MB, under a minute. Despite the name this works fine locally - it lists exactly what the
pipeline imports. Verify:

```bash
python -c "import sys; print(sys.version)"
python -c "import pandas, sklearn, matplotlib, joblib, tabulate; print('All libraries OK')"
```

### 4. Dataset

```bash
cp /path/to/Wednesday-workingHours.pcap_ISCX.csv data/raw/
ls -lh data/raw/
```

### 5. Run

Run the steps individually the first time - if something breaks you will know exactly which step.

```bash
python src/explore.py        # ~1 min
python src/clean.py          # ~2 min
python src/prepare.py        # ~1 min
python src/train_binary.py   # 5-15 min  <- slow
python src/ablation.py       # 5-15 min  <- slow
python src/multiclass.py     # ~3 min
python src/compare.py        # seconds
```

Then the whole thing in one command:

```bash
rm -f data/processed/* results/tables/* results/figures/* results/models/*
python run_all.py
```

**Expect 20-35 minutes.** Random Forest and the MLP are the slow parts. A quiet terminal for several
minutes is normal.

### Local resource needs

| Resource | Needed |
|---|---|
| Disk | ~1 GB (dataset + intermediates + saved models) |
| RAM | ~2 GB peak for one day's file |
| CPU | Any; more cores help (Random Forest uses `n_jobs=-1`) |
| GPU | Not used - scikit-learn is CPU-only |

---

## Running on Google Colab

### 1. Put the folder in Drive

Upload the `collab` folder to **My Drive** at drive.google.com. Without the dataset it is only about
50 KB, so this is instant.

Then add the CSV to `collab/data/raw/` in Drive. Uploading it once to Drive is much better than
uploading it to Colab each session, because **Colab wipes its local disk every time the runtime
disconnects**.

### 2. Open the notebook

In Drive, **right-click `Lab1_IDS_Colab.ipynb` → Open with → Google Colaboratory**.

If Colaboratory is not listed: *Open with → Connect more apps →* search **Colaboratory** → Install,
then retry.

### 3. Work through it

The notebook has 26 cells in seven sections. It ships with **the complete output of a successful
run** - every pipeline stage, the final results table, and all six figures rendered inline. Read
those outputs first: they tell you exactly what each cell should print, so you can spot a
divergence immediately instead of discovering it twenty minutes later.

| Section | Cells | What it does |
|---|---|---|
| 1. Set up the project files | 2-4 | Mount Drive, check the environment, install dependencies |
| 2. Get the dataset | 6-7 | List `data/raw/`, verify the filename matches `config.py` |
| 3. Run the pipeline | 9-15 | One cell per stage, in order |
| 4. Everything at once | 17 | Wipes old output, then `run_all.py` |
| 5. Look at the results | 19-20 | Print the final table, display every figure inline |
| 6. Save your results | 22 | Zip `results/` and download it |
| 7. Test without the dataset | 24-25 | Fake-data smoke test, then a mandatory cleanup cell |

Cell 2 sets the project path. If you put the folder somewhere other than the top level of My Drive,
edit that line to match.

### What the saved run produced

The stored outputs come from a **single-day run** (Wednesday only). Use them as your reference -
if your numbers differ substantially, something is wrong.

| Stage | What it printed |
|---|---|
| `explore.py` | 692,703 rows x 79 columns, 6 classes |
| `clean.py` | 1,297 rows dropped for inf/NaN; 106,415 duplicates; 10 constant columns; `PROTECTED Heartbleed: kept all 11 rows`; **117,007 rows x 67 columns** |
| `prepare.py` | train 70,203 / val 23,402 / test 23,402; attack rate **0.3313 in all three** |
| `multiclass.py` | macro-F1 **0.9937**, macro-FAR **0.0005** |

Binary results from that run:

| Model | Accuracy | macro-F1 | Recall | ROC-AUC | FAR |
|---|---|---|---|---|---|
| Logistic Regression | 0.9804 | 0.9779 | 0.9768 | 0.9978 | 0.0178 |
| **Random Forest** | **0.9984** | **0.9982** | **0.9977** | 0.9999 | **0.0012** |
| MLP (neural network) | 0.9943 | 0.9935 | 0.9914 | 0.9998 | 0.0043 |

The single check that matters most is `prepare.py`'s three attack rates agreeing to four decimal
places - that is the evidence stratification worked. If they diverge, the split is wrong and nothing
downstream can be trusted.

> Small differences between environments are expected on the **unscaled** ablation rows only. See
> [Reproducibility](#reproducibility).

### What Colab actually gives you

Measured on the saved run in this notebook:

| | Value |
|---|---|
| Python | 3.13.15 |
| CPU cores | 2 |
| RAM | 12 GB |
| Free disk | 66 GB |

Two cores is fewer than most laptops, so Colab is **not** faster than a decent local machine here.
Its advantages are the free 12 GB of RAM and not tying up your own computer.

### Colab-specific warnings

**Do not install the main project's `requirements.txt`.** It pins `tensorflow<2.18` and `torch`,
which forces a numpy downgrade to 1.26 and a runtime restart. **No script in `src/` imports either** -
the neural network is scikit-learn's `MLPClassifier`. Use `requirements-colab.txt`, which cell 4
already does.

**Save `results/` before you close the tab.** Colab deletes local disk on disconnect. Run section 6,
or copy the folder back to Drive. Otherwise you lose 20-30 minutes of training.

**A GPU runtime will not help.** scikit-learn does not use one; requesting a GPU only spends quota.

**Editing `config.py` needs a restart.** Once `import config` has run in a Colab kernel, editing the
file changes nothing - Python caches the module. `importlib.reload(config)` handles simple cases but
does *not* update modules that already imported it. After editing `config.py`, use
**Runtime → Restart session** and re-run from the top. Shell cells (`!python src/explore.py`) are
unaffected - each starts a fresh interpreter.

**Reading the CSV over the Drive mount is slow.** Copy it to local Colab disk first if you want the
speed:

```python
!cp /content/drive/MyDrive/collab/data/raw/Wednesday-workingHours.pcap_ISCX.csv data/raw/
```

---

## Configuration

Everything lives in `src/config.py`. Change settings there, not in individual scripts.

| Setting | Line | Default | What it does |
|---|---|---|---|
| `SEED` | 14 | `42` | Fixes all randomness. **Required by the lab; put it in your report** |
| `RAW_FILE` | 29 | `Wednesday-...csv` | Which file to load; must match your filename exactly |
| `SAMPLE_FRACTION` | 51 | `0.20` | Fraction of rows used. Lower if you hit memory limits |
| `MIN_CLASS_COUNT` | 58 | `10` | Attack types with fewer rows are dropped |
| `PROTECT_CLASS_BELOW` | 75 | `20` | Classes smaller than this skip sampling and are kept whole |
| `TEST_SIZE` | 80 | `0.20` | Test split |
| `VAL_SIZE_OF_REMAINDER` | 81 | `0.25` | 25% of the remaining 80% = 20% overall |

**Why `PROTECT_CLASS_BELOW` exists.** Heartbleed has only 11 rows in the Wednesday file. A plain 20%
sample cuts it to 2 - enough to stay in training, not enough to reach the test set. That leaves a
phantom class: an empty row in the confusion matrix and a distorted averaged false-alarm rate. The
policy is **drop below 10, keep whole below 20, sample normally at 20 and above.** When it triggers,
`clean.py` prints a `PROTECTED` line - record it for your report.

### Using several days' files together

`src/config.py` and `src/explore.py` both carry commented instructions for combining all eight
CICIDS2017 day-files (2.8 million rows and 15 attack classes, instead of 692,703 and 6). Read the
comment block in `config.py` first - it lists the settings that must change at the same time.

> **A trap this notebook's own saved output still demonstrates.** Uncommenting `RAW_FILES` in
> `config.py` is **not enough on its own**. In the saved run, cell 7 reports:
>
> ```
> mode: MULTI file - glob matched 8 file(s)
> ```
>
> and cell 10 then reports:
>
> ```
> Starting with 692,703 rows x 79 columns
> ```
>
> That is one day, not eight. Nothing errored - the pipeline silently ignored seven files, because
> `load_raw()` in `explore.py` still defaulted to the single `RAW_FILE`. The run completed and
> produced a full set of plausible-looking results for the wrong dataset.
>
> **You must change both**: uncomment `RAW_FILES` in `config.py` *and* swap in the multi-file
> `load_raw()` in `explore.py`. **Verify against the row count `clean.py` prints, never the filename
> check** - all eight files should give `Starting with 2,830,743 rows`.

---

## Testing without the dataset

If the download is slow, verify the modelling half runs on generated data:

```bash
python src/make_dummy_splits.py
python src/train_binary.py
python src/compare.py
```

**Every number this produces is meaningless.** Fake attack names begin with "Fake" and there are
6,000 rows instead of ~117,000. Destroy it before doing anything real:

```bash
rm -f data/processed/* results/tables/* results/figures/* results/models/*
```

---

## Output

| Location | Contents |
|---|---|
| `results/tables/binary_results.csv` | The three tuned models |
| `results/tables/ablation_results.csv` | Scaling on/off |
| `results/tables/final_comparison.csv` | Everything merged - **this is the report table** |
| `results/figures/class_balance.png` | Class imbalance, log scale |
| `results/figures/confusion_*.png` | Per-model confusion matrices |
| `results/figures/confusion_multiclass.png` | Which attacks get confused with which |
| `results/figures/model_comparison.png` | macro-F1 and FAR side by side |
| `results/models/*.joblib` | Trained models |

The Wednesday data is about 64% normal traffic, so **judge by macro-F1 (higher is better) and FAR
(lower is better), not accuracy.** A model that always answers "normal" scores ~64% accuracy while
catching zero attacks.

---

## Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Not in the venv | `source .venv/bin/activate` |
| `Unable to locate package python3.11` | Ubuntu 25.10+ has no 3.11 package | Use uv, not apt |
| `externally-managed-environment` | Installing outside a venv | Activate the venv first |
| `Cannot find the data file` | Filename mismatch | `ls data/raw/`, make it match `RAW_FILE` |
| `module 'config' has no attribute 'RAW_FILE'` | You switched to `RAW_FILES` | Update whatever still references `RAW_FILE` |
| Row count says one day when you expected eight | `load_raw()` still single-file | Swap `load_raw()` too, not just `config.py` |
| `KeyError: 'Label'` | Column names carry leading spaces | `explore.py` strips them - check the file copied intact |
| `ValueError: Input contains NaN or infinity` | Cleaning did not run | Run `clean.py` before `prepare.py` |
| `MemoryError`, or the machine freezes | Too much data | Lower `SAMPLE_FRACTION` to `0.05` |
| `ConvergenceWarning` | A solver hit its iteration limit | A warning, not an error. Worth a sentence in the report |
| `n_splits/class cannot be less than...` | A class has too few rows | Raise `MIN_CLASS_COUNT` to 50 |
| Config edits ignored (Colab) | Module cached in the kernel | Runtime → Restart session |
| Nothing happens for minutes | Training is genuinely slow | Wait |

Read the **last line** of any traceback first - that is the actual error.

---

## Reproducibility

Seed 42, set in `src/config.py` and passed to every split and every model. The same seed on the same
data with the same library versions gives identical numbers.

Record the Python and scikit-learn versions you used - the notebook prints them in section 1. Results
can differ slightly between environments when features are left **unscaled**, because solvers that
fail to converge stop at points that depend on the underlying maths library. Scaled results are
reproducible across environments; unscaled ones are not.
