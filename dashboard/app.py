"""
app.py — Arctic Micro-Reactor Feasibility Explorer (Streamlit).

Enter any Arctic / subarctic coordinate (or pick a community). The app pulls a
10-year monthly climatology for that point — Open-Meteo (ERA5) first, NASA POWER
as a cross-check, and a trained ML surrogate if both are unreachable — scores
micro-reactor feasibility, and explains the verdict with charts, siting flags,
and an ML confidence estimate.

Run:  streamlit run app.py
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

import physics as ph
import feasibility as fz
import inference as inf
import nasa_power as npw
import openmeteo as om

st.set_page_config(page_title='Arctic Micro-Reactor Feasibility',
                   page_icon='*', layout='wide')

# ── Theme ────────────────────────────────────────────────────────────────────
DARK, PANEL, ACCENT = '#0A0E14', '#0F1820', '#60D5F5'
RED, AMBER, GREEN = '#FF4D4D', '#F5A623', '#C8F560'
plt.rcParams.update({
    'figure.facecolor': DARK, 'axes.facecolor': DARK, 'savefig.facecolor': DARK,
    'text.color': '#DDE3EE', 'axes.labelcolor': '#8899AA',
    'xtick.color': '#8899AA', 'ytick.color': '#8899AA', 'axes.edgecolor': '#33414F',
})
st.markdown(f"""<style>
.stApp {{ background:{DARK}; }}
.verdict {{ padding:18px 22px; border-radius:12px; font-size:24px; font-weight:700;
            margin-bottom:6px; }}
