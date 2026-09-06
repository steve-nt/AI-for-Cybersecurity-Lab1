"""Central settings for the whole lab.

Change things HERE, not in the other files. That way there is one place to look
when you are asked "what settings did you use?"
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
# A "seed" fixes the randomness. Splitting data and training models both involve
# random choices. With a fixed seed, you get the SAME numbers every time you run.
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
#RAW_FILE = DATA_RAW / "Wednesday-workingHours.pcap_ISCX.csv"

# ---------------------------------------------------------------------------
# OPTIONAL: using several days' files together
# ---------------------------------------------------------------------------
# The pipeline reads ONE file. To combine all eight CICIDS2017 day-files,
# uncomment the line below and swap load_raw() in explore.py for the commented
# multi-file version there. Nothing else downstream needs to change - clean.py
# calls load_raw(), and every later script reads clean.csv.
#
RAW_FILES = sorted(DATA_RAW.glob("*.csv"))
#


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

# Classes that survive MIN_CLASS_COUNT but are still smaller than this are kept
# WHOLE - they skip the sampling step in clean.py.
#
# WHY: Heartbleed has 11 rows in the Wednesday file. It clears MIN_CLASS_COUNT by
# one row, but a 20% sample cuts it to 2 - enough to survive the split, not enough
# to land in the test set at all. The result is a "phantom" class: it is in the
# training data, so the confusion matrix reserves an all-zero row for it, and
# macro-FAR averages over a class that was never actually tested.
#
# The full policy is: drop below MIN_CLASS_COUNT, keep whole below
# PROTECT_CLASS_BELOW, sample normally at or above it.
#
# FOR THE REPORT: a protected class is deliberately over-represented compared with
# a true 20% sample, and its per-class scores rest on only a handful of test rows.
# State both facts plainly - a perfect score on 2 test rows proves nothing.
PROTECT_CLASS_BELOW = 20

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
