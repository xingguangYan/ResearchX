# [Artifact name] — reproduction instructions

Paper: [title, DOI] | Version: [tag] | Licence: [e.g. MIT for code, CC-BY-4.0 for data]

## What this reproduces
| Paper result | Command | Expected output | Runtime |
|---|---|---|---|

## Environment
```bash
python --version          # tested on 3.11
pip install -r requirements.txt   # versions pinned
# GPU: ... / CUDA: ...
```
Determinism: seeds in `configs/*.yaml`; hardware used for reported numbers: ...

## Data
| Dataset | Source | Licence | Access instructions | Checksum |
|---|---|---|---|---|
Splits are provided as files: `splits/train.csv`, `splits/val.csv`, `splits/test.csv`
(no overlap by [spatial/temporal/group] blocking).

## Quick start (30 minutes)
```bash
make setup && make reproduce-table2
```

## Full pipeline
```bash
python train.py --config configs/main.yaml
python evaluate.py --checkpoint results/main/best.pt
```

## Hyperparameters
| Parameter | Search range | Final value |
|---|---|---|

## Known limitations
- [What does not reproduce exactly, and why]

## Citation
```bibtex
@article{..., }
```
