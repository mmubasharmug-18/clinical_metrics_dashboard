SUMMARY_COLUMNS = [
    "patient_id", "patient_name", "age", "gender", "visits", "last_visit",
    "systolic_bp", "diastolic_bp", "heart_rate", "glucose",
    "temperature", "spo2", "risk_score", "risk_level",
]


def build_patient_summary(df):
    """One row per patient, using their most recent visit."""
    ordered = df.sort_values(["patient_id", "visit_date"])
    grouped = ordered.groupby("patient_id")

    latest = grouped.tail(1).set_index("patient_id")
    latest["visits"] = grouped.size()
    latest = latest.rename(columns={"visit_date": "last_visit"}).reset_index()

    keep = [c for c in SUMMARY_COLUMNS if c in latest.columns]
    return latest[keep]
