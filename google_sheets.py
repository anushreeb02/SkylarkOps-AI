import gspread
import pandas as pd
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

PILOT_SHEET = "pilot_roster"
PILOT_TAB = "pilot_roster"

DRONE_SHEET = "drone_fleet"
DRONE_TAB = "drone_fleet"

MISSION_SHEET = "missions"
MISSION_TAB = "missions"


def get_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    return gspread.authorize(creds)



def read_sheet(client, sheet_name, tab_name):
    ws = client.open(sheet_name).worksheet(tab_name)
    data = ws.get_all_records()
    return pd.DataFrame(data)


def update_cell_by_match(client, sheet_name, tab_name, match_column, match_value, update_column, new_value):
    ws = client.open(sheet_name).worksheet(tab_name)
    records = ws.get_all_records()

    if len(records) == 0:
        return False, "Sheet is empty."

    headers = list(records[0].keys())

    if match_column not in headers:
        return False, f"Column '{match_column}' not found."

    if update_column not in headers:
        return False, f"Column '{update_column}' not found."

    update_col_index = headers.index(update_column) + 1

    for i, row in enumerate(records, start=2):
        if str(row.get(match_column, "")).strip().lower() == str(match_value).strip().lower():
            ws.update_cell(i, update_col_index, new_value)
            return True, f"Updated {update_column} for {match_value} -> {new_value}"

    return False, f"Value '{match_value}' not found in column '{match_column}'."


# ---------------- REQUIRED WRITES ----------------

def update_pilot_status(client, pilot_name, new_status):
    return update_cell_by_match(
        client,
        PILOT_SHEET,
        PILOT_TAB,
        "name",
        pilot_name,
        "status",
        new_status
    )


def update_drone_status(client, drone_id, new_status):
    return update_cell_by_match(
        client,
        DRONE_SHEET,
        DRONE_TAB,
        "drone_id",
        drone_id,
        "status",
        new_status
    )


def assign_mission(client, project_id, pilot_name, drone_id):
    ok1, msg1 = update_cell_by_match(
        client,
        MISSION_SHEET,
        MISSION_TAB,
        "project_id",
        project_id,
        "assigned_pilot",
        pilot_name
    )

    ok2, msg2 = update_cell_by_match(
        client,
        MISSION_SHEET,
        MISSION_TAB,
        "project_id",
        project_id,
        "assigned_drone",
        drone_id
    )

    return ok1 and ok2, msg1 + " | " + msg2


