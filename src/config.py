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
