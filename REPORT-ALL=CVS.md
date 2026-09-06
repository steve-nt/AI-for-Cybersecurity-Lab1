# Lab 1: Building Your First Intrusion Detector
## Full-dataset run - all eight CICIDS2017 day-files

**Dataset:** CICIDS2017, all 8 `MachineLearningCVE` day-files combined
**Random seed:** 42 (`src/config.py`)
**Code:** `collab/src/` + `run_all.py`; results in `collab/results/`
**Authors:** Kirill Silchenko (kirsil-5@student.ltu.se) and Stefanos Ntentopoulos (stente-5@student.ltu.se)

> This report covers the **multi-day** run. A separate single-day run (Wednesday only) is written
> up in `REPORT.md`. The numbers are not interchangeable - different rows, different classes,
> different class balance.

---

## 1. What the problem is

An Intrusion Detection System watches network traffic and raises an alarm when a connection looks
like an attack. Writing the rules by hand - *"more than 500 connections a minute from one address,
alarm"* - works only until an attacker does something the rule author did not anticipate. Instead we
give a model a large table of labelled connections and let it learn the difference itself.

We built two detectors from the same data:

- **Binary detection.** One yes/no question per connection: normal, or attack? This is what an alarm
  needs.
- **Multiclass detection.** Name the attack - *PortScan*, *DDoS*, *Bot*, *Infiltration*, and so on.
  This is what an analyst needs after the alarm fires, because the response to a volumetric flood is
  not the response to a SQL injection attempt.

The defining property of the data is severe class imbalance: **80.3% of connections are normal**.
That single fact makes accuracy an actively misleading metric and drives every evaluation choice
below.

## 2. What we did

### 2.1 The data (Lab Step 1)

We combined **all eight** CICIDS2017 day-files rather than the single day the brief suggests as a
starting point. We verified first that this is safe: all eight share **identical 79-column headers**,
so they concatenate without producing mismatched or NaN columns.

**Raw combined data: 2,830,743 rows x 79 columns, 15 classes.**

| Class | Rows | Share |
|---|---|---|
| BENIGN | 2,273,097 | 80.300% |
| DoS Hulk | 231,073 | 8.163% |
| PortScan | 158,930 | 5.614% |
| DDoS | 128,027 | 4.523% |
| DoS GoldenEye | 10,293 | 0.364% |
| FTP-Patator | 7,938 | 0.280% |
| SSH-Patator | 5,897 | 0.208% |
| DoS slowloris | 5,796 | 0.205% |
| DoS Slowhttptest | 5,499 | 0.194% |
| Bot | 1,966 | 0.069% |
| Web Attack - Brute Force | 1,507 | 0.053% |
| Web Attack - XSS | 652 | 0.023% |
| Infiltration | 36 | 0.001% |
| Web Attack - Sql Injection | 21 | 0.001% |
| Heartbleed | 11 | 0.000% |

**Figure 1 - `collab/results/figures/class_balance.png`.** Rows per traffic type on a logarithmic
axis. Figure 1 is the justification for everything in section 4: the largest class is five orders of
magnitude bigger than the smallest. A linear axis would render the bottom six classes as invisible
flat lines, which is itself the point - these are the attacks a careless evaluation will silently
ignore.

### 2.2 Cleaning (Lab Step 2, "cleaning you must do and why")

**Removing ID columns - with an honest caveat.** The brief requires dropping name-tag columns (IP
addresses, timestamps, Flow ID) because they identify *who* and *when* rather than describing attack
behaviour. A model given them memorises "traffic from 192.168.10.50 is bad", scores brilliantly on a
test set drawn from the same capture, and is worthless on a real network. That is **data leakage**.

However, **the `MachineLearningCVE` distribution has already had those columns stripped upstream by
CIC**, so our cleaning step found only two of the twelve names it looks for. We are not claiming
credit for removing columns that were never present. What we did drop:

- **`Destination Port`** - present, and leaky in this dataset. Attack traffic sits on fixed ports, so
  a model can shortcut to "port 80 means Hulk" instead of learning traffic behaviour.
