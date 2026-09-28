import io

from src.data_loader import load_patient_csv
from src.summary import build_patient_summary

CSV = """patient_id,patient_name,visit_date,systolic_bp,risk_score,risk_level
P1,Ann,2025-01-01,120,20,Low
P1,Ann,2025-03-01,150,70,High
P1,Ann,2025-02-01,130,40,Medium
P2,Bob,2025-01-15,110,10,Low
"""


def summary():
    df, _ = load_patient_csv(io.StringIO(CSV))
    return build_patient_summary(df)


def test_one_row_per_patient():
    s = summary()
    assert list(s["patient_id"]) == ["P1", "P2"]


def test_uses_latest_visit_not_last_row_in_file():
    row = summary().set_index("patient_id").loc["P1"]
    assert row["systolic_bp"] == 150
    assert row["risk_level"] == "High"
    assert str(row["last_visit"].date()) == "2025-03-01"


def test_visit_count():
    s = summary().set_index("patient_id")
    assert s.loc["P1", "visits"] == 3
    assert s.loc["P2", "visits"] == 1
