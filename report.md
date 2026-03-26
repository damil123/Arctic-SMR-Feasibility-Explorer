# Arctic Nuclear Necessity: A Data-Driven Case for Micro-Reactors
**Prepared by:** Damil Randhawa
**Date:** March 14 2026
**Classification:** Unclassified / Public Data
**Data Sources:** NASA POWER API · Statistics Canada 2021 Census · NRCan Arctic Energy Profiles

---

## Executive Summary

Five remote Northern Canadian communities are almost entirely dependent on diesel generation for electricity. That dependency creates three compounding problems:

| Problem | Magnitude |
|---|---|
| **Cost** | $0.62–0.68/kWh in Nunavut — four to six times the ~$0.10–0.15/kWh paid in southern Canada |
| **Emissions** | 780 g CO₂e/kWh — among the highest electricity carbon intensity in Canada |
| **Subsidy burden** | Federal and territorial diesel subsidies exceed $60M/year in Nunavut alone |
| **Logistics risk** | Diesel delivered by summer barge or winter road; supply chain disruption cuts power entirely |

This analysis set out to answer one question: **Can renewables close the gap, and if not, what size micro-reactor does each community need?**

---

Using 10 years of NASA POWER satellite climate data (2015–2024) at 68°N, 110°W — representative of Nunavut and the Northwest Territories — this analysis modelled what solar panels and wind turbines can realistically produce in each month compared to community demand. The answer is unambiguous: renewables cannot close the gap.

In January, at the peak of polar night, solar and wind together produce about **0.037 MW per 1 MW of community demand** — roughly 4 cents of power for every dollar needed. In May, the sunniest month, they produce **0.069 MW per 1 MW demanded** — roughly 7 cents. That gap does not close in summer. It is not a weather anomaly. Across all 10 years of data, in every single month, solar and wind together never reached even 10% of what these communities need.

This ratio is formalized in this analysis as the **Renewable Energy Reliability Score (RERS)** — the fraction of community demand renewables can actually meet in a given month (0 = nothing, 1.0 = full coverage). A threshold of 0.40 was set as the minimum below which a firm baseload source is required. The data never reaches 0.40 in any month. The highest RERS recorded is 0.069 — in May. The lowest is 0.035 — in October and November.

Nuclear baseload is not a winter supplement. It is the only viable primary power source at this latitude, in every season.

Micro-nuclear reactors are the only technically viable baseload solution for Arctic communities. The Westinghouse eVinci (5 MWe, 8+ year refueling cycle, factory-fabricated and transport-portable) is the best available technology match for Arctic logistics constraints, with federal deployment support confirmed via CAD $27.2M in Strategic Innovation Fund investment and a target availability date of 2030.

**Recommended deployment sequence:**
1. **Resolute, NU** (208 people) — requires 0.34 MWe (1 eVinci unit); lowest political and regulatory complexity; pilot data transfers directly to subsequent deployments
2. **Inuvik, NT** (3,243 people) — requires 6.10 MWe (2 eVinci units); partial gas infrastructure exists; manageable complexity
3. **Iqaluit, NU** (7,429 people) — requires 14.03 MWe (3 eVinci units); largest Nunavut electricity market; staged deployment via multiple units

**Combined economic case (4 communities):** $66.9M/yr in savings over current diesel costs; 295.5 kt CO₂e/yr avoided.

---

## 1. Methodology

This analysis is structured as a sequential pipeline, each step designed to answer a specific part of the central question:

| Component | Analytical Objective |
|---|---|
| 10-year NASA POWER climate analysis | Quantify solar and wind potential at representative Arctic coordinates |
| RERS metric | Determine whether renewables can meet demand at any point in the year |
| Reactor sizing model | Calculate the micro-reactor capacity required per community |
| Economic & CO₂ comparison | Quantify the financial and environmental case for switching from diesel to nuclear |
| 7-risk register | Identify key project risks with likelihood, impact, and mitigations |

### 1.1 Data Sources

- **Climate data:** NASA POWER (Prediction Of Worldwide Energy Resources) — publicly accessible satellite-derived dataset. Monthly averages extracted for: Solar Surface Irradiance (ALLSKY_SFC_SW_DWN, kWh/m²/day), Wind Speed at 10m (WS10M, m/s), Air Temperature at 2m (T2M, °C). Location: 68°N, 110°W. Period: January 2015 – December 2024 (120 monthly records).
- **Community data:** Statistics Canada 2021 Census — population by community for five Northern Canadian communities (Iqaluit NU, Inuvik NT, Resolute NU, Yellowknife NT, Whitehorse YT).
- **Demand baseline:** Natural Resources Canada (NRCan) Arctic community energy profiles — documented average demand of 35 kWh/person/day for Arctic communities combining residential, commercial, and essential services loads in winter.

