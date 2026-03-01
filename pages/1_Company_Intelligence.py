import streamlit as st
from database.db import connect_sheet
import pandas as pd

st.title("Company Intelligence Dashboard")

sheet = connect_sheet()
signals = sheet.worksheet("Signals").get_all_records()
df = pd.DataFrame(signals)

if df.empty:
    st.warning("No data available.")
    st.stop()

company = st.selectbox("Select Company", df["Company Name"].unique())

company_df = df[df["Company Name"] == company]

st.subheader("Confidence Timeline")
st.line_chart(company_df["AI Confidence"])

st.subheader("Event Distribution")
event_dist = company_df["Event Type"].value_counts()
st.bar_chart(event_dist)

st.subheader("Recent Signals")
st.dataframe(company_df)