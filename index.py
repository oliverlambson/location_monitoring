import streamlit as st
import plotly.graph_objects as go

from location_monitoring.data_utils import (
    fetch_days_list,
    fetch_boxes_list,
    get_misplaced_boxes,
)

st.set_page_config(page_title="ItemIT Box Locations", layout="wide")

days = fetch_days_list()
boxes = fetch_boxes_list()

st.write(
    """
    # ItemIT box location monitoring
    ## Misplaced boxes:
"""
)

day = st.sidebar.selectbox("Day", days)

df = get_misplaced_boxes(day=day)
st.table(df)