- **`Fwd Header Length.1`** - a duplicated column in CICIDS2017 carrying no new information.

**Fixing broken numbers.** Several features are computed as bytes-per-second, which is division by
flow duration. When duration is zero the result is infinity, which no model accepts. We replaced
infinities with NaN and dropped the affected rows.

**Removing duplicates.** Exact duplicate rows are dangerous rather than merely redundant: the same
row can land in training *and* test, so the model is scored on something it memorised. That inflates
results dishonestly, and on this dataset the effect is large.

**Trimming label text.** CICIDS2017 column names carry leading spaces and label values carry
trailing ones. We stripped both. The Web Attack labels additionally contain a literal U+FFFD
replacement character baked into the CSV by CIC upstream (raw bytes `ef bf bd`); we normalised it to
a hyphen so the class names render correctly in Figure 3.

**Dropping dead columns.** Columns with the same value in every row teach nothing and were removed.

**Duplicates dominate the cleaning, and one class almost vanishes.** Removing exact duplicates
deleted **594,712 rows - 21% of the dataset**. The effect is wildly uneven across classes, and one
result deserves its own line:

| Class | Raw rows | After de-duplication | Retained |
|---|---|---|---|
| DDoS | 128,027 | ~128,015 | 100.0% |
| DoS GoldenEye | 10,293 | ~10,285 | 99.9% |
| BENIGN | 2,273,097 | ~1,896,670 | 83.4% |
| DoS Hulk | 231,073 | ~172,845 | 74.8% |
| SSH-Patator | 5,897 | ~3,220 | 54.6% |
| **PortScan** | **158,930** | **~1,955** | **1.2%** |

**98.8% of PortScan rows were exact duplicates.** That is not a bug, it is what port scanning *is*:
the attacker sends near-identical probes to many ports, so the resulting flow records are
indistinguishable from one another. Keeping them would have inflated PortScan from a rare class to
the third-largest, and every duplicate would have risked landing in both training and test. This
single cleaning step changes PortScan from 5.6% of the data to roughly 0.1% of it.

**Rare-class protection, and where it failed.** Our `PROTECT_CLASS_BELOW = 20` rule holds classes
smaller than 20 rows out of the sampling step and keeps them whole. It was tuned on a single day's
data, where it correctly rescued Heartbleed (11 rows).

**On the full dataset it was set one row too low, and we report that as a methodological error.**
After de-duplication, Web Attack - SQL Injection has roughly **20** rows and Infiltration roughly
**35**. Both sit *just above* the threshold, so neither was protected, and both were sampled at 20%:

| Class | Raw | After cleaning | After 20% sample | Rows in test set |
|---|---|---|---|---|
| Heartbleed | 11 | 11 | 11 *(protected)* | **2** |
| Web Attack - SQL Injection | 21 | ~20 | 4 | **1** |
| Infiltration | 36 | ~35 | 7 | **1** |

The consequence is visible in section 3.2: both classes are evaluated on a **single test row each**,
and both score zero. Raising the threshold to around 200 would have kept all three whole. We have
left the run as it stands rather than re-running to a flattering configuration, and we discuss the
consequence in section 4.6.

**The cleaning in numbers:**

| Stage | Value |
|---|---|
| Raw combined | 2,830,743 rows x 79 columns |
| ID columns dropped | 2 - `Destination Port`, `Fwd Header Length.1` |
| Infinity values found | 4,376 |
| Missing values found | 5,734 |
| Rows dropped for inf/NaN | 2,867 |
| **Duplicate rows dropped** | **594,712** (21% of the dataset) |
| Constant columns dropped | 8 |
| Classes dropped (< 10 rows) | none |
| **After 20% stratified sample** | **446,641 rows x 69 columns** (68 features + label) |

### 2.3 Split and scaling (Lab Steps 3 and 4)

A **stratified 60/20/20** split, stratified on the *multiclass* label rather than the binary one, so
each of the 15 attack types keeps its proportion in all three parts. Stratifying only on normal-vs-
attack could still have placed every Infiltration row in a single split.

