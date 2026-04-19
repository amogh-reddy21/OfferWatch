import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("Home.py")

SideBarLinks()

API_BASE = "http://api:4000"

st.title("📛 System Logs")
st.write("Monitor platform errors and system issues.")


def fetch_json(endpoint: str):
    response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


try:
    data = fetch_json("/admin/logs")

    if isinstance(data, dict) and "error" in data:
        st.error(f"Backend error: {data['error']}")
    else:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Failed to load logs: {e}")