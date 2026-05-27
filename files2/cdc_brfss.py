"""
CDC BRFSS via Socrata (chronicdata.cdc.gov).
Dataset: Behavioral Risk Factor Surveillance System: Prevalence Data (2011 to present).
Endpoint: https://chronicdata.cdc.gov/resource/dttw-5yxu.json
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
    year = c1.selectbox("Year", list(range(2023, 2010, -1)), index=1)
    states = c2.multiselect("State(s)", US_STATES, default=["TX", "CA"])
    row_limit = c3.number_input("Row limit", 1000, 50000, 10000, step=1000)
    topic = st.text_input(
        "Topic filter (optional, partial match — e.g. 'Mental Health', 'Depression', 'Alcohol')",
        value="",
    )
    return {"year": year, "states": states, "topic": topic, "limit": int(row_limit)}


def fetch(year: int, states: list[str], topic: str, limit: int) -> pd.DataFrame:
    where_parts = [f"yearstart = '{year}'"]
    if states:
        quoted = ",".join(f"'{s}'" for s in states)
        where_parts.append(f"locationabbr in({quoted})")
    if topic:
        t = topic.replace("'", "''").lower()
        where_parts.append(f"lower(topic) like '%{t}%'")

    params = {
        "$where": " AND ".join(where_parts),
        "$limit": limit,
    }
    r = requests.get(ENDPOINT, params=params, timeout=60)
    if r.status_code != 200:
        # Surface the real Socrata error message instead of a generic HTTP error
        try:
            err = r.json().get("message", r.text[:300])
        except Exception:
            err = r.text[:300]
        raise RuntimeError(f"BRFSS API said: {err}")

    df = pd.DataFrame(r.json())
    if df.empty:
        return df

    # Type cleanup for downstream tools (Power BI / Excel)
    numeric_candidates = [
        "data_value", "low_confidence_limit", "high_confidence_limit",
        "sample_size", "yearstart", "yearend",
    ]
    for col in numeric_candidates:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
