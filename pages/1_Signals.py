import streamlit as st
from database.db import connect_sheet
import pandas as pd
from datetime import datetime, timedelta

st.title("Signals")

sheet = connect_sheet()
signals = sheet.worksheet("Signals").get_all_records()
df = pd.DataFrame(signals)

if df.empty:
    st.warning("No data available.")
    st.stop()

df["Detection Timestamp"] = pd.to_datetime(df["Detection Timestamp"])

last_24h = datetime.utcnow() - timedelta(days=1)
df = df[df["Detection Timestamp"] >= last_24h]

company = st.selectbox("Company", ["All"] + list(df["Company Name"].unique()))

if company != "All":
    df = df[df["Company Name"] == company]

event = st.selectbox("Event Type", ["All"] + list(df["Event Type"].unique()))

if event != "All":
    df = df[df["Event Type"] == event]

st.download_button(
    "Download CSV",
    df.to_csv(index=False),
    "signals.csv",
    "text/csv"
)

st.dataframe(df, use_container_width=True)