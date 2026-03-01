import streamlit as st
from database.db import connect_sheet
import pandas as pd

st.title("AI Executive Summary")

sheet = connect_sheet()
signals = sheet.worksheet("Signals").get_all_records()
df = pd.DataFrame(signals)

if df.empty:
    st.warning("No signals available.")
    st.stop()

top_signals = df.sort_values(by="AI Confidence", ascending=False).head(5)

st.subheader("Top 5 High Impact Signals")

for _, row in top_signals.iterrows():
    st.markdown(f"### {row['Company Name']}")
    st.markdown(row["Event Summary"])
    st.markdown("---")