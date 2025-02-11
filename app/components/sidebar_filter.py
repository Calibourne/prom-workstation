import streamlit as st
from app.utils import safe_exec

def sidebar_filter(log, column_map):
    """Renders sidebar filters for log analysis."""
    st.sidebar.write("### 🔧 Log Filters")
    activity_col, resource_col = column_map.get("activity"), column_map.get("resource")
    timestamp_col, case_col = column_map.get("timestamp"), column_map.get("case_id")
    
    mandatory_columns = [case_col, activity_col, timestamp_col]
    additional_columns = list(set(log.columns.tolist()) - set(mandatory_columns))
    selected_columns = st.sidebar.multiselect(
        "Select Columns to Display:", 
        additional_columns, default=additional_columns
    )

    available_activities = log[activity_col].unique().tolist() if activity_col in log.columns else []
    available_resources = log[resource_col].unique().tolist() if resource_col in log.columns else []

    start_event = st.sidebar.selectbox("Select Start Event:", ["All"] + available_activities)
    end_event = st.sidebar.selectbox("Select End Event:", ["All"] + available_activities)

    with st.sidebar.expander("Resource Filter"):
        selected_resources = (
            st.multiselect("Select Resources:", available_resources, default=available_resources)
            if resource_col else []
        )

    with st.sidebar.expander("Activity Filter"):
        selected_activities = st.multiselect("Select Activities:", available_activities, default=available_activities)

    return start_event, end_event, selected_resources, selected_activities, list(set(selected_columns).union(set(mandatory_columns)))


@safe_exec
def apply_filters(log, case_col, activity_col, resource_col, start_event, end_event, selected_resources, selected_activities):
    """Applies user-selected filters to the log."""
    filtered_log = log.copy()

    if start_event != "All":
        start_cases = filtered_log.groupby(case_col)[activity_col].transform("first") == start_event
        filtered_log = filtered_log[start_cases]

    if end_event != "All":
        end_cases = filtered_log.groupby(case_col)[activity_col].transform("last") == end_event
        filtered_log = filtered_log[end_cases]

    if selected_resources and resource_col:
        filtered_log = filtered_log[filtered_log[resource_col].isin(selected_resources)]

    if selected_activities and activity_col:
        filtered_log = filtered_log[filtered_log[activity_col].isin(selected_activities)]

    return filtered_log
