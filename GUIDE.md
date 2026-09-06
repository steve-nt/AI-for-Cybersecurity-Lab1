# GUIDE.md - Do These Things, In This Order

This guide assumes you have **never written Python**, have **never studied cybersecurity**, and
have **never used a terminal**. Nothing is skipped.

Work through it top to bottom. Do not jump ahead. Each part ends with a check so you know it
worked before you move on.

The code you need to copy lives in [SCAFFOLD.md](SCAFFOLD.md). This guide tells you *when* to copy
it and *what it does*.

**Realistic time:** 4–7 hours total, best split over two or three sittings.

---

# Part 0 - What am I even building?

## 0.1 The security problem

Every time a computer talks to another computer, that conversation is a **connection** (also called
a *flow*). A busy company network has millions a day. Almost all are ordinary - someone loading a
webpage, an email arriving. A few are an attacker: scanning for a way in, flooding a server so it
falls over, guessing passwords over and over.

An **Intrusion Detection System (IDS)** is the software that watches all of it and raises an alarm
on the bad ones.

The old way of building one: a human writes rules by hand. *"If one address opens more than 500
connections in a minute, alarm."* This works until an attacker does something slightly different
from the rule.

## 0.2 The machine learning way

Instead of writing rules, we hand a program a large table. Each **row** is one connection. Each
**column** is a measured fact about that connection: how long it lasted, how many bytes went each
way, how big the packets were, and about 75 other things. One final column, the **label**, says
what it actually was: `BENIGN` (normal) or the name of an attack.

The program looks at all those rows and works out the pattern by itself. Afterwards you can show
it a connection it has never seen and it will tell you whether it looks like an attack.

That is what you are building. Twice:

- **Binary**: normal or attack? (a yes/no answer)
- **Multiclass**: *which* attack? (port scan / denial-of-service / brute force / ...)

## 0.3 The single most important idea in this lab

Roughly **80% of the rows are normal traffic.** So imagine a lazy program that ignores everything
and always answers "normal". It gets **80% of its answers right.** 80% sounds like a good score.

That program catches **zero attacks.** It is completely worthless.

This is why the lab bans you from reporting accuracy on its own. You will report five numbers, and
the two that actually matter are **macro-F1** and **FAR**. Part 5 of this guide explains them in
detail. If you understand nothing else, understand this paragraph - it is the point of the whole
lab, and the report marks hang on it.

---

# Part 1 - Set up your computer

## 1.1 Opening a terminal

Press `Ctrl` + `Alt` + `T`. A window appears where you type commands and press `Enter`.

Some words you will see:

| Word | Means |
|---|---|
| **terminal** / shell | the black window you type commands into |
| **directory** | exactly the same thing as a folder |
| **command** | a line you type, then press Enter |
| `sudo` | "do this as administrator". It will ask for your login password. |
| `cd` | change directory - move into a folder |
| `ls` | list - show what is in the current folder |

When you type your password after `sudo`, **nothing appears on screen.** No dots, no stars. That is
normal and deliberate. Type it and press Enter.

## 1.2 Go to your project folder

Type this and press Enter:

```bash
cd ~/Desktop/AI-for-Cybersecurity-Lab1
```

The `~` means "my home folder". Now check you are in the right place:

```bash
ls
```

**You should see:** `GUIDE.md`, `SCAFFOLD.md`, `README.md`, and the lab PDF.

If instead you see `No such file or directory`, the folder is somewhere else. Find it with
`find ~ -name "AI-for-Cybersecurity-Lab1" -type d`.

## 1.3 Install Python 3.11

**This project uses Python 3.11.** Your machine's system Python is 3.13.7, which is *not* the
version we want, and you must not remove or replace it - Ubuntu itself depends on it.

> **Why 3.11?** It is the version with the broadest, most settled support across TensorFlow,
> PyTorch and scikit-learn simultaneously. Pinning it means the three libraries agree with each
> other, and it is the version your marker is most likely to be able to reproduce.

> **The trap:** `sudo apt install python3.11` **does not work on this machine** and never will.
> Ubuntu 25.10 ("questing") ships only `python3.13` and `python3.14` in its archive. Most tutorials
> tell you to add the deadsnakes PPA instead; deadsnakes has no `questing` release either (it went
> 24.04 straight to 26.04), so that fails too. Use one of the methods below.

