# Clinical Metrics Dashboard — Widgets & Live Updates

A Streamlit app demonstrating widgets connected to live, session state driven
updates, built on the `patients_data_with_alerts.xlsx` dataset.

## What it does

- Sidebar patient selector and a 0-4 minimum active alerts slider, both
  bound to `st.session_state`.
- The patient table filters live as the slider moves, based on Alert_Count
  a derived 0-4 score: how many of a patient's four alert flags are
  currently active.
- The selected patient's vitals show as metric cards with a status badge
  per vital Normal = green, anything else = red.
- A comparison chart marks the selected patient's chosen vital sign against
  the population currently passing the slider filter so the chart reacts
  to both widgets, not just one.

## Why the threshold works the way it does

The dataset has no single numeric alert level field it has four
separate alert columns heart rate, SpO2, blood pressure, temperature,
each either Normal or not. Alert_Count is computed directly from those four
columns 0 = all normal, 4 = all flagged, which gives the slider something
real to filter on instead of a field that doesn't exist in the data.

## Setup

```bash
pip install -r requirements.txt
streamlit run clinical_metrics_dashboard_widgets.py
```

## Files

- `clinical_metrics_dashboard_widgets.py` — the application
- `patients_data_with_alerts.xlsx` — the dataset
- `requirements.txt` — dependencies (streamlit, pandas, altair, openpyxl)

## Known limitations

- One reading per patient, no visit history so live update here means
  widgets changing what's displayed instantly, not a real time-series trend.
- No age, glucose, or readmission risk score in the source data.
