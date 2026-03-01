import os
import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def connect_sheet():
    creds = Credentials.from_service_account_file(
        "database/credentials.json",
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID)


# ==============================
# GET ACTIVE COMPANIES
# ==============================
def get_active_companies():
    sheet = connect_sheet()
    worksheet = sheet.worksheet("Companies")
    records = worksheet.get_all_records()

    active_companies = []

    for row in records:
        if str(row.get("Active", "")).lower() == "yes":
            active_companies.append({
                "company_name": row.get("Company Name"),
                "industry": row.get("Industry"),
                "geography": row.get("Geography"),
                "domain": row.get("Official Domain"),
            })

    return active_companies


# ==============================
# SAVE SIGNAL
# ==============================
def save_signal(data):
    sheet = connect_sheet()
    worksheet = sheet.worksheet("Signals")
    worksheet.append_row(data)


# ==============================
# SAVE LOG
# ==============================
def save_log(data):
    sheet = connect_sheet()
    worksheet = sheet.worksheet("Logs")
    worksheet.append_row(data)