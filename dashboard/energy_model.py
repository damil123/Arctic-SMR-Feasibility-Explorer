"""
energy_model.py — Realistic hybrid energy + economics model.

Replaces the original fixed "1000 m^2 array + one turbine vs 1 MW" toy with a
scalable solar + wind + battery + baseload system sized to the community's actual
demand, run as a monthly energy balance. Produces the numbers a planner cares
about: achievable renewable penetration, residual firm-power need, cost vs diesel,
and CO2 avoided. Outputs vary by location and by system design, so the charts and
verdict respond to the queried point.

Resolution caveat: inputs are monthly climatology, so storage is modelled as
intra-month shifting (one cycle/day cap). Sub-daily effects are not resolved.
"""
from __future__ import annotations
import numpy as np
import physics as ph

HOURS = 24
DAYS_IN_MONTH = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

# PV / wind technical assumptions
PV_PERFORMANCE_RATIO = 0.75     # losses: inverter, soiling, snow, temperature
WIND_CUT_IN, WIND_RATED, WIND_CUT_OUT = 3.0, 12.0, 25.0  # m/s

# Default economics ($/MWh)
DIESEL_LCOE = 600.0     # remote Arctic diesel generation (~$0.60/kWh)
NUCLEAR_LCOE = 250.0    # micro-reactor estimate (~$0.25/kWh)
RENEW_LCOE = 90.0       # solar+wind+storage levelised in remote build
# Emissions (g CO2e/kWh -> t/MWh = value/1000)
CO2_DIESEL = 780.0
CO2_NUCLEAR = 20.0
CO2_RENEW = 15.0


def pv_generation_mwh(solar_kwh_m2_day, pv_kw, days):
    """Monthly PV energy (MWh). Peak-sun-hours = daily irradiance (kWh/m^2/day)."""
    return np.asarray(solar_kwh_m2_day) * pv_kw * PV_PERFORMANCE_RATIO * days / 1000.0


def wind_capacity_factor(v):
    """Capacity factor from monthly-mean wind speed via a simple power curve."""
    v = np.asarray(v, dtype=float)
    cf = np.where(
        v < WIND_CUT_IN, 0.0,
        np.where(v >= WIND_CUT_OUT, 0.0,
                 np.where(v >= WIND_RATED, 1.0,
                          (v ** 3 - WIND_CUT_IN ** 3) /
                          (WIND_RATED ** 3 - WIND_CUT_IN ** 3))))
    return np.clip(cf, 0.0, 1.0)


def wind_generation_mwh(wind_ms, wind_kw, days):
    """Monthly wind energy (MWh)."""
    return wind_capacity_factor(wind_ms) * wind_kw * HOURS * days / 1000.0


def simulate_hybrid(solar, wind, demand_mw, pv_kw, wind_kw, battery_mwh):
    """Monthly energy balance with simple storage shifting.

    Returns per-month MWh arrays and annual penetration / residual firm need.
    """
    solar, wind = np.asarray(solar), np.asarray(wind)
    days = DAYS_IN_MONTH
    load = demand_mw * HOURS * days                      # MWh/month
    pv = pv_generation_mwh(solar, pv_kw, days)
    wd = wind_generation_mwh(wind, wind_kw, days)
    gen = pv + wd

    direct = np.minimum(gen, load)
    surplus = gen - direct
    deficit = load - direct
    # storage shifts up to one cycle/day within the month
    storage_cap = battery_mwh * days
    storage_served = np.minimum(np.minimum(surplus, deficit), storage_cap)
    renewable_served = direct + storage_served
    firm_needed = load - renewable_served                # residual (diesel or nuclear)
    curtailed = gen - renewable_served

    return {
        'days': days, 'load_mwh': load, 'pv_mwh': pv, 'wind_mwh': wd,
        'renewable_served_mwh': renewable_served, 'storage_served_mwh': storage_served,
        'firm_needed_mwh': firm_needed, 'curtailed_mwh': curtailed,
        'annual_load_mwh': float(load.sum()),
        'annual_renewable_mwh': float(renewable_served.sum()),
        'annual_firm_mwh': float(firm_needed.sum()),
        'penetration': float(renewable_served.sum() / load.sum()),
        'worst_month_penetration': float((renewable_served / load).min()),
        'best_month_penetration': float((renewable_served / load).max()),
    }


def economics(sim, diesel_lcoe=DIESEL_LCOE, nuclear_lcoe=NUCLEAR_LCOE,
              renew_lcoe=RENEW_LCOE, co2_diesel=CO2_DIESEL,
              co2_nuclear=CO2_NUCLEAR, co2_renew=CO2_RENEW):
    """Annual cost ($M/yr) and CO2 (kt/yr) for the system options.

    cost ($) = energy (MWh) * lcoe ($/MWh);  /1e6 -> $M.
    CO2 (kt) = energy (MWh) * intensity (g/kWh) * 1000 (kWh/MWh) / 1e9.
    """
    load = sim['annual_load_mwh']
    renew = sim['annual_renewable_mwh']
    firm = sim['annual_firm_mwh']

    def M(x):
        return x / 1e6

    def kt(mwh, g_per_kwh):
        return mwh * g_per_kwh * 1000 / 1e9

    diesel_only = {'cost_m': M(load * diesel_lcoe), 'co2_kt': kt(load, co2_diesel)}
    hybrid_diesel = {'cost_m': M(renew * renew_lcoe + firm * diesel_lcoe),
                     'co2_kt': kt(renew, co2_renew) + kt(firm, co2_diesel)}
    nuclear = {'cost_m': M(load * nuclear_lcoe), 'co2_kt': kt(load, co2_nuclear)}
    hybrid_nuclear = {'cost_m': M(renew * renew_lcoe + firm * nuclear_lcoe),
                      'co2_kt': kt(renew, co2_renew) + kt(firm, co2_nuclear)}

    return {
        'diesel_only': diesel_only,
        'hybrid_diesel': hybrid_diesel,
        'nuclear': nuclear,
        'hybrid_nuclear': hybrid_nuclear,
        'best_option': min(
            [('Diesel only', diesel_only['cost_m']),
             ('Renewables + diesel backup', hybrid_diesel['cost_m']),
             ('Nuclear baseload', nuclear['cost_m']),
             ('Renewables + nuclear backup', hybrid_nuclear['cost_m'])],
            key=lambda t: t[1]),
        'diesel_saving_vs_nuclear_m': M(load * diesel_lcoe) - M(load * nuclear_lcoe),
        'co2_avoided_nuclear_kt': kt(load, co2_diesel) - kt(load, co2_nuclear),
    }
