import streamlit as st
from scraper.engine import run_engine
from database.db import connect_sheet
import pandas as pd
from datetime import datetime, timedelta
import re

# =====================================
# PAGE CONFIG (MUST BE FIRST)
# =====================================
st.set_page_config(layout="wide")

# =====================================
# CLEAN PREMIUM CSS
# =====================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stSidebar"] {
    background-color: #f3f4f6 !important;
}

h1, h2, h3 {
    color: #111827 !important;
    font-weight: 600;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.stButton>button {
    background-color: #111827;
    color: white;
    border-radius: 6px;
}

.stButton>button:hover {
    background-color: #1f2937;
}

.signal-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.signal-card div {
    color: #111827 !important;
}

.badge-high {
    background-color: #dcfce7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
}

.badge-medium {
    background-color: #fef3c7;
    color: #92400e;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
}

.badge-low {
    background-color: #fee2e2;
    color: #991b1b;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# HEADER
# =====================================
st.markdown("<h1>Growth Intelligence Monitor</h1>", unsafe_allow_html=True)
st.caption("Corporate Event Intelligence Platform")

col1, col2 = st.columns([1,5])

with col1:
    if st.button("Run Scan"):
        run_engine()
        st.success("Scan Completed")

st.divider()

# =====================================
# LOAD DATA
# =====================================
sheet = connect_sheet()
signals_data = sheet.worksheet("Signals").get_all_records()
signals_df = pd.DataFrame(signals_data)

if signals_df.empty:
    st.warning("No signals available.")
    st.stop()

# Convert types safely
signals_df["AI Confidence"] = pd.to_numeric(signals_df["AI Confidence"], errors="coerce")
signals_df["Detection Timestamp"] = pd.to_datetime(
    signals_df["Detection Timestamp"], errors="coerce"
)

# =====================================
# FILTER LAST 24 HOURS
# =====================================
last_24h = datetime.utcnow() - timedelta(days=1)
signals_df = signals_df[signals_df["Detection Timestamp"] >= last_24h]

if signals_df.empty:
    st.info("No signals detected in the last 24 hours.")
    st.stop()

# =====================================
# SIDEBAR FILTERS
# =====================================
st.sidebar.markdown("### Filters")

companies = signals_df["Company Name"].dropna().unique()
event_types = signals_df["Event Type"].dropna().unique()

selected_company = st.sidebar.selectbox("Company", ["All"] + list(companies))
selected_type = st.sidebar.selectbox("Event Type", ["All"] + list(event_types))
confidence_filter = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.8)

filtered_df = signals_df.copy()

if selected_company != "All":
    filtered_df = filtered_df[filtered_df["Company Name"] == selected_company]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Event Type"] == selected_type]

filtered_df = filtered_df[filtered_df["AI Confidence"] >= confidence_filter]

# Sort newest first
filtered_df = filtered_df.sort_values("Detection Timestamp", ascending=False)

# =====================================
# EXECUTIVE OVERVIEW
# =====================================
st.markdown("### Overview (Last 24 Hours)")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Signals", len(filtered_df))
col2.metric("Expansion", len(filtered_df[filtered_df["Event Type"] == "Expansion"]))
col3.metric("M&A", len(filtered_df[filtered_df["Event Type"] == "Acquisition"]))
col4.metric("Leadership", len(filtered_df[filtered_df["Event Type"] == "Leadership Appointment"]))

st.divider()

# =====================================
# SIGNAL CARDS
# =====================================
st.markdown("### Signals")

for _, row in filtered_df.iterrows():

    confidence = row["AI Confidence"]

    if confidence >= 0.9:
        badge_class = "badge-high"
        impact_label = "High Impact"
    elif confidence >= 0.8:
        badge_class = "badge-medium"
        impact_label = "Medium Impact"
    else:
        badge_class = "badge-low"
        impact_label = "Low Impact"

    # Remove HTML tags from summary
    clean_summary = re.sub('<.*?>', '', str(row["Event Summary"]))

    st.markdown(f"""
    <div class="signal-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{row['Company Name']}</strong>
            <span class="{badge_class}">{impact_label}</span>
        </div>

        <div style="margin-top:6px; font-size:13px; color:#6b7280;">
            {row['Event Type']}
        </div>

        <div style="margin-top:10px;">
            {clean_summary}
        </div>

        <div style="margin-top:12px; font-size:12px; color:#6b7280;">
            Detected: {row['Detection Timestamp']}
        </div>

        <div style="margin-top:8px;">
            <a href="{row['Source URL']}" target="_blank">View Source</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown(
    "<p style='text-align:center; font-size:12px; color:#9ca3af;'>© 2026 Growth Intelligence Monitor</p>",
    unsafe_allow_html=True
)