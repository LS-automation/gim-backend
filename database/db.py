import os
import json
import gspread
from google.oauth2.service_account import Credentials

def connect_sheet():

    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if not creds_json:
        raise Exception("Missing GOOGLE_CREDENTIALS_JSON environment variable")

    creds_dict = json.loads(creds_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

    return client.open_by_key(spreadsheet_id)