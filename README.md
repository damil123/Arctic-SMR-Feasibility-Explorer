# Arctic Nuclear Necessity
### A Data-Driven Case for Micro-Reactors in Northern Canada

**Author:** Damil Randhawa
**Skills demonstrated:** Data Analysis · Energy Modelling · Risk Assessment · Technical Documentation · Stakeholder Reporting

---

## Overview

Five remote Northern Canadian communities are almost entirely dependent on diesel generation for electricity. That dependency creates three compounding problems:

| Problem | Magnitude |
|---|---|
| **Cost** | $0.62–0.68/kWh in Nunavut — four to six times the ~$0.10–0.15/kWh paid in southern Canada |
| **Emissions** | 780 g CO₂e/kWh  among the highest electricity carbon intensity in Canada |
| **Subsidy burden** | Federal and territorial diesel subsidies exceed $60M/year in Nunavut alone |
| **Logistics risk** | Diesel delivered by summer barge or winter road; supply chain disruption cuts power entirely |

This project answers one question using publicly available data: **Can renewables close the gap, and if not, what size micro-reactor does each community need?**

Using 10 years of NASA POWER satellite climate data (2015–2024) and Statistics Canada census figures, this analysis models what solar panels and wind turbines can actually produce at 68°N  representative of Nunavut and the Northwest Territories  compared to what communities need. The result: **solar and wind together never supply more than 7% of community demand in any month, across any year studied.** The gap does not close in summer. Nuclear is not a backup  it is the only viable primary power source at this latitude, year-round.

| Component | What It Does |
|---|---|
| 10-year NASA POWER climate analysis | Quantifies solar and wind potential month by month |
| RERS metric (original) | Determines whether renewables can meet demand at any point in the year |
| Reactor sizing model | Calculates micro-reactor capacity required per community |
| Economic & CO₂ comparison | Quantifies the financial and environmental case for switching from diesel to nuclear |
| 7-risk register | Identifies key risks with likelihood, impact scores, and mitigations |

---

## Key Findings

1. Solar and wind at 68°N supply between 3.5% and 6.9% of community demand depending on the month — never enough to serve as a primary power source in any season; this is a permanent physical feature of high-latitude geography, confirmed across 10 years of data
2. There is no combination of solar, wind, and battery storage that can bridge a 93–97% energy gap; nuclear baseload is not one option among several — it is the only viable option at this latitude
3. The Westinghouse eVinci (5 MWe, 8+ year refueling, transport-portable by truck or air) is the right technology for Arctic logistics: no year-round road access, all resupply by sealift or air, and annual diesel delivery now made obsolete
4. Resolute (1 eVinci unit, 0.34 MWe) is the lowest-risk first deployment; Inuvik (2 units) follows; Iqaluit (3 units) is the highest-visibility Nunavut market
5. Replacing diesel with nuclear saves a combined $66.9M/yr and avoids 295.5 kt of CO₂ emissions annually across four communities — more than Canada currently spends on Nunavut diesel subsidies in a year
6. Every Arctic SMR deployment builds engineering heritage applicable to defence forward operating bases and space surface power programmes

---

## Project Structure

```
arctic_project/
├── analysis.ipynb                    ← Main Jupyter notebook (run this first)
├── report.md                         ← Full technical report
├── project_log.md                    ← Project documentation and decision log
├── README.md                         ← This file
├── requirements.txt                  ← Python dependencies
├── data/
│   ├── nasa_power_arctic_68N_110W.csv   ← Climate dataset (10yr monthly, 120 records)
│   ├── arctic_communities.csv           ← 5 Arctic communities (StatsCan 2021)
│   ├── risk_register.csv               ← 7-risk energy supply register
│   ├── analysis_output.csv             ← RERS computed dataset
│   └── reactor_sizing.csv              ← Reactor sizing outputs by community
└── charts/
    ├── chart1_seasonal_energy_gap.png
    ├── chart2_rers_heatmap.png
    ├── chart3_reactor_sizing.png
    ├── chart4_risk_matrix.png
    └── chart5_economic_environmental.png
```

---

## How to Run

### 1. Clone & install dependencies
```bash
git clone https://github.com/YOURUSERNAME/csmc-arctic-nuclear.git
cd csmc-arctic-nuclear
pip install -r requirements.txt
```

### 2. Run the notebook
```bash
jupyter notebook analysis.ipynb
```
Run all cells top to bottom (Cell → Run All).

### 3. Optional: Download real NASA POWER data
```bash
curl "https://power.larc.nasa.gov/api/temporal/monthly/point\
?parameters=ALLSKY_SFC_SW_DWN,WS10M,T2M\
&community=RE&longitude=-110&latitude=68\
&start=20150101&end=20241231&format=CSV" \
-o data/nasa_power_real.csv
```
Then update the `pd.read_csv()` path in the notebook.

---

## Data Sources

| Dataset | Source | Access |
|---|---|---|
| Solar irradiance, wind speed, temperature (120 monthly records) | [NASA POWER API](https://power.larc.nasa.gov) | Free, no login |
| Arctic community populations | [Statistics Canada 2021 Census](https://statcan.gc.ca) | Open data |
| Arctic energy demand baseline (35 kWh/person/day) | [NRCan Arctic Energy](https://nrcan.gc.ca) | Public report |
| Risk framework | Standard 5×5 likelihood × impact matrix | Engineering standard |

---

## Assumptions & Limitations

| Parameter | Value | Rationale |
|---|---|---|
| Solar panel efficiency | 18% | Commercial monocrystalline silicon standard |
| Solar array size | 1,000 m² (~100 panels) | Illustrative — real sizing requires site survey |
| Wind turbine model | 500 kW simplified curve (P = 0.00015 × v³) | Real analysis would use manufacturer power curve |
| Winter demand | 35 kWh/person/day | NRCan documented Arctic community average |
| Safety margin | 30% | Standard nuclear/power engineering practice |
| Analysis location | 68°N, 110°W | Single point — multi-site analysis improves accuracy |
| High Arctic renewable floor | 0.039 MW | Data-derived: Nov–Feb 10yr average at 68°N, 110°W |
| Subarctic renewable floor | 0.20 MW | Estimated for ~60°N — not directly data-derived |
| Nuclear LCOE | $0.25/kWh | Conservative SMR remote deployment estimate |

**Key limitations:** single-coordinate climate analysis; simplified wind model (no terrain/icing probability); static demand model (no hourly/seasonal variation); no battery storage sizing.

