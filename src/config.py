from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PATH = ROOT / "data" / "sample_patients.csv"

# a file without these can't be used at all
REQUIRED_COLUMNS = ["patient_id", "visit_date"]

NUMERIC_COLUMNS = [
    "age", "systolic_bp", "diastolic_bp", "heart_rate",
    "glucose", "temperature", "spo2", "risk_score",
]

# used only when the file has risk_score but no risk_level:
# Low < 35 <= Medium < 60 <= High
RISK_ORDER = ["Low", "Medium", "High"]
RISK_BINS = [float("-inf"), 35, 60, float("inf")]

RISK_COLORS = {
    "Low": "#c8e6c9",
    "Medium": "#fff3b0",
    "High": "#ffcdd2",
    "Unknown": "#e0e0e0",
}

LABELS = {
    "patient_id": "Patient ID",
    "patient_name": "Name",
    "age": "Age",
    "gender": "Gender",
    "visits": "Visits",
    "last_visit": "Last visit",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "heart_rate": "Heart rate",
    "glucose": "Glucose",
    "temperature": "Temp (°C)",
    "spo2": "SpO2 (%)",
    "risk_score": "Risk score",
    "risk_level": "Risk level",
}

# label shown in the trend dropdown -> columns plotted
VITALS = {
    "Blood pressure (mmHg)": ["systolic_bp", "diastolic_bp"],
    "Heart rate (bpm)": ["heart_rate"],
    "Glucose (mg/dL)": ["glucose"],
    "Temperature (°C)": ["temperature"],
    "SpO2 (%)": ["spo2"],
}
