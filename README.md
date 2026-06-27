# Arctic SMR Feasibility Explorer

Interactive tool that takes **any Arctic or subarctic coordinate (50–84°N)** and answers
one question: can a community here run on renewables, or does the climate force a nuclear
baseload? It pulls a 10-year climate record for the point (Open-Meteo ERA5, with NASA POWER
as a cross-check), falls back to a trained ML surrogate if both are offline, scores
micro-reactor feasibility, and explains the verdict with charts, siting flags, and an ML
confidence estimate.

## Run it
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```
Trained models ship with the repo, so that's all you need. To rebuild from real data:
```bash
python generate_training_data.py --source openmeteo   # real ERA5 grid (network)
python train_model.py
```

## What's here
```
dashboard/
├── app.py                     Streamlit UI
├── physics.py                 constants + FAO-56 solar geometry (shared)
├── feasibility.py             transparent scoring + verdict
├── inference.py               model loading, prediction, uncertainty, classification
├── openmeteo.py               live Open-Meteo (ERA5) client  ← primary data source
├── nasa_power.py              live NASA POWER client (cross-check)
├── generate_training_data.py  builds the circumpolar training grid
├── train_model.py             trains + saves the surrogate and classifier
├── data/    training grid, per-location feasibility, NASA calibration CSV
├── models/  surrogate.joblib, feasibility_clf.joblib, metrics.json
├── README.md       full usage + methodology
├── DESIGN.md       architecture, ML approach, scoring, limitations
└── DATA_SOURCES.md data sources (Open-Meteo implemented; others recommended)
```

See `dashboard/README.md` for the detailed write-up.
