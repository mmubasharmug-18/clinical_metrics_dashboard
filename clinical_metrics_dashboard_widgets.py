import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Clinical Metrics Dashboard", layout="wide")

DATA_PATH = "patients_data_with_alerts.xlsx"

RENAME_MAP = {
    "Patient Number": "Patient_ID",
    "Heart Rate (bpm)": "Heart_Rate",
    "SpO2 Level (%)": "SpO2",
    "Systolic Blood Pressure (mmHg)": "Systolic_BP",
    "Diastolic Blood Pressure (mmHg)": "Diastolic_BP",
    "Body Temperature (°C)": "Temperature",
    "Fall Detection": "Fall_Detected",
    "Predicted Disease": "Predicted_Disease",
    "Data Accuracy (%)": "Data_Accuracy",
    "Heart Rate Alert": "HR_Alert",
    "SpO2 Level Alert": "SpO2_Alert",
    "Blood Pressure Alert": "BP_Alert",
    "Temperature Alert": "Temp_Alert",
}

ALERT_COLS = ["HR_Alert", "SpO2_Alert", "BP_Alert", "Temp_Alert"]

VITALS = {
    "Heart_Rate": "Heart Rate (bpm)",
    "SpO2": "SpO2 (%)",
    "Systolic_BP": "Systolic BP (mmHg)",
    "Diastolic_BP": "Diastolic BP (mmHg)",
    "Temperature": "Temperature (°C)",
}


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=RENAME_MAP)
    df["Alert_Count"] = (df[ALERT_COLS] != "Normal").sum(axis=1)
    return df


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"""Couldn't find '{DATA_PATH}'. Place the patient data file in the same
        folder as this script (or update DATA_PATH above) and reload."""
    )
    st.stop()

st.markdown(
    """
    <style>
    h1 { text-align: center; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Clinical Metrics Dashboard")

st.session_state.setdefault("selected_patient", int(df["Patient_ID"].iloc[0]))
st.session_state.setdefault("alert_threshold", 0)

st.sidebar.header("Filters")

patients = sorted(df["Patient_ID"].unique())

st.sidebar.selectbox("Select Patient", patients, key="selected_patient")

st.sidebar.slider(
    "Minimum active alerts out of 4",
    min_value=0,
    max_value=4,
    key="alert_threshold",
    help="Shows patients with at least this many non-Normal alert flags.",
)

st.header("Patient Metrics")

filtered_df = df[df["Alert_Count"] >= st.session_state.alert_threshold]
st.caption(f"Showing {len(filtered_df):,} of {len(df):,} patients with "
           f"at least {st.session_state.alert_threshold} active alert(s).")

display_cols = [
    "Patient_ID", "Heart_Rate", "SpO2", "Systolic_BP", "Diastolic_BP",
    "Temperature", "Predicted_Disease", "Alert_Count",
    "HR_Alert", "SpO2_Alert", "BP_Alert", "Temp_Alert",
]


def highlight_alerts(val):
    if val in ("High", "Low", "Abnormal"):
        return "background-color: #ffcccc; color: #000000; font-weight: 600"
    if val == "Normal":
        return "background-color: #ccffcc; color: #000000; font-weight: 600"
    return ""


styled = filtered_df[display_cols].head(500).style.map(highlight_alerts, subset=ALERT_COLS)
st.dataframe(styled, use_container_width=True, height=350)
if len(filtered_df) > 500:
    st.caption("Table capped at the first 500 matching rows for display performance.")

st.header("Selected Patient")

patient_row = df[df["Patient_ID"] == st.session_state.selected_patient].iloc[0]

st.write(f"**Patient:** {st.session_state.selected_patient}  |  "
         f"**Active alerts:** {patient_row['Alert_Count']} of 4  |  "
         f"**Predicted disease:** {patient_row['Predicted_Disease']}")

metric_cols = st.columns(5)
metric_specs = [
    ("Heart Rate", "Heart_Rate", "bpm", patient_row["HR_Alert"]),
    ("SpO2", "SpO2", "%", patient_row["SpO2_Alert"]),
    ("Systolic BP", "Systolic_BP", "mmHg", patient_row["BP_Alert"]),
    ("Diastolic BP", "Diastolic_BP", "mmHg", patient_row["BP_Alert"]),
    ("Temperature", "Temperature", "°C", patient_row["Temp_Alert"]),
]
for col, (label, field, unit, alert) in zip(metric_cols, metric_specs):
    col.metric(label, f"{patient_row[field]:.1f} {unit}")
    badge_bg = "#1b5e20" if alert == "Normal" else "#7a1f1f"
    badge_text = "#a5d6a7" if alert == "Normal" else "#ffcdd2"
    col.markdown(
        f"<span style='background-color:{badge_bg}; color:{badge_text}; "
        f"padding:2px 10px; border-radius:12px; font-weight:600; font-size:0.85rem'>"
        f"{alert}</span>",
        unsafe_allow_html=True,
    )

st.header("Vital Sign Comparison")

vital_choice = st.selectbox("Select Vital Sign", list(VITALS.keys()), format_func=lambda k: VITALS[k])

patient_value = patient_row[vital_choice]

if filtered_df.empty:
    st.warning("No patients meet the current alert threshold to compare against.")
else:
    hist = (
        alt.Chart(filtered_df)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(f"{vital_choice}:Q", bin=alt.Bin(maxbins=40), title=VITALS[vital_choice]),
            y=alt.Y("count()", title="Number of patients"),
        )
    )
    marker = (
        alt.Chart(pd.DataFrame({vital_choice: [patient_value]}))
        .mark_rule(color="red", size=3)
        .encode(x=f"{vital_choice}:Q")
    )
    st.altair_chart((hist + marker).properties(height=320), use_container_width=True)
    st.caption(
        f"Red line: Patient {st.session_state.selected_patient}'s {VITALS[vital_choice]} "
        f"({patient_value:.1f}), against the {len(filtered_df):,} patients currently meeting "
        f"the alert-threshold filter above."
    )

st.caption("Dashboard built on patients_data_with_alerts.")