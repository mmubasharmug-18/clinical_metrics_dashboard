import io

import pandas as pd
import pytest

from src.data_loader import CSVLoadError, load_patient_csv


def load(text):
    return load_patient_csv(io.StringIO(text))


def test_loads_basic_file_and_sorts_by_patient_then_date():
    df, notes = load(
        "patient_id,visit_date,heart_rate,risk_level\n"
        "P2,2025-03-01,80,High\n"
        "P1,2025-02-01,70,Low\n"
        "P1,2025-01-01,72,Low\n"
    )
    assert list(df["patient_id"]) == ["P1", "P1", "P2"]
    assert list(df[df["patient_id"] == "P1"]["heart_rate"]) == [72, 70]
    assert notes == []


def test_headers_are_normalised():
    df, _ = load("Patient ID, Visit Date ,Heart Rate\nP1,2025-01-01,70\n")
    assert {"patient_id", "visit_date", "heart_rate"} <= set(df.columns)


def test_excel_bom_does_not_break_first_column():
    df, _ = load_patient_csv(io.BytesIO("\ufeffpatient_id,visit_date\nP1,2025-01-01\n".encode("utf-8")))
    assert "patient_id" in df.columns


def test_missing_required_column_raises_with_helpful_message():
    with pytest.raises(CSVLoadError, match="visit_date"):
        load("patient_id,heart_rate\nP1,70\n")


def test_empty_file_raises():
    with pytest.raises(CSVLoadError, match="empty"):
        load("")


def test_header_only_file_raises():
    with pytest.raises(CSVLoadError, match="no rows"):
        load("patient_id,visit_date\n")


def test_bad_dates_and_blank_ids_are_skipped_with_a_note():
    df, notes = load(
        "patient_id,visit_date\n"
        "P1,2025-01-01\n"
        "P1,not-a-date\n"
        ",2025-01-02\n"
    )
    assert len(df) == 1
    assert any("Skipped 2" in n for n in notes)


def test_all_rows_bad_raises():
    with pytest.raises(CSVLoadError, match="No usable rows"):
        load("patient_id,visit_date\nP1,garbage\n")


def test_non_numeric_vitals_become_nan_not_errors():
    df, _ = load("patient_id,visit_date,heart_rate\nP1,2025-01-01,abc\nP1,2025-01-02,75\n")
    assert pd.isna(df["heart_rate"].iloc[0])
    assert df["heart_rate"].iloc[1] == 75


def test_risk_level_is_cleaned():
    df, notes = load(
        "patient_id,visit_date,risk_level\n"
        "P1,2025-01-01, high \n"
        "P2,2025-01-01,LOW\n"
        "P3,2025-01-01,critical\n"
    )
    assert list(df["risk_level"]) == ["High", "Low", "Unknown"]
    assert any("Unknown" in n for n in notes)


def test_risk_level_derived_from_score_when_missing():
    df, notes = load(
        "patient_id,visit_date,risk_score\n"
        "P1,2025-01-01,10\n"
        "P2,2025-01-01,35\n"
        "P3,2025-01-01,59.9\n"
        "P4,2025-01-01,60\n"
        "P5,2025-01-01,\n"
    )
    assert list(df["risk_level"]) == ["Low", "Medium", "Medium", "High", "Unknown"]
    assert any("worked out from risk_score" in n for n in notes)


def test_no_risk_columns_gives_unknown_and_a_note():
    df, notes = load("patient_id,visit_date\nP1,2025-01-01\n")
    assert list(df["risk_level"]) == ["Unknown"]
    assert notes


def test_day_first_dates_are_detected():
    df, notes = load("patient_id,visit_date\nP1,01/02/2025\nP1,15/03/2025\n")
    assert list(df["visit_date"].dt.strftime("%Y-%m-%d")) == ["2025-02-01", "2025-03-15"]
    assert any("day/month/year" in n for n in notes)


def test_iso_dates_need_no_note():
    df, notes = load("patient_id,visit_date,risk_level\nP1,2025-02-01,Low\nP1,2025-03-15,Low\n")
    assert list(df["visit_date"].dt.strftime("%Y-%m-%d")) == ["2025-02-01", "2025-03-15"]
    assert notes == []


def test_ambiguous_slash_dates_get_a_warning():
    df, notes = load("patient_id,visit_date\nP1,01/02/2025\nP1,03/04/2025\n")
    assert df["visit_date"].iloc[0].month == 1   # read as month/day
    assert any("could be day/month or month/day" in n for n in notes)


def test_same_day_and_month_is_not_ambiguous():
    _, notes = load("patient_id,visit_date,risk_level\nP1,05/05/2025,Low\n")
    assert notes == []
