from datetime import datetime

import pandas as pd
import pydeck as pdk
import streamlit as st

from location_monitoring.data_utils import (
    fetch_boxes_list,
    fetch_days_list,
    fetch_misplaced_boxes,
    fetch_location_list,
)


# def get_days():
#     return fetch_days_list()


# def get_boxes():
#     return fetch_boxes_list()


# def get_misplaced_boxes(day, clear_cache=False):
    # return fetch_misplaced_boxes(day, clear_cache=clear_cache)


st.set_page_config(page_title="ItemIT Box Locations", layout="wide")

days = fetch_days_list()
boxes = fetch_boxes_list()

st.write(
    """
    # ItemIT box location monitoring
    ## Misplaced boxes:
    ### Hello World
"""
)

day = st.sidebar.selectbox("Current Schedule Day:", days)

last_updated = datetime.now().strftime("%I:%M%p on %d %b '%y")

clear_cache = st.sidebar.button("Reload ItemIT data")
st.sidebar.write(f"""__Last updated:__ {last_updated}""")


with st.spinner("Loading data from ItemIT"):
    if clear_cache:
        df = fetch_misplaced_boxes(day=day, clear_cache=True)
    else:
        df = fetch_misplaced_boxes(day=day)

st.table(df)


### MAP ###
st.write(
    """
    ## Locations last seen:
"""
)

df_locs = fetch_location_list()

df_map = (
    df.reset_index()
    .merge(df_locs, how="left", left_on="location", right_on="name")
    .drop("name", axis=1)
)
df_map = df_map.dropna()
df_map["date"] = df_map["date"].apply(lambda x: x.strftime("%Y-%m-%d"))

initial_view_state = pdk.data_utils.compute_view(df_map[["lng", "lat"]])

icon_layer = pdk.Layer(
    "IconLayer",
    data=df_map,
    get_icon="icon_data",
    get_size=4,
    size_scale=12,
    get_position=["lng", "lat"],
    pickable=True,
)

tooltip = {
    "html": "<b>Box:</b> {box}<br/><b>Location:</b> {location}<br/><b>Last Seen:</b> {date}<br/><b>Last Seen By:</b> {last_seen_by}<br/>",
    "style": {"backgroundColor": "steelblue", "color": "white", "fontSize": "12px"},
}

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=initial_view_state,
        layers=[icon_layer],
        tooltip=tooltip,
    )
)
