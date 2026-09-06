# Lab 1: Building Your First Intrusion Detector

**Dataset:** CICIDS2017, `Wednesday-workingHours.pcap_ISCX.csv`
**Random seed:** 42 (set in `src/config.py`)
**Code:** `src/` + `run_all.py` - see `README.md` for how to run it
**Authors:** [NAME A] and [NAME B]

---

## 1. What the problem is

An Intrusion Detection System watches network traffic and raises an alarm when a connection looks
like an attack. The traditional approach is hand-written rules - *"if one address opens more than
500 connections a minute, alarm"* - which works until an attacker behaves slightly differently from
whatever the rule anticipated. Instead we give a machine-learning model thousands of labelled
examples of normal and malicious traffic and let it learn the distinction itself.

We built this twice. **Binary detection** answers one yes/no question per connection: normal, or
attack? **Multiclass detection** goes further and names the attack - *DoS Hulk*, *DoS GoldenEye*,
*Heartbleed* and so on. The binary task is what an alarm needs; the multiclass task is what an
analyst needs once the alarm has fired, because the response to a denial-of-service flood is not the
response to a Heartbleed exploit.

The central difficulty is that the classes are wildly imbalanced, and that makes the obvious metric
actively misleading. This shapes every evaluation decision below.

## 2. What we did

### Data and cleaning

We used one day of CICIDS2017 - the Wednesday capture, which contains several denial-of-service
attack families plus normal office traffic. The raw file is **692,703 rows x 79 columns**.

| Cleaning stage | Result |
|---|---|
| Raw | 692,703 rows x 79 columns |
| ID columns dropped | 2 - `Destination Port`, `Fwd Header Length.1` |
| Infinity / missing values found | 1,586 infinities, 2,594 NaNs |
| Rows dropped for inf/NaN | 1,297 |
| Exact duplicate rows dropped | 106,415 |
| Constant (zero-variance) columns dropped | 10 |
| Classes below 10 rows dropped | none |
| Classes protected from sampling | Heartbleed - all 11 rows kept |
| After 20% stratified sample | **117,007 rows x 67 columns** (66 features + label) |

**On removing ID columns, and an honest caveat.** The lab requires dropping name-tag columns - IP
addresses, timestamps, Flow ID - because they identify *who* and *when* rather than describing what
an attack does. A model given them memorises "traffic from 192.168.10.50 is bad", scores brilliantly
on a test set drawn from the same capture, and is useless on any real network. That is data leakage.
**However, the `MachineLearningCVE` distribution we downloaded has already had those columns
stripped upstream**, so our cleaning step found only two of the twelve it looks for. We are not
claiming credit for removing columns that were never there. We did drop `Destination Port`, which
*was* present and which we consider leaky in this dataset: the attack traffic sits on fixed ports, so
the model could shortcut to "port 80 means Hulk" rather than learning traffic behaviour.

`Fwd Header Length.1` is a known duplicated column in CICIDS2017 and carries no new information.

The 106,415 duplicates matter more than their share suggests. An identical row appearing twice can
land once in training and once in test, so the model is scored on something it already memorised -
an inflated result obtained dishonestly rather than by learning.

**Rare-class handling.** Heartbleed appears only 11 times in 692,703 rows. Our first design dropped
classes under 10 rows, which Heartbleed survived by one; the 20% sample then cut it to 2 rows, which
was enough to stay in training but not enough to reach the test set at all. The class became a
phantom - present in training, never scored, contributing an empty row to the confusion matrix and
diluting the averaged false-alarm rate across a class that had never been tested. We therefore
adopted a three-tier policy: **drop below 10 rows, keep whole below 20, sample normally at 20 and
above.** Heartbleed keeps all 11 rows and splits 7/2/2, so it appears in the test set. The cost to
the headline multiclass macro-F1 was 0.0001. **The limitation this creates is stated in section 4.**

### Split and scaling

A **stratified 60/20/20** split, stratified on the *multiclass* label rather than the binary one, so
each attack type keeps its proportion in all three parts - a binary stratification could still have
put every Heartbleed row in one split.

