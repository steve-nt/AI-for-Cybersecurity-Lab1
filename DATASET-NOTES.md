# DATASET-NOTES.md - What we downloaded and what to do with it

Notes from checking `ids-2017.md` and the `cicresearch/` folder on 2026-09-05.
Everything below was verified against the actual files, not assumed.

---

## 1. `ids-2017.md`

The CIC dataset description page for CICIDS2017: the 5-day capture schedule
(Mon 3 July to Fri 7 July 2017), attack timings, and the victim/attacker IP map.

The relevant part for this lab is the Wednesday section:

| Wednesday, July 5, 2017 | Time |
|---|---|
| DoS slowloris | 9:47 - 10:10 a.m. |
| DoS Slowhttptest | 10:14 - 10:35 a.m. |
| DoS Hulk | 10:43 - 11:00 a.m. |
| DoS GoldenEye | 11:10 - 11:23 a.m. |
| Heartbleed (port 444) | 15:12 - 15:32 |

Attacker: Kali, 205.174.165.73. Victim: WebServer Ubuntu, 205.174.165.68
(local IP 192.168.10.50).

This matches the file `GUIDE.md:300` recommends.

**Citation for the report (required by the dataset licence):**

> Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, "Toward Generating
> a New Intrusion Detection Dataset and Intrusion Traffic Characterization",
> 4th International Conference on Information Systems Security and Privacy
> (ICISSP), Portugal, January 2018.

---

## 2. `cicresearch/` - what is actually there

All three checksums verified against the `.md5` files downloaded alongside them.

| File | Size | MD5 | Need it? |
|---|---|---|---|
| `MachineLearningCSV.zip` | 224 MB | OK `4f83860afbf29cac8163854095bf6cf7` | **Yes. The only one we need.** |
| `GeneratedLabelledFlows.zip` | 271 MB | OK `5ca3f8f69e3514950681615824149973` | No |
| `Friday-WorkingHours.pcap` | **8.8 GB** | OK `7366c552425956e610bd69f57feb7e7a` | No |

Note: `MachineLearningCSV.md5` names the file `MachineLearningCVE.zip` (the
original name on the CIC server). The hash still matches our copy.

**What each one is:**

- `MachineLearningCSV.zip` holds the 8 per-day CSVs, including
  `Wednesday-workingHours.pcap_ISCX.csv` (225 MB). It extracts into a folder
  called `MachineLearningCVE/`, not `CSV`.
- `GeneratedLabelledFlows.zip` is the same days but keeps `Flow ID`,
  source/destination IP, ports and timestamp. Our `config.ID_COLUMNS` exists
  precisely to throw those away, so this zip buys us nothing.
- `Friday-WorkingHours.pcap` is raw packets, for people running CICFlowMeter
  themselves. Nothing in GUIDE/SCAFFOLD touches it, and it is *Friday* anyway,
  not the Wednesday we want. 8.8 GB that can be deleted whenever.

### Contents of `MachineLearningCSV.zip`

| File | Size |
|---|---|
| `Wednesday-workingHours.pcap_ISCX.csv` | 225 MB |
| `Monday-WorkingHours.pcap_ISCX.csv` | 177 MB |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | 135 MB |
| `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | 83 MB |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | 77 MB |
| `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | 77 MB |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | 58 MB |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | 52 MB |

---

## 3. Extract the one file we need (T05)

```bash
cd /home/steven/Desktop/AI-for-Cybersecurity-Lab1
mkdir -p data/raw
unzip -j cicresearch/MachineLearningCSV.zip \
  "MachineLearningCVE/Wednesday-workingHours.pcap_ISCX.csv" -d data/raw/
```

`-j` flattens the `MachineLearningCVE/` folder away. This produces the exact
filename `RAW_FILE` already expects (`SCAFFOLD.md:179`), so **no config edit is
needed** for the path.

---

## 4. The CSV checked against the scaffold

`Wednesday-workingHours.pcap_ISCX.csv`: **692,703 rows x 79 columns.**

| Label | Rows | % |
|---|---|---|
| BENIGN | 440,031 | 63.52% |
| DoS Hulk | 231,073 | 33.36% |
| DoS GoldenEye | 10,293 | 1.49% |
| DoS slowloris | 5,796 | 0.84% |
| DoS Slowhttptest | 5,499 | 0.79% |
| **Heartbleed** | **11** | 0.00% |