| Split | Rows | Share |
|---|---|---|
| Train | 267,984 | 60% |
| Validation | 89,328 | 20% |
| **Test** | **89,329** | 20% |

The test set contains **75,868 normal and 13,461 attack** connections. The attack rate is **0.1507
in all three splits**, which is the evidence stratification worked.

Note that de-duplication raised the benign share: BENIGN is 80.3% of the raw data but **84.9% of the
cleaned data**, because so many attack rows (PortScan especially) were duplicates.

The `StandardScaler` was fitted on **training data only** and then applied unchanged to validation
and test. Fitting on everything would leak the test set's mean and spread into training.

**The test set was used exactly once per model, at the very end.** Every choice of hyperparameter was
made on the validation set. This is the "no test-set peeking" requirement, and it is what makes the
numbers in section 3 an honest estimate of performance on unseen traffic.

### 2.4 Models and settings (Lab Steps 5 and 6)

The brief asks for one classical model plus one neural network. We used **two** classical models plus
a neural network:

| Model | Scaled input? | Settings tried | Winner (chosen on validation) |
|---|---|---|---|
| Logistic Regression | yes | `C=0.1`; `C=1.0`; `C=1.0` + `class_weight='balanced'` | `C=1.0` |
| Random Forest | no | 100 trees / unlimited depth; 300 trees / depth 20 | **300 trees, depth 20** |
| MLP (neural network) | yes | one hidden layer `(32)`; two hidden layers `(64, 32)` | **`(64, 32)`** |

The neural network is scikit-learn's `MLPClassifier`, which the brief explicitly permits ("also
counts and is the easiest to start with"). It is a genuine multi-layer perceptron and needs no GPU.

Per the brief's scaling cheat-sheet, Logistic Regression and the MLP receive standardised features
and Random Forest receives raw ones. Section 3.3 tests whether that guidance actually matters.

For multiclass we trained a 200-tree Random Forest on the identical split, changing only the target
from the 0/1 label to the full attack name.

## 3. Results

### 3.1 Binary detection (Lab Step 8)

**Table 1 - Binary detection on the held-out test set** (89,329 rows: 75,868 normal, 13,461 attack).
Rows 1-3 are the tuned models; rows 4-9 are the scaling ablation of section 3.3.

| Model | Accuracy | macro-F1 | Recall (attack) | ROC-AUC | FAR |
|---|---|---|---|---|---|
| Logistic Regression | 0.9721 | 0.9418 | 0.8325 | 0.9915 | 0.0032 |
| **Random Forest** | **0.9984** | **0.9968** | **0.9923** | **0.9999** | **0.0006** |
| MLP (neural network) | 0.9948 | 0.9898 | 0.9825 | 0.9995 | 0.0030 |
| LR [without scaling] | 0.9552 | 0.9075 | 0.7881 | 0.9033 | 0.0152 |
| LR [with scaling] | 0.9721 | 0.9418 | 0.8325 | 0.9915 | 0.0032 |
| RF [without scaling] | 0.9984 | 0.9968 | 0.9932 | 0.9997 | 0.0007 |
| RF [with scaling] | 0.9984 | 0.9968 | 0.9931 | 0.9997 | 0.0007 |
| MLP [without scaling] | 0.9716 | 0.9446 | 0.9089 | 0.9686 | 0.0173 |
| MLP [with scaling] | 0.9948 | 0.9898 | 0.9825 | 0.9995 | 0.0030 |

As Table 1 shows, **Random Forest wins on every metric simultaneously** - highest macro-F1 (0.9968),
highest attack recall (0.9923) and lowest false-alarm rate (0.0006). There is no trade-off to
adjudicate.

**Table 2 - the same results as counts**, which makes the differences concrete:

| Model | False alarms (FP) | Attacks missed (FN) | Attacks caught (TP) |
|---|---|---|---|
| Logistic Regression | 239 | **2,255** | 11,206 |
| **Random Forest** | **42** | **104** | **13,357** |
| MLP (neural network) | 230 | 236 | 13,225 |

