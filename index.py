from datetime import datetime

import streamlit as st

from location_monitoring.data_utils import (
    fetch_boxes_list,
    fetch_days_list,
    fetch_misplaced_boxes,
)


def get_days():
    return fetch_days_list()


def get_boxes():
    return fetch_boxes_list()


def get_misplaced_boxes(day, clear_cache=False):
    return fetch_misplaced_boxes(day, clear_cache=clear_cache)


st.set_page_config(page_title="ItemIT Box Locations", layout="wide")

days = get_days()
boxes = get_boxes()

st.write(
    """
    # ItemIT box location monitoring
    ## Misplaced boxes:
"""
)

day = st.sidebar.selectbox("Current Schedule Day:", days)

last_updated = datetime.now().strftime("%I:%M%p on %d %b '%y")

clear_cache = st.sidebar.button("Reload ItemIT data")
st.sidebar.write(f"""__Last updated:__ {last_updated}""")


with st.spinner("Loading data from ItemIT..."):
    if clear_cache:
        df = get_misplaced_boxes(day=day, clear_cache=True)
    else:
        df = get_misplaced_boxes(day=day)

st.table(df)
