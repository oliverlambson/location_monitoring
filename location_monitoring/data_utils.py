import json
from functools import lru_cache
from typing import List

import pandas as pd
import requests
from decouple import config

WORKSPACE_ID = config("ITEMIT_WORKSPACE_ID", default="")
USER_ID = config("ITEMIT_USER_ID", default="")
TOKEN_VALUE = config("ITEMIT_TOKEN_VALUE", default="")
API_KEY = config("ITEMIT_API_KEY", default="")
API_SECRET = config("ITEMIT_API_SECRET", default="")

HEADERS = {
    "workspaceId": WORKSPACE_ID,
    "userId": USER_ID,
    "tokenValue": TOKEN_VALUE,
    "apiKey": API_KEY,
    "apiSecret": API_SECRET,
}

FILTERS = {
    "allOf": [
        {
            "anyOf": [
                {
                    "where": "COLLECTION",
                    "has": {"name": "Drop-Off Point Box"},
                },
                {
                    "where": "COLLECTION",
                    "has": {"name": "Delivery Box - Red"},
                },
            ]
        },
        {"allOf": []},
        {"noneOf": []},
    ]
}

loc_map = {
    "*West-Forvie Building": "WFB",
    "Box Storage Room": "WFB",
    "Goods In": "WFB",
    "Overflow": "WFB",
    "Production Lines": "WFB",
    "Anne McLaren Building": "AMB",
    "CUED Pod": None,
    "Christs College": "Colleges",
    "Churchill College": "Colleges",
    "Clare College": "Colleges",
    "Clare Colony": "Colleges",
    "Clare Hall": "Colleges",
    "Corpus Christi Main Plodge": "Colleges",
    "Corpus Leckhampton": "Colleges",
    "Damaged": None,
    "Darwin College": "Colleges",
    "Downing Main Plodge": "Colleges",
    "Drop-Off Pods": "DO",
    "Engineering Pod": "DO",
    "Homerton Pod": "DO",
    "Jesus Pod": "DO",
    "Johns Pod": "DO",
    "Newnham Pod": "DO",
    "Wychfield Pod": "DO",
    "Emmanuel Main Plodge": "Colleges",
    "Fitzwilliam College": "Colleges",
    "Girton College": "Colleges",
    "Gonville & Caius College": "Colleges",
    "Homerton Main Plodge": "Colleges",
    "Homterton Pod": None,
    "Hughes Hall": "Colleges",
    "In Transit": "UMS",
    "In-Transit Paul": "UMS",
    "Jesus College": "Colleges",
    "Kings Main Plodge": "Colleges",
    "Lost": None,
    "Lucy Cavendish": "Colleges",
    "MBIT": None,
    "Magdalene College": "Colleges",
    "Murray Edwards College": "Colleges",
    "Newnham College": "Colleges",
    "Pembroke Main Plodge": "Colleges",
    "Peterhouse Main Plodge": "Colleges",
    "Queens Owlstone Croft": "Colleges",
    "Queens' College": "Colleges",
    "Ridley Hall": "Colleges",
    "Robinson College": "Colleges",
    "Selwyn College": "Colleges",
    "Sidney Sussex College": "Colleges",
    "St Catherine’s Main Plodge": "Colleges",
    "St Catherine’s St Chads": "Colleges",
    "St Edmunds College": "Colleges",
    "St Johns College": "Colleges",
    "Test Site": None,
    "Trinity College": "Colleges",
    "Trinity Hall": "Colleges",
    "Wesley House": "Colleges",
    "Westcot House": "Colleges",
    "Westfield House": "Colleges",
    "Westminster College": "Colleges",
    "Wolfson College": "Colleges",
}


def fetch_location_list():
    url = "https://server.itemit.com/collections/itemit/v2.0/locations/hierarchy"
    payload = {}
    response = requests.request("GET", url, headers=HEADERS, data=payload)
    response.raise_for_status()
    locations = response.json()
    location_list = []
    for location in locations:
        location_list.append(location["location"]["name"])
        if location["nodes"]:
            for node in location["nodes"]:
                location_list.append(node["location"]["name"])
    return location_list


def fetch_group_schedule():
    return pd.read_excel(
        "UMS_Courier_Schedules.xlsx", sheet_name="Group_Schedule", index_col="Group"
    )


def fetch_box_groups():
    df_boxA = pd.read_excel("UMS_Courier_Schedules.xlsx", sheet_name="Box_Group_Lookup")
    df_boxB = df_boxA.copy()

    df_boxA["rota"] = "A"
    df_boxA["id"] = df_boxA["Box"]
    df_boxA["Box"] = df_boxA["Box"] + "-" + df_boxA["rota"]
    df_boxA["Group"] = df_boxA["Group"] + "-" + df_boxA["rota"]

    df_boxB["rota"] = "B"
    df_boxB["id"] = df_boxB["Box"]
    df_boxB["Box"] = df_boxB["Box"] + "-" + df_boxB["rota"]
    df_boxB["Group"] = df_boxB["Group"] + "-" + df_boxB["rota"]

    df_box = (
        pd.concat([df_boxA, df_boxB]).sort_values("Box").set_index("Box", drop=True)
    )

    return df_box