### Two quirks the scaffold already handles

1. Column names have **leading spaces** (`" Destination Port"`, `" Label"`).
   `load_raw()` calls `df.columns.str.strip()`, so this is covered.
2. `Fwd Header Length` genuinely appears **twice** (columns 35 and 56). pandas
   renames the second to `Fwd Header Length.1`, which is already listed in
   `config.ID_COLUMNS`. Covered.

### One thing that WILL crash

**Heartbleed has 11 rows.** `MIN_CLASS_COUNT = 10` lets it through step 2e of
`clean.py`. Step 2f then samples 20%, leaving about **2** Heartbleed rows, and
`prepare.py`'s stratified 60/20/20 split raises:

```
ValueError: The least populated class in y has only 1 member,
which is too few. The minimum number of groups for any class cannot
be less than 2.
```

The cause is ordering: the rare-class filter (2e) runs *before* the sample (2f),
so it never sees the post-sample count.

**Fix - one line in `src/config.py`:**

```python
MIN_CLASS_COUNT = 50   # was 10; must survive SAMPLE_FRACTION too
```

Heartbleed then gets dropped cleanly at step 2e and printed to the console,
which is exactly what T08 asks us to record. **Mention the dropped Heartbleed
class in the report** (§2, limitations).

Alternative fix if we want to keep it honest at `SAMPLE_FRACTION = 1.0`: move
step 2e to run *after* step 2f, so the threshold applies to the sampled data.

### Rough expected numbers after cleaning

Simulated by streaming the real file: drop rows containing Infinity/NaN, then
drop exact duplicates.

| Label | After clean | After 20% sample |
|---|---|---|
| BENIGN | 416,736 | ~83,300 |
| DoS Hulk | 172,846 | ~34,600 |
| DoS GoldenEye | 10,286 | ~2,060 |
| DoS slowloris | 5,385 | ~1,080 |
| DoS Slowhttptest | 5,228 | ~1,050 |
| Heartbleed | 11 | ~2 (dropped, see above) |
| **Total** | **~610,500** | **~122,100** |

Duplicates removed: about 80,900 rows, of which 57,278 are DoS Hulk and 22,947
are BENIGN. Infinity/NaN rows: about 1,300.

> These are close estimates from a text-level pass, **not** exact pandas output.
> Use whatever `clean.py` actually prints when recording numbers for T08.

---

## 5. How all of this connects to TASKLIST.md

### Where we actually are

Only **T01 is done**. Nothing else exists yet: no `src/`, no `data/`, no
`results/`, no `report/`, no `requirements.txt`, no `.gitignore`, no `.venv`.
`python3 -c "import pandas"` fails on this machine, so T02 has not happened either.

| Task | Status | What this document contributes |
|---|---|---|
| **T01** Download the dataset | **Done** | All three MD5s verified. The CSV we need is inside `MachineLearningCSV.zip`. |
| **T02** Install tools | Not started | Confirmed: no pandas system-wide. The venv step is mandatory, not optional. |
| **T03** Project skeleton | Not started | Blocks T05, because `data/raw/` does not exist yet. |
| **T04** `config.py` | Not started | Section 4 says which line to change (`MIN_CLASS_COUNT`) when you copy it in. |
| **T05** Put dataset in place | Ready | The `unzip -j` command in section 3 **is** T05. |
| **T06** `explore.py` | Blocked on T05 | The label table in section 4 is exactly what it will print. Use it to confirm the run worked. |
| **T07** `clean.py` | Blocked on T06 | This is where the Heartbleed bug is introduced. |
| **T08** Record cleaning numbers | Blocked on T07 | Section 4 has predicted numbers to sanity-check against. |
| **T09** `prepare.py` | Blocked on T07 | This is where the Heartbleed bug actually **crashes**. |
| **T14** `multiclass.py` | Blocked | Determines the confusion matrix size: 5 classes, not 6. |
| **T19/T20** Report §1, §2 | Can start now | `ids-2017.md` supplies the attack descriptions and the required citation. |
| **T27** Optional full-size run | Later | The `MIN_CLASS_COUNT` fix behaves differently here. See below. |

---

### T01 - Download the dataset

