# Lab 1: Building Your First Intrusion Detector

An intrusion detection system built with machine learning on the CICIDS2017 dataset.

## Requirements

**Python 3.11.** Not the system Python. On Ubuntu 25.10 `sudo apt install python3.11` does not
work - the archive carries only 3.13 and 3.14, and the deadsnakes PPA has no `questing` series.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.11
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Roughly 3 GB and 5–15 minutes, mostly TensorFlow, PyTorch and PyTorch's CUDA packages.

Other install methods - pyenv, conda, Docker, standalone tarball, source build - are written out in
**GUIDE.md, Appendix A**, along with the ones that look like they should work but do not.

Verify:

```bash
python -c "import sys; print(sys.version)"          # must start 3.11.
python -c "import pandas, sklearn, matplotlib, joblib, tabulate; print('Core libraries OK')"
python -c "import tensorflow, torch; print('TF', tensorflow.__version__, '| torch', torch.__version__)"
```

## Where to start

| Document | What it is |
|---|---|
| `GUIDE.md` | The step-by-step walkthrough. Start here. Appendix A covers Python 3.11 install methods. |
| `TASKLIST.md` | The work split into tasks T01–T15, with owners and dependencies. |
| `SCAFFOLD.md` | Every file's full contents, ready to copy. |
| `DATASET-NOTES.md` | Notes on the CICIDS2017 data as it exists on this machine. |
| `ids-2017.md` | Background on the dataset itself. |

## Data

Download CICIDS2017 (`MachineLearningCSV.zip`, 224 MB) from
https://www.unb.ca/cic/datasets/ids-2017.html and place
`Wednesday-workingHours.pcap_ISCX.csv` in `data/raw/`.

## Run

```bash
python run_all.py
```

## Reproducibility

Python 3.11. Random seed 42 (`src/config.py`). Sample fraction 0.20 of one day's traffic.
Library versions constrained in `requirements.txt`.
The neural network is scikit-learn's `MLPClassifier`, one of the three options the lab brief allows.
