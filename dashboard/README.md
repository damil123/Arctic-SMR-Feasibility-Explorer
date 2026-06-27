# Arctic Micro-Reactor Feasibility Explorer

An interactive tool that answers one question for **any location in the Arctic or
subarctic (50–84°N)**: can a community here realistically run on renewable energy, or
does the climate force a firm baseload — diesel today, or a small nuclear reactor? Type a
coordinate (or pick a community) and the app pulls a 10-year climate record for that exact
point, models a solar + wind + battery system sized to local demand, compares the cost and
carbon of diesel / nuclear / hybrid options, and returns a clear verdict with the numbers
behind it.

Built in Python with Streamlit and scikit-learn. Live climate data from NASA POWER and
Open-Meteo (ERA5), with a trained machine-learning model as an instant offline fallback.

---

## 1. The problem

Remote northern communities are largely off the main electricity grid and depend on diesel
generators fueled by an annual barge or winter-road delivery. That dependence is:

- **Expensive** — roughly $0.30–0.68/kWh for diesel generation, several times the
  ~$0.10–0.15/kWh paid in southern Canada.
- **High-emission** — about 720–780 g CO₂e per kWh, among the highest electricity carbon
  intensities anywhere.
- **A supply risk** — a single missed sealift can become an energy emergency.

The obvious question is whether solar and wind can replace diesel. This project tests that
against real climate data and finds that at high latitude they cannot do it alone — and
then quantifies what a nuclear or hybrid alternative would cost.

## 2. What the tool does

For any coordinate it produces, in seconds:

- A **feasibility verdict** — *Strong*, *Conditional*, or *Weak* case for a micro-reactor —
  with a 0–100 score and an independent machine-learning confidence estimate.
- **Climate KPIs** — best- and average-month renewable reliability, mean-annual and
  coldest-month temperature, and number of polar-night (zero-sun) months.
- An **energy-system analysis** — for a solar + wind + battery build you size with sliders:
  what share of annual demand renewables actually cover, how badly that collapses in winter,
  and how much firm power is still required.
- An **economic comparison** — annual cost ($M/yr) and CO₂ for four supply options (diesel
  only, renewables + diesel, nuclear baseload, renewables + nuclear) at cost assumptions you
  control, with the cheapest option flagged.
- **Reactor sizing** — recommended capacity in MWe and number of Westinghouse-eVinci-class
  units, plus the savings and CO₂ avoided versus diesel.
- **Siting flags** — permafrost and extreme-cold engineering cautions, and a map of the point.

## 3. Key findings

- **Renewables hit a hard ceiling at high latitude.** Under a strict reliability screen
  (a fixed reference build vs. demand), solar + wind never exceed ~7% of demand in the high
  Arctic, and the screen is failed in every month of every year — this is structural
  geography (polar night + low winter wind), not a bad-weather year.
- **A realistic, scaled build does much better — but winter still breaks it.** With a large
  solar + wind + battery system sized to the community, annual renewable penetration reaches
  ~30–50%, but the worst winter month drops to ~13%. Firm baseload is therefore unavoidable.
- **The cheapest answer is usually a hybrid.** Because renewables are cheap to run but can't
  cover winter, the least-cost option is typically **renewables + a small nuclear reactor**,
  not either one alone.
- **Feasibility strengthens toward the pole.** Every location in the 50–84°N domain scores
  at least *Conditional*; the high Arctic scores *Strong*. No location scores *Weak* —
  renewable insufficiency alone guarantees a baseline case.

## 4. How it works (pipeline)

```
coordinate ─▶ climate data ─▶ feasibility score ─▶ energy model ─▶ economics ─▶ verdict + charts
              (live or ML)     (transparent rule)    (PV+wind+      (4 options,
                                + ML confidence       battery)       cost & CO₂)
```