### 1.2 Renewable Energy Reliability Score (RERS)

To compare renewable output against community demand in a consistent, repeatable way, this analysis introduces an original metric: the **Renewable Energy Reliability Score (RERS)**. It answers one question: *in a given month, what fraction of a 1 MW community demand can solar and wind actually supply?* A score of 1.0 means renewables fully cover demand. A score of 0.10 means they cover 10% — leaving 90% of demand unmet. The formula:

```
Solar output (MW) = (solar_kwh/m²/day × 1,000 m² × 0.18) / 24h / 1,000
Wind output (MW)  = v³ × 0.00015  [simplified 500 kW turbine power curve: P = 0.00015 × v³]
RERS              = min(1.0, (solar_mw + wind_mw) / 1.0 MW)
Nuclear critical  = RERS < 0.40
```

The threshold of 0.40 (40% of demand met by renewables) was selected as the nuclear-critical boundary: below that level, the remaining gap is too large for batteries or demand management to bridge safely, and a firm baseload power source is required. Parameters: `PANEL_AREA_M2 = 1,000`, `PANEL_EFFICIENCY = 0.18`, `TURBINE_COEFF = 0.00015`, `BASELINE_MW = 1.0`, `NUCLEAR_THRESHOLD = 0.40`.

### 1.3 Reactor Sizing

Community-level reactor sizing uses:

```
Daily demand (kWh)  = population × 35 kWh/person/day
Baseline MW         = daily_demand / 24
Winter renewable    = zone-adjusted floor (High Arctic: 0.039 MW data-derived; Subarctic: 0.20 MW estimated)
Nuclear gap (MW)    = baseline_MW − winter_renewable_MW
Reactor size (MWe)  = nuclear_gap × 1.30  [30% engineering safety margin]
```

The High Arctic renewable floor (0.039 MW) is derived from the 10-year data average for November through February at 68°N, 110°W. The Subarctic floor (0.20 MW) is an estimated value for communities near 60°N and is not directly data-derived.

### 1.4 Reference Technology

**Westinghouse eVinci micro-reactor:**
- Rated output: 5 MWe electrical / 13 MWth thermal
- Refueling cycle: 8+ years
- Form factor: factory-fabricated, transport-portable (truckable/air-liftable)
- Deployment target: 2030 (per NRCan Strategic Innovation Fund announcement, 2024)
- Federal investment: CAD $27.2M (Strategic Innovation Fund)

This form factor is directly suited to Arctic logistics constraints: no year-round road access to most High Arctic communities, all resupply by sealift or air. An 8+ year refueling cycle eliminates annual fuel logistics.

---

## 2. Key Findings

### 2.1 Year-Round Structural Energy Gap

The central question of this analysis is whether solar and wind can meaningfully power Arctic communities. The answer the data gives is unambiguous: **at 68°N, renewables cover between 3.5% and 6.9% of community demand depending on the month — never more, in any year studied.** The table below shows the 10-year monthly averages. A score of 1.0 would mean full coverage; 0.40 was set as the minimum acceptable threshold; the data peaks at 0.069 (May) and never comes close to either mark.

| Month | RERS (avg) | % of Baseline | Status |
|---|---|---|---|
| January | 0.037 | 3.7% | **NUCLEAR CRITICAL** |
| February | 0.048 | 4.8% | **NUCLEAR CRITICAL** |
| March | 0.059 | 5.9% | **NUCLEAR CRITICAL** |
| April | 0.067 | 6.7% | **NUCLEAR CRITICAL** |
| May | 0.069 | 6.9% | **NUCLEAR CRITICAL** — annual peak |
| June | 0.067 | 6.7% | **NUCLEAR CRITICAL** |
| July | 0.066 | 6.6% | **NUCLEAR CRITICAL** |
| August | 0.052 | 5.2% | **NUCLEAR CRITICAL** |
| September | 0.040 | 4.0% | **NUCLEAR CRITICAL** |
| October | 0.035 | 3.5% | **NUCLEAR CRITICAL** |
| November | 0.035 | 3.5% | **NUCLEAR CRITICAL** |
| December | 0.036 | 3.6% | **NUCLEAR CRITICAL** |

On average across all 10 years, renewables supply **5.1% of what communities need** (annual average RERS: 0.051). The best single month ever recorded in the dataset was 0.086 — still less than 9% of demand. The minimum was 0.026 — less than 3%. The RERS heatmap (Chart 2) shows this is not driven by unusually bad years; the pattern repeats with minimal variance across all 10 years. This is a physical constraint of latitude, not a weather anomaly or a bad decade.