| Split | Rows | Attack rate |
|---|---|---|
| Train | 70,203 | 0.3313 |
| Validation | 23,402 | 0.3313 |
| Test | 23,402 | 0.3313 |

The three attack rates agreeing to four decimal places is the evidence that stratification worked.

The scaler (`StandardScaler`) was fitted on the **training data only**, then applied unchanged to
validation and test. Fitting it on everything would let the mean and spread of the test set leak
into training - a subtle form of cheating that is easy to commit accidentally.

**The test set was used exactly once per model, at the very end.** All model selection was done on
the validation set. This is the "no test-set peeking" rule, and it is why the numbers in section 3
can be read as an estimate of performance on genuinely unseen traffic.

### Models and settings

Two classical models and one neural network, per the brief:

| Model | Scaled input? | Settings tried | Winner (chosen on validation) |
|---|---|---|---|
| Logistic Regression | yes | `C=0.1`, `C=1.0`, `C=1.0 + balanced` | `C=1.0` |
| Random Forest | no | 100 trees unlimited depth; 300 trees depth 20 | **100 trees, unlimited depth** |
| MLP (neural network) | yes | one hidden layer (32); two hidden layers (64, 32) | **(64, 32)** |

The neural network is scikit-learn's `MLPClassifier`, which the brief explicitly permits. It is a
genuine multi-layer perceptron, trains in minutes on this data and needs no GPU.

For the multiclass task we used a 200-tree Random Forest on the same split, changing only the target
from the 0/1 label to the full attack name.

## 3. Results

**Table 1 - Binary detection on the held-out test set (23,402 rows: 15,650 normal, 7,752 attack).**
The top three rows are the tuned models; the remaining six are the scaling ablation.

| Model | Accuracy | macro-F1 | Recall (attack) | ROC-AUC | FAR |
|---|---|---|---|---|---|
| Logistic Regression | 0.9804 | 0.9779 | 0.9768 | 0.9978 | 0.0178 |
| **Random Forest** | **0.9984** | **0.9982** | **0.9977** | 0.9999 | **0.0012** |
| MLP (neural network) | 0.9943 | 0.9935 | 0.9914 | 0.9998 | 0.0043 |
| LR [without scaling] | 0.9197 | 0.9091 | 0.8727 | 0.9448 | 0.0570 |
| LR [with scaling] | 0.9804 | 0.9779 | 0.9768 | 0.9978 | 0.0178 |
| RF [without scaling] | 0.9984 | 0.9982 | 0.9977 | 0.9999 | 0.0012 |
| RF [with scaling] | 0.9985 | 0.9984 | 0.9977 | 0.9998 | 0.0010 |
| MLP [without scaling] | 0.9715 | 0.9675 | 0.9347 | 0.9819 | 0.0103 |
| MLP [with scaling] | 0.9943 | 0.9935 | 0.9914 | 0.9998 | 0.0043 |

As Table 1 shows, Random Forest wins on every metric that matters: the highest macro-F1 (0.9982) and
the lowest false-alarm rate (0.0012), with the highest attack recall (0.9977). Note that ROC-AUC
displays as 0.9999 rather than a literal 1.0 - it is rounded from approximately 0.99988, not perfect.

Converting those rates into counts on the test set makes the differences concrete:

| Model | False alarms (FP) | Attacks missed (FN) |
|---|---|---|
| Logistic Regression | 279 | 180 |
| **Random Forest** | **19** | **18** |
| MLP | 67 | 67 |

**Figure 1 - `results/figures/class_balance.png`.** Row counts per traffic type in the raw file, on a
logarithmic scale. Figure 1 is the reason this report leads with macro-F1 and FAR rather than
accuracy: BENIGN accounts for 440,031 of 692,703 rows (63.52%) and DoS Hulk for a further 231,073
(33.36%), while Heartbleed appears just 11 times. The logarithmic axis is necessary - on a linear
scale the four smallest classes would be invisible flat lines.

