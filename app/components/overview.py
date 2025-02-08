import re
from app.utils import safe_exec
import streamlit as st
import pandas as pd


@safe_exec
def dist_viz(viz_col, log):
    """Displays bar chart for categorical distribution."""
    if viz_col in log.columns:
        st.write(f"### 📊 {viz_col} Distribution")

        # Drop NaNs and check if there's any data left
        value_counts = log[viz_col].dropna().value_counts().reset_index()
        value_counts.columns = [viz_col, "Count"]

        if value_counts.empty:
            st.warning(f"No valid data available for {viz_col}.")
            return

        # Ensure categories are properly sorted
        value_counts = value_counts.sort_values(by="Count", ascending=False)
        value_counts[viz_col] = pd.Categorical(value_counts[viz_col], categories=value_counts[viz_col], ordered=True)

        st.bar_chart(value_counts.set_index(viz_col))
    else:
        st.warning(f"Column {viz_col} does not exist in the dataset.")


def render_preview(filtered_log, case_col):
    """Displays a preview of the filtered log."""
    st.write("### 🔍 Preview of Log")

    if case_col in filtered_log.columns:
        st.dataframe(filtered_log.set_index(case_col))
    else:
        st.dataframe(filtered_log)


@safe_exec
def render_statistics(filtered_log, case_col, activity_col, timestamp_col, resource_col):
    """Displays computed statistics about the log."""
    st.write("### 📊 Log Statistics")

    stats_dict = {
        "Metric": ["Total Events", "Unique Cases", "Unique Activities"],
        "Value": [str(len(filtered_log)), str(filtered_log[case_col].nunique()), str(filtered_log[activity_col].nunique())],
    }

    if timestamp_col:
        temp_log = filtered_log.copy()  # Prevent modifying original DataFrame
        temp_log[timestamp_col] = pd.to_datetime(temp_log[timestamp_col])

        stats_dict["Metric"] += ["Time Range Start", "Time Range End", "Avg Case Duration"]
        stats_dict["Value"] += [
            temp_log[timestamp_col].min().isoformat(),  # Convert to string
            temp_log[timestamp_col].max().isoformat(),  # Convert to string
            str((temp_log.groupby(case_col)[timestamp_col].max() - temp_log.groupby(case_col)[timestamp_col].min()).mean())  # Convert to string
        ]

    if resource_col and filtered_log[resource_col].notna().sum() > 0:
        top_resource = filtered_log[resource_col].value_counts().idxmax()
        stats_dict["Metric"].append("Top Resource")
        stats_dict["Value"].append(str(top_resource))

    stats_df = pd.DataFrame(stats_dict).set_index("Metric")
    st.dataframe(stats_df)


@safe_exec
def render_distributions(filtered_log, column_map):
    """Displays activity or resource distribution based on user selection."""
    
    resource_col = column_map.get("resource")
    activity_col = column_map.get("activity")
    
    st.write("### 🔄 Distribution")

    # Ensure columns exist before visualizing
    has_activities = activity_col in filtered_log.columns
    has_resources = resource_col and resource_col in filtered_log.columns

    if has_resources:
        activities, resources = st.tabs(["Activities", "Resources"])
    else:
        activities = st.empty()

    if has_activities:
        with activities:
            dist_viz(activity_col, filtered_log)

    if has_resources:
        with resources:
            dist_viz(resource_col, filtered_log)
    elif not has_activities:
        st.warning("No valid activity or resource column found for visualization.")


def overview(filtered_log, column_map):
    """Generates the overview section, including preview, statistics, and distributions."""

    case_col = column_map["case_id"]
    activity_col = column_map["activity"]
    timestamp_col = column_map["timestamp"]
    resource_col = column_map["resource"]
    
    preview_section, stats_section, viz_section = st.columns([5, 2, 3])

    with preview_section:
        render_preview(filtered_log, case_col)

    with stats_section:
        render_statistics(filtered_log, case_col, activity_col, timestamp_col, resource_col)

    with viz_section:
        render_distributions(filtered_log, column_map)
