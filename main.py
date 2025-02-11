from numpy import select
import streamlit as st
from app.utils import detect_columns, load_log
from app.components.sidebar_filter import sidebar_filter, apply_filters
from app.components.overview import overview

def app():
    """Main application logic."""
    st.set_page_config(layout="wide", page_title="ProM Workstation", page_icon="📊")
    st.title("📊 ProM Workstation")

    uploaded_log = st.file_uploader("Upload a file", type=["csv", "xes"])

    if uploaded_log:
        log = load_log(uploaded_log)
        if log is None:
            st.error("Invalid file format. Please upload a valid CSV or XES file.")
            return

        overview_tab, dfg_tab, inductive_tab = st.tabs(["Overview", "Directly-Follows Graph", "Inductive Miner"])
        column_map = detect_columns(log)
        case_col, activity_col, timestamp_col, resource_col = (
            column_map["case_id"], column_map["activity"], column_map["timestamp"], column_map["resource"]
        )

        if not case_col or not activity_col:
            st.error("Missing essential columns (case/activity). Please check the data format.")
            return

        # Render sidebar filters
        start_event, end_event, selected_resources, selected_activities, selected_columns = sidebar_filter(log, column_map)

        # Apply filters
        filtered_log = apply_filters(log, case_col, activity_col, resource_col, start_event, end_event, selected_resources, selected_activities)[selected_columns]

        # Layout: Preview, Statistics, Distributions
        with overview_tab:
            overview(filtered_log, column_map)

        with dfg_tab:
            st.write("### Directly-Follows Graph")
            st.write("Coming soon...")

        with inductive_tab:
            st.write("### Inductive Miner")
            st.write("Coming soon...")


if __name__ == "__main__":
    app()