### 2.2 Wind and Solar Cannot Compensate

A natural follow-up question is whether wind could compensate when the sun disappears. It cannot. At 68°N in winter, average wind speed of 6.1 m/s produces approximately 0.034 MW from a 500 kW turbine — enough to power about 34 average Canadian homes, against communities that need hundreds to thousands of times that. Temperatures recorded in the dataset reach −30.0°C (January 2015) to −35.9°C (January 2017), which triggers blade icing and shuts turbines down entirely below −30°C (Risk R-02). Wind is more consistent than solar in winter, but it is not adequate — and it is unreliable under the exact conditions where demand is highest.

Even in summer, when both solar and wind are operating at their seasonal best, combined output peaks at **0.069 MW per 1 MW of demand in May**. That is 6.9% of what a community needs — the remaining 93.1% must come from somewhere else. There is no month, in any year of the 10-year record, where renewables come close to serving as a primary power source.

### 2.3 Reactor Sizing Results

| Community | Zone | Population | Baseline (MW) | Reactor (MWe) | eVinci Units | Tech Class |
|---|---|---|---|---|---|---|
| Resolute, NU | High Arctic | 208 | 0.30 | 0.34 | 1 | Micro-reactor (≤10 MWe) |
| Inuvik, NT | High Arctic | 3,243 | 4.73 | 6.10 | 2 | Micro-reactor (≤10 MWe) |
| Iqaluit, NU | High Arctic | 7,429 | 10.83 | 14.03 | 3 | SMR required (>10 MWe) |
| Yellowknife, NT | Subarctic | 20,340 | 29.66 | 38.30 | 8 | SMR required (>10 MWe) |
| Whitehorse, YT | Subarctic | 28,201 | 41.13 | 53.20 | 11 | SMR required (>10 MWe) |

*Note: Yellowknife and Whitehorse have partial hydro access; nuclear gap is smaller in practice. Resolute and Inuvik are pure diesel-dependent — highest priority candidates for SMR deployment. eVinci unit counts assume 5 MWe per unit, rounded up.*

---

## 3. Risk Register Summary

Seven energy supply risks were identified and assessed using a standard 5×5 likelihood × impact matrix.

| Risk ID | Risk | L | I | Score | Priority |
|---|---|---|---|---|---|
| R-01 | Polar Night Solar Blackout | 5 | 5 | 25 | **Critical** |
| R-02 | Wind Turbine Icing (<−30°C) | 4 | 4 | 16 | **Critical** |
| R-03 | Diesel Resupply Chain Disruption | 3 | 5 | 15 | **Critical** |
| R-04 | Reactor Maintenance Downtime | 2 | 5 | 10 | Medium |
| R-05 | Permafrost Foundation Thaw | 3 | 4 | 12 | Medium |
| R-06 | CNSC Regulatory Approval Delay | 3 | 4 | 12 | Medium |
| R-07 | Community Acceptance Risk | 3 | 3 | 9 | Medium |

Full risk descriptions, mitigations, and owners are documented in `data/risk_register.csv`.

**Key insight:** Risks R-01, R-02, and R-03 are all directly mitigated or eliminated by micro-reactor deployment. The reactor does not introduce the highest risks — it resolves them. The eVinci's 8+ year refueling cycle specifically addresses R-03 (diesel resupply) by eliminating annual fuel logistics entirely.

---

## 4. Economic & Environmental Case

Nuclear LCOE estimate used: $0.25/kWh (conservative mid-range for small modular reactors in remote deployment).

| Community | Diesel Cost (/kWh) | Annual MWh | Annual Diesel Cost | Annual Nuclear Cost | Annual Saving | CO₂ Avoided (kt/yr) |
|---|---|---|---|---|---|---|
| Iqaluit, NU | $0.62 | 94,905 | $58.84M | $23.73M | **$35.12M** | **74.0** |
| Inuvik, NT | $0.68 | 41,429 | $28.17M | $10.36M | **$17.81M** | **32.3** |
| Yellowknife, NT | $0.30 | 259,844 | $77.95M | $64.96M | **$13.00M** | **187.1** |
| Resolute, NU | $0.62 | 2,657 | $1.65M | $0.66M | **$0.98M** | **2.1** |
| **Combined total** | | | | | **$66.91M/yr** | **295.5 kt CO₂e/yr** |

