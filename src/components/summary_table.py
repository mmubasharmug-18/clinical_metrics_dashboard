import streamlit as st

from src.config import LABELS, RISK_COLORS


def _risk_style(value):
    color = RISK_COLORS.get(value)
    if color is None:
        return ""
    return f"background-color: {color}; color: #000000; font-weight: 600"


def render(summary, total_patients):
    st.header("Patient Summary")

    cols = st.columns(4)
    cols[0].metric("Patients shown", f"{len(summary)} of {total_patients}")
    cols[1].metric(
        "High risk",
        int((summary["risk_level"] == "High").sum())
    )

    if "age" in summary.columns:
        cols[2].metric(
            "Average age",
            f"{summary['age'].mean():.0f}"
        )

    if "risk_score" in summary.columns:
        cols[3].metric(
            "Average risk score",
            f"{summary['risk_score'].mean():.1f}"
        )

    table = summary.copy()

    if "last_visit" in table.columns:
        table["last_visit"] = table["last_visit"].dt.strftime("%Y-%m-%d")

    table = table.rename(columns=LABELS)

    display_table = table.head(1000).copy()

    styled = display_table.style.map(
        _risk_style,
        subset=[LABELS["risk_level"]]
    )

    st.dataframe(
        styled,
        hide_index=True,
        use_container_width=True
    )

    # Inform user when results are truncated
    if len(table) > 1000:
        st.info(
            f"Showing first 1,000 of {len(table):,} patients. "
            "Use the filters to narrow the results."
        )