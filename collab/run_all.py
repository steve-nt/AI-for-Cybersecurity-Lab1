"""Run the entire lab from raw CSV to final table.

Run:  python run_all.py
"""
import subprocess
import sys
from pathlib import Path

STEPS = [
    ("Step 1  - explore",    "src/explore.py"),
    ("Step 2  - clean",      "src/clean.py"),
    ("Steps 3&4 - prepare",  "src/prepare.py"),
    ("Steps 5&6 - train",    "src/train_binary.py"),
    ("Step 7  - ablation",   "src/ablation.py"),
    ("Multiclass",           "src/multiclass.py"),
    ("Step 8  - compare",    "src/compare.py"),
]

root = Path(__file__).resolve().parent
for title, script in STEPS:
    print(f"\n{'#' * 70}\n### {title}\n{'#' * 70}")
    result = subprocess.run([sys.executable, str(root / script)])
    if result.returncode != 0:
        print(f"\nFAILED at {script}. Fix the error above, then re-run.")
        sys.exit(1)

print("\nAll steps finished. Look in results/ for your tables and figures.")
