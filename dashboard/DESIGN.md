# Design — Arctic Micro-Reactor Feasibility Explorer

## 1. What changed and why
The original project was a fixed study of five named communities. This pivot turns
that logic into an **interactive tool that scores any Arctic/subarctic coordinate**
(50–84°N) for micro-reactor feasibility, backed by live NASA data and machine
learning. The energy physics (RERS, reactor sizing, the 40% threshold, the eVinci
5 MWe reference) is preserved exactly so results stay comparable to `analysis.ipynb`.

## 2. Architecture
```
User (lat/lon, optional population)
        │
        ▼
  nasa_power.py ──► live NASA POWER climatology API  (cached to dashboard/cache/)
        │  (on failure / "instant" mode)
        ▼
  inference.py ──► ML surrogate predicts 12-month solar/wind/temp + uncertainty
        │
        ▼
  feasibility.py ──► transparent score (renewable insufficiency + demand + siting)
        │            + verdict (Strong / Conditional / Weak)
        ▼
  inference.py ──► ML classifier cross-checks verdict, returns confidence
        │
        ▼
  app.py (Streamlit) ──► verdict banner, KPIs, charts, siting flags, reactor sizing, map
```
`physics.py` is the shared core (constants + solar geometry) imported everywhere.

## 3. Data strategy
The live POWER API serves one point per request, so a dense training grid can't be
built by API calls at runtime. The design uses two tiers:

- **Live tier (preferred):** at query time the app calls Open-Meteo (ERA5) for the exact
  coordinate (10-year monthly climatology), with NASA POWER as a cross-check; both cached on disk.
- **ML tier (fallback / instant):** a circumpolar training grid (50–84°N × every
  15° lon × 12 months = 5,184 samples) generated in `generate_training_data.py`,
  calibrated to the one real 10-year record we have (68°N, 110°W):
  - **Solar** is the physically exact top-of-atmosphere insolation (FAO-56 solar
    geometry, monthly-mean integrated) × a per-month clearness index derived from
    the real 68°N surface/TOA ratio. This makes solar correct at every latitude.
  - **Temperature** uses a latitude lapse (~1.1°C/°lat) + poleward-growing seasonal
    amplitude + a longitude continentality term, calibrated so 68°N reproduces the
    real monthly curve (Jan −32.8 vs real −32.7; Jul +12.4 vs real +12.7).
  - **Wind** is a calibrated climatology (winter-high, ~5 m/s) with a longitude term.
  Gaussian noise + the longitude terms give the ML real structure to learn.

## 4. Machine learning
- **Surrogate (RandomForestRegressor, multi-output):** `(lat, lon, sin month,
  cos month) → (solar, wind, temp)`. Held-out R²: solar 0.998, temp 0.994,
  wind 0.85. Lets the app score any coordinate instantly and offline, and yields a
  genuine **uncertainty band** from the spread across trees (wider away from the grid).
- **Feasibility classifier (RandomForestClassifier):** per-location annual features
  → {strong, conditional, weak}. Labels come from the transparent scoring rule, so
  the classifier *reproduces* that rule (held-out accuracy 1.0) — its job is a
  deployable model artifact and a **calibrated confidence** (class-probability spread
  near the Strong/Conditional boundary), not to replace the rule. The app shows both.

The surrogate is the substantive ML; the classifier is a confidence/cross-check layer.
This split is stated plainly rather than dressed up as a single black-box predictor.

## 5. Feasibility scoring (transparent, in feasibility.py)
Score 0–100 = weighted sum of three 0–1 components:

| Component | Weight | Definition |
|---|---|---|
| Renewable insufficiency | 0.45 | `(0.40 − best-month RERS) / 0.40` — strict test from the study |
| Climate demand pressure | 0.35 | `(8 − mean annual temp) / 38` — colder = higher load, deeper diesel reliance |
| Siting suitability | 0.20 | starts at 1, minus permafrost (MAAT<−8 / <−2) and extreme-cold (min<−45 / <−38) penalties |

Verdict: **Strong** ≥62, **Conditional** ≥48, **Weak** <48.

**Honest finding:** no point in the 50–84°N domain scores Weak — renewable
insufficiency alone (best-month RERS ~6–10% everywhere) sets a floor that keeps the
case at least Conditional. The verdict strengthens monotonically toward the pole.
The "Weak" band is kept on the scale but is effectively unreachable in-domain, which
is itself the study's core result: there is no Arctic location where renewables suffice.

## 6. File layout
```
dashboard/
├── app.py                     Streamlit UI
├── physics.py                 constants + FAO-56 solar geometry (shared)
├── feasibility.py             transparent scoring + verdict
├── inference.py               model loading, prediction, uncertainty, classification
├── nasa_power.py              live POWER client + disk cache + graceful fallback
├── generate_training_data.py  builds the calibrated circumpolar grid
├── train_model.py             trains + persists surrogate and classifier
├── requirements.txt
├── data/   arctic_climate_grid.csv, location_feasibility.csv
└── models/ surrogate.joblib, feasibility_clf.joblib, metrics.json
```

## 7. Limitations
Single real calibration point (68°N) propagated by physics + climatology, not a full
reanalysis dataset; clearness and wind are climatological, not site-measured.
Feasibility is a screening signal — it omits grid connection, demand beyond the
NRCan per-person model, regulatory/waste/decommissioning factors, and bathymetry/
transport access. The live NASA tier removes the climate-model assumption for any
specific point the user queries.

## Energy model & economics (energy_model.py)
The original RERS/1-MW comparison was a fixed toy (one array + one turbine), so every
location looked identical. `energy_model.py` replaces it with a scalable system sized to
the community's demand:
- **PV** from irradiance x capacity x performance ratio; **wind** from a power-curve
  capacity factor; **battery** shifts surplus to deficit (one cycle/day, monthly resolution).
- Outputs **renewable penetration**, worst-month (winter) penetration, and residual firm
  power - all of which vary by location and by the PV/wind/battery sliders.
- **Economics** compare four options (diesel only, renewables+diesel, nuclear baseload,
  renewables+nuclear) on $/yr and CO2, at user-set LCOEs. Typical result: a renewables+
  nuclear hybrid is cheapest, because renewables are cheap but winter forces firm baseload.

