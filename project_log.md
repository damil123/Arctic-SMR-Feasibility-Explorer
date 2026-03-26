# Project Log — Arctic Nuclear Necessity
**Project:** Arctic Nuclear Necessity: A Data-Driven Case for Micro-Reactors
**Author:** Damil Randhawa
**Start Date:** March 6 2026
**Status:** Complete

---

## Objective

Five remote Northern Canadian communities depend almost entirely on diesel generation — at $0.62–0.68/kWh (four to six times southern Canadian rates), 780 g CO₂e/kWh, and over $60M/year in federal and territorial subsidies. Diesel is also delivered by summer barge or winter road, making supply chain disruptions a direct power security risk.

**Central question:** Can renewables close the gap, and if not, what size micro-reactor does each community need?

This project answers that question using publicly available data only (NASA POWER, Statistics Canada, NRCan). Deliverables: an original reliability metric (RERS), a reactor sizing model, a 7-risk register, and a diesel-vs-nuclear economic and CO₂ comparison.

---

## Decision Log

| Decision | Rationale | Date |
|---|---|---|
| Use NASA POWER as primary climate source | Standard reference for energy site assessment globally; free; covers Arctic latitudes with satellite data | Day 1 |
| Set analysis coordinate to 68°N, 110°W | Representative of NWT/Nunavut geography where remote diesel-dependent communities are concentrated | Day 1 |
| Define RERS threshold at 0.40 | RERS measures what fraction of community demand renewables can actually supply (0 = nothing, 1.0 = full coverage). Below 0.40 (40% coverage), the remaining gap is too large for batteries or demand management to close safely — a firm baseload source is required | Day 1 |
| Apply 30% safety margin to reactor sizing | Standard engineering practice for power systems design; aligns with nuclear engineering conventions | Day 2 |
| Use 35 kWh/person/day demand baseline | Sourced from NRCan documented Arctic community energy profiles; conservative but defensible | Day 2 |
| Include 7 risks in register | Covers energy, logistics, nuclear, geotechnical, regulatory, and social dimensions | Day 2 |
| Limit scope to 5 communities | Covers both High Arctic (3) and Subarctic (2) zones; statistically representative without over-scoping | Day 1 |
| Use Westinghouse eVinci as reference reactor | 5 MWe, 8+ year refueling, factory-fabricated; best available technology match for Arctic logistics constraints; CAD $27.2M federal investment confirms deployment pathway | Day 2 |
| Use $0.25/kWh as nuclear LCOE | Conservative mid-range estimate for small modular reactors in remote deployment; enables like-for-like comparison with diesel costs | Day 2 |

---

## Progress Checklist

### Setup
- [x] Python environment configured (pandas, numpy, matplotlib, seaborn, jupyter)
- [x] Project folder structure created
- [x] Data sources identified and documented

### Data
- [x] NASA POWER climate dataset — 120 monthly records (2015–2024) at 68°N, 110°W
- [x] Arctic communities reference table (5 communities, StatsCan 2021)
- [x] Risk register — 7 risks documented with mitigations and owners

### Analysis
- [x] RERS metric computed for all 120 records
- [x] Monthly averages calculated (annual average RERS: 0.051)
- [x] Nuclear-critical month classification applied (threshold 0.40) — all 12 months nuclear-critical across all 10 years
- [x] Reactor sizing model run for all 5 communities
- [x] eVinci unit count calculated per community
- [x] Economic analysis: diesel vs nuclear cost comparison for 4 communities
- [x] CO₂ avoidance calculated per community

### Visualizations
- [x] Chart 1: Seasonal energy gap (stacked area + baseline)
- [x] Chart 2: RERS heatmap (year × month)
- [x] Chart 3: Reactor sizing by community (horizontal bar)
- [x] Chart 4: Risk matrix (5×5 scatter)

### Documentation
- [x] Technical report (report.md)
- [x] Jupyter notebook with inline documentation (analysis.ipynb)
- [x] Risk register CSV (data/risk_register.csv)
- [x] README.md with GitHub instructions
- [x] This project log

---

## Key Findings

