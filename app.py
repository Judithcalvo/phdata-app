"""
PHData Pipeline — public health / behavioral health data fetcher.
Streamlit app: pick a source, preview, download CSV (Excel & Power BI ready).
"""
import io
import streamlit as st
import pandas as pd
from sources import REGISTRY

# ============================================================
# Page setup
# ============================================================
st.set_page_config(
    page_title="PHData Pipeline",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS for polish ----
st.markdown(
    """
    <style>
      /* Tighten top padding */
      .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

      /* Hero */
      .hero {
        background: linear-gradient(135deg, #0F766E 0%, #134E4A 100%);
        color: white; padding: 2rem 2.5rem; border-radius: 14px;
        margin-bottom: 1.5rem;
      }
      .hero h1 { color: white; margin: 0 0 .35rem 0; font-size: 2rem; font-weight: 700;}
      .hero p  { color: #D1FAE5; margin: 0; font-size: 1.05rem; }

      /* Step header */
      .step-header {
        display: flex; align-items: center; gap: .75rem;
        margin: 1.5rem 0 .5rem 0;
      }
      .step-number {
        background: #0F766E; color: white; width: 32px; height: 32px;
        border-radius: 50%; display: inline-flex; align-items: center;
        justify-content: center; font-weight: 700; font-size: .95rem;
      }
      .step-title { font-size: 1.25rem; font-weight: 600; color: #0F172A; }

      /* Source-info card */
      .source-card {
        background: #F1F5F9; border-left: 4px solid #0F766E;
        padding: .85rem 1rem; border-radius: 6px; margin: .5rem 0 1rem 0;
        font-size: .92rem;
      }
      .source-card a { color: #0F766E; }

      /* Download buttons: make CSV primary visually */
      div[data-testid="stDownloadButton"] button { width: 100%; padding: .75rem; }

      /* Footer */
      .footer { color: #64748B; font-size: .85rem; text-align: center;
                margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #E2E8F0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Hero
# ============================================================
st.markdown(
    """
    <div class="hero">
      <h1>📊 Public & Behavioral Health Data Pipeline</h1>
      <p>Pick a dataset, set your filters, and download a clean spreadsheet — ready for Excel or Power BI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar — source selection
# ============================================================
with st.sidebar:
    st.markdown("### 🔎 Choose your data source")
    source_key = st.selectbox(
        "Available datasets",
        options=list(REGISTRY.keys()),
        format_func=lambda k: REGISTRY[k]["label"],
        label_visibility="collapsed",
    )
    source = REGISTRY[source_key]

    st.markdown("---")
    st.markdown("**Need help?**")
    st.caption(
        "1️⃣ Pick a dataset above\n\n"
        "2️⃣ Set filters on the right\n\n"
        "3️⃣ Click **Fetch data**\n\n"
        "4️⃣ Download as CSV — open in Excel or import into Power BI"
    )

# ============================================================
# Step 1 — Source info
# ============================================================
st.markdown(
    f'<div class="step-header"><span class="step-number">1</span>'
    f'<span class="step-title">About this source</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="source-card">
      <strong>{source['label']}</strong><br>
      {source['description']}<br>
      <em>Provider:</em> {source['provider']} •
      <a href="{source['url']}" target="_blank">View source documentation ↗</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Step 2 — Filters
# ============================================================
st.markdown(
    '<div class="step-header"><span class="step-number">2</span>'
    '<span class="step-title">Set your filters</span></div>',
    unsafe_allow_html=True,
)
params = source["render_filters"]()

# ============================================================
# Step 3 — Fetch
# ============================================================
st.markdown(
    '<div class="step-header"><span class="step-number">3</span>'
    '<span class="step-title">Fetch the data</span></div>',
    unsafe_allow_html=True,
)

fetch = st.button("🚀  Fetch data", type="primary", use_container_width=True)

if fetch:
    with st.spinner("Connecting to the source and fetching your data…"):
        try:
            df: pd.DataFrame = source["fetch"](**params)
            if df.empty:
                st.warning("No rows returned. Try loosening your filters.")
                st.session_state.pop("df", None)
            else:
                st.session_state["df"] = df
                st.session_state["source_key"] = source_key
                st.success(f"✅ Loaded **{len(df):,}** rows × **{len(df.columns)}** columns.")
        except Exception as e:
            st.error(f"❌ Could not fetch data: {e}")
            st.session_state.pop("df", None)

# ============================================================
# Step 4 — Preview + download
# ============================================================
if "df" in st.session_state:
    df = st.session_state["df"]

    st.markdown(
        '<div class="step-header"><span class="step-number">4</span>'
        '<span class="step-title">Preview & download</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Preview** — first 100 rows:")
    st.dataframe(df.head(100), use_container_width=True, height=320)

    st.markdown(" ")
    st.markdown("##### 📥 Download your file")
    c1, c2, c3 = st.columns([2, 2, 1])

    fname_base = st.session_state["source_key"]

    with c1:
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")  # BOM = Excel-friendly
        st.download_button(
            "⬇️  CSV — for Excel or Power BI",
            data=csv_bytes,
            file_name=f"{fname_base}.csv",
            mime="text/csv",
            type="primary",
            help="Universal format. Opens directly in Excel. In Power BI: Get Data → Text/CSV.",
        )

    with c2:
        xbuf = io.BytesIO()
        with pd.ExcelWriter(xbuf, engine="openpyxl") as w:
            df.to_excel(w, index=False, sheet_name="data")
        st.download_button(
            "⬇️  Excel (.xlsx)",
            data=xbuf.getvalue(),
            file_name=f"{fname_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Excel workbook with formatting.",
        )

    with c3:
        with st.popover("Advanced"):
            st.caption("Parquet — smaller, faster, but Excel can't open it directly. Use this only for very large datasets in Power BI.")
            try:
                pbuf = io.BytesIO()
                df.to_parquet(pbuf, index=False, engine="pyarrow")
                st.download_button(
                    "Parquet (.parquet)",
                    data=pbuf.getvalue(),
                    file_name=f"{fname_base}.parquet",
                    mime="application/octet-stream",
                )
            except Exception as e:
                st.caption(f"(Parquet unavailable: {e})")

    with st.expander("📋 Column details (schema)"):
        st.dataframe(
            pd.DataFrame({
                "Column": df.columns,
                "Type": [str(t) for t in df.dtypes],
                "Non-null rows": df.notna().sum().values,
            }),
            use_container_width=True,
            hide_index=True,
        )

# ============================================================
# Footer
# ============================================================
st.markdown(
    '<div class="footer">PHData Pipeline · '
    'Built for public-, behavioral-, and mental-health data professionals.</div>',
    unsafe_allow_html=True,
)