.sub {{ color:#8899AA; font-size:14px; }}
</style>""", unsafe_allow_html=True)

VERDICT_COLOR = {'Strong case for micro-reactor': GREEN,
                 'Conditional / site-dependent': AMBER, 'Weak case': RED}

PRESETS = {
    'Custom (enter below)': (74.0, -95.0),
    'Resolute, NU': (74.69, -94.97),
    'Iqaluit, NU': (63.75, -68.51),
    'Inuvik, NT': (68.36, -133.72),
    'Yellowknife, NT': (62.45, -114.37),
    'Whitehorse, YT': (60.72, -135.05),
    'Utqiagvik (Barrow), AK': (71.29, -156.79),
    'Longyearbyen, Svalbard': (78.22, 15.65),
    'Nuuk, Greenland': (64.18, -51.69),
}

SRC_AUTO = 'Auto (Open-Meteo -> NASA -> ML)'
SRC_OM = 'Open-Meteo (ERA5, live)'
SRC_NASA = 'NASA POWER (live)'
SRC_ML = 'ML surrogate (instant)'


@st.cache_resource
def warm_models():
    inf._load()
    return True


def _finalize(d):
    d = d.copy()
    d['month_name'] = ph.MONTH_NAMES
    d['solar_mw'] = ph.solar_mw(d['solar_kwh_m2_day'])
    d['wind_mw'] = ph.wind_mw(d['wind_ms'])
    d['RERS'] = ph.rers(d['solar_kwh_m2_day'], d['wind_ms'])
    return d


@st.cache_data(show_spinner=False)
def get_climate(lat, lon, source):
    """Return (DataFrame, source_label) with per-month solar/wind/temp + derived
    solar_mw/wind_mw/RERS. Tries live sources per selection, falls back to ML."""
    df, used = None, None
    if source in (SRC_AUTO, SRC_OM):
        d = om.fetch_climatology(lat, lon)
        if d is not None:
            df, used = _finalize(d), 'Open-Meteo ERA5 (live, 2015-2024)'
    if df is None and source in (SRC_AUTO, SRC_NASA):
        d = npw.fetch_climatology(lat, lon)
        if d is not None:
            df, used = _finalize(d), 'NASA POWER (live, 2015-2024)'
    if df is None:
        df = inf.predict_monthly(lat, lon)
        used = ('ML surrogate (live API unreachable)'
                if source in (SRC_OM, SRC_NASA) else 'ML surrogate (NASA-calibrated grid)')
    df.attrs['lat'] = lat
    return df, used


warm_models()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title('* Site selector')
preset = st.sidebar.selectbox('Reference community', list(PRESETS.keys()))
plat, plon = PRESETS[preset]
lat = st.sidebar.number_input('Latitude (deg N)', 50.0, 84.0, float(plat), 0.1)
lon = st.sidebar.number_input('Longitude (deg E, west = negative)', -180.0, 180.0, float(plon), 0.1)
source = st.sidebar.radio('Climate data source', [SRC_AUTO, SRC_OM, SRC_NASA, SRC_ML])
pop = st.sidebar.number_input('Community population (optional - for reactor sizing)',
                              0, 200000, 0, 50)
st.sidebar.caption('Domain: 50-84 deg N. Live data from Open-Meteo (ERA5) or NASA POWER; '
                   'the ML surrogate (calibrated to NASA POWER) is the instant/offline fallback.')

# ── Compute ──────────────────────────────────────────────────────────────────
df, used = get_climate(round(lat, 2), round(lon, 2), source)
res = fz.score_location(df['solar_kwh_m2_day'].values, df['wind_ms'].values, df['temp_c'].values)
clf_label, clf_proba = inf.classify_location(df)
clf_conf = max(clf_proba.values())

# ── Header + verdict ─────────────────────────────────────────────────────────
st.title('Arctic Micro-Reactor Feasibility Explorer')
st.markdown('<span class="sub">Can a community at this coordinate rely on renewables - '
            'or does the climate force a nuclear baseload? Real climate data + ML scoring.</span>',
            unsafe_allow_html=True)

color = VERDICT_COLOR[res['verdict']]
st.markdown(
    f'<div class="verdict" style="background:{PANEL};border-left:8px solid {color};color:{color}">'
    f'{res["verdict"]} &nbsp;-&nbsp; feasibility score {res["score"]}/100</div>'
    f'<span class="sub">ML classifier agrees: <b>{clf_label}</b> '
    f'(confidence {clf_conf*100:.0f}%) &nbsp;|&nbsp; data: {used}</span>',
    unsafe_allow_html=True)
st.write('')

# ── KPI row ──────────────────────────────────────────────────────────────────
k = st.columns(5)
k[0].metric('Peak monthly RERS', f"{res['peak_rers']*100:.1f}%",
            help='Best-month renewable share of a 1 MW demand. Below 40% = renewables cannot be primary.')
k[1].metric('Annual mean RERS', f"{res['annual_rers']*100:.1f}%")
k[2].metric('Mean annual temp', f"{res['annual_temp']:.1f} C")
k[3].metric('Coldest month', f"{res['min_temp']:.0f} C")
k[4].metric('Polar-night months', f"{res['polar_night_months']}")

# ── Reactor sizing (optional) ────────────────────────────────────────────────
if pop > 0:
    floor = df[df.month.isin([11, 12, 1, 2])][['solar_mw', 'wind_mw']].sum(axis=1).mean()
    sizing = ph.size_reactor(ph.demand_mw(pop), floor)
    st.info(f"**Reactor sizing for {pop:,} people** - average demand "
            f"{ph.demand_mw(pop):.2f} MW; winter renewable floor {floor:.3f} MW -> "
            f"**{sizing['reactor_mw']} MWe** ({sizing['evinci_units']}x eVinci, "
            f"{sizing['tech_class']}), incl. 30% safety margin.")

# ── Charts ───────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
x = df['month'].values

with c1:
    st.markdown('**Seasonal energy gap** - renewables vs 1 MW demand')
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.fill_between(x, 0, df['solar_mw'], color='#F5A623', alpha=0.9, label='Solar MW')
    ax.fill_between(x, df['solar_mw'], df['solar_mw'] + df['wind_mw'], color=ACCENT,
                    alpha=0.85, label='+ Wind MW')
    ax.fill_between(x, df['solar_mw'] + df['wind_mw'], ph.BASELINE_MW, color=RED,
                    alpha=0.20, label='Nuclear gap')
    ax.axhline(ph.BASELINE_MW, color=RED, ls='--', lw=1.5)
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7)
    ax.set_ylim(0, 1.15); ax.set_ylabel('MW'); ax.legend(fontsize=7, facecolor=PANEL)
    st.pyplot(fig); plt.close(fig)

with c2:
    st.markdown('**Monthly RERS vs 40% nuclear threshold**')
    fig, ax = plt.subplots(figsize=(6, 3.6))
    cols = [GREEN if v >= ph.NUCLEAR_THRESHOLD else RED for v in df['RERS']]
    ax.bar(x, df['RERS'], color=cols, alpha=0.85)
    ax.axhline(ph.NUCLEAR_THRESHOLD, color=AMBER, ls=':', lw=1.5, label='40% threshold')
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7)
    ax.set_ylim(0, max(0.45, df['RERS'].max() * 1.2)); ax.set_ylabel('RERS')
    ax.legend(fontsize=7, facecolor=PANEL)
    st.pyplot(fig); plt.close(fig)

c3, c4 = st.columns(2)
with c3:
    st.markdown('**Temperature climatology**')
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(x, df['temp_c'], color=ACCENT, marker='o', lw=1.5)
    if 'temp_std' in df:
        ax.fill_between(x, df['temp_c'] - df['temp_std'], df['temp_c'] + df['temp_std'],
                        color=ACCENT, alpha=0.18, label='ML uncertainty')
        ax.legend(fontsize=7, facecolor=PANEL)
    ax.axhline(0, color='#33414F', lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7); ax.set_ylabel('C')
    st.pyplot(fig); plt.close(fig)

with c4:
    st.markdown('**Why this verdict** - score components')
    comp = res['components']
    labels = {'renewable_insufficiency': 'Renewable insufficiency (x0.45)',
              'demand_pressure': 'Climate demand pressure (x0.35)',
              'siting_suitability': 'Siting suitability (x0.20)'}
    for key, lab in labels.items():
        st.caption(lab)
        st.progress(float(comp[key]))
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=2, size=40000)

# ── Siting flags ─────────────────────────────────────────────────────────────
st.subheader('Siting & engineering flags')
if res['flags']:
    for fl in res['flags']:
        st.warning(fl)
else:
    st.success('No major cold/permafrost siting flags at this location.')

st.caption('Verdict combines renewable insufficiency (best-month RERS vs the 40% threshold), '
           'climate demand pressure (mean annual temperature), and siting suitability '
           '(permafrost + extreme-cold penalties). Reactor sizing uses the eVinci 5 MWe '
           'reference and a 30% safety margin. Live data: Open-Meteo ERA5 or NASA POWER; '
           'offline/instant: ML surrogate trained on a NASA-calibrated circumpolar grid.')
