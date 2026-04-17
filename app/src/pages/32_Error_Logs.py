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
        .stApp {
            background-color: #FAF9F6;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Error Logs")
st.write("View recent system errors and failed operations")

col1, col2 = st.columns(2)

status_option = ["All", "Resolved", "Unresolved"]
severity_option = ["All", "Low", "Medium", "High"]

with col1:
    status_filter = st.selectbox("Filter by Status", options=status_option)

with col2:
    severity_filter = st.selectbox("Filter by Severity", options=severity_option)