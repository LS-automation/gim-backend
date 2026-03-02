import streamlit as st
from scraper.engine import run_engine
from database.db import connect_sheet
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# =============================
# CLEAN WHITE EXECUTIVE THEME
# =============================
st.markdown("""
<style>

/* Remove dark header */
header {visibility: hidden;}
footer {visibility: hidden;}

/* White background */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* Sidebar fix */
[data-testid="stSidebar"] {
    background-color: #f3f4f6 !important;
}

[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* Title */
.main-title {
    font-size: 32px;
    font-weight: 700;
    color: #111827;
}

.subtitle {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 20px;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #e5e7eb;
}

/* Signal card */
.signal-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.signal-title {
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 5px;
}

.signal-type {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 10px;
}

.signal-summary {
    font-size: 14px;
    color: #111827;
    margin-bottom: 8px;
}

.signal-meta {
    font-size: 12px;
    color: #6b7280;
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

# =============================
# HEADER
# =============================

col_logo, col_title = st.columns([1,6])

with col_logo:
    st.image("assets/logo.png", width=100)

with col_title:
    st.markdown("<div class='main-title'>Growth Intelligence Monitor</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Corporate Event Intelligence Platform</div>", unsafe_allow_html=True)

if st.button("Run Scan"):
    run_engine()
    st.success("Scan Completed")

st.divider()

# =============================
# LOAD DATA
# =============================

sheet = connect_sheet()
signals_data = sheet.worksheet("Signals").get_all_records()
signals_df = pd.DataFrame(signals_data)

if signals_df.empty:
    st.warning("No signals available.")
    st.stop()

# Convert timestamp properly
signals_df["Detection Timestamp"] = pd.to_datetime(signals_df["Detection Timestamp"], errors="coerce")

# Only last 24 hours
now = datetime.utcnow()
last_24h = now - timedelta(hours=24)
signals_df = signals_df[signals_df["Detection Timestamp"] >= last_24h]

# =============================
# SIDEBAR FILTERS
# =============================

st.sidebar.markdown("### Filters")

companies = signals_df["Company Name"].unique()
event_types = signals_df["Event Type"].unique()

selected_company = st.sidebar.selectbox("Company", ["All"] + list(companies))
selected_type = st.sidebar.selectbox("Event Type", ["All"] + list(event_types))
confidence_filter = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.8)

filtered_df = signals_df.copy()

if selected_company != "All":
    filtered_df = filtered_df[filtered_df["Company Name"] == selected_company]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Event Type"] == selected_type]

filtered_df = filtered_df[filtered_df["AI Confidence"] >= confidence_filter]

# Sort by confidence then time
filtered_df = filtered_df.sort_values(
    by=["AI Confidence", "Detection Timestamp"],
    ascending=[False, False]
)

# =============================
# EXECUTIVE OVERVIEW
# =============================

st.markdown("### Overview (Last 24 Hours)")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Signals", len(filtered_df))
col2.metric("Expansion", len(filtered_df[filtered_df["Event Type"] == "Expansion"]))
col3.metric("M&A", len(filtered_df[filtered_df["Event Type"] == "Acquisition"]))
col4.metric("Leadership", len(filtered_df[filtered_df["Event Type"] == "Leadership Appointment"]))

st.divider()

# =============================
# SIGNALS
# =============================

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

    st.markdown(f"""
    <div class="signal-card">

        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="signal-title">{row['Company Name']}</div>
            <span class="{badge_class}">{impact_label}</span>
        </div>

        <div class="signal-type">
            {row['Event Type']}
        </div>

        <div class="signal-summary">
            {row['Event Summary']}
        </div>

        <div class="signal-meta">
            Detected: {row['Detection Timestamp']} |
            <a href="{row['Source URL']}" target="_blank">View Source</a>
        </div>

    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown(
    "<p style='text-align:center; font-size:12px; color:#9ca3af;'>© 2026 Growth Intelligence Monitor</p>",
    unsafe_allow_html=True
)