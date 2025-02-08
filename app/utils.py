from textwrap import wrap
import os
import tempfile
import re
import pandas as pd
from pm4py import format_dataframe
import pm4py as pm
import streamlit as st

def safe_exec(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return None
    return wrapper
    

def detect_columns(df):
    """Dynamically detect column names based on heuristics."""
    col_mapping = {
        "case_id": next((col for col in df.columns if "case" in col.lower()), None),
        # cactivity is either "activity" or "concept:name" in the column name (without case prefix)
        "activity": next((col for col in df.columns 
                          if "activity" in col.lower() or 
                          ("concept:name" in col.lower() and "case" not in col.lower())), None),
        
        "timestamp": next((col for col in df.columns if "time" in col.lower() or "timestamp" in col.lower()), None),
        "resource": next((col for col in df.columns if "resource" in col.lower()), None),
    }
    return col_mapping

@st.cache_data
def process_csv(file):
    df = pd.read_csv(file)
    with st.popover("CSV Column Selection"):
        st.write("Uploaded CSV file:", df.head())
        case_col = st.selectbox("Select the case column:", df.columns, index=next((i for i, col in enumerate(df.columns) if 'case' in col.lower()), 0))
        activity_col = st.selectbox("Select the activity column:", df.columns, index=next((i for i, col in enumerate(df.columns) if 'activity' in col.lower()), 0))
        timestamp_col = st.selectbox("Select the timestamp column:", df.columns, index=next((i for i, col in enumerate(df.columns) if 'time' in col.lower()), -1))
    
    log = format_dataframe(
        df, case_id=case_col, activity_key=activity_col, timestamp_key=timestamp_col
    )
    return log

@st.cache_data
def process_xes(file):
    """
    Process an uploaded XES file using PM4Py and clean up temporary files.

    Args:
        file (UploadedFile): The uploaded XES file.

    Returns:
        log: The parsed event log.
    """
    temp_file_path = None
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xes") as temp_file:
            temp_file.write(file.read())  # Write the file content to temp file
            temp_file.flush()  # Ensure all content is written
            temp_file_path = temp_file.name

        # Read the XES file using PM4Py
        log = pm.read_xes(temp_file_path)
        st.success("Uploaded XES file successfully processed.")

    finally:
        # Cleanup: Delete the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    return log


@safe_exec
def load_log(uploaded_log):
    """Loads the log file based on its extension."""
    if uploaded_log.name.endswith(".csv"):
        return process_csv(uploaded_log)
    elif uploaded_log.name.endswith(".xes"):
        return process_xes(uploaded_log)
    return None