**Table 2 is the most important table in this report, and this run makes the point unusually
sharply.** Logistic Regression and the MLP have **almost identical false-alarm rates** - 0.0032
against 0.0030, a difference of nine false alarms across 75,868 normal connections. On that metric
alone you would call them equivalent.

They are not remotely equivalent. Logistic Regression **misses 2,255 of 13,461 attacks - one in six.**
The MLP misses 236. Same false-alarm behaviour, **almost ten times the intrusions let through.**

Its accuracy of 0.9721 also looks respectable. Random Forest, 2.6 percentage points higher, misses
104 - **twenty-two times fewer**.

**Figure 2 - `collab/results/figures/model_comparison.png`.** The three tuned models on macro-F1
(left) and false-alarm rate (right). The right-hand panel of Figure 2 shows Logistic Regression's FAR
bar at roughly six times Random Forest's. Note that the left panel compresses all three models into
the top 6% of its axis, which is a fair illustration of why we do not argue from single high-valued
metrics.

### 3.2 Multiclass detection

**Figure 3 - `collab/results/figures/confusion_multiclass.png`.** Row-normalised confusion matrix
across all 15 classes; rows are the true label, columns the prediction, and the diagonal is per-class
recall. Figure 3 is where this run becomes genuinely informative, because unlike the binary task the
diagonal is **not** clean.

**Table 3 - per-class results.** Overall **macro-F1 0.7761**, **macro-FAR 0.0005**.

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| BENIGN | 1.00 | 1.00 | 1.00 | 75,868 |
| DDoS | 1.00 | 1.00 | 1.00 | 5,121 |
| FTP-Patator | 1.00 | 1.00 | 1.00 | 237 |
| DoS Hulk | 1.00 | 0.99 | 1.00 | 6,914 |
| DoS GoldenEye | 1.00 | 0.98 | 0.99 | 412 |
| DoS slowloris | 0.98 | 0.98 | 0.98 | 215 |
| DoS Slowhttptest | 0.94 | 0.97 | 0.95 | 209 |
| SSH-Patator | 1.00 | 0.93 | 0.96 | 129 |
| PortScan | 0.97 | 0.91 | 0.94 | 78 |
| Heartbleed | 1.00 | 1.00 | 1.00 | **2** |
| **Web Attack - Brute Force** | 0.73 | **0.75** | 0.74 | 59 |
| **Bot** | 0.74 | **0.65** | 0.69 | 57 |
| **Web Attack - XSS** | 0.45 | **0.35** | 0.39 | 26 |
| **Infiltration** | **0.00** | **0.00** | **0.00** | **1** |
| **Web Attack - SQL Injection** | **0.00** | **0.00** | **0.00** | **1** |

**The headline multiclass score is macro-F1 0.7761, against 0.9968 for the binary task.** That gap is
the single most informative result in this report. The same model, on the same data, looks close to
flawless when asked "attack or not?" and distinctly mediocre when asked "which attack?". Macro-F1
weights all 15 classes equally, so the classes it fails on cannot hide behind the 85% of traffic it
handles perfectly.

Four findings follow from Table 3 and Figure 3:

1. **Infiltration and SQL Injection score zero - but each has a support of 1.** They were evaluated on
   a single test connection each, because our sampling threshold was one row too low (section 2.2).
   These zeros are real - the model does classify both as benign - but they are measured on evidence
   far too thin to support a conclusion. **Both facts must be stated together.** With a corrected
   threshold these classes would have roughly 7 and 4 test rows, which is still too few for a
   trustworthy per-class score.
2. **Web Attack Brute Force and XSS are systematically confused with each other** (Figure 3: 0.17 of
   Brute Force predicted as XSS, 0.58 of XSS predicted as Brute Force). This is the most interesting
   *security* observation in the run. Both are attacks carried over ordinary HTTP, and their
   flow-level statistics - packet sizes, timings, durations - are nearly identical. The distinguishing
   information is in the request payload, which this feature set does not capture. No amount of model
   tuning fixes that.
