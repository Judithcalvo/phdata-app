"""
CDC PLACES — Local Data for Better Health, County Data (current release).
Endpoint: https://chronicdata.cdc.gov/resource/swc5-untb.json

Actual columns on this dataset (lowercased Socrata names):
  year, stateabbr, statedesc, locationname, datasource, category,
  measure, data_value_unit, data_value_type, data_value, data_value_footnote_symbol,
  data_value_footnote, low_confidence_limit, high_confidence_limit, totalpopulation,
  locationid, categoryid, measureid, datavaluetypeid, short_question_text, geolocation

Strategy: filter on state server-side (small, fast), filter measure client-side.
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://chronicdata.cdc.gov/resource/swc5-untb.json"

MEASURE_KEYWORDS = [
    "mental health",
    "depression",
    "binge drinking",
    "smoking",
    "sleeping less",
    "physical health",
    "stress",
]


def render_filters() -> dict:
    c1, c2 = st.columns(2)
    state = c1.text_input("State abbreviation (e.g. TX, CA — blank for all)", value="TX")
    limit = c2.number_input("Max rows", 1000, 50000, 10000, step=1000)
    measure_keyword = st.selectbox(
        "Measure keyword (matched against the measure description)",
        MEASURE_KEYWORDS,
        index=0,
    )
    return {
        "state": state.strip().upper(),
        "measure_keyword": measure_keyword,
        "limit": int(limit),
    }


def fetch(state: str, measure_keyword: str, limit: int) -> pd.DataFrame:
    params = {"$limit": limit}
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

    # Client-side measure filter (case-insensitive partial match)
    if measure_keyword and "measure" in df.columns:
        df = df[df["measure"].str.contains(measure_keyword, case=False, na=False)]

    # Type cleanup
    for col in ("data_value", "low_confidence_limit", "high_confidence_limit",
                "totalpopulation", "year"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)