1. **Climate.** `openmeteo.py` fetches the Open-Meteo ERA5 archive for the exact lat/lon
   (cached on disk); `nasa_power.py` is a live cross-check. If both are unreachable, or you
   choose "instant" mode, `inference.py` predicts the climate with the ML surrogate. Every
   path returns the same 12-month schema (solar, wind, temperature), so the rest of the
   pipeline is source-agnostic.
2. **Feasibility score.** `feasibility.py` converts the climate into a transparent 0–100
   score and verdict (details in §6).
3. **Energy model.** `energy_model.py` sizes a solar + wind + battery system to demand and
   runs a monthly energy balance for achievable renewable penetration and residual firm
   power (details in §7).
4. **Economics.** The same module prices four supply options and computes CO₂.
5. **Presentation.** `app.py` (Streamlit) renders the verdict, KPIs, and location-responsive
   charts, with sidebar controls for the system design and cost assumptions.

## 5. Data sources

| Source | Provides | Access | Auth |
|---|---|---|---|
| **Open-Meteo (ERA5 reanalysis)** | Primary live climate: solar irradiance, wind speed, temperature | REST JSON (`archive-api.open-meteo.com`) | None |
| **NASA POWER** | Live cross-check + the calibration record for the ML grid | REST JSON (`power.larc.nasa.gov`) | None |
| **NRCan** | 35 kWh/person/day demand standard; 30% renewable benchmark behind the 40% screen | Public report | None |

The ML surrogate is trained on a circumpolar grid built from these sources (see §8 and
`DATA_SOURCES.md` for the full data roadmap, including permafrost, hub-height wind, and
sea-ice options).

## 6. The feasibility score

A transparent 0–100 score (in `feasibility.py`), a weighted sum of three components:

| Component | Weight | Meaning |
|---|---|---|
| Renewable insufficiency | 0.45 | How far the best month's renewable reliability (RERS) falls below the 40% "can renewables be primary?" threshold |
| Climate demand pressure | 0.35 | Colder mean-annual temperature → higher heating load and deeper diesel reliance |
| Siting suitability | 0.20 | Starts at 1.0, minus permafrost and extreme-cold engineering penalties |

**RERS** (Renewable Energy Reliability Score) is the share of a 1 MW reference demand that a
reference solar+wind build covers in a month. The **40% threshold** is the screen for whether
renewables can serve as primary power; it sits slightly above NRCan's 30% renewable
benchmark, so it's deliberately conservative. Verdict bands: **Strong** ≥ 62, **Conditional**
≥ 48, **Weak** < 48.

## 7. The energy model & economics

`energy_model.py` replaces a fixed toy comparison with a scalable, demand-sized system:

- **Solar PV** — monthly energy = irradiance (peak-sun-hours) × installed kW × performance
  ratio (0.75) × days.
- **Wind** — monthly energy from a power-curve capacity factor (cut-in 3 m/s, rated 12 m/s,
  cut-out 25 m/s) × installed kW.
- **Battery** — shifts surplus generation to deficit within the month (capped at one cycle
  per day; monthly-resolution approximation).
- **Outputs** — annual renewable penetration, worst-month (winter) penetration, residual
  firm energy, and curtailment.

**Economics** price four options on annual cost and CO₂ at user-set LCOEs (defaults: diesel
$600/MWh, nuclear $250/MWh, renewables+storage $90/MWh; CO₂ 780 / 20 / 15 g per kWh):
diesel only, renewables + diesel backup, nuclear baseload, and renewables + nuclear. The
cheapest is flagged. Reactor sizing uses a 5 MWe eVinci reference and a 30% safety margin.

## 8. Machine learning

Two models (in `models/`, trained by `train_model.py`):