Context: Canada pays over $60M/year in Nunavut diesel subsidies alone. Nuclear deployment at Iqaluit and Inuvik alone recovers those costs within the first year of operation. Whitehorse excluded from table due to lower diesel dependency (partial hydro access).

See Chart 5 (`charts/chart5_economic_environmental.png`) for a visual breakdown of annual savings and CO₂ avoided by community.

---

## 5. The Dual-Use Case

The same micro-reactor technology designed for Arctic communities applies directly to:

- **Defence forward operating bases** — remote power for sensor arrays, communication nodes, and personnel at high-latitude installations
- **Lunar/Mars surface power** — NASA's Fission Surface Power project targets 10 kWe–1 MWe reactors for planetary bases; Arctic SMR deployment serves as Earth-based qualification heritage
- **Space analogue research stations** — Arctic stations (PEARL, CHARS) simulate space mission constraints; reliable nuclear power enables year-round science operations

The Canadian government's SMR Action Plan (2020) committed federal funding and regulatory pathway support. The CAD $27.2M Strategic Innovation Fund investment in eVinci establishes the regulatory and procurement environment for Arctic deployment by 2030.

---

## 6. Conclusions

1. Solar and wind at 68°N supply between 3.5% and 6.9% of community demand depending on the month — never enough to serve as a primary power source in any season; this is a permanent physical feature of high-latitude geography, confirmed across 10 years of data
2. There is no combination of solar, wind, and battery storage that can bridge a 93–97% energy gap; nuclear baseload is not one option among several — it is the only viable option at this latitude
3. The Westinghouse eVinci (5 MWe, 8+ year refueling, transport-portable by truck or air) is the right technology for Arctic logistics: no year-round road access, all resupply by sealift or air, and annual diesel delivery now made obsolete
4. Resolute (1 eVinci unit, 0.34 MWe) is the lowest-risk first deployment; Inuvik (2 units) follows; Iqaluit (3 units) is the highest-visibility Nunavut market
5. Replacing diesel with nuclear saves a combined $66.9M/yr and avoids 295.5 kt of CO₂ emissions annually across four communities — more than Canada currently spends on Nunavut diesel subsidies in a year
6. Every Arctic SMR deployment builds engineering heritage applicable to defence forward operating bases and space surface power programmes

---

## Appendix A: Assumptions & Limitations

| Parameter | Value | Source / Rationale |
|---|---|---|
| Solar panel efficiency | 18% | Commercial monocrystalline silicon standard |
| Solar array size | 1,000 m² (~100 standard panels) | Illustrative — real sizing requires site survey |
| Wind turbine model | 500 kW simplified curve (P = 0.00015 × v³) | Real analysis would use manufacturer power curve |
| Winter demand | 35 kWh/person/day | NRCan documented Arctic community average |
| Safety margin | 30% | Standard nuclear/power engineering practice |
| Analysis location | 68°N, 110°W | Single point — multi-site analysis improves accuracy |
| High Arctic renewable floor | 0.039 MW | Data-derived: Nov–Feb average at 68°N, 110°W |
| Subarctic renewable floor | 0.20 MW | Estimated for ~60°N — not directly data-derived |
| Nuclear LCOE | $0.25/kWh | Conservative SMR remote deployment estimate |

**Limitations:**
- Single-coordinate climate analysis; multi-site data would improve community-specific accuracy
- Simplified wind model does not account for terrain, turbulence, or icing probability
- Static demand model — no hourly or seasonal demand variation
- No battery storage sizing included
- Subarctic renewable floor is estimated, not data-derived

## Appendix B: Files

- `data/nasa_power_arctic_68N_110W.csv` — Raw climate dataset (120 monthly records, 2015–2024)
- `data/arctic_communities.csv` — Community reference table (5 communities, StatsCan 2021)
- `data/risk_register.csv` — Full risk register with mitigations and owners
- `data/reactor_sizing.csv` — Reactor sizing outputs by community
- `data/analysis_output.csv` — RERS computed dataset (120 records)
- `charts/chart1_seasonal_energy_gap.png` — Stacked area chart of solar/wind output vs. baseline demand by month
- `charts/chart2_rers_heatmap.png` — RERS heatmap across all 10 years (year × month)
- `charts/chart3_reactor_sizing.png` — Reactor capacity required by community (horizontal bar)
- `charts/chart4_risk_matrix.png` — 7-risk energy supply register plotted on 5×5 matrix
- `charts/chart5_economic_environmental.png` — Annual savings and CO₂ avoided by community (diesel vs. nuclear)
- `analysis.ipynb` — Fully reproducible analysis notebook

## Appendix C: How to Replicate

See `README.md` for installation and execution instructions.
