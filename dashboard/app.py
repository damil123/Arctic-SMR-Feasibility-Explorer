"""
app.py — Arctic Micro-Reactor Feasibility Explorer (Streamlit).

Pick any Arctic / subarctic coordinate. The app pulls a 10-year monthly climatology
(Open-Meteo ERA5, NASA POWER cross-check, ML surrogate fallback), screens micro-
reactor feasibility, then runs a scalable solar+wind+battery+baseload energy model
with economics so the renewable penetration, cost comparison, and charts respond to
the actual location and system design.

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
import energy_model as em

st.set_page_config(page_title='Arctic Micro-Reactor Feasibility',
                   page_icon='*', layout='wide')

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
pop = st.sidebar.number_input('Community population (0 = use 1 MW reference)', 0, 200000, 1000, 50)

with st.sidebar.expander('Energy system design'):
    pv_mult = st.slider('Solar PV capacity (x avg load)', 0.0, 6.0, 3.0, 0.5)
    wind_mult = st.slider('Wind capacity (x avg load)', 0.0, 4.0, 1.5, 0.5)
    batt_hours = st.slider('Battery autonomy (hours)', 0, 72, 12, 4)
with st.sidebar.expander('Economics ($/kWh)'):
    diesel_kwh = st.slider('Diesel LCOE', 0.30, 1.00, 0.60, 0.01)
    nuclear_kwh = st.slider('Nuclear LCOE', 0.15, 0.60, 0.25, 0.01)
    renew_kwh = st.slider('Renewables + storage LCOE', 0.04, 0.30, 0.09, 0.01)

# ── Compute: climate + feasibility ───────────────────────────────────────────
df, used = get_climate(round(lat, 2), round(lon, 2), source)
res = fz.score_location(df['solar_kwh_m2_day'].values, df['wind_ms'].values, df['temp_c'].values)
clf_label, clf_proba = inf.classify_location(df)
clf_conf = max(clf_proba.values())

# ── Compute: energy system + economics ───────────────────────────────────────
demand_mw = ph.demand_mw(pop) if pop > 0 else ph.BASELINE_MW
avg_kw = demand_mw * 1000
sim = em.simulate_hybrid(df['solar_kwh_m2_day'].values, df['wind_ms'].values, demand_mw,
                         pv_kw=pv_mult * avg_kw, wind_kw=wind_mult * avg_kw,
                         battery_mwh=batt_hours * demand_mw)
eco = em.economics(sim, diesel_lcoe=diesel_kwh * 1000, nuclear_lcoe=nuclear_kwh * 1000,
                   renew_lcoe=renew_kwh * 1000)

# ── Header + verdict ─────────────────────────────────────────────────────────
st.title('Arctic Micro-Reactor Feasibility Explorer')
st.markdown('<span class="sub">Can a community at this coordinate rely on renewables - '
            'or does the climate force a nuclear baseload? Real climate data + ML + energy model.</span>',
            unsafe_allow_html=True)

color = VERDICT_COLOR[res['verdict']]
st.markdown(
    f'<div class="verdict" style="background:{PANEL};border-left:8px solid {color};color:{color}">'
    f'{res["verdict"]} &nbsp;-&nbsp; feasibility score {res["score"]}/100</div>'
    f'<span class="sub">ML classifier agrees: <b>{clf_label}</b> '
    f'(confidence {clf_conf*100:.0f}%) &nbsp;|&nbsp; data: {used}</span>',
    unsafe_allow_html=True)
st.write('')

k = st.columns(5)
k[0].metric('Peak monthly RERS', f"{res['peak_rers']*100:.1f}%",
            help='Best-month renewable share of a 1 MW demand. Below 40% = renewables cannot be primary.')
k[1].metric('Annual mean RERS', f"{res['annual_rers']*100:.1f}%")
k[2].metric('Mean annual temp', f"{res['annual_temp']:.1f} C")
k[3].metric('Coldest month', f"{res['min_temp']:.0f} C")
k[4].metric('Polar-night months', f"{res['polar_night_months']}")

# ── Energy system & economics ────────────────────────────────────────────────
st.subheader('Energy system & economics')
demand_note = (f"{pop:,} people -> {demand_mw:.2f} MW avg demand" if pop > 0
               else "no population set -> 1 MW reference demand")
st.markdown(f'<span class="sub">System: {pv_mult:g}x PV + {wind_mult:g}x wind + '
            f'{batt_hours}h battery, sized to {demand_note}.</span>', unsafe_allow_html=True)

e = st.columns(4)
e[0].metric('Renewable penetration', f"{sim['penetration']*100:.0f}%",
            help='Share of annual demand met by solar+wind+storage in this design.')
e[1].metric('Winter (worst month)', f"{sim['worst_month_penetration']*100:.0f}%",
            help='Renewable share in the worst month - why firm baseload is still required.')
e[2].metric('Firm power still needed', f"{sim['annual_firm_mwh']:,.0f} MWh/yr")
best_name, best_cost = eco['best_option']
e[3].metric('Cheapest option', best_name, help=f"${best_cost:.1f}M/yr")

if pop > 0:
    floor = df[df.month.isin([11, 12, 1, 2])][['solar_mw', 'wind_mw']].sum(axis=1).mean()
    sizing = ph.size_reactor(demand_mw, floor)
    st.info(f"**Reactor sizing** - to firm {demand_mw:.2f} MW demand: "
            f"**{sizing['reactor_mw']} MWe** ({sizing['evinci_units']}x eVinci, "
            f"{sizing['tech_class']}), incl. 30% safety margin. "
            f"Nuclear vs diesel saves ~${eco['diesel_saving_vs_nuclear_m']:.1f}M/yr and "
            f"avoids ~{eco['co2_avoided_nuclear_kt']:.1f} kt CO2/yr.")

x = df['month'].values
g1, g2 = st.columns(2)
with g1:
    st.markdown('**Monthly energy balance** - renewables served vs firm power needed')
    fig, ax = plt.subplots(figsize=(6, 3.6))
    rs = sim['renewable_served_mwh']
    fn = sim['firm_needed_mwh']
    ax.bar(x, rs, color=GREEN, alpha=0.85, label='Renewables + storage')
    ax.bar(x, fn, bottom=rs, color=RED, alpha=0.7, label='Firm (diesel/nuclear)')
    ax.plot(x, sim['load_mwh'], color='#DDE3EE', lw=1.2, ls='--', label='Demand')
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7)
    ax.set_ylabel('MWh / month'); ax.legend(fontsize=7, facecolor=PANEL)
    st.pyplot(fig); plt.close(fig)

with g2:
    st.markdown('**Annual cost by system option** ($M/yr)')
    fig, ax = plt.subplots(figsize=(6, 3.6))
    opts = ['Diesel\nonly', 'Renew +\ndiesel', 'Nuclear\nbaseload', 'Renew +\nnuclear']
    vals = [eco['diesel_only']['cost_m'], eco['hybrid_diesel']['cost_m'],
            eco['nuclear']['cost_m'], eco['hybrid_nuclear']['cost_m']]
    barcols = [RED, AMBER, ACCENT, GREEN]
    bars = ax.bar(opts, vals, color=barcols, alpha=0.85)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v, f'${v:.1f}M', ha='center', va='bottom',
                fontsize=8, color='#DDE3EE')
    ax.set_ylabel('$M / year'); ax.set_ylim(0, max(vals) * 1.18)
    st.pyplot(fig); plt.close(fig)

# ── Feasibility detail charts ────────────────────────────────────────────────
st.subheader('Feasibility detail')
c1, c2 = st.columns(2)
with c1:
    st.markdown('**Monthly RERS vs 40% nuclear threshold**')
    fig, ax = plt.subplots(figsize=(6, 3.4))
    cols = [GREEN if v >= ph.NUCLEAR_THRESHOLD else RED for v in df['RERS']]
    ax.bar(x, df['RERS'], color=cols, alpha=0.85)
    ax.axhline(ph.NUCLEAR_THRESHOLD, color=AMBER, ls=':', lw=1.5, label='40% threshold')
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7)
    ax.set_ylim(0, max(0.45, df['RERS'].max() * 1.2)); ax.set_ylabel('RERS')
    ax.legend(fontsize=7, facecolor=PANEL)
    st.pyplot(fig); plt.close(fig)
with c2:
    st.markdown('**Temperature climatology**')
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.plot(x, df['temp_c'], color=ACCENT, marker='o', lw=1.5)
    if 'temp_std' in df:
        ax.fill_between(x, df['temp_c'] - df['temp_std'], df['temp_c'] + df['temp_std'],
                        color=ACCENT, alpha=0.18, label='ML uncertainty')
        ax.legend(fontsize=7, facecolor=PANEL)
    ax.axhline(0, color='#33414F', lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(ph.MONTH_NAMES, fontsize=7); ax.set_ylabel('C')
    st.pyplot(fig); plt.close(fig)

c3, c4 = st.columns(2)
with c3:
    st.markdown('**Why this verdict** - score components')
    comp = res['components']
    labels = {'renewable_insufficiency': 'Renewable insufficiency (x0.45)',
              'demand_pressure': 'Climate demand pressure (x0.35)',
              'siting_suitability': 'Siting suitability (x0.20)'}
    for key, lab in labels.items():
        st.caption(lab)
        st.progress(float(comp[key]))
with c4:
    st.markdown('**Location**')
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=2, size=40000)

st.subheader('Siting & engineering flags')
if res['flags']:
    for fl in res['flags']:
        st.warning(fl)
else:
    st.success('No major cold/permafrost siting flags at this location.')

st.caption('Energy model: scalable PV + wind + battery sized to demand, monthly balance with '
           'storage shifting; firm power covers the residual. Economics compare diesel, nuclear, '
           'and hybrids at the LCOEs set in the sidebar. Feasibility verdict combines renewable '
           'insufficiency, climate demand pressure, and permafrost/extreme-cold siting penalties. '
           'Live data: Open-Meteo ERA5 / NASA POWER; offline: ML surrogate.')
