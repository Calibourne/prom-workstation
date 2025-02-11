import re
import time
from app.utils import safe_exec
import streamlit as st
import pandas as pd


@safe_exec
def dist_viz(viz_col, log):
    """Displays bar chart for activity or resource distribution."""
    
    activity_counts = log[viz_col].value_counts().reset_index()
    if ":" in viz_col:
        viz_col = viz_col.replace(":", " ")

    activity_counts.columns = [viz_col, "Count"]
    
    activity_counts = activity_counts.sort_values(by="Count", ascending=False)
    st.bar_chart(activity_counts.set_index(viz_col))


def render_preview(filtered_log, case_col):
    """Displays a preview of the filtered log."""
    st.write("### 🔍 Log View")

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

    if resource_col in filtered_log.columns and filtered_log[resource_col].notna().sum() > 0:
        top_resource = filtered_log[resource_col].value_counts().idxmax()
        stats_dict["Metric"].append("Top Resource")
        stats_dict["Value"].append(str(top_resource))
    else:
        stats_dict["Metric"].append("Top Resource")
        stats_dict["Value"].append("N/A")

    stats_df = pd.DataFrame(stats_dict).set_index("Metric")
    st.dataframe(stats_df)


@safe_exec
def render_distributions(filtered_log, column_map):
    """Displays activity or resource distribution based on user selection."""
    
    resource_col = column_map.get("resource")
    activity_col = column_map.get("activity")
    timestamp_col = column_map.get("timestamp")
    case_col = column_map.get("case_id")
    
    st.write("### 🔄 Distributions")

    # Ensure columns exist before visualizing
    has_activities = activity_col in filtered_log.columns
    has_resources = resource_col and resource_col in filtered_log.columns

    columns = [
        col for col in filtered_log.columns if col not in [activity_col, resource_col, timestamp_col, case_col]
    ]

    columns.append(activity_col) if has_activities else None
    columns.append(resource_col) if has_resources else None


    dist_tabs = st.tabs(columns)
    for col, tab in zip(columns, dist_tabs):
        if col:
            with tab:
                dist_viz(col, filtered_log)

def overview(filtered_log, column_map):
    """Generates the overview section, including preview, statistics, and distributions."""

    case_col = column_map["case_id"]
    activity_col = column_map["activity"]
    timestamp_col = column_map["timestamp"]
    resource_col = column_map["resource"]
    
    preview_section, stats_section, viz_section = st.columns([4, 2, 3])

    with preview_section:
        render_preview(filtered_log, case_col)

    with stats_section:
        render_statistics(filtered_log, case_col, activity_col, timestamp_col, resource_col)

    with viz_section:
        render_distributions(filtered_log, column_map)
