import warnings

import pandas as pd

from src.config import NUMERIC_COLUMNS, REQUIRED_COLUMNS, RISK_BINS, RISK_ORDER


class CSVLoadError(ValueError):
    """The uploaded file can't be turned into patient data."""


def _clean_headers(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


# 01/02/2025 style dates where day and month are both 12 or less can't be told apart
_AMBIGUOUS_DATE = r"^\s*(0?[1-9]|1[0-2])[/.-](0?[1-9]|1[0-2])[/.-]\d{2,4}\s*$"


def _parse_dates(series, notes):
    """Parse visit dates, working out whether the file is month-first or day-first."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        month_first = pd.to_datetime(series, errors="coerce")
        day_first = pd.to_datetime(series, errors="coerce", dayfirst=True)

    if day_first.isna().sum() < month_first.isna().sum():
        notes.append("Dates look like day/month/year, so they were read that way.")
        return day_first

    text = series.astype("string")
    parts = text.str.extract(_AMBIGUOUS_DATE)
    if (parts[0].notna() & (parts[0] != parts[1])).any():
        notes.append(
            "Some dates (like 01/02/2025) could be day/month or month/day. "
            "They were read as month/day; use YYYY-MM-DD dates if that's wrong."
        )
    return month_first


def load_patient_csv(source):
    """Read a patient CSV. Returns (dataframe, list of notes about what was fixed/skipped)."""
    notes = []

    try:
        df = pd.read_csv(source, encoding_errors="replace")
    except pd.errors.EmptyDataError:
        raise CSVLoadError("The file is empty.")
    except pd.errors.ParserError as err:
        raise CSVLoadError(f"This doesn't look like a valid CSV: {err}")

    df = _clean_headers(df)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise CSVLoadError(
            "Missing required column(s): " + ", ".join(missing)
            + ". Found: " + ", ".join(df.columns)
        )
    if df.empty:
        raise CSVLoadError("The file has headers but no rows.")

    df["visit_date"] = _parse_dates(df["visit_date"], notes)
    df["patient_id"] = df["patient_id"].astype("string").str.strip()

    bad = df["visit_date"].isna() | df["patient_id"].isna() | (df["patient_id"] == "")
    if bad.any():
        notes.append(f"Skipped {int(bad.sum())} row(s) with a missing patient_id or unreadable visit_date.")
        df = df[~bad]
    if df.empty:
        raise CSVLoadError("No usable rows: every row had a bad patient_id or visit_date.")

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = _add_risk_level(df, notes)
    df = df.sort_values(["patient_id", "visit_date"]).reset_index(drop=True)
    df["patient_id"] = df["patient_id"].astype(str)
    return df, notes


def _add_risk_level(df, notes):
    if "risk_level" in df.columns:
        level = df["risk_level"].astype("string").str.strip().str.title()
        unknown = ~level.isin(RISK_ORDER)
        if unknown.any():
            notes.append(f"{int(unknown.sum())} row(s) had a risk_level other than Low/Medium/High; shown as Unknown.")
        df["risk_level"] = level.where(~unknown, "Unknown").astype(str)
    elif "risk_score" in df.columns:
        df["risk_level"] = (
            pd.cut(df["risk_score"], bins=RISK_BINS, labels=RISK_ORDER, right=False)
            .astype("string")
            .fillna("Unknown")
            .astype(str)
        )
        notes.append("No risk_level column, so it was worked out from risk_score (Low < 35, Medium 35-60, High 60+).")
    else:
        df["risk_level"] = "Unknown"
        notes.append("No risk_level or risk_score column found, so risk filtering is unavailable.")
    return df