**Figure 2 - `results/figures/model_comparison.png`.** The three tuned models compared on macro-F1
(left) and false-alarm rate (right). The right-hand panel of Figure 2 carries the real information:
Logistic Regression's FAR bar is roughly fifteen times the length of Random Forest's, a difference
invisible in the left-hand panel where all three bars sit above 0.97 on a 0-to-1 axis. This is
itself a small lesson in presenting imbalanced results - the metric that separates the models is not
the one that looks impressive.

**Figure 3 - `results/figures/confusion_multiclass.png`.** Row-normalised confusion matrix for the
multiclass task. Figure 3 shows a clean diagonal: every attack family is identified correctly at
0.99 or above, with no systematic confusion between families.

**Table 2 - Multiclass detection, per attack type.** Overall macro-F1 **0.9937**, macro-FAR **0.0006**.

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| BENIGN | 1.00 | 1.00 | 1.00 | 15,650 |
| DoS GoldenEye | 1.00 | 1.00 | 1.00 | 412 |
| DoS Hulk | 1.00 | 1.00 | 1.00 | 6,914 |
| DoS Slowhttptest | 0.96 | 0.99 | 0.97 | 209 |
| DoS slowloris | 1.00 | 0.99 | 0.99 | 215 |
| Heartbleed | 1.00 | 1.00 | 1.00 | **2** |

**The Heartbleed row must be read with its support column.** Two test rows, both classified
correctly. That is not evidence the model detects Heartbleed - it is one correct pair. We report the
class because excluding it would hide a real limitation, not because the score means anything.

### The ablation: with vs. without feature scaling

We changed exactly one thing - whether the model receives standardised features - and held
everything else identical.

| Model | macro-F1 without -> with | FAR without -> with |
|---|---|---|
| Logistic Regression | 0.9091 -> **0.9779** | 0.0570 -> **0.0178** |
| MLP (neural network) | 0.9675 -> **0.9935** | 0.0103 -> **0.0043** |
| Random Forest | 0.9982 -> 0.9984 | 0.0012 -> 0.0010 |

The prediction held. Logistic Regression gains 0.069 macro-F1 and cuts its false-alarm rate by more
than two thirds; the MLP gains 0.026 and cuts its FAR by well over half. Random Forest moves by 0.0002, which is
noise.

The mechanism explains the split. Features here span wildly different ranges - flow duration in
microseconds runs to millions, while flag counts run 0 to 8. Logistic Regression and the MLP both
compute weighted sums of their inputs, so an unscaled large-magnitude column dominates purely
because its numbers are bigger, and gradient descent struggles on the resulting ill-conditioned
surface. A decision tree asks *"is this value above 500?"*, and that question means exactly the same
thing whatever units the column is in - so Random Forest is indifferent by construction.

## 4. Discussion

**Which model we would deploy: Random Forest.** It achieves the highest macro-F1 (0.9982) *and* the
lowest false-alarm rate (0.0012), so there is no trade-off to argue about - it is not a case of
buying detection at the cost of noise.

**What FAR actually means.** Scale it to a realistic network. On a link carrying a million normal
connections a day:

| Model | FAR | False alarms per day |
|---|---|---|
| Random Forest | 0.0012 | **~1,214** |
| MLP | 0.0043 | ~4,281 |
| Logistic Regression | 0.0178 | **~17,827** |

Logistic Regression's accuracy of 0.9804 sounds perfectly respectable. It would also generate
roughly **17,800 false alarms every day** - about twelve per minute, around the clock. No analyst
team reads that. The alarm gets muted or switched off, and the detector becomes worse than useless
because it also created false confidence that the network was being watched. Random Forest's ~1,200
a day is still substantial but is at least triageable. This is why FAR belongs in the table
alongside accuracy: two models a couple of accuracy points apart can be operationally worlds apart.

**Why accuracy alone misleads here.** BENIGN is 63.52% of the raw data (Figure 1). A model that
ignores its input entirely and always answers "normal" scores 63.5% accuracy while catching zero
attacks. Macro-F1 exposes this immediately, because it computes F1 separately for the normal and
attack classes and averages them with equal weight - the lazy model scores near-perfectly on one
class and zero on the other, and the average collapses. Accuracy hides exactly what we care about.

