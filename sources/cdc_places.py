"""
CDC PLACES — Local Data for Better Health, County Data (current release).
Endpoint: https://chronicdata.cdc.gov/resource/swc5-untb.json

Strategy:
  - Filter by state + category server-side (both reliable exact-match fields).
  - Optionally narrow with measure keyword client-side.
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://chronicdata.cdc.gov/resource/swc5-untb.json"

CATEGORIES = [
    "Health Outcomes",
    "Prevention",
    "Health Risk Behaviors",
    "Health Status",
    "Disability",
    "Health-Related Social Needs",
]


def render_filters() -> dict:
    c1, c2 = st.columns(2)
    state = c1.text_input(
        "State abbreviation (e.g. TX, CA — leave blank for all states)",
        value="TX",
    )
    category = c2.selectbox(
        "Measure category",
        CATEGORIES,
        index=0,
        help="Top-level grouping. Use the keyword box below to narrow further.",
    )
    c3, c4 = st.columns(2)
    measure_keyword = c3.text_input(
        "Optional keyword to narrow measures (e.g. 'mental', 'depression', 'sleep')",
        value="",
    )
    limit = c4.number_input("Max rows", 1000, 50000, 30000, step=1000)
    return {
        "state": state.strip().upper(),
        "category": category,
        "measure_keyword": measure_keyword.strip(),
        "limit": int(limit),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_cached(state: str, category: str, measure_keyword: str, limit: int) -> pd.DataFrame:
    """Cached inner fetch. All args are scalar/hashable."""
    params = {"$limit": limit, "category": category}
    if state:
        params["stateabbr"] = state

    r = requests.get(ENDPOINT, params=params, timeout=60)
    if r.status_code != 200:
        try:
            err = r.json().get("message", r.text[:300])
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"PLACES API ({r.status_code}): {err}")

    df = pd.DataFrame(r.json())
    if df.empty:
        return df

    if measure_keyword and "measure" in df.columns:
        df = df[df["measure"].str.contains(measure_keyword, case=False, na=False)]

    for col in ("data_value", "low_confidence_limit", "high_confidence_limit",
                "totalpopulation", "year"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def fetch(state: str, category: str, measure_keyword: str, limit: int) -> pd.DataFrame:
    """Public entry point."""
    return _fetch_cached(state, category, measure_keyword.strip().lower(), limit)
