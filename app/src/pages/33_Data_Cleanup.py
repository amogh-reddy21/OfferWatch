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

st.title("Data Cleanup")
st.write("Review and Permantly delete outdated/archived records")

st.subheader("Outdated / Archived Records")

response = requests.get(f"{API_BASE}/admin/data-cleanup")
records = response.json()

if records:
    st.dataframe(records, use_container_width=True)
    st.write(f"**{len(records)} record(s)** flagged for cleanup")
else:
    st.success("No Outdated/Archieved Records Found")