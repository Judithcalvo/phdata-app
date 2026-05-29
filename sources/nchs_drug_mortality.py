"""
NCHS Drug Poisoning Mortality by County — National Center for Health Statistics.
Endpoint: https://data.cdc.gov/resource/pbkm-d27e.json

Model-based county-level estimates of drug poisoning (overdose) mortality,
1999 to most recent release. Public, no key required.

Strategy: simple state filter server-side, year filter client-side.
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://data.cdc.gov/resource/pbkm-d27e.json"

US_STATES = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
    "Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois",
    "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts",
    "Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
    "New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
    "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina",
    "South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington",
    "West Virginia","Wisconsin","Wyoming",
]


def render_filters() -> dict:
    c1, c2, c3 = st.columns(3)
    state = c1.selectbox("State", US_STATES, index=US_STATES.index("Texas"))
    year_from = c2.number_input("From year", 1999, 2022, 2015)
    year_to = c3.number_input("To year", 1999, 2022, 2020)
    limit = st.number_input("Max rows", 1000, 50000, 20000, step=1000)
    return {
        "state": state,
        "year_from": int(year_from),
        "year_to": int(year_to),
        "limit": int(limit),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_cached(state: str, year_from: int, year_to: int, limit: int) -> pd.DataFrame:
    """Cached inner fetch. All args are scalar/hashable."""
    params = {"$limit": limit}
    if state:
        params["state"] = state

    r = requests.get(ENDPOINT, params=params, timeout=60)
    if r.status_code != 200:
        try:
            err = r.json().get("message", r.text[:300])
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"NCHS API ({r.status_code}): {err}")

    df = pd.DataFrame(r.json())
    if df.empty:
        return df

    for col in ("year", "estimated_age_adjusted_rate", "estimated_age_adjusted_rate_lower",
                "estimated_age_adjusted_rate_upper", "population"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "year" in df.columns:
        df = df[(df["year"] >= year_from) & (df["year"] <= year_to)]

    return df.reset_index(drop=True)


def fetch(state: str, year_from: int, year_to: int, limit: int) -> pd.DataFrame:
    """Public entry point."""
    return _fetch_cached(state, year_from, year_to, limit)