1. **Solar and wind cover 4–7% of community demand year-round — never enough** — at 68°N, the best renewable output in the entire 10-year dataset was 6.9% of demand (May 2020). In the darkest winter months it falls below 4%. Across all 120 monthly records, renewables never supply more than 10% of what communities need. The required threshold to avoid baseload dependency was set at 40%; the data never approaches it. RERS (Renewable Energy Reliability Score) formalizes this as a number between 0 and 1: the highest recorded value is 0.086; the lowest is 0.026; the annual average is 0.051
2. **Wind cannot fill the gap solar leaves** — winter wind at 6.1 m/s produces ~0.034 MW from a 500 kW turbine (3.4% of demand); temperatures of −30°C to −35.9°C (recorded Jan–Feb in dataset) trigger turbine blade icing below −30°C, cutting output further; even combined peak solar+wind in May produces only 0.069 MW per 1 MW of demand — 93% still unmet
3. **The gap is a physical feature of latitude, not a weather pattern** — RERS < 0.10 in all 12 months across all 10 years; year-to-year variation is minimal (full dataset range: 0.026–0.086); a bad year does not explain this; a bad decade does not explain this; it is geometry
4. **Resolute (208 people) needs 0.34 MWe — one eVinci unit** — smallest and lowest-complexity SMR deployment candidate; pure diesel-dependent today; recommended as first-mover pilot to generate real-world Arctic operational data
5. **The three highest-rated risks are all solved by nuclear, not introduced by it** — R-01 (polar night solar blackout, score 25/25), R-02 (wind turbine icing, 16/25), R-03 (diesel resupply disruption, 15/25); micro-reactor deployment eliminates all three; the eVinci's 8+ year refueling cycle specifically ends annual diesel logistics
6. **The economic case is clear** — replacing diesel with nuclear saves a combined $66.9M/yr and avoids 295.5 kt CO₂e/yr across four communities; Iqaluit alone saves $35.1M/yr — roughly equivalent to Canada's entire annual Nunavut diesel subsidy
7. **The same reactor serves Arctic, defence, and space** — the Westinghouse eVinci (5 MWe, 8+ year refueling, air-liftable) covers Arctic communities (0.34–14 MWe range), remote defence forward operating bases, and builds qualification heritage for NASA Fission Surface Power planetary applications

---

## Deployment Recommendation

Based on the analysis, the recommended deployment sequence is:

| Priority | Community | Reactor Need | eVinci Units | Rationale |
|---|---|---|---|---|
| 1st | Resolute, NU | 0.34 MWe | 1 | Lowest political/regulatory risk; pure diesel-dependent; pilot data transfers to all subsequent deployments |
| 2nd | Inuvik, NT | 6.10 MWe | 2 | Partial gas infrastructure reduces cold-start complexity; manageable scale |
| 3rd | Iqaluit, NU | 14.03 MWe | 3 | Largest Nunavut electricity market; highest strategic visibility as territorial capital; staged multi-unit deployment |

---

## Assumptions

- Single coordinate (68°N, 110°W) used for all climate analysis
- Solar array fixed at 1,000 m², 18% efficiency
- Wind turbine simplified power curve (500 kW): P = 0.00015 × v³
- Demand: 35 kWh/person/day (NRCan Arctic baseline)
- Safety margin: 30% (standard nuclear/power engineering)
- High Arctic renewable floor: 0.039 MW (data-derived: Nov–Feb 10yr average at 68°N, 110°W)
- Subarctic renewable floor: 0.20 MW (estimated for ~60°N — not directly data-derived)
- Nuclear LCOE: $0.25/kWh (conservative SMR remote deployment estimate)
- Reference reactor: Westinghouse eVinci at 5 MWe per unit

## Limitations

- Single-coordinate climate analysis; multi-site data would improve community-specific accuracy
- Simplified wind model does not account for terrain, turbulence, or icing probability
- Static demand model — no hourly or seasonal demand variation
- No battery storage sizing included
- Subarctic renewable floor is estimated, not data-derived
- Nuclear LCOE estimate is a mid-range assumption; actual project costs require detailed engineering

---

## Data Sources

| Source | URL | Access |
|---|---|---|
| NASA POWER | power.larc.nasa.gov | Free API |
| Statistics Canada Census 2021 | statcan.gc.ca | Open data |
| NRCan Arctic Energy | nrcan.gc.ca | Public report |
| Westinghouse eVinci specs | NRCan Strategic Innovation Fund announcement, 2024 | Public |