3. **Bot recall is 0.65**: 35% of botnet traffic is classified as benign. That is the expected
   outcome, because command-and-control traffic is explicitly designed to resemble ordinary traffic.
4. **PortScan reaches 0.91 recall on only 78 test rows.** Before cleaning it was the third-largest
   class with 158,930 rows; 98.8% were exact duplicates (section 2.2). The model detects it well from
   what genuinely remains.

### 3.3 The ablation: with vs. without feature scaling (Lab Step 7)

We changed **exactly one thing** - whether the model receives standardised features - and held the
split, the seed and every hyperparameter identical.

| Model | macro-F1 without -> with | Recall without -> with | FAR without -> with |
|---|---|---|---|
| Logistic Regression | 0.9075 -> **0.9418** | 0.7881 -> **0.8325** | 0.0152 -> **0.0032** |
| MLP (neural network) | 0.9446 -> **0.9898** | 0.9089 -> **0.9825** | 0.0173 -> **0.0030** |
| Random Forest | 0.9968 -> 0.9968 | 0.9932 -> 0.9931 | 0.0007 -> 0.0007 |

The brief's cheat-sheet is confirmed. The MLP gains **0.045 macro-F1** and cuts its false-alarm rate
by **83%**; Logistic Regression gains 0.034 and cuts FAR by **79%**. Random Forest does not move at
all - its macro-F1 changes in the fourth decimal place, which is noise.

The mechanism explains the split cleanly. Features here span wildly different ranges: flow duration in
microseconds runs to millions while flag counts run 0 to 8. Logistic Regression and the MLP both
compute weighted sums of their inputs, so an unscaled large-magnitude column dominates purely because
its numbers are bigger, and gradient descent struggles on the resulting ill-conditioned surface. A
decision tree asks *"is this value above 500?"*, and that question means the same thing in any units -
so Random Forest is indifferent **by construction**, not by luck.

**Direct evidence for that mechanism: the solver told us.** Training Logistic Regression on unscaled
features emits a `ConvergenceWarning` from scikit-learn:

```
ConvergenceWarning: lbfgs failed to converge (status=1):
STOP: TOTAL NO. OF ITERATIONS REACHED LIMIT.
Increase the number of iterations (max_iter) or scale the data
```

The warning appears **only on the unscaled arm**. We verified this from the saved model rather than
inferring it from the console: the fitted scaled model reports `n_iter_ = 170` against a limit of
`max_iter = 1000`, so it converged comfortably. The unscaled model exhausted all 1000 iterations and
stopped without reaching a solution.

This matters for three reasons.

1. **It confirms the mechanism rather than merely the outcome.** We are not just observing that
   unscaled scores are lower; we can see *why*. The features span microseconds-to-millions alongside
   flag counts of 0 to 8, which makes the optimisation surface badly conditioned. The same solver
   that flounders for 1000 iterations on raw features finds the optimum in 170 once they are
   standardised.
2. **The headline numbers in Table 1 are unaffected.** Every tuned model in rows 1-3 converged. The
   warning belongs solely to the ablation's unscaled arm, which exists precisely to be worse.
3. **scikit-learn's own advice is the experiment.** The warning suggests *"increase max_iter **or**
   scale the data"*. Our ablation runs that second option as a controlled comparison.

**We deliberately did not raise `max_iter` to silence the warning.** An ablation must change exactly
one thing. Granting the unscaled model a larger iteration budget while the scaled model kept 1000
would have changed two variables at once and invalidated the comparison. Both arms use
`max_iter=1000` (`src/ablation.py:33`). It would also probably not have helped: the obstacle is
ill-conditioning, not an insufficient budget.

One methodological note in the interest of precision. Python displays a given warning only once per
code location by default, so seeing the message once does not by itself prove that only one fit
failed to converge. The saved model's `n_iter_` value settles it independently, which is why we
checked that rather than relying on the console output.

