import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

SideBarLinks()

API_BASE = "http://api:4000"

st.title("👥 User Management")

def fetch():
    return requests.get(f"{API_BASE}/admin/users").json()

try:
    data = fetch()
    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load users: {e}")