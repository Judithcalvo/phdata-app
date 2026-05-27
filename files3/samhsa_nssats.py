"""
SAMHSA — substance use & mental health treatment facility locator.
Uses the findtreatment.gov public JSON endpoint.

Note: this is the same endpoint findtreatment.gov uses for its own search.
Schema can change without notice. We surface raw columns and let the user pick.
"""
import requests
import pandas as pd
import streamlit as st

ENDPOINT = "https://findtreatment.gov/locator/exportsAsJson/v2"

SERVICE_TYPES = {
    "SA": "Substance Abuse",
    "MH": "Mental Health",
    "BHA": "Both (BHA)",
}


def render_filters() -> dict:
    c1, c2, c3 = st.columns(3)
    state = c1.text_input("State (e.g. TX, CA)", value="TX")
    service_type = c2.selectbox(
        "Service type",
        list(SERVICE_TYPES.keys()),
        format_func=lambda s: SERVICE_TYPES[s],
    )
    pages = c3.number_input("Pages to fetch (250 per page)", 1, 20, 2)
    return {
        "state": state.strip().upper(),
        "service_type": service_type,
        "pages": int(pages),
    }


def fetch(state: str, service_type: str, pages: int) -> pd.DataFrame:
    all_rows: list[dict] = []
    last_status = None
    last_text = ""

    for page in range(1, pages + 1):
        params = {
            "sType": service_type,
            "sCodes": "1",
            "limitType": 2,
            "pageSize": 250,
            "page": page,
        }
        if state:
            params["sAddr"] = state
        try:
            r = requests.get(ENDPOINT, params=params, timeout=60)
        except requests.RequestException as e:
            raise RuntimeError(f"SAMHSA request failed: {e}")

        last_status = r.status_code
        last_text = r.text[:300]
        if r.status_code != 200:
            raise RuntimeError(
                f"SAMHSA API ({r.status_code}): {last_text}"
            )

        try:
            data = r.json()
        except ValueError:
            raise RuntimeError(f"SAMHSA returned non-JSON: {last_text}")

        rows = data.get("rows") if isinstance(data, dict) else data
        if not rows:
            break
        all_rows.extend(rows)

    if not all_rows:
        return pd.DataFrame()

    df = pd.json_normalize(all_rows)
    # Drop noisy internal columns
    keep = [c for c in df.columns if not c.startswith("_")]
    return df[keep].reset_index(drop=True)