The MLP is configured with `max_iter=100` and `early_stopping=True` (`src/ablation.py:37`), so its
unscaled degradation is a genuine difference in fit quality rather than an artefact of a truncated
optimisation.

## 4. Discussion

### 4.1 Which model we would deploy

**Random Forest**, and the case is not close. It has the best macro-F1 (0.9968), the best recall
(0.9923) and the lowest FAR (0.0006). Deploying it costs nothing relative to the alternatives.

### 4.2 What FAR actually tells you

FAR is `FP / (FP + TN)` - of all genuinely normal traffic, the fraction wrongly flagged. Scaled to a
network carrying a million normal connections a day:

| Model | FAR | False alarms per day |
|---|---|---|
| **Random Forest** | 0.0006 | **~554** |
| MLP | 0.0030 | ~3,032 |
| Logistic Regression | 0.0032 | ~3,150 |

Around 554 alerts a day is triageable by a small team. Roughly 3,100 is not - at one every 27 seconds,
round the clock, an analyst team stops reading them, and a detector nobody reads is worse than no
detector because it manufactures false confidence that the network is being watched.

**But FAR alone would mislead you badly here, and this run proves it.** Logistic Regression and the
MLP have effectively the same false-alarm rate - 0.0032 against 0.0030, nine alarms apart across
75,868 normal connections. Judged on FAR they are interchangeable. Yet Logistic Regression misses
**2,255 attacks to the MLP's 236**.

A model can earn a flattering false-alarm rate simply by rarely crying wolf - which, on data that is
85% benign after cleaning, means predicting "normal" and being right most of the time. **FAR and
recall must be read together**, and that is precisely the argument for macro-F1 as the headline
number: it collapses both into one score that neither can game alone.

### 4.3 Why accuracy alone is misleading

BENIGN is **80.3%** of the raw data and **84.9%** after cleaning (Figure 1). A model that ignores its
input entirely and always answers "normal" scores **84.9% accuracy while catching zero attacks**. It would look like a
respectable B-grade classifier and be completely worthless.

Macro-F1 exposes this immediately, because it computes F1 separately for each class and averages with
**equal weight**. The lazy model scores near-perfectly on the majority class and zero on the rest, and
the average collapses. Accuracy hides precisely what a security team cares about.

Our own results make the point without a hypothetical: Logistic Regression reaches 0.9721 accuracy -
a number most people would call good - while letting one attack in six through.

The multiclass task drives it home further. Overall accuracy there is **1.00** to two decimal places,
while macro-F1 is **0.7761**. The accuracy figure is carried almost entirely by the 75,868 benign
rows; macro-F1 gives the two failing classes the same weight as BENIGN and immediately exposes them.

### 4.4 What the ablation proved

Scaling is not cosmetic for the models that need it. For the MLP it is the difference between **1,313
false alarms and 230** on the same test set, and between **1,226 missed attacks and 236**. It also
established that Random Forest's indifference is structural rather than lucky, which has a practical
consequence: one fewer preprocessing step that can be got wrong in deployment.

### 4.5 Comparison with the single-day run

Against the Wednesday-only run in `REPORT.md`, the full dataset is a **harder and more honest**
problem:

| | Single day | All eight days |
|---|---|---|
| Rows (raw) | 692,703 | 2,830,743 |
| Classes | 6 | 15 |
| BENIGN share | 63.5% | 80.3% |
| BENIGN share after cleaning | 63.5% | 84.9% |
| Best macro-F1 (binary) | 0.9982 | 0.9968 |
| **macro-F1 (multiclass)** | **0.9937** | **0.7761** |
| Multiclass diagonal | every class >= 0.97 | two classes at 0.00 |

The multiclass macro-F1 falling from 0.9937 to 0.7761 is the clearest illustration. The single-day
scores are *higher* and considerably less informative. Wednesday contains only
denial-of-service families, which are volumetric and trivially separable from browsing; its confusion
matrix is a clean diagonal that reveals nothing. The full dataset introduces stealthy, low-volume
attacks - Infiltration, SQL injection, botnet C2 - which the same pipeline fails to detect. **The
lower score is the more trustworthy result.**

