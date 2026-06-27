"""
inference.py — Load the trained models and expose two clean calls for the app:

  predict_monthly(lat, lon)   -> 12-row DataFrame of surrogate solar/wind/temp
                                 plus per-prediction uncertainty (tree spread).
  classify_location(features) -> (label, probability_dict) from the classifier.

The surrogate's uncertainty is the standard deviation across the random-forest
trees: a genuine epistemic-uncertainty estimate, larger where the queried point
is far from the training grid.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import joblib

import physics as ph
import feasibility as fz

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, 'models')

_surrogate = None
_clf = None


def _load():
    global _surrogate, _clf
    if _surrogate is None:
        _surrogate = joblib.load(os.path.join(MODELS, 'surrogate.joblib'))
        _clf = joblib.load(os.path.join(MODELS, 'feasibility_clf.joblib'))
    return _surrogate, _clf


def predict_monthly(lat, lon):
    """Return a 12-month DataFrame of predicted climate + uncertainty bands."""
    rf, _ = _load()
    months = np.arange(1, 13)
    s, c = np.sin(2 * np.pi * months / 12), np.cos(2 * np.pi * months / 12)
    X = np.column_stack([np.full(12, lat), np.full(12, lon), s, c])
    # mean prediction
    pred = rf.predict(X)  # (12, 3): solar, wind, temp
    # tree spread for uncertainty
    per_tree = np.stack([est.predict(X) for est in rf.estimators_])  # (n_trees,12,3)
    std = per_tree.std(axis=0)
    df = pd.DataFrame({
        'month': months,
        'month_name': ph.MONTH_NAMES,
        'solar_kwh_m2_day': pred[:, 0].clip(min=0),
        'wind_ms': pred[:, 1].clip(min=0),
        'temp_c': pred[:, 2],
        'solar_std': std[:, 0],
        'temp_std': std[:, 2],
    })
    df['solar_mw'] = ph.solar_mw(df['solar_kwh_m2_day'])
    df['wind_mw'] = ph.wind_mw(df['wind_ms'])
    df['RERS'] = ph.rers(df['solar_kwh_m2_day'], df['wind_ms'])
    return df


def classify_location(monthly_df):
    """Run the feasibility classifier; return (label, proba dict, mean_uncertainty)."""
    _, clf = _load()
    agg = fz.annual_aggregates(monthly_df['solar_kwh_m2_day'].values,
                               monthly_df['wind_ms'].values,
                               monthly_df['temp_c'].values)
    feats = {'lat': monthly_df.attrs.get('lat', np.nan),
             'annual_solar': agg['annual_solar'], 'annual_wind': agg['annual_wind'],
             'annual_temp': agg['annual_temp'], 'winter_temp': agg['winter_temp'],
             'peak_rers': agg['peak_rers']}
    X = np.array([[feats[k] for k in fz.CLF_FEATURES]])
    label = clf.predict(X)[0]
    proba = dict(zip(clf.classes_, clf.predict_proba(X)[0].round(3)))
    return label, proba