TASKLIST asks for `MachineLearningCSV.zip` and nothing else. We downloaded two
extra things that no task needs:

- `GeneratedLabelledFlows.zip` (271 MB) - not referenced anywhere in TASKLIST,
  GUIDE or SCAFFOLD.
- `Friday-WorkingHours.pcap` (8.8 GB) - likewise, and it is the wrong day.

Neither is a problem, they just cost disk. **T01's "done when" is satisfied.**

One part of T01 is *not* satisfied: *"Both of you need your own copy... having it
on both machines means either person can run the whole pipeline alone."* Only
this machine has it. The other person still needs to download
`MachineLearningCSV.zip` (224 MB, not the 8.8 GB pcap).

### T02 - Install tools

`python3 -c "import pandas"` returns `ModuleNotFoundError` here. Combined with
the TASKLIST note that this machine has **no pip and no ensurepip**, the
`sudo apt install -y python3-venv python3-pip` line is genuinely blocking. Do
T02 before trying to run anything in section 3 or 4 of this document.

### T05 - Put the dataset in place

T05's "done when" is: `ls data/raw/` shows the CSV **and the name matches
`config.py` exactly**.

The `unzip -j` command in section 3 produces
`Wednesday-workingHours.pcap_ISCX.csv`, which is character-for-character what
`SCAFFOLD.md:179` sets `RAW_FILE` to. So the usual T05 failure mode - filename
mismatch, the one GUIDE.md:752 lists in its troubleshooting table - **cannot
happen if you use that command.** No `config.py` edit needed for the path.

The `-j` flag matters. Without it you get `data/raw/MachineLearningCVE/Wednesday-...csv`,
one directory too deep, and `RAW_FILE` will not find it.

### T06 - `explore.py`

T06's "watch out" says: *"`KeyError: 'Label'` means you dropped the `.str.strip()`
lines. The CICIDS column names have leading spaces in them."*

**Confirmed - the leading spaces are real.** The header genuinely reads
`" Destination Port"`, `" Label"`, and so on. Keep both `.str.strip()` calls in
`load_raw()`.

When T06 runs, it should print the exact label table from section 4 above
(692,703 rows, 79 columns, BENIGN 63.52%). If your numbers differ, something
went wrong in T05 - most likely you extracted the wrong day.

### T07 - `clean.py`, and the data-leakage discussion

T07 says: *"Understand before moving on: why dropping IP addresses, ports and
timestamps matters... Leave them in and the model memorises 'traffic from
192.168.10.50 is bad'... That is data leakage, and explaining it is the single
best way to show understanding in the report."*

`GeneratedLabelledFlows.zip` is a **concrete illustration of exactly that point**,
and worth a sentence in the report. It contains the same flows *with* `Flow ID`,
`Source IP`, `Destination IP`, ports and `Timestamp` still attached. And
`ids-2017.md` tells us the victim was always 192.168.10.50 and the attacker
always 205.174.165.73. A model trained on that version would score near-perfectly
by learning two IP addresses and nothing about attacks. We chose the
`MachineLearningCSV` version, which has those columns already stripped - that is
*why* `config.ID_COLUMNS` finds so little left to drop.

Also confirmed for T07: `Fwd Header Length` really does appear twice in the
header, pandas renames the second to `Fwd Header Length.1`, and `ID_COLUMNS`
already lists it. No action needed.

### T07 + T09 - the Heartbleed bug

This is the one finding that will cost real time if not handled now.

- **Introduced in T07.** `clean.py` step 2e drops classes below
  `MIN_CLASS_COUNT = 10`. Heartbleed has 11 rows, so it survives. Step 2f then
  takes a 20% sample, leaving ~2 rows.
- **Crashes in T09.** `prepare.py` does a stratified 60/20/20 split, which needs
  at least 2 members per class per split, and raises `ValueError`.

So T07 will appear to succeed, print its six numbered lines, satisfy its
"done when", and hand a broken file to T09. Person A loses time debugging
`prepare.py` when the cause is one line in `config.py`.

**Apply the fix at T04**, when you first copy `config.py` in, so it never bites:

```python
MIN_CLASS_COUNT = 50   # was 10; must survive SAMPLE_FRACTION too
```

