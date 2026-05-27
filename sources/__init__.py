"""
Source registry. Add new sources by writing a module in sources/ and
registering it here. Each source exposes:
    label, description, provider, url, render_filters(), fetch(**params)
"""
from sources import cdc_brfss, cdc_places, nchs_drug_mortality

REGISTRY = {
    "cdc_brfss": {
        "label": "CDC BRFSS — Behavioral Risk Factor Surveillance",
        "description": "Adult risk-behavior + chronic condition survey, state-level.",
        "provider": "CDC (Socrata)",
        "url": "https://chronicdata.cdc.gov",
        "render_filters": cdc_brfss.render_filters,
        "fetch": cdc_brfss.fetch,
    },
    "cdc_places": {
        "label": "CDC PLACES — Local-area mental & behavioral health",
        "description": "County-level estimates: mental distress, depression, sleep, etc.",
        "provider": "CDC (Socrata)",
        "url": "https://www.cdc.gov/places",
        "render_filters": cdc_places.render_filters,
        "fetch": cdc_places.fetch,
    },
    "nchs_drug_mortality": {
        "label": "NCHS Drug Poisoning Mortality by County",
        "description": "County-level age-adjusted drug overdose mortality rates, 1999-present.",
        "provider": "CDC NCHS",
        "url": "https://www.cdc.gov/nchs/data-visualization/drug-poisoning-mortality/",
        "render_filters": nchs_drug_mortality.render_filters,
        "fetch": nchs_drug_mortality.fetch,
    },
}
