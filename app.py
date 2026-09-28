import hashlib
import io

import streamlit as st

from src.components import patient_detail, sidebar, summary_table, trend_chart
from src.config import SAMPLE_PATH
from src.data_loader import CSVLoadError, load_patient_csv
from src.summary import build_patient_summary

st.set_page_config(page_title="Patient Summary Dashboard", layout="wide")


@st.cache_data(show_spinner="Reading file...")
def parse_csv(raw: bytes):
    return load_patient_csv(io.BytesIO(raw))


def show_empty_state():
    st.info("Upload a patient CSV in the sidebar to get started, or tick 'Use sample data'.")
    st.markdown(
        "**Required columns:** `patient_id`, `visit_date`  \n"
        "**Used if present:** `patient_name`, `age`, `gender`, `systolic_bp`, `diastolic_bp`, "
        "`heart_rate`, `glucose`, `temperature`, `spo2`, `risk_score`, `risk_level`  \n"
        "One row per patient visit, so a patient with several visits appears on several rows."
    )


st.title("Patient Summary Dashboard")

uploaded, use_sample = sidebar.upload_section()

if uploaded is not None:
    raw, source_name = uploaded.getvalue(), uploaded.name
elif use_sample:
    raw, source_name = SAMPLE_PATH.read_bytes(), SAMPLE_PATH.name
else:
    show_empty_state()
    st.stop()

try:
    df, notes = parse_csv(raw)
except CSVLoadError as err:
    st.error(f"Couldn't load {source_name}: {err}")
    st.stop()

st.caption(f"Loaded {source_name}: {len(df):,} visits across {df['patient_id'].nunique():,} patients.")
for note in notes:
    st.warning(note)

summary = build_patient_summary(df)
data_key = hashlib.md5(raw).hexdigest()[:8]
filtered = sidebar.filters(summary, data_key)

if filtered.empty:
    st.warning("No patients match the current filters.")
    st.stop()

summary_table.render(filtered, total_patients=len(summary))

st.divider()
patient_id = patient_detail.select_patient(filtered)
patient_row = filtered[filtered["patient_id"] == patient_id].iloc[0]
patient_visits = df[df["patient_id"] == patient_id].sort_values("visit_date")

patient_detail.render(patient_row, patient_visits)

st.divider()
trend_chart.render(patient_visits)