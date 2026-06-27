"""
feasibility.py — Transparent feasibility scoring for a single Arctic location.

The verdict combines (per the chosen design):
  1. Renewable insufficiency  -> can solar+wind ever serve as primary power?
  2. Demand pressure          -> colder climate = higher load, deeper diesel reliance
  3. Siting suitability       -> permafrost + extreme-cold engineering penalties

Works on 12-element monthly arrays from EITHER the live NASA POWER API or the ML
surrogate, so the scoring is identical regardless of data source.
"""
from __future__ import annotations
import numpy as np
import physics as ph

# Verdict thresholds on the 0-100 score
STRONG, CONDITIONAL = 62.0, 48.0
# Component weights
W_NUCLEAR, W_DEMAND, W_SITING = 0.45, 0.35, 0.20


def annual_aggregates(solar, wind, temp):
    """Reduce 12 monthly values to the features scoring + the classifier use."""
    solar, wind, temp = map(np.asarray, (solar, wind, temp))
    monthly_rers = ph.rers(solar, wind)
    winter = [10, 11, 0, 1]  # Nov, Dec, Jan, Feb indices
    return {
        'annual_solar': float(solar.mean()),
        'annual_wind': float(wind.mean()),
        'annual_temp': float(temp.mean()),
        'winter_temp': float(temp[winter].mean()),
        'min_temp': float(temp.min()),
        'peak_rers': float(monthly_rers.max()),
        'annual_rers': float(monthly_rers.mean()),
        'polar_night_months': int((solar < 0.2).sum()),
        'monthly_rers': monthly_rers,
    }


def score_location(solar, wind, temp):
    """Return verdict dict for one location given 12 monthly solar/wind/temp."""
    a = annual_aggregates(solar, wind, temp)

    # 1. Renewable insufficiency — uses the BEST month (strict test from study)
    nuclear_just = float(np.clip(
        (ph.NUCLEAR_THRESHOLD - a['peak_rers']) / ph.NUCLEAR_THRESHOLD, 0, 1))

    # 2. Demand pressure — colder mean annual temp => stronger case
    demand = float(np.clip((-a['annual_temp'] + 8.0) / 38.0, 0, 1))

    # 3. Siting suitability — start at 1, subtract engineering penalties
    siting, flags = 1.0, []
    maat = a['annual_temp']
    if maat < -8:
        siting -= 0.25
        flags.append('Continuous permafrost likely (MAAT < -8 C) — thermosyphon foundation required')
    elif maat < -2:
        siting -= 0.12
        flags.append('Discontinuous permafrost (MAAT < -2 C) — geotechnical survey required')
    if a['min_temp'] < -45:
        siting -= 0.20
        flags.append(f"Extreme cold (min {a['min_temp']:.0f} C) — Arctic-rated materials needed")
    elif a['min_temp'] < -38:
        siting -= 0.10
        flags.append(f"Severe cold (min {a['min_temp']:.0f} C) — cold-weather hardening advised")
    if a['polar_night_months'] >= 1:
        flags.append(f"{a['polar_night_months']} polar-night month(s) — zero solar contribution")
    siting = float(np.clip(siting, 0, 1))

    score = 100.0 * (W_NUCLEAR * nuclear_just + W_DEMAND * demand + W_SITING * siting)
    if score >= STRONG:
        verdict = 'Strong case for micro-reactor'
    elif score >= CONDITIONAL:
        verdict = 'Conditional / site-dependent'
    else:
        verdict = 'Weak case'

    return {
        'score': round(score, 1),
        'verdict': verdict,
        'components': {
            'renewable_insufficiency': round(nuclear_just, 3),
            'demand_pressure': round(demand, 3),
            'siting_suitability': round(siting, 3),
        },
        'flags': flags,
        **{k: a[k] for k in ('annual_solar', 'annual_wind', 'annual_temp',
                             'winter_temp', 'min_temp', 'peak_rers',
                             'annual_rers', 'polar_night_months')},
    }


# Feature vector the classifier is trained on (order matters)
CLF_FEATURES = ['lat', 'annual_solar', 'annual_wind', 'annual_temp',
                'winter_temp', 'peak_rers']


def verdict_class(score):
    if score >= STRONG:
        return 'strong'
    if score >= CONDITIONAL:
        return 'conditional'
    return 'weak'
