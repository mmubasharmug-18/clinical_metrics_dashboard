import streamlit as st

from src.config import RISK_ORDER


def upload_section():
    st.sidebar.header("Data")
    uploaded = st.sidebar.file_uploader("Upload patient CSV", type="csv")
    use_sample = st.sidebar.checkbox("Use sample data instead", key="use_sample")
    return uploaded, use_sample


def _risk_levels(summary):
    present = set(summary["risk_level"])
    ordered = [level for level in RISK_ORDER if level in present]
    return ordered + sorted(present - set(ordered))


def filters(summary, data_key):
    """Risk-level and search filters. Returns the filtered summary table."""
    st.sidebar.header("Filters")

    levels = _risk_levels(summary)
    if levels == ["Unknown"]:
        st.sidebar.caption("No risk data in this file, so the risk filter is off.")
        chosen = levels
    else:
        # key includes the file id so a new upload starts with every level selected
        chosen = st.sidebar.multiselect(
            "Risk level", levels, default=levels, key=f"risk_{data_key}"
        )

    query = st.sidebar.text_input("Search by name or ID", key="search").strip().lower()

    result = summary[summary["risk_level"].isin(chosen)]
    if query:
        match = result["patient_id"].str.lower().str.contains(query, regex=False)
        if "patient_name" in result.columns:
            names = result["patient_name"].fillna("").str.lower()
            match = match | names.str.contains(query, regex=False)
        result = result[match]
    return result
