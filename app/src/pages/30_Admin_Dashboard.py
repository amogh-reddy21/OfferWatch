import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.markdown("""
    <style>
        [data-testid="stMetric"] {
            background-color: #c2bebe;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
        }
        [data-testid="stMetricLabel"] {
            color: #aaaaaa;
        }
        [data-testid="stMetricValue"] {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

response = requests.get(f"{API_BASE}/admin/health")
health = response.json()

st.title("Platform Health Dashboard")
st.subheader("System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Active Users", value=health["active_users"])

with col2:
    st.metric(label="API Response (avg)", value=f"{health['api_response']}ms")

with col3:
    st.metric(label="Errors (last 24h)", value=health["errors_24h"])

with col4:
    st.metric(label="Uptime", value=f"{health['uptime']}%" if health["uptime"] else "N/A")

# ---- System Status ----------------------------------------------------------
st.subheader("System Status")

for component in health["components"]:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"""
            <div style="
                background-color: #2c2c2c;
                padding: 12px 20px;
                border-radius: 6px;
                margin-bottom: 8px;
                color: white;
            ">
                {component["Component_Name"]}
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = "green" if component["Current_Status"] == "Operational" else "red"
        st.markdown(f"""
            <div style="
                background-color: #2c2c2c;
                padding: 12px 20px;
                border-radius: 6px;
                margin-bottom: 8px;
                color: {color};
                text-align: right;
            ">
                {component["Current_Status"]}
            </div>
        """, unsafe_allow_html=True)