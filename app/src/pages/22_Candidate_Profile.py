import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("Home.py")

SideBarLinks()

API_BASE = "http://api:4000"

st.title("📋 Candidate Profiles")
st.write("Review detailed candidate information.")


def fetch_json(method: str, endpoint: str, payload=None):
    url = f"{API_BASE}{endpoint}"
    response = requests.request(method, url, json=payload, timeout=10)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


profiles = None
load_error = None

try:
    profiles = fetch_json("GET", "/recruiter/candidate-profiles")
except Exception as e:
    load_error = str(e)

if load_error:
    st.error(f"Could not load candidate profiles: {load_error}")
else:
    rows = profiles if isinstance(profiles, list) else []

    if len(rows) > 0:
        df = pd.DataFrame(rows)

        names = sorted(df["CandidateName"].dropna().unique().tolist()) if "CandidateName" in df.columns else []
        selected_name = st.selectbox("Select Candidate", names)

        filtered = df[df["CandidateName"] == selected_name] if selected_name else df

        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.info("No candidate profiles found.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(profiles)