**What the ablation proved.** Scaling is not cosmetic for the two models that need it: it is the
difference between a Logistic Regression that raises 279 false alarms and one that raises 892 on the
same test set. It also proved something about Random Forest - its indifference to scaling is not
luck but a consequence of how trees make decisions, which means one less preprocessing step to get
wrong in a deployment.

A secondary observation: we ran the identical pipeline locally (Python 3.11.16, scikit-learn 1.9.0)
and on Google Colab (scikit-learn 1.6.1). **Every scaled result was bit-identical across the two
environments; every unscaled result differed.** Unscaled inputs prevent the iterative solvers from
converging, so where they stop depends on floating-point details of the underlying maths library.
Scaling therefore buys reproducibility as well as accuracy. All numbers in this report come from the
local run.

### Limitations, stated plainly

- **One day of one dataset.** Wednesday of CICIDS2017 contains denial-of-service families and
  Heartbleed. It contains no port scans, no botnet traffic, no infiltration. Our scores say nothing
  about those.
- **A synthetic capture.** CICIDS2017 was generated on a purpose-built testbed with scripted attacks.
  Real networks are messier, and the attack traffic here may be more separable than reality.
- **A 20% sample.** 117,007 of 585,000 available rows after cleaning.
- **Heartbleed rests on 2 test rows.** Its perfect scores are statistically meaningless, and our
  protection rule deliberately over-represents it relative to a true 20% sample.
- **Near-ceiling scores invite suspicion, and should.** A macro-F1 of 0.9982 is high enough to ask
  whether something leaked. Our defence: the test set was split before any training, touched once,
  and never used for model selection; duplicates were removed before splitting; and `Destination
  Port` was dropped. The honest residual concern is that DoS Hulk - a third of the data - is a
  volumetric flood whose traffic features differ enormously from normal browsing, so the binary task
  may simply be easy on this particular day.
- **2017 attacks.** A detector trained on eight-year-old traffic may not generalise to current
  techniques.

## 5. Who did what

> **[FILL THIS IN BEFORE SUBMITTING - do not leave the placeholders.]**
>
> [NAME A] owned the data pipeline: `config.py`, `explore.py`, `clean.py`, `prepare.py`, the
> cleaning-numbers record, and the README. [NAME B] owned the modelling and evaluation:
> `metrics.py`, `train_binary.py`, `ablation.py`, `multiclass.py`, `compare.py` and `run_all.py`.
> [NAME A] wrote report sections 1-2; [NAME B] wrote sections 3-4. Both ran the full pipeline
> independently and confirmed matching numbers.

## 6. Use of AI assistance

We used Claude (an AI assistant, Anthropic) during this lab. Its contribution was substantial and we
state that plainly: it helped scaffold the project structure, draft the pipeline code in `src/`,
diagnose the Heartbleed phantom-class problem described in section 2, and draft this report.

All code was reviewed and executed by us. **Every number in this report was produced by running our
own submitted code on our own machines**, not supplied by the assistant. We understand the code we
are handing in and can explain any part of it.

## 7. Reproducibility

| Item | Value |
|---|---|
| Random seed | 42, in `src/config.py` |
| Python | 3.11.16 |
| scikit-learn | 1.9.0 (local run - Colab run used 1.6.1) |
| Sample fraction | 0.20 |
| Run command | `python run_all.py` |
| Runtime | ~30 minutes |

Running `python run_all.py` from a clean checkout regenerates every table and figure in this report.

## References

- Sharafaldin, I., Habibi Lashkari, A., & Ghorbani, A. A. (2018). *A detailed analysis of the
  CICIDS2017 data set.* International Conference on Information Systems Security and Privacy,
  172-188. Springer.
- CICIDS2017 dataset: https://www.unb.ca/cic/datasets/ids-2017.html
- scikit-learn documentation, "Supervised learning" and "Model evaluation" user guides.