- **Climate surrogate** — a multi-output `RandomForestRegressor` mapping
  `(latitude, longitude, sin month, cos month) → (solar, wind, temperature)`. Trained on a
  circumpolar grid (50–84°N × every 15° longitude × 12 months ≈ 5,200 samples). Held-out
  performance: **R² 0.998 solar, 0.994 temperature, 0.85 wind**. It lets the app score any
  coordinate instantly and offline, and reports a per-prediction **uncertainty band** from
  the spread across trees. The grid is built either from real Open-Meteo data
  (`generate_training_data.py --source openmeteo`) or from a physics-calibrated synthetic
  generator (FAO-56 solar geometry calibrated to the real 68°N NASA record).
- **Feasibility classifier** — a `RandomForestClassifier` over annual features that
  reproduces the scoring rule and supplies a **calibrated confidence** (class-probability
  spread near the Strong/Conditional boundary). Stated honestly: it cross-checks the
  transparent rule rather than replacing it. The surrogate is the substantive ML; the
  classifier is a confidence layer.

## 9. Using the app

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py          # or: python -m streamlit run app.py
```

The trained models ship with the repo, so that one command runs it (opens at
`http://localhost:8501`). To rebuild from scratch:

```bash
python generate_training_data.py            # synthetic, offline
python generate_training_data.py --source openmeteo   # real ERA5 grid (needs network)
python train_model.py
```

**Controls (sidebar):** reference community or custom lat/lon; climate source (Auto /
Open-Meteo / NASA POWER / ML); population (for demand and sizing); an *Energy system design*
panel (PV ×, wind ×, battery hours) and an *Economics* panel (diesel / nuclear / renewable
$/kWh). Charts and verdict update live.

**Try this:** compare **Resolute (74.7°N)** — Strong, deep winter, permafrost flags — with a
custom **52°N** point — Conditional, milder, fewer flags — then raise the PV slider and watch
penetration climb while the winter month stays low.

## 10. Project structure

| File | Role |
|---|---|
| `app.py` | Streamlit user interface |
| `physics.py` | Shared constants + FAO-56 solar geometry |
| `feasibility.py` | Transparent feasibility scoring + verdict |
| `energy_model.py` | Hybrid PV+wind+battery balance + LCOE/CO₂ economics |
| `inference.py` | Model loading, prediction, uncertainty, classification |
| `openmeteo.py` | Primary live Open-Meteo (ERA5) client, caching, fallback |
| `nasa_power.py` | Live NASA POWER client (cross-check) |
| `generate_training_data.py` | Builds the circumpolar training grid (real or synthetic) |
| `train_model.py` | Trains and saves the surrogate + classifier |
| `data/` | Training grid, per-location feasibility table, NASA calibration CSV |
| `models/` | `surrogate.joblib`, `feasibility_clf.joblib`, `metrics.json` |
| `DESIGN.md` | Architecture, ML rationale, scoring, limitations |
| `DATA_SOURCES.md` | Data sources implemented + recommended next |

## 11. Assumptions & limitations

- **Screening tool, not an engineering design.** Demand uses a per-person standard, the wind
  capacity factor is derived from monthly-mean speeds (not a full Weibull/hub-height model),
  and storage is modelled at monthly resolution (intra-day shifting is approximated).
- **Not modelled:** existing grid/hydro connections, regulatory licensing, spent-fuel and
  waste handling, decommissioning, Indigenous consultation, and financing — all of which
  matter for real deployment.
- **Climate fidelity.** Live mode uses real ERA5/NASA data for the queried point; the offline
  surrogate is calibrated from a single real record propagated by physics, so it is best for
  fast exploration rather than final figures.
- **The "Weak" band is effectively unreachable** in 50–84°N — renewable insufficiency alone
  floors every location at *Conditional*, which is itself the central finding.

## 12. Roadmap

Real-data grid + spatial cross-validation for the surrogate; NRCan Remote Communities Energy
Database for real demand and supervised diesel-dependence labels; Global Wind Atlas
(hub-height wind), Obu permafrost data, and NSIDC sea-ice (logistics) as added features. See
`DATA_SOURCES.md`.

## 13. Tech stack

Python · Streamlit · scikit-learn · pandas · NumPy · Matplotlib · Requests · Joblib.