### 4.6 Limitations, stated plainly

- **Our rare-class threshold was set one row too low, and we did not re-run to hide it.**
  `PROTECT_CLASS_BELOW = 20` was tuned on a single day. On the full dataset, SQL Injection (~20 rows
  after cleaning) and Infiltration (~35) fell just outside it, were sampled at 20%, and ended with
  **one test row each**. A value near 200 would have kept them whole. This is a genuine methodological
  error, and it is ours.
- **Two attack classes score zero - on one test row each.** Infiltration and SQL Injection are
  classified as benign, which is a real failure, but the measurement rests on a single connection
  apiece and cannot support a strong claim either way.
- **Heartbleed's perfect score rests on 2 test rows** and is not evidence of anything.
- **De-duplication removed 98.8% of PortScan.** The retained rows are the genuinely distinct ones, so
  we consider this correct, but it means our PortScan result is measured on 78 test rows rather than
  the ~32,000 the raw counts would suggest.
- **A synthetic capture.** CICIDS2017 was generated on a purpose-built testbed with scripted attacks
  on a fixed schedule. Real traffic is messier and the attacks here are likely more separable.
- **A sample, not the full data.** 446,641 rows of roughly 2.23 million after cleaning.
- **Flow features only.** No payload inspection, which is why Brute Force and XSS are inseparable
  here. That is a limit of the feature set, not of the model.
- **Near-ceiling binary scores still invite scrutiny.** Our defence: the test set was split before any
  training, touched once, never used for selection; duplicates were removed before splitting; and
  `Destination Port` was dropped. The honest residual concern is that DoS Hulk, PortScan and DDoS
  together are 18% of the data and are all high-volume floods that differ enormously from normal
  browsing, so the binary task may simply be easy.
- **2017 traffic.** A detector trained on eight-year-old attacks may not transfer to current
  techniques.

## 5. Who did what

Kirill Silchenko owned the data pipeline - `config.py`, `explore.py`, `clean.py` and `prepare.py` -
including the multi-file loading change and the rare-class protection rule. Stefanos Ntentopoulos
owned the modelling and evaluation - `metrics.py`, `train_binary.py`, `ablation.py`,
`multiclass.py`, `compare.py` and `run_all.py`. Kirill wrote sections 1-2; Stefanos wrote sections
3-4. Both of us ran the full pipeline and confirmed the numbers matched.

## 6. Use of AI assistance

We used Claude (an AI assistant, Anthropic) during this lab. Its contribution was substantial and we
state that plainly: it helped scaffold the project structure, draft the pipeline code in `src/`,
diagnose the phantom rare-class problem described in section 2.2, design the multi-file loading
change, and draft this report.

All code was reviewed and executed by us. **Every number in this report was produced by running our
own submitted code**, not supplied by the assistant. We understand the code we are handing in and can
explain any part of it.

## 7. How to reproduce

| Item | Value |
|---|---|
| Random seed | 42, in `src/config.py` |
| Python | 3.11 |
| Libraries | scikit-learn, pandas, numpy, matplotlib, joblib, tabulate |
| `SAMPLE_FRACTION` | 0.20 |
| `MIN_CLASS_COUNT` | 10 |
| `PROTECT_CLASS_BELOW` | 20 (see section 2.2 - too low for this dataset) |
| Input | all 8 CSVs in `data/raw/`, loaded via `RAW_FILES` |
| Run | `python run_all.py` |
| Output | `collab/results/` |

## References

- Sharafaldin, I., Habibi Lashkari, A., & Ghorbani, A. A. (2018). *A detailed analysis of the
  CICIDS2017 data set.* International Conference on Information Systems Security and Privacy,
  172-188. Springer.
- CICIDS2017: https://www.unb.ca/cic/datasets/ids-2017.html
- scikit-learn documentation, "Supervised learning" and "Model evaluation" user guides.
