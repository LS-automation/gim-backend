import streamlit as st
from scraper.engine import run_engine
from database.db import connect_sheet
import pandas as pd

st.set_page_config(layout="wide")

# =============================
# CLEAN PREMIUM CSS
# =============================
st.markdown("""
<style>

/* Page background spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
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

/* Signal cards */
.signal-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 18px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

/* Impact badges */
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
st.markdown("<div class='main-title'>Growth Intelligence Monitor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Corporate Event Intelligence Platform</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1,5])

with col1:
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

# =============================
# EXECUTIVE OVERVIEW
# =============================
st.markdown("### Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Signals", len(filtered_df))
col2.metric("Expansion", len(filtered_df[filtered_df["Event Type"] == "Expansion"]))
col3.metric("M&A", len(filtered_df[filtered_df["Event Type"] == "Acquisition"]))
col4.metric("Leadership", len(filtered_df[filtered_df["Event Type"] == "Leadership Appointment"]))

st.divider()

# =============================
# SIGNAL CARDS
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
            <strong>{row['Company Name']}</strong>
            <span class="{badge_class}">{impact_label}</span>
        </div>

        <div style="margin-top:6px; font-size:13px; color:#6b7280;">
            {row['Event Type']}
        </div>

        <div style="margin-top:10px; color:#374151;">
            {row['Event Summary']}
        </div>

        <div style="margin-top:12px; font-size:12px; color:#9ca3af;">
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