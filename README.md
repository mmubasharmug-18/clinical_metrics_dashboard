# Patient Summary Dashboard

Streamlit app where a clinician uploads a CSV of patient visits and gets:

- a summary table with one row per patient latest visit, colour-coded by risk level
- a filter by risk level, plus a search box for name or ID
- a detail view for the selected patient latest vitals, change since last visit, full visit history
- a vital-sign trend chart across that patient's visits

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

No file handy? Tick **Use sample data instead** in the sidebar. The sample is
synthetic (`python scripts/generate_sample_data.py` rebuilds it).

## CSV format

One row per visit, so a patient with 8 visits has 8 rows.

| Column | Required | Notes |
|---|---|---|
| `patient_id` | yes | |
| `visit_date` | yes | `YYYY-MM-DD` is safest, see dates below |
| `patient_name`, `age`, `gender` | no | |
| `systolic_bp`, `diastolic_bp`, `heart_rate`, `glucose`, `temperature`, `spo2` | no | each one present gets its own trend |
| `risk_level` | no | Low / Medium / High |
| `risk_score` | no | used to work out `risk_level` when that column is missing (Low < 35, Medium 35-60, High 60+) |

Header case and spacing don't matter (`Patient ID` works). Missing optional
columns are fine, the dashboard just shows less.

## Project layout

```
app.py                      entry point
src/
  config.py                 column names, risk colours, vital groups
  data_loader.py            CSV parsing and validation
  summary.py                one-row-per-patient table
  state.py                  keeps widget selections valid after filtering
  components/
    sidebar.py              upload, risk filter, search
    summary_table.py        metrics row + patient table
    patient_detail.py       patient picker + detail view
    trend_chart.py          vital-sign chart
data/sample_patients.csv    synthetic sample (40 patients)
scripts/generate_sample_data.py
tests/                      pytest
```

## Tests

```bash
pytest
```