Heartbleed then gets dropped at step 2e with a printed message - which is exactly
what **T08** asks you to record (*"which rare classes were dropped, and their
counts"*) and what **T20** asks you to write up under limitations.

### T08 - Record the cleaning numbers

T08 warns: *"Do it now, not later - the output scrolls away and re-running costs
minutes."*

The estimate table in section 4 is a **pre-check, not a substitute**. Compare
what `clean.py` prints against it: roughly 80,900 duplicates, ~1,300 inf/NaN
rows, ~610,500 rows surviving, ~122,100 after sampling. Numbers in the same
ballpark mean the pipeline behaved. **Record the real printed numbers**, not
these ones.

A safer way to satisfy T08 in one shot:

```bash
python src/clean.py 2>&1 | tee results/tables/clean_log.txt
```

### T09 - `prepare.py`

Beyond the Heartbleed crash, T09 says two checks carry 25% of the grade:
stratification and train-only scaling. Section 4's class percentages are what
those three attack rates should hover around - roughly 36.5% attack in each of
train, val and test after Heartbleed is dropped.

### T14 - `multiclass.py`

With Heartbleed dropped, the multiclass problem has **5 classes**: BENIGN,
DoS Hulk, DoS GoldenEye, DoS slowloris, DoS Slowhttptest. The confusion matrix
is 5x5. Expect the two small DoS classes (~1,080 and ~1,050 rows in the sample)
to be where the errors concentrate - that is the interesting thing to discuss in
**T22**.

### T19 / T20 - Report sections

`ids-2017.md` is the source for these, and both can be written **now**, before
any code runs:

- **T19 (§1 the problem):** the attack list in section 1 above gives concrete
  examples of what "attack" means - four DoS variants with different mechanics,
  which is also the honest answer to "why is multiclass harder than binary".
- **T20 (§2 what we did):** the capture setup (25 profiled users, 5 days, mirror
  port) belongs here, plus the citation in section 1. Also the limitation that
  we used one day of one synthetic dataset, generated in 2017.

**The citation is not optional** - it is a condition of the dataset licence.

### T27 - Optional full-size run

At `SAMPLE_FRACTION = 1.0`, Heartbleed's 11 rows would survive a 60/20/20 split
(6/2/3), so it *could* be kept. But `MIN_CLASS_COUNT = 50` still drops it.

If you want Heartbleed included in the full-size run, use the alternative fix
from section 4 instead: move step 2e to run *after* step 2f, so the threshold
applies to the sampled data. Then leave `MIN_CLASS_COUNT = 10`.

**If you do this, T23 applies** (*"confirm nothing came from a fake-data run"*) -
the class list changes between the 20% and 100% runs, so every table and
confusion matrix in the report must be regenerated, not just the accuracy
numbers.

### Not connected to any task

Deleting `Friday-WorkingHours.pcap` reclaims 8.8 GB. No task needs it. Worth
doing before T17, which wipes and regenerates `data/processed/` and `results/`.

---

## 6. Appendix - the 2018 dataset (CSE-CIC-IDS2018), if we ever switch

The AWS bucket `s3://cse-cic-ids2018/` is ~477 GB, but that is almost all pcap.
The `Processed Traffic Data for ML Algorithms/` prefix is only **6.9 GB** across
10 CSVs, and the bucket is readable over plain HTTPS with no AWS CLI:

```bash
curl -o data/raw/Wednesday-14-02-2018.csv \
  "https://cse-cic-ids2018.s3.amazonaws.com/Processed%20Traffic%20Data%20for%20ML%20Algorithms/Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv"
```

Never run the `aws s3 sync` from the CIC website as-is. It pulls all 477 GB.

**But 2018 is not drop-in compatible** with our scaffold:

- 80 columns with different names (`Tot Fwd Pkts`, not `Total Fwd Packets`),
  and no leading spaces.
- A `Timestamp` string column that must be dropped.
- Labels are `Benign`, not `BENIGN`, so `config.BENIGN_LABEL` would change.
- No `Flow ID`/IP columns, except in `Thuesday-20-02-2018` (sic), which has 4
  extra ID columns and is 4.1 GB. Avoid that one.

Switching would mean editing `DROP_COLS` and `BENIGN_LABEL` in `config.py`.
**Recommendation: stay on CICIDS2017.** We already have it, verified, and the
whole scaffold is written for it.
