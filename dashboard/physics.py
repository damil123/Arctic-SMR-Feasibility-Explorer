"""
physics.py — Shared physical models and constants.

Two jobs:
1. Hold the energy constants used by the original feasibility study so the
   dashboard's RERS/sizing math is identical to analysis.ipynb.
2. Provide a solar-geometry model (FAO-56 extraterrestrial radiation) used to
   generate a physically-grounded training climatology for the ML surrogate.

All functions are pure and vectorised-friendly (accept floats or numpy arrays).
"""
from __future__ import annotations
import numpy as np

# Energy model constants (identical to analysis.ipynb)
PANEL_AREA_M2 = 1000      # solar array area, m^2 (~100 panels)
PANEL_EFFICIENCY = 0.18   # commercial monocrystalline silicon
TURBINE_COEFF = 0.00015   # P = TURBINE_COEFF * v^3 (MW), 500 kW-class turbine
TURBINE_RATED_MW = 0.5    # rated cap the original notebook omitted; applied here
BASELINE_MW = 1.0         # 1 MWe reference demand (smallest eVinci unit)
NUCLEAR_THRESHOLD = 0.40  # RERS below this => renewables cannot be primary power
SAFETY_MARGIN = 1.30      # 30% engineering margin on reactor sizing
KWH_PER_PERSON_DAY = 35   # NRCan Arctic community demand standard
EVINCI_MW = 5.0           # Westinghouse eVinci unit size

GSC = 0.0820             # solar constant, MJ / m^2 / min (FAO-56)

# Representative mid-month day-of-year (non-leap)
MONTH_DOY = np.array([16, 45, 75, 105, 136, 166, 197, 228, 259, 289, 320, 350])
_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_MONTH_START = np.cumsum([1] + _MONTH_DAYS[:-1])
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def extraterrestrial_kwh(lat_deg, doy):
    """Daily top-of-atmosphere solar radiation (kWh/m^2/day) via FAO-56.
    Handles polar night (sunset angle 0) and midnight sun (pi)."""
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    decl = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    x = np.clip(-np.tan(phi) * np.tan(decl), -1.0, 1.0)
    ws = np.arccos(x)
    ra_mj = (24 * 60 / np.pi) * GSC * dr * (
        ws * np.sin(phi) * np.sin(decl) + np.cos(phi) * np.cos(decl) * np.sin(ws))
    ra_mj = np.maximum(ra_mj, 0.0)
    return ra_mj / 3.6


def monthly_mean_toa(lat_deg, month):
    """Monthly-mean daily TOA radiation (kWh/m^2/day), averaged over the month's
    days. More accurate than a single mid-month day, especially near equinox."""
    start = _MONTH_START[month - 1]
    days = np.arange(start, start + _MONTH_DAYS[month - 1])
    return float(np.mean(extraterrestrial_kwh(lat_deg, days)))


def solar_mw(solar_kwh_m2_day):
    """Average solar power from the reference array, MW."""
    return (np.asarray(solar_kwh_m2_day) * PANEL_AREA_M2 * PANEL_EFFICIENCY) / 24 / 1000


def wind_mw(wind_ms):
    """Average wind power from the reference turbine, MW (rated-capped)."""
    p = np.asarray(wind_ms) ** 3 * TURBINE_COEFF
    return np.minimum(p, TURBINE_RATED_MW)


def rers(solar_kwh_m2_day, wind_ms):
    """Renewable Energy Reliability Score, clipped 0..1, vs 1 MW baseline."""
    renew = solar_mw(solar_kwh_m2_day) + wind_mw(wind_ms)
    return np.clip(renew / BASELINE_MW, 0.0, 1.0)


def demand_mw(population):
    """Average community load, MW, at the NRCan per-person standard."""
    return population * KWH_PER_PERSON_DAY / 24 / 1000


def size_reactor(demand_mw_value, renewable_floor_mw):
    """Recommended reactor size (MWe) and eVinci unit count for a demand."""
    gap = max(demand_mw_value - renewable_floor_mw, 0.0)
    reactor = round(gap * SAFETY_MARGIN, 2)
    units = int(np.ceil(reactor / EVINCI_MW)) if reactor > 0 else 0
    cls = 'Micro-reactor (<=10 MWe)' if reactor <= 10 else 'SMR (>10 MWe)'
    return {'gap_mw': round(gap, 2), 'reactor_mw': reactor,
            'evinci_units': units, 'tech_class': cls}
