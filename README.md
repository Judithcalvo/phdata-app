# PHData Pipeline

A web app that lets visitors pick a public-health / behavioral-health dataset, set filters, preview, and download a clean **CSV** (opens in Excel or imports into Power BI).

Runs in any modern browser — Mac, PC, mobile. Nothing for the end user to install.

## What's inside

```
phdata-app/
├── app.py                    ← main Streamlit app (the UI)
├── requirements.txt          ← Python packages needed
├── .streamlit/
│   └── config.toml           ← theme (teal/slate palette)
└── sources/
    ├── __init__.py           ← source registry
    ├── cdc_brfss.py          ← CDC BRFSS survey
    ├── cdc_places.py         ← CDC PLACES county estimates
    └── samhsa_nssats.py      ← SAMHSA facility locator
```

## How to run it on your Windows machine

Streamlit apps don't run *inside* a Jupyter notebook cell, but you can launch one from any terminal — including the terminal built into Jupyter Lab, or Anaconda Prompt.

### One-time setup

1. Open **Anaconda Prompt** (Start menu → Anaconda → Anaconda Prompt).
2. Navigate to wherever you saved this folder:
   ```bash
   cd C:\Powerstats\phdata-app
   ```
3. Install the packages (one time only):
   ```bash
   pip install -r requirements.txt
   ```

### Every time you want to run it

In the same Anaconda Prompt:
```bash
cd C:\Powerstats\phdata-app
streamlit run app.py
```

A browser tab opens at `http://localhost:8501`. To stop, press `Ctrl+C` in the prompt window.

### From Jupyter Lab

If you prefer Jupyter, open Jupyter Lab → **File → New → Terminal** → run the same two commands. You don't need a notebook.

## File format options (in plain English)

| Format | When to use it |
|--------|----------------|
| **CSV** (default) | Universal. Double-click to open in Excel. In Power BI: *Get Data → Text/CSV*. **Pick this unless you have a reason not to.** |
| **Excel (.xlsx)** | Same data, but pre-formatted as an Excel workbook. |
| **Parquet** | Tucked in an "Advanced" menu. Smaller file, faster Power BI refresh, but only useful for very large datasets and Excel can't open it. |

## How clients use the live app

1. Open the URL in any browser.
2. Pick a dataset from the sidebar.
3. Adjust filters (state, year, topic).
4. Click **🚀 Fetch data**.
5. Preview the result.
6. Click **⬇️ CSV** to download.

## Datasets currently wired up

| Source | What it gives you |
|--------|-------------------|
| **CDC BRFSS** | Adult risk-behavior + chronic condition survey, by state/year/topic |
| **CDC PLACES** | County-level estimates: mental distress, depression, sleep, etc. |
| **SAMHSA findtreatment.gov** | Substance use & mental health treatment facilities by state |

### Adding a new source

Drop a new file into `sources/` that defines two functions:
```python
def render_filters() -> dict: ...   # build Streamlit filter widgets, return a params dict
def fetch(**params) -> pd.DataFrame: ...  # call the API, return a DataFrame
```
Then register it in `sources/__init__.py`. Done.

## Deploy publicly (when you're ready)

| Option | Cost | Notes |
|--------|------|-------|
| **Streamlit Community Cloud** | Free | Push to GitHub, connect, deploy. Easiest for a demo URL. |
| **Azure App Service** | ~$13/mo (B1) | Fits your Microsoft stack. |
| **Render** | $7/mo | Free tier sleeps after inactivity. |
