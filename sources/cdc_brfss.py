"""
CDC BRFSS via Socrata (chronicdata.cdc.gov).
Dataset: Behavioral Risk Factor Surveillance System: Prevalence Data (2011 to present).
Endpoint: https://chronicdata.cdc.gov/resource/dttw-5yxu.json

Actual columns on this dataset (lowercased Socrata names):
  year, locationabbr, locationdesc, class, topic, question, response,
  break_out, break_out_category, sample_size, data_value,
  confidence_limit_low, confidence_limit_high, display_order,
  data_value_unit, data_value_type, datasource, classid, topicid,
  locationid, breakoutid, breakoutcategoryid, questionid, responseid,
  geolocation

Strategy: minimal server-side filter (year only), then filter client-side.
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://chronicdata.cdc.gov/resource/dttw-5yxu.json"

US_STATES = [
    "US","AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
    "VT","VA","WA","WV","WI","WY","DC","PR","GU","VI",
]


def render_filters() -> dict:
    c1, c2, c3 = st.columns(3)
    year = c1.selectbox("Year", list(range(2022, 2010, -1)), index=0)
    states = c2.multiselect("State(s)", US_STATES, default=["TX", "CA"])
    row_limit = c3.number_input("Max rows", 1000, 50000, 10000, step=1000)
    topic = st.text_input(
        "Topic filter (optional — e.g. 'mental', 'depression', 'alcohol')",
        value="",
    )
    return {"year": year, "states": states, "topic": topic, "limit": int(row_limit)}


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_cached(year: int, states: tuple, topic: str, limit: int) -> pd.DataFrame:
    """Cached inner fetch. Uses tuple for states (hashable)."""
    params = {"year": str(year), "$limit": limit}
    r = requests.get(ENDPOINT, params=params, timeout=60)
    if r.status_code != 200:
        try:
            err = r.json().get("message", r.text[:300])
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"BRFSS API ({r.status_code}): {err}")

    df = pd.DataFrame(r.json())
    if df.empty:
        return df

    if states and "locationabbr" in df.columns:
        df = df[df["locationabbr"].isin(states)]
    if topic and "topic" in df.columns:
        df = df[df["topic"].str.contains(topic, case=False, na=False)]

    for col in ("data_value", "confidence_limit_low", "confidence_limit_high",
                "sample_size", "year"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.reset_index(drop=True)


def fetch(year: int, states: list, topic: str, limit: int) -> pd.DataFrame:
    """Public entry point — converts list → tuple for cache compatibility."""
    return _fetch_cached(year, tuple(sorted(states)), topic.strip().lower(), limit)
