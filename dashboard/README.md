# Arctic Micro-Reactor Feasibility Explorer

Interactive Streamlit tool that takes **any Arctic or subarctic coordinate (50–84°N)**
and answers one question: can a community here run on renewables, or does the climate
force a nuclear baseload? It pulls a 10-year climate record for the point (Open-Meteo ERA5,
with NASA POWER as a cross-check), falls back to a trained ML surrogate if both are offline, scores micro-reactor
feasibility, and explains the verdict with charts, siting flags, and an ML confidence.

This generalises the fixed five-community study in `../analysis.ipynb` into a
point-and-score tool. The energy physics (RERS, the 40% renewable threshold, eVinci
5 MWe sizing, 30% safety margin) is identical to the original study.

## What it shows
- **Verdict** — Strong / Conditional / Weak case for a micro-reactor, with a 0–100 score.
- **ML cross-check** — an independent classifier verdict and confidence.
- **KPIs** — peak & annual RERS, mean annual and coldest-month temperature, polar-night months.
- **Charts** — seasonal energy gap (renewables vs 1 MW demand), monthly RERS vs the 40% line, temperature climatology with ML uncertainty band, and a score-component breakdown.
- **Siting flags** — permafrost and extreme-cold engineering cautions.
- **Reactor sizing** — optional: enter a population to get the recommended MWe / eVinci unit count.
- **Map** of the queried point.

## Quick start
```bash
cd dashboard
pip install -r requirements.txt

# (optional) regenerate the training grid and models from scratch
python generate_training_data.py
python train_model.py

streamlit run app.py
```
The repo already ships the trained models (`models/`), so step 3 alone runs the app.

## How it works
1. **Climate** — `openmeteo.py` calls the Open-Meteo ERA5 archive for the exact lat/lon
   (cached on disk), with `nasa_power.py` as a cross-check. If both fail or you pick
   "instant" mode, `inference.py` uses the ML surrogate instead.
2. **ML surrogate** — a RandomForest mapping `(lat, lon, month) → (solar, wind, temp)`,
   trained on a circumpolar grid calibrated to real NASA data at 68°N. Held-out R²:
   solar 0.998, temp 0.994, wind 0.85. It also returns an uncertainty band from the
   spread across trees.
3. **Feasibility** — `feasibility.py` scores the point transparently from renewable
   insufficiency (best-month RERS vs the 40% threshold), climate demand pressure
   (mean annual temperature), and siting suitability (permafrost + extreme-cold penalties).
4. **Classifier** — a second RandomForest reproduces the rule and supplies a calibrated
   confidence; the app shows the rule score and the model's confidence side by side.

See `DESIGN.md` for the full rationale, including the data-calibration method and an
honest account of what the ML does and doesn't add.

## Data sources
- **Open-Meteo (ERA5)** — primary live climatology (`archive-api.open-meteo.com`), solar / wind / temperature, no key.
- **NASA POWER** — live cross-check (`power.larc.nasa.gov`) and grid-calibration anchor.
- **Calibration record** — the study's real 10-year 68°N, 110°W NASA POWER CSV.
- **NRCan** — 35 kWh/person/day demand standard and the 30% renewable benchmark behind the 40% screen.

## Files
| File | Role |
|---|---|
| `app.py` | Streamlit UI |
| `physics.py` | constants + FAO-56 solar geometry (shared) |
| `feasibility.py` | transparent scoring + verdict |
| `inference.py` | model loading, prediction, uncertainty, classification |
| `openmeteo.py` | primary live Open-Meteo (ERA5) client, caching, fallback |
| `nasa_power.py` | live NASA POWER client (cross-check) |
| `generate_training_data.py` | builds the NASA-calibrated circumpolar grid |
| `train_model.py` | trains and saves the surrogate + classifier |
| `models/` | `surrogate.joblib`, `feasibility_clf.joblib`, `metrics.json` |
| `data/` | training grid + per-location feasibility table |

## Limitations
The offline surrogate is calibrated from a single real point (68°N) propagated by solar
physics and climatology, not a full reanalysis — query a coordinate in live mode to use
real NASA data for that point. Feasibility is a screening signal: it omits grid
connection, demand beyond the per-person model, and regulatory / waste / decommissioning
factors. No point in the 50–84°N domain scores "Weak" — renewable insufficiency alone
guarantees at least a Conditional case, which is the study's central finding.

## Tech stack
Python · Streamlit · scikit-learn · pandas · numpy · matplotlib · requests · joblib.