Install [uv](https://docs.astral.sh/uv/), which fetches a prebuilt 3.11 in seconds without touching
your system Python and without needing your password:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.11
```

**Check:**

```bash
uv python list --only-installed
```

**You should see:** a line containing `cpython-3.11`.

> **Other ways to do this.** uv is the recommendation, but it is not the only option, and if you
> are on a different machine (or your partner is) another one may suit you better. All of them are
> written out in **Appendix A** at the end of this guide - pyenv, conda, Docker, a plain tarball,
> and building from source, plus the ones that look plausible but do not work here.

## 1.4 Create a virtual environment

```bash
uv venv --python 3.11 .venv
```

**You should see:** `Using CPython 3.11.x` and `Creating virtual environment at: .venv`.

> **What did that do?** It made a hidden folder called `.venv` containing a private, isolated copy
> of Python 3.11 just for this project. Libraries you install go in there instead of being mixed
> into your whole operating system.
>
> **Why bother?** Three reasons. First, it is how you get 3.11 while the system stays on 3.13.
> Second, modern Ubuntu actively blocks you from installing libraries system-wide (you would hit an
> `externally-managed-environment` error). Third, six months from now another project needing a
> different version of pandas will not break this one.

> **Not using uv?** Whichever method from Appendix A you picked, it ends by giving you a 3.11
> interpreter. Create the environment with `<path-to-3.11> -m venv .venv` instead of the line
> above. Everything after this point is identical.

## 1.5 Activate it

```bash
source .venv/bin/activate
```

**Check:** your prompt now starts with `(.venv)`, like this:

```
(.venv) steven@computer:~/Desktop/AI-for-Cybersecurity-Lab1$
```

> **READ THIS, IT CATCHES EVERYONE:** that `(.venv)` disappears every time you close the terminal.
> Every single new terminal session, you must `cd` to the project and run the `source` line again
> before anything works. If you ever get `ModuleNotFoundError: No module named 'pandas'`, the cause
> is almost always that you forgot this.

## 1.6 Install the libraries

Create the shopping list. Copy this **whole block** including the `EOF` lines:

```bash
cat > requirements.txt <<'EOF'
# Python 3.11
tensorflow>=2.15.0,<2.18.0
torch>=2.1.0
scikit-learn>=1.3.0
pandas>=2.0.0
matplotlib>=3.7.0
joblib>=1.4.0
tabulate>=0.9.0
EOF
```

Now install:

```bash
uv pip install -r requirements.txt
```

**This is a big download - roughly 3 GB, and 5–15 minutes on a normal connection.** Most of that is
TensorFlow, PyTorch, and the ~20 `nvidia-*` CUDA packages PyTorch pulls in by default. It is normal.
Do not interrupt it.

> **Short on disk or bandwidth?** PyTorch has a CPU-only build that skips the CUDA packages and
> saves about 2.5 GB. Your VM has no GPU, so you lose nothing:
>
> ```bash
> uv pip install torch --index-url https://download.pytorch.org/whl/cpu
> uv pip install -r requirements.txt
> ```

> **`pip` instead of `uv pip`?** Both work. `uv pip` is dramatically faster on an install this
> size. If you used a non-uv method from Appendix A, activate the venv and use plain
> `pip install -r requirements.txt`.

> **What are these?**
> - **tensorflow** - Google's deep learning framework (includes Keras). The lab offers it as one of
>   the options for the neural network.
> - **torch** - PyTorch, Meta's deep learning framework. The other option the lab offers.
> - **scikit-learn** - the machine learning library. All your models and scores come from here,
>   including `MLPClassifier`, the neural network this project actually trains.
> - **pandas** - spreadsheets for Python. Loads your CSV and lets you filter and clean it.
> - **matplotlib** - draws the charts.
> - **joblib** - saves trained models and data splits to disk.
> - **tabulate** - formats the final results table nicely.
>
> `numpy` is not listed because TensorFlow, pandas and scikit-learn all depend on it - pip installs
> it automatically. TensorFlow 2.17 requires `numpy<2`, so you will get 1.26.x. Let it.
>
> **Why install TensorFlow and PyTorch when the code uses `MLPClassifier`?** The lab brief lets you
> pick any of the three, and having all three present means you can swap the neural network for a
> Keras or PyTorch model later without redoing setup. See SCAFFOLD.md section 4.1.
>
> Versions are constrained so your results are reproducible. That is worth a line in your README -
> the rubric asks for it.

## 1.7 Check it worked

```bash
python -c "import sys; print(sys.version)"
python -c "import pandas, sklearn, matplotlib, joblib, tabulate; print('Core libraries OK')"
python -c "import tensorflow, torch; print('TF', tensorflow.__version__, '| torch', torch.__version__)"
```

**You should see:** a version string starting `3.11.`, then `Core libraries OK`, then the TF and
torch versions.

If the first line does not say `3.11`, your venv was built from the wrong interpreter - delete
`.venv` and redo 1.4.

If you see `ModuleNotFoundError`, go back to 1.5 - you are not in the venv.

> TensorFlow prints a few lines about `cuda` drivers or `TF-TRT` on that import. Those are
> informational, not errors. Your VM has no GPU; TensorFlow falls back to CPU and works fine.

**Part 1 is done.**

---

# Part 2 - Build the project skeleton

## 2.1 Create the folders

```bash
mkdir -p src data/raw data/processed results/figures results/tables results/models report
```

> `mkdir` makes directories. `-p` means "make parent folders too, and don't complain if they
> already exist".

Check:

```bash
ls
```

**You should see:** `data`, `report`, `results`, `src` alongside your markdown files.

## 2.2 Create the `.gitignore`

```bash
cat > .gitignore <<'EOF'
.venv/
python/
Python-3.11.*/
py311.tar.gz
__pycache__/
*.pyc
data/raw/*
data/processed/*
results/models/*
EOF
```

> Datasets are hundreds of megabytes. This tells git to ignore them so you never accidentally try
> to upload them. Your *code* still gets tracked - that is what you submit.

## 2.3 Create the code files

Open SCAFFOLD.md and copy each code block into the matching file. There are eight files in `src/`
plus `run_all.py` at the top level.

**How to create a file:** the simplest way is a text editor. Ubuntu has one built in:

```bash
gedit src/config.py
```

That opens a blank window. Paste the code from SCAFFOLD.md section 4.3, save (`Ctrl+S`), close.

If `gedit` is not installed, use `nano src/config.py` instead - paste, then `Ctrl+O`, `Enter`,
`Ctrl+X` to save and exit. Or use VS Code if you have it: `code .` opens the whole folder.

Create these, in this order:

| File | SCAFFOLD.md section |
|---|---|
| `src/config.py` | 4.3 |
| `src/metrics.py` | 4.4 |
| `src/explore.py` | 4.5 |
| `src/clean.py` | 4.6 |
| `src/prepare.py` | 4.7 |
| `src/train_binary.py` | 4.8 |
| `src/ablation.py` | 4.9 |
| `src/multiclass.py` | 4.10 |
| `src/compare.py` | 4.11 |
| `run_all.py` | 4.12 |

> **Python is picky about indentation.** The spaces at the start of lines are part of the language,
> not decoration. Copy blocks whole; do not retype them, and do not "tidy up" the spacing.

## 2.4 Check

```bash
ls src/
```

**You should see all eight `.py` files.**

---

# Part 3 - Get the data

## 3.1 Download it

Go to: **https://www.unb.ca/cic/datasets/ids-2017.html**

Scroll to the download section and fill in the short form (name, email, organisation - it is free
and instant). You are looking for the **`MachineLearningCSV.zip`** download, which contains eight
CSV files of already-processed connection records.

*Alternative if the form is slow:* search Kaggle for **"CICIDS2017"**. Several users have mirrored
the same `MachineLearningCVE` folder. Any mirror of those eight CSVs works.

> **What is this dataset?** In 2017, the Canadian Institute for Cybersecurity built a realistic
> office network, ran normal user activity on it for five days, and at scheduled times launched
> real attacks against it. They recorded everything, then converted the raw traffic into these
> tables - one row per connection, ~78 measured columns, plus the true label. It is one of the
> standard datasets for IDS research, and the paper describing it is cited in your lab PDF.

## 3.2 Pick ONE file

You do not need all eight. Unzip and pick one:

| File | What is in it | Good because |
|---|---|---|
| **`Wednesday-workingHours.pcap_ISCX.csv`** | Several denial-of-service attacks + normal traffic | **Recommended.** Good size, several attack types, sensible balance. |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | Port scanning + normal | Also fine, close to 50/50 |
| `Monday-WorkingHours.pcap_ISCX.csv` | Normal traffic only | **Do not use** - no attacks at all, nothing to learn |

> **Why only one day?** Your lab PDF says so directly: *"Datasets are big. For a first run, load one
> day's file (or a random 10–20% sample)."* One day is roughly 700,000 rows. On top of that, our
> `config.py` takes a 20% sample of it, giving ~140,000 rows - plenty to learn from, and it trains
> in minutes rather than hours. You can raise `SAMPLE_FRACTION` to `1.0` later for a final run.

## 3.3 Put it in place

Move your chosen CSV into `data/raw/`. Drag it there in the file manager, or:

```bash
mv ~/Downloads/Wednesday-workingHours.pcap_ISCX.csv data/raw/
```

## 3.4 Confirm the filename matches

```bash
ls data/raw/
```

Whatever that prints must **exactly** match the `RAW_FILE` line in `src/config.py`. Exactly -
capital letters, hyphens, dots, everything.

If it differs, edit `src/config.py` and fix this line:

```python
RAW_FILE = DATA_RAW / "Wednesday-workingHours.pcap_ISCX.csv"
```

---

# Part 4 - Run it, one step at a time

Run each script on its own and read what it prints. Do not skip to `run_all.py` yet - when
something goes wrong, you want to know exactly which step broke.

## Step 1 - Load and look

```bash
python src/explore.py
```

**You should see** the number of rows and columns, a list of column names, and a breakdown of how
many rows are each type. Something like:

```
Shape: 692,703 rows x 79 columns
  BENIGN                            440,031  (63.52%)
  DoS Hulk                          231,073  (33.36%)
  DoS GoldenEye                      10,293  ( 1.49%)
  ...
```

Then look at the chart it saved:

```bash
xdg-open results/figures/class_balance.png
```

**This is the bar chart the lab requires in Step 1.** Keep it for the report.

> **What to notice:** the bars are wildly different heights - that is the class imbalance from
> section 0.3 made visible. The chart uses a logarithmic scale, otherwise the small attack classes
> would be invisible flat lines next to the huge BENIGN bar.

## Step 2 - Clean

```bash
python src/clean.py
```

**You should see** six numbered lines reporting what was removed. Read them. They are the raw
material for the "what you did" section of your report - write the numbers down.

> **What just happened, and why each part matters:**
>
> 1. **Dropped ID columns.** IP addresses, timestamps, Flow ID. These are name tags. They tell you
>    *who* and *when*, not *what an attack looks like*. Leave them in and the model memorises
>    "traffic from 192.168.10.50 is bad" - it scores brilliantly on your test set and is useless on
>    any real network. This mistake is called **data leakage** and it is the classic way to
>    accidentally fake a great result.
> 2. **Fixed infinity and blanks.** Some columns are "bytes ÷ duration". When duration is zero the
>    answer is infinity, which crashes every model.
> 3. **Dropped duplicates.** An identical row appearing twice can land once in training and once in
>    testing - so the model is tested on something it already memorised. Inflates your score
>    dishonestly.
> 4. **Dropped dead columns** where every row has the same value. They teach nothing.
> 5. **Dropped ultra-rare attack types** (under 10 examples). Too few to learn from, and they break
>    the split in the next step. **Mention this in your report** - it is a limitation, and naming
>    your own limitations earns marks.
> 6. **Took a 20% sample**, keeping the same mix of attack types.

## Step 3 - Split and scale

```bash
python src/prepare.py
```

**You should see** three row counts near 60% / 20% / 20%, and three attack rates that are nearly
identical to each other.

> **What are the three parts for?** This is the heart of honest machine learning.
>
> - **Training set (60%)** - the model learns from this. It sees the answers.
> - **Validation set (20%)** - you try several settings and pick the best using this. The model
>   never learns from it; you use it to make *your* choices.
> - **Test set (20%)** - locked in a drawer until the very end. Used exactly once, to report your
>   final numbers.
>
> The point of the test set is to answer "how will this do on traffic it has genuinely never
> seen?". The moment you use it to make a decision - try a setting, look, try another - it stops
> being unseen and your reported score becomes a lie. This is called **test-set peeking** and it is
> 25% of your grade.
>
> **Stratified** means each of the three parts keeps the same proportion of each attack type. A
> plain random split could put every single example of a rare attack in the test set, so the model
> never learns it and then gets tested on it.
>
> **Scaling** rewrites every column to have average 0 and a comparable spread. One column might be
> "duration in microseconds" (values in the millions), another "number of flags set" (0 to 8).
> Logistic Regression, SVMs and neural networks all secretly treat the big-numbered column as more
> important purely because its numbers are bigger. Scaling removes that unfair advantage. Decision
> Trees and Random Forests do not care, because they ask "is this above 500?" and that question
> means the same thing in any units.
>
> **The subtle bit:** the scaler learns the average and spread from the **training data only**,
> then applies those same numbers to validation and test. If it learned from all the data, facts
> about the test set would leak into training. Look for the line in the output confirming this -
> it is a specific thing markers check for.

## Step 4 - Train the models

```bash
python src/train_binary.py
```

This takes **2–10 minutes**. Random Forest and the neural network are the slow parts.

**You should see**, for each of the three model families, a few settings tried with their
validation scores, a declared winner, and then one line of final test scores.

> **You may see a yellow `ConvergenceWarning` about the neural network.** That is a warning, not an
> error. It means the network hit its iteration limit before fully settling. It is fine for this
> lab - and honestly, it is worth one sentence in your report.

**The three models:**

- **Logistic Regression** - the simplest. Draws one straight boundary between normal and attack.
  Fast, easy to explain, struggles when the real boundary is not straight.
- **Random Forest** - builds hundreds of flowchart-style decision trees, each on a random slice of
  the data, then has them vote. Usually the strongest on this kind of data and very forgiving.
- **MLP (neural network)** - layers of simple units that each learn a small piece of the pattern,
  stacked so later layers combine earlier ones. This is the neural network the lab requires.

The lab asks for **classical models plus one neural network** - you now have two classical and one
neural, which covers it.

## Step 5 - The ablation

```bash
python src/ablation.py
```

**You should see** each model scored twice: once WITHOUT scaling, once WITH.

> **What is an ablation?** You change **exactly one thing**, hold everything else identical, and
> see what moves. It is how you demonstrate that a choice actually mattered rather than just
> asserting it did.
>
> **What to expect:** Logistic Regression and the neural network should get clearly worse without
> scaling. Random Forest should barely move. If that is what you see - say so in the report, and
> explain *why* the forest does not care (it asks threshold questions, which are unit-independent).
> That single sentence shows you understood the mechanism instead of just running code.
>
> **If your results disagree with that prediction, report what you actually got.** Real results
> that contradict the expectation, honestly explained, are worth more than results you massaged to
> match. Never edit numbers.

**Write down the before/after numbers.** The lab explicitly requires them.

## Step 6 - Multiclass

```bash
python src/multiclass.py
```

**You should see** a table with one line per attack type, then a confusion matrix chart.

```bash
xdg-open results/figures/confusion_multiclass.png
```

> **How to read a confusion matrix:** rows are what the traffic *actually was*, columns are what
> the model *guessed*. The diagonal (top-left to bottom-right) is where it got things right -
> you want that dark and everything else pale. A bright square off the diagonal means "the model
> systematically mistakes attack X for attack Y".
>
> Find one off-diagonal bright spot and write a sentence about it. Attacks that resemble each
> other in their traffic patterns get confused, and that is a genuinely interesting security
> observation - exactly the kind of thing the "Discussion" section wants.

## Step 7 - The final table

```bash
python src/compare.py
```

**You should see** a formatted table printed to the terminal. **This is the table for your
report** - copy it directly.

## Step 8 - Prove it runs start to finish

```bash
python run_all.py
```

Everything, in order, from raw CSV to final table. The rubric says your code must *"run
start-to-finish and reproduce your numbers"*. This is you proving it. Confirm it completes without
errors.

---

# Part 5 - Understanding your numbers

**Do not write the report until you have read this part.** The marks are in the interpretation, not
the running.

## 5.1 The four outcomes

Every single prediction lands in one of four boxes:

|  | Model said ATTACK | Model said NORMAL |
|---|---|---|
| **Really was an attack** | **TP** - true positive: caught it | **FN** - false negative: **missed an attack** |
| **Really was normal** | **FP** - false positive: **a false alarm** | **TN** - true negative: correctly ignored |

The two dangerous boxes are the bold ones, and they hurt in different ways:

- **FN (missed attack)** - the attacker gets in and nobody knows. This is the catastrophe.
- **FP (false alarm)** - a security analyst is dragged out of bed for nothing. One is annoying;
  ten thousand a day means the team switches the alarm off, and then you are back to catastrophes.

Almost every choice in intrusion detection is a trade between these two.

## 5.2 The five scores

### Accuracy - *"what fraction did I get right?"*
`(TP + TN) / everything`

**Easy to understand, and the lab bans you from relying on it.** Reread section 0.3: on 80%-normal
data, a model that always says "normal" gets 80% accuracy and catches nothing. Report it, but never
argue from it.

### Recall (on the attack class) - *"of all the real attacks, how many did I catch?"*
`TP / (TP + FN)`

The security question that matters most. Recall of 0.95 means you caught 95% of attacks and 5% got
through. **Higher is better.**

### Precision - *"when I shouted 'attack', how often was I right?"*
`TP / (TP + FP)`

Not in your required table, but it is the other half of F1, so know it.

### macro-F1 - *the balanced single number*

F1 combines precision and recall into one score. **Macro**-F1 computes F1 separately for the normal
class and the attack class, then averages the two **giving each equal weight**.

That last part is the whole point. The lazy always-say-normal model scores brilliantly on the
normal class and zero on the attack class - macro-F1 averages those and exposes it immediately,
where accuracy hid it.

**This is your headline number.** **Higher is better**, 1.0 is perfect.

### ROC-AUC - *"how well does it rank?"*

Models do not really output yes/no; they output a confidence, and we cut at 0.5. ROC-AUC asks: if I
pick one random attack and one random normal connection, how often does the model rate the attack
as more suspicious? **1.0 is perfect, 0.5 is coin-flipping.** Useful because it judges the model
independently of where you put the cutoff.

### FAR - False Alarm Rate - *"how much did I cry wolf?"*
`FP / (FP + TN)`

Of all the genuinely normal traffic, what fraction did you wrongly flag?

**LOWER is better** - this is the one score in the table where that is true, so do not mix it up.

**Why it matters so much in security:** a network carrying a million normal connections a day with
a 5% FAR produces **50,000 false alarms every day**. No team can read that. The alarm gets ignored
or disabled, and the detector is worse than useless - it created false confidence. A "great" model
with a bad FAR is not deployable, and saying that clearly in your discussion is exactly what the
report is asking for.

## 5.3 Choosing a winner

Judge on **macro-F1 and FAR together**. Argue it out loud in the report:

> "Random Forest achieved the highest macro-F1 (0.98) with a FAR of 0.004, meaning only 4 in every
> 1,000 normal connections raised a false alarm. Logistic Regression reached similar accuracy but a
> FAR of 0.03 - nearly ten times higher - which on a network of a million daily connections would
> mean 30,000 false alerts a day. We would deploy the Random Forest."

That paragraph - a number, what it means in practice, and a decision - is what "with evidence"
means in the lab brief. Write yours in that shape, with your own numbers.

---

# Part 6 - Write the README

The rubric wants a README explaining how to run your code, which libraries you used, and your seed.

```bash
gedit README.md
```

Replace the contents with something like this, edited to match what you actually did:

```markdown
# Lab 1: Building Your First Intrusion Detector

## What this is
An intrusion detection system built with machine learning on the CICIDS2017
dataset. It classifies network connections as normal or attack (binary), and
also identifies which type of attack (multiclass).

## Setup
Requires Python 3.11.
    uv python install 3.11
    uv venv --python 3.11 .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt

## Data
Download CICIDS2017 from https://www.unb.ca/cic/datasets/ids-2017.html
Place `Wednesday-workingHours.pcap_ISCX.csv` in `data/raw/`.

## Run everything
    python run_all.py

Or run the steps individually:
    python src/explore.py       # Step 1: load and look
    python src/clean.py         # Step 2: clean
    python src/prepare.py       # Steps 3-4: split and scale
    python src/train_binary.py  # Steps 5-6: classical + neural network
    python src/ablation.py      # Step 7: ablation
    python src/multiclass.py    # multiclass task
    python src/compare.py       # Step 8: results table

## Reproducibility
Python 3.11.
Random seed: 42 (set in src/config.py).
Sample fraction: 0.20 of one day's traffic.
Library versions are constrained in requirements.txt.

## Libraries
tensorflow, torch, scikit-learn, pandas, matplotlib, joblib, tabulate
The neural network is scikit-learn's MLPClassifier (permitted by the lab brief).

## Output
Tables in results/tables/, figures in results/figures/.
```

---

# Part 7 - Write the report

2–3 pages. Submitted as a PDF. Use the sections the lab asks for.

## 7.1 What problem is this (short paragraph)

What an IDS is. Binary vs. multiclass. One sentence on why machine learning instead of hand-written
rules. Section 0 of this guide has everything you need - write it in your own words.

## 7.2 What you did

- Which dataset file, and how many rows before and after cleaning (from your Step 2 output).
- What you removed and **why** - especially the ID columns and the leakage reasoning. This is
  where you show you understand it.
- The 60/20/20 stratified split, and that the seed is 42.
- That the scaler was fitted on training data only.
- Which models, and which settings you tried.
- That rare classes below 10 rows were dropped.

## 7.3 Results

**One clear table.** Copy from `results/tables/final_comparison.csv` or the printed output of
`compare.py`. Columns: accuracy, macro-F1, recall, ROC-AUC, FAR.

**One or two figures.** Good picks: `class_balance.png`, `model_comparison.png`, or
`confusion_multiclass.png`.

**Caption everything, and then actually refer to the captions in your text.** "As Table 1 shows..."
and "Figure 2 shows that DoS Hulk is occasionally mistaken for DoS GoldenEye...". The rubric
explicitly rewards figures that the writing uses. A figure nobody mentions earns nothing.

Include the **ablation before/after numbers** here too, and one line on what they show.

## 7.4 Discussion

The most valuable section. Cover:

- **Which model wins and why** - argue from macro-F1 and FAR, in the shape shown in section 5.3.
- **What FAR means in practice** - do the arithmetic. Multiply your FAR by a million connections.
- **Why accuracy alone misleads here** - the always-say-normal argument from section 0.3.
- **What the ablation proved** - and why Random Forest was unaffected.
- **Limitations, stated honestly:** one day of one synthetic dataset; a 20% sample; rare attack
  classes dropped; a lab network is not a real one; a model trained on 2017 attacks may not
  generalise to today's. Naming your own limitations gains marks, it does not lose them.

## 7.5 Who did what

One or two lines. The lab is explicit that if one person does everything, it shows up in individual
grades.

## 7.6 AI disclosure - do not skip this

Your lab PDF says: *"If you use an AI assistant, say so in the report."* You used one to build this
scaffold. Write a line such as:

> "We used Claude (an AI assistant) to help scaffold the project structure and explain the
> evaluation metrics. All code was reviewed and run by us, and all reported results come from our
> own submitted code."

Being straightforward here costs you nothing. Not disclosing is an academic honesty problem.

---

# Part 8 - Submit

```bash
cd ~/Desktop
zip -r Lab1_submission.zip AI-for-Cybersecurity-Lab1 \
  -x "*/.venv/*" "*/data/*" "*/.git/*" "*/__pycache__/*"
```

> The `-x` part excludes the virtual environment, the dataset, and git internals. Without it your
> zip is over a gigabyte. Your *code* is what gets marked.

Upload to Canvas: the zip (or a repository link) **and** the report as a PDF.

---

# Part 9 - When something breaks

Errors are normal. Read the **last line** of the error message first - that is the actual problem.

| What you see | What it means | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Not in the virtual environment | `source .venv/bin/activate` |
| `externally-managed-environment` | Installing outside a venv | Activate the venv first (1.5) |
| `Unable to locate package python3.11` | Ubuntu 25.10 has no 3.11 package | Do not use apt. Use uv (1.3) or Appendix A |
| `E: The repository ... questing Release does not have a Release file` | deadsnakes has no questing series | Do not use deadsnakes here. See Appendix A |
| `uv: command not found` | Shell has not picked up uv yet | `source ~/.bashrc`, or open a new terminal |
| Python version is 3.13, not 3.11 | venv built from system Python | `rm -rf .venv`, redo 1.4 |
| `Could not find a version that satisfies tensorflow` | venv is not 3.11 | Check `python -c "import sys; print(sys.version)"`, redo 1.4 |
| TensorFlow prints `cuda`/`TF-TRT` warnings on import | No GPU in this VM | Informational only. Ignore them. |
| Install fills the disk | torch's CUDA packages are ~2.5 GB | Use the CPU-only torch index in 1.6 |
| `FileNotFoundError: .../data/raw/...csv` | Filename mismatch | `ls data/raw/`, make `RAW_FILE` in `config.py` match exactly |
| `KeyError: 'Label'` | Column name has stray spaces | The `.str.strip()` in `explore.py` handles this - check you copied it |
| `ValueError: Input contains NaN or infinity` | Cleaning did not run | Run `python src/clean.py` before `prepare.py` |
| `MemoryError` or the machine freezes | Too much data | Lower `SAMPLE_FRACTION` in `config.py` to `0.05` |
| `ConvergenceWarning` | The neural net hit its iteration limit | A warning, not an error. Safe to continue; mention it in the report. |
| `IndentationError` | Spacing got mangled when pasting | Recopy that whole code block from SCAFFOLD.md |
| `n_splits/class cannot be less than...` | A class has too few rows | Raise `MIN_CLASS_COUNT` in `config.py` to 50 |
| Nothing happens for minutes | Normal - training is slow | Wait. Random Forest on 140k rows takes a few minutes. |

**Cannot fix it?** Copy the last 10 lines of the error and ask. An error message is information,
not failure.

---

# Checklist

Setup:
- [ ] Python 3.11 installed (uv, or a method from Appendix A)
- [ ] `.venv` created **from 3.11** and activated (prompt shows `(.venv)`)
- [ ] `python -c "import sys; print(sys.version)"` prints `3.11.x`
- [ ] Libraries installed, `import` check passes
- [ ] Folders created
- [ ] All nine code files created from SCAFFOLD.md
- [ ] Dataset downloaded into `data/raw/`
- [ ] `RAW_FILE` in `config.py` matches the actual filename

Lab steps:
- [ ] Step 1 - explore ran, `class_balance.png` exists
- [ ] Step 2 - clean ran, cleaning numbers written down
- [ ] Steps 3–4 - split 60/20/20, scaler fitted on train only
- [ ] Steps 5–6 - two classical models + one neural network trained
- [ ] Step 7 - ablation ran, before/after numbers written down
- [ ] Multiclass ran, confusion matrix inspected
- [ ] Step 8 - final comparison table produced
- [ ] `python run_all.py` completes with no errors

Hand-in:
- [ ] README written, with the seed in it
- [ ] Report: problem / what you did / results / discussion / who did what
- [ ] Table has accuracy, macro-F1, recall, ROC-AUC **and** FAR
- [ ] Every figure has a caption, and the text refers to each one
- [ ] Ablation before/after numbers are in the report
- [ ] AI use disclosed
- [ ] Report exported as PDF
- [ ] Zip excludes `.venv/` and `data/`
- [ ] Uploaded to Canvas before the deadline

---

# Glossary

**Ablation** - changing one thing and holding everything else fixed, to show that thing mattered.
**Class imbalance** - one label far more common than the others. Here, ~80% normal traffic.
**Classifier** - a model that sorts things into categories.
**Confusion matrix** - a grid of actual vs. predicted, showing exactly what gets mistaken for what.
**Data leakage** - information reaching the model that it would not have in real use, producing
fake-good scores. Keeping IP addresses is the classic example.
**DataFrame** - a table in pandas. Rows and columns, like a spreadsheet.
**DoS** - denial of service. Flooding a system so it cannot serve real users.
**FAR** - false alarm rate, `FP/(FP+TN)`. Fraction of normal traffic wrongly flagged. Lower better.
**Feature** - one measured column describing a connection.
**Flow / connection** - one conversation between two machines. One row of your data.
**IDS** - intrusion detection system.
**Label** - the true answer for a row: `BENIGN` or an attack name.
**macro-F1** - F1 computed per class then averaged with equal weight. Your headline score.
**MLP** - multi-layer perceptron. The standard simple neural network.
**Overfitting** - memorising the training data instead of learning the pattern. Shows up as great
training scores and poor test scores.
**Port scan** - probing many ports to find an open way in. Often the first move of an attack.
**Scaling / standardisation** - putting all columns on a comparable numeric range.
**Seed** - a fixed number that makes randomness repeatable.
**Stratified split** - splitting while preserving each class's proportion in every part.
**Test set** - data held back and used exactly once, at the end.
**Validation set** - data used to choose between settings, so the test set stays untouched.
**venv** - virtual environment. A private Python installation for one project.
**uv** - a fast Python package and version manager. Used here to install Python 3.11.

---

# Appendix A: every way to install Python 3.11

Section 1.3 gives you one method. This appendix lists all of them, so you can pick a different one
if uv does not suit your machine, and so your report can say why you chose what you chose.

**Context:** this VM runs Ubuntu 25.10 ("questing"), glibc 2.42, x86_64. The questing archive
contains only `python3.13` and `python3.14`. There is no 3.11 package, so every working method
below gets Python from somewhere other than `apt`.

## The recommendation

### A1. uv — no sudo, no compiler, seconds

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.11
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Downloads a prebuilt interpreter into `~/.local/share/uv/`. Nothing outside your home directory
changes, and your system Python 3.13 is untouched. `uv pip` also installs the ~3 GB of TensorFlow
and PyTorch considerably faster than plain pip.

## Also verified to work here

### A2. Standalone build — a plain tarball, no tools at all

uv's interpreters come from the `python-build-standalone` project. You can download one directly:

```bash
curl -sLo py311.tar.gz "https://github.com/astral-sh/python-build-standalone/releases/download/20260901/cpython-3.11.16%2B20260901-x86_64-unknown-linux-gnu-install_only.tar.gz"
tar xzf py311.tar.gz            # creates ./python/
./python/bin/python3 --version  # Python 3.11.16
./python/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

47 MB, no password, no build step. This was run on this machine and confirmed working, including
`ssl`, `sqlite3`, `ctypes`, `lzma` and `tkinter`. Add `python/` to `.gitignore` if you use it.

### A3. Docker — fully isolated, host untouched

Docker is already installed here (29.7.2).

```bash
docker run -it --rm -v "$PWD:/work" -w /work python:3.11 bash
pip install -r requirements.txt
python run_all.py
```

The strongest reproducibility story for your report, and the easiest to hand to a marker. The
trade-off is that you work inside the container, and results land in your mounted folder.

### A4. conda / miniforge — the ML-coursework standard

```bash
curl -LsO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
# restart the shell, then:
conda create -n lab1 python=3.11
conda activate lab1
pip install -r requirements.txt
```

Heaviest install, but it handles TensorFlow and CUDA dependencies well and is what most ML courses
assume. Note you would use `conda activate lab1` everywhere this guide says
`source .venv/bin/activate`.

## Workable, but more effort

### A5. pyenv — compiles from source

```bash
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev libffi-dev liblzma-dev tk-dev
curl https://pyenv.run | bash
# add pyenv's init lines to ~/.bashrc as its output instructs, then restart the shell
pyenv install 3.11.16
pyenv local 3.11.16
python -m venv .venv && source .venv/bin/activate
```

Takes 5–15 minutes to compile. **Install every build dependency listed.** Miss one and you get a
Python silently lacking `ssl` or `lzma`, which does not fail at build time - it fails later, when
pip cannot reach the internet or pandas cannot read a compressed file.

### A6. Build from python.org directly

```bash
# same build dependencies as A5, then:
curl -LO https://www.python.org/ftp/python/3.11.16/Python-3.11.16.tgz
tar xzf Python-3.11.16.tgz && cd Python-3.11.16
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall        # NOT "make install"
python3.11 -m venv ~/Desktop/AI-for-Cybersecurity-Lab1/.venv
```

> **`make altinstall`, never `make install`.** `make install` overwrites `/usr/bin/python3`, which
> Ubuntu's own tooling (including apt) depends on. That breaks the operating system and is
> genuinely hard to recover from on a VM. `altinstall` installs as `python3.11` alongside, safely.

### A7. mise or asdf — general version managers

```bash
curl https://mise.run | sh
mise use python@3.11
```

Same idea as pyenv, newer tooling. Sensible if you already use one of them for Node or Ruby.
Neither is installed on this machine.

## Do not use these

### A8. `sudo apt install python3.11` — impossible

This is the command that fails with `Unable to locate package python3.11`. Ubuntu 25.10 carries
only 3.13 and 3.14. No amount of `apt update` changes this.

### A9. deadsnakes PPA — no questing release

The standard tutorial answer, and it does not work here. The PPA publishes these series:

```
bionic  devel  focal  jammy  noble  precise  resolute  trusty  vivid  xenial
```

There is no `questing`; it skipped 25.10 entirely, going from noble (24.04) to resolute (26.04).
Adding the PPA gives you a 404 on the Release file and leaves apt in an error state on every
subsequent `apt update`.

### A10. deadsnakes pinned to `noble` — works, but risks your system

Noble does carry `python3.11`, `python3.11-venv` and `python3.11-dev`, and you can force apt to
read the 24.04 archive from a 25.10 system. Do not. You would be mixing packages built against
glibc 2.39 into a glibc 2.42 system, with apt then free to pull noble versions of unrelated
dependencies. It can break packages far outside Python. Not worth it when A1 takes ten seconds.

### A11. Snap — does not exist

There is no Python 3.11 snap. Searching `snap find python` returns hobby packages for 3.6, 3.8 and
similar, none maintained and none 3.11.

## Which to pick

| Situation | Method |
|---|---|
| This VM, normal case | **A1 uv** |
| No network tooling, want one file | A2 standalone tarball |
| Want maximum reproducibility for the marker | A3 Docker |
| Already comfortable with conda | A4 conda |
| Already use pyenv for other projects | A5 pyenv |
| Different machine, different distro | A1 uv still works everywhere |

Whichever you use, record it in your README. The rubric asks for reproducibility, and "Python 3.11
via uv" is a concrete, checkable answer.
