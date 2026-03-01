import streamlit as st
from database.db import connect_sheet
import pandas as pd
from datetime import datetime

st.title("Daily Brief")

sheet = connect_sheet()
signals = sheet.worksheet("Signals").get_all_records()
df = pd.DataFrame(signals)

today = datetime.now().strftime("%Y-%m-%d")
today_df = df[df["Detection Timestamp"].str.contains(today)]

st.subheader("Daily Brief Generated at 08:00 AM")

if today_df.empty:
    st.info("No signals today.")
else:
    st.dataframe(today_df)

    csv = today_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Daily Brief",
        data=csv,
        file_name="daily_brief.csv",
        mime="text/csv"
    )