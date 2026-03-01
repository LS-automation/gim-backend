import streamlit as st
from database.db import connect_sheet

st.title("Watchlist Manager")

sheet = connect_sheet()
companies_sheet = sheet.worksheet("Companies")

companies = companies_sheet.get_all_records()

for i, company in enumerate(companies):
    current_status = company.get("Watchlist", "No")

    new_status = st.checkbox(
        company["Company Name"],
        value=True if current_status == "Yes" else False,
        key=i
    )

    companies_sheet.update_cell(i + 2, 7, "Yes" if new_status else "No")

st.success("Watchlist Updated")