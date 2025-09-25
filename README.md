Utilities to ingest GW volume localizations and evaluate association with arbitrary transients.
```bash
conda create -n gwPackage python=3.11 -y
conda activate gwPackage
pip install -e .
pytest -q
