"""
train_model.py — Train and persist the two ML models behind the dashboard.

1. SURROGATE (RandomForestRegressor, multi-output)
   (lat, lon, sin month, cos month) -> (solar, wind, temp)
   Lets the app score ANY Arctic coordinate instantly and offline, and provides
   per-prediction uncertainty from the spread across trees.

2. FEASIBILITY CLASSIFIER (RandomForestClassifier)
   per-location annual features -> {strong, conditional, weak}
   Labels come from feasibility.score_location (transparent rule). The classifier
   learns a smooth, probabilistic decision surface over that rule and reports a
   confidence (max class probability). It generalises the rule; it does not
   replace it — the app shows both the rule score and the model's confidence.

Artifacts -> dashboard/models/{surrogate.joblib, feasibility_clf.joblib, metrics.json}
"""
from __future__ import annotations
import os, json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, f1_score
import joblib

import physics as ph
import feasibility as fz

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, 'data', 'arctic_climate_grid.csv')
MODELS = os.path.join(HERE, 'models')


def month_cyc(m):
    return np.sin(2 * np.pi * m / 12), np.cos(2 * np.pi * m / 12)


def train_surrogate(df):
    s, c = month_cyc(df['month'].values)
    X = np.column_stack([df['lat'], df['lon'], s, c])
    y = df[['solar_kwh_m2_day', 'wind_ms', 'temp_c']].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7)
    rf = RandomForestRegressor(n_estimators=200, max_depth=None,
                               min_samples_leaf=2, random_state=7, n_jobs=-1)
    rf.fit(Xtr, ytr)
    pred = rf.predict(Xte)
    metrics = {}
    for i, name in enumerate(['solar', 'wind', 'temp']):
        metrics[name] = {'r2': round(r2_score(yte[:, i], pred[:, i]), 4),
                         'mae': round(mean_absolute_error(yte[:, i], pred[:, i]), 4)}
    joblib.dump(rf, os.path.join(MODELS, 'surrogate.joblib'))
    return metrics


def build_location_table(df):
    """Collapse the monthly grid to one row per (lat, lon) with annual features
    and the rule-based feasibility label."""
    rows = []
    for (lat, lon), g in df.groupby(['lat', 'lon']):
        g = g.sort_values('month')
        res = fz.score_location(g.solar_kwh_m2_day.values, g.wind_ms.values, g.temp_c.values)
        rows.append({'lat': lat, 'lon': lon, **{k: res[k] for k in
                     ('annual_solar', 'annual_wind', 'annual_temp', 'winter_temp',
                      'peak_rers', 'score')},
                     'label': fz.verdict_class(res['score'])})
    return pd.DataFrame(rows)


def train_classifier(df):
    loc = build_location_table(df)
    X = loc[fz.CLF_FEATURES].values
    y = loc['label'].values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=7,
                                          stratify=y if loc['label'].nunique() > 1 else None)
    clf = RandomForestClassifier(n_estimators=300, max_depth=None,
                                 min_samples_leaf=2, random_state=7, n_jobs=-1)
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    metrics = {'accuracy': round(accuracy_score(yte, pred), 4),
               'f1_macro': round(f1_score(yte, pred, average='macro'), 4),
               'class_counts': loc['label'].value_counts().to_dict(),
               'classes': sorted(loc['label'].unique().tolist())}
    joblib.dump(clf, os.path.join(MODELS, 'feasibility_clf.joblib'))
    loc.to_csv(os.path.join(HERE, 'data', 'location_feasibility.csv'), index=False)
    return metrics


def main():
    os.makedirs(MODELS, exist_ok=True)
    df = pd.read_csv(GRID)
    print(f"Training on {len(df):,} monthly rows / {df[['lat','lon']].drop_duplicates().shape[0]} locations")
    sm = train_surrogate(df)
    cm = train_classifier(df)
    metrics = {'surrogate': sm, 'classifier': cm,
               'features_surrogate': ['lat', 'lon', 'sin_month', 'cos_month'],
               'features_classifier': fz.CLF_FEATURES}
    with open(os.path.join(MODELS, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    print("\nSurrogate R2/MAE:")
    for k, v in sm.items():
        print(f"  {k:6s} R2={v['r2']:.3f}  MAE={v['mae']:.3f}")
    print(f"\nClassifier accuracy={cm['accuracy']:.3f}  f1_macro={cm['f1_macro']:.3f}")
    print(f"  class balance: {cm['class_counts']}")
    print(f"\nSaved -> {MODELS}")


if __name__ == '__main__':
    main()