def fetch_boxes_list():
    return fetch_box_groups().index.to_list()


def fetch_days_list():
    return fetch_group_schedule().columns.to_list()


def get_expected_location(day: str) -> pd.DataFrame:
    """
    Gets expected location of boxes at the end of day

    Params
    ------
    day: str
        - day

    Returns
    -------
    pd.DataFrame

    """
    boxes = fetch_boxes_list()

    df_box = fetch_box_groups()
    df_sch = fetch_group_schedule()

    group = df_box.loc[boxes, "Group"]
    df_out = df_sch.loc[group, [day]]
    df_out["Box"] = boxes
    df_out = df_out.set_index("Box", drop=True)
    df_out["Group"] = group
    df_out = df_out.rename(columns={f"{day}": "loc_exp"})
    return df_out


def fetch_num_boxes():
    url = "https://server.itemit.com/items/itemit/v4/count"

    payload = {
        "search": "",
        "filters": FILTERS,
        "sorts": [],
    }

    response = requests.request("POST", url, headers=HEADERS, data=json.dumps(payload))
    response.raise_for_status()
    size = response.json()
    return size


@lru_cache(maxsize=1)
def fetch_box_data():
    url = "https://server.itemit.com/items/itemit/v7/profiles/_search"
    sorts = [{"sort": "ITEM", "by": {"name": "ASC"}}]
    payload = {
        "size": fetch_num_boxes(),
        "page": 1,
        "search": "",
        "filters": FILTERS,
        "sorts": sorts,
    }
    response = requests.request("POST", url, headers=HEADERS, data=json.dumps(payload))
    response.raise_for_status()
    items = response.json()

    data = {
        "box": [],
        "collection": [],
        "location": [],
        "last_seen_dt": [],
        "last_seen_by": [],
        "last_seen_by_email": [],
    }
    for i, item in enumerate(items):
        box = item["_source"]["name"]
        collection = [
            element["_source"]["name"]
            for element in item["parentObjects"]["elements"]
            if element["_source"]["collectionType"] == "COLLECTION"
        ]
        collection = next(iter(collection), None)

        location = [
            element["_source"]["name"]
            for element in item["parentObjects"]["elements"]
            if element["_source"]["collectionType"] == "LOCATION"
        ]
        location = next(iter(location), None)

        try:
            last_seen_time = item["_source"]["lastSeen"]["datetime"]
            last_seen_time = pd.to_datetime(last_seen_time)
        except TypeError:
            last_seen_time = None

        try:
            first_name = item["_source"]["lastSeen"]["_user"]["firstName"]
        except TypeError:
            first_name = ""
        try:
            last_name = item["_source"]["lastSeen"]["_user"]["lastName"]
        except TypeError:
            last_name = ""
        last_seen_by = f"{first_name} {last_name}"
        last_seen_by = last_seen_by if last_seen_by != " " else None

        try:
            last_seen_by_email = item["_source"]["lastSeen"]["_user"]["email"]
        except TypeError:
            last_seen_by_email = None

        data["box"].append(box)
        data["collection"].append(collection)
        data["location"].append(location)
        data["last_seen_dt"].append(last_seen_time)
        data["last_seen_by"].append(last_seen_by)
        data["last_seen_by_email"].append(last_seen_by_email)

    df = pd.DataFrame(data)
    df["id"] = df["box"].str[:-2]
    df["rota"] = df["box"].str[-1]

    df["loc_curr"] = df["location"]
    df["loc_curr"].fillna("None")
    df["loc_curr"] = df["loc_curr"].map(loc_map).fillna("Colleges")

    df["date"] = df["last_seen_dt"].dt.date
    df["time"] = df["last_seen_dt"].dt.strftime("%H:%M")

    return df


def get_location_comparison(day: str, clear_cache=False):
    boxes = fetch_boxes_list()

    if clear_cache:
        fetch_box_data.cache_clear()
    df = fetch_box_data()

    df_exp = get_expected_location(day)

    df_act = df.loc[df["box"].isin(boxes), :]

    df_locations = pd.merge(df_act, df_exp, left_on="box", right_index=True).set_index(
        "box", drop=True
    )

    df_locations["location_is_correct"] = (
        df_locations["loc_curr"] == df_locations["loc_exp"]
    )

    df_locations = df_locations[
        [
            "location_is_correct",
            "date",
            "last_seen_by",
            "Group",
            "loc_exp",
            "loc_curr",
            "location",
        ]
    ]
    df_locations = df_locations.sort_values(["location_is_correct", "date", "box"])

    return df_locations


def fetch_misplaced_boxes(day: str, clear_cache=False):
    df = get_location_comparison(day, clear_cache=clear_cache)
    return df[~df["location_is_correct"]].drop(columns="location_is_correct")
