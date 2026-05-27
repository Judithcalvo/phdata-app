"""
CDC PLACES — Local Data for Better Health.
County-level estimates including mental health & behavioral measures.
Endpoint: https://chronicdata.cdc.gov/resource/swc5-untb.json  (County data)
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://chronicdata.cdc.gov/resource/swc5-untb.json"

MEASURES = [
    "Mental health not good for >=14 days among adults aged >=18 years",
    "Depression among adults aged >=18 years",
    "Binge drinking among adults aged >=18 years",
    "Current smoking among adults aged >=18 years",
    "Sleeping less than 7 hours among adults aged >=18 years",
]


def render_filters() -> dict:
    c1, c2 = st.columns(2)
    state = c1.text_input("State abbreviation (e.g. TX, CA, blank=all)", value="TX")
    limit = c2.number_input("Row limit", 1000, 50000, 5000, step=1000)
    measure = st.selectbox("Measure", MEASURES, index=0)
    return {"state": state.strip().upper(), "measure": measure, "limit": int(limit)}


def fetch(state: str, measure: str, limit: int) -> pd.DataFrame:
    safe_measure = measure.replace("'", "''")
    where = [f"measure = '{safe_measure}'"]
    if state:
        where.append(f"stateabbr = '{state}'")
    params = {
        "$where": " AND ".join(where),
        "$limit": limit,
        "$select": (
            "stateabbr,statedesc,locationname,countyfips,"
            "measure,data_value,low_confidence_limit,high_confidence_limit,"
            "totalpopulation,year"
        ),
    }
    r = requests.get(ENDPOINT, params=params, timeout=60)
    if r.status_code != 200:
        try:
            err = r.json().get("message", r.text[:300])
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"CDC PLACES API said: {err}")
    df = pd.DataFrame(r.json())
    if df.empty:
        return df
    for col in ["data_value", "low_confidence_limit", "high_confidence_limit", "totalpopulation"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df
