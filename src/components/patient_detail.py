import pandas as pd
import streamlit as st

from src.config import RISK_COLORS
from src.state import keep_valid

# (column, label, unit, decimals) for vitals shown as single-number metrics
SINGLE_VITALS = [
    ("heart_rate", "Heart rate", "bpm", 0),
    ("glucose", "Glucose", "mg/dL", 0),
    ("temperature", "Temperature", "°C", 1),
    ("spo2", "SpO2", "%", 0),
]


def select_patient(summary):
    ids = summary["patient_id"].tolist()
    names = {}
    if "patient_name" in summary.columns:
        names = dict(zip(summary["patient_id"], summary["patient_name"]))

    def label(pid):
        return f"{pid} - {names[pid]}" if names.get(pid) else pid

    keep_valid("selected_patient", ids)
    return st.selectbox("Select a patient", ids, format_func=label, key="selected_patient")


def _risk_badge(level):
    color = RISK_COLORS.get(level, RISK_COLORS["Unknown"])
    return (
        f"<span style='background-color:{color}; color:#000; padding:2px 12px; "
        f"border-radius:12px; font-weight:600'>{level} risk</span>"
    )


def _delta(latest, previous, column, decimals, note="since last visit"):
    if previous is None:
        return None
    now, before = latest.get(column), previous.get(column)
    if pd.isna(now) or pd.isna(before):
        return None
    return f"{now - before:+.{decimals}f} {note}"


def _fmt(value, decimals):
    return "n/a" if pd.isna(value) else f"{value:.{decimals}f}"


def render(patient, visits):
    """patient: one row of the summary table. visits: that patient's visits, oldest first."""
    st.header("Patient Detail")

    latest = visits.iloc[-1]
    previous = visits.iloc[-2] if len(visits) > 1 else None

    left, right = st.columns([1, 3])

    with left:
        name = patient.get("patient_name")
        st.subheader(name if pd.notna(name) and name else patient["patient_id"])
        st.caption(f"ID {patient['patient_id']}")
        bits = []
        if "age" in patient.index and pd.notna(patient["age"]):
            bits.append(f"Age {patient['age']:.0f}")
        if "gender" in patient.index and pd.notna(patient["gender"]):
            bits.append(str(patient["gender"]))
        if bits:
            st.write(" · ".join(bits))
        st.markdown(_risk_badge(patient["risk_level"]), unsafe_allow_html=True)
        st.write(
            f"{len(visits)} visit(s), "
            f"{visits['visit_date'].min():%d %b %Y} to {visits['visit_date'].max():%d %b %Y}"
        )

    with right:
        st.caption(f"Latest visit: {latest['visit_date']:%d %b %Y}")
        metrics = []
        if {"systolic_bp", "diastolic_bp"} <= set(visits.columns):
            value = f"{_fmt(latest['systolic_bp'], 0)}/{_fmt(latest['diastolic_bp'], 0)}"
            delta = _delta(latest, previous, "systolic_bp", 0, note="systolic since last visit")
            metrics.append(("Blood pressure", value, delta))
        for column, label, unit, decimals in SINGLE_VITALS:
            if column in visits.columns:
                value = f"{_fmt(latest[column], decimals)} {unit}"
                metrics.append((label, value, _delta(latest, previous, column, decimals)))

        if metrics:
            for col, (label, value, delta) in zip(st.columns(len(metrics)), metrics):
                col.metric(label, value, delta=delta, delta_color="off")
        else:
            st.info("No vital-sign columns found for this patient.")

    with st.expander("Visit history"):
        history = visits.copy()
        history["visit_date"] = history["visit_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(history, hide_index=True)
