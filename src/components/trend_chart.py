import altair as alt
import streamlit as st

from src.config import LABELS, VITALS
from src.state import keep_valid


def render(visits):
    st.header("Vital-Sign Trend")

    options = {
        label: cols for label, cols in VITALS.items()
        if any(c in visits.columns for c in cols)
    }
    if not options:
        st.info("No vital-sign columns found in this file.")
        return

    keep_valid("trend_vital", list(options))
    choice = st.selectbox("Vital sign", list(options), key="trend_vital")
    columns = [c for c in options[choice] if c in visits.columns]

    long = visits.melt(
        id_vars="visit_date", value_vars=columns, var_name="measure", value_name="value"
    ).dropna(subset=["value"])
    long["measure"] = long["measure"].map(lambda c: LABELS.get(c, c))

    if long.empty:
        st.info("This patient has no readings recorded for that vital sign.")
        return
    if long["visit_date"].nunique() < 2:
        st.info("Only one reading on record. A trend needs at least two visits.")

    chart = (
        alt.Chart(long)
        .mark_line(point=True)
        .encode(
            x=alt.X("visit_date:T", title="Visit date"),
            y=alt.Y("value:Q", title=choice, scale=alt.Scale(zero=False)),
            color=alt.Color(
                "measure:N", title=None,
                legend=alt.Legend(orient="top") if len(columns) > 1 else None,
            ),
            tooltip=[
                alt.Tooltip("visit_date:T", title="Visit"),
                alt.Tooltip("measure:N", title="Measure"),
                alt.Tooltip("value:Q", title="Value"),
            ],
        )
        .properties(height=340)
    )
    st.altair_chart(chart)