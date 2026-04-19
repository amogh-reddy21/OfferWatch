import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("Home.py")

SideBarLinks()

API_BASE = "http://api:4000"

st.title("📝 Recruiter Notes")
st.write("Review notes added to candidate applications.")


def fetch_json(method: str, endpoint: str, payload=None):
    url = f"{API_BASE}{endpoint}"
    response = requests.request(method, url, json=payload, timeout=10)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


notes = None
load_error = None

try:
    notes = fetch_json("GET", "/recruiter/notes")
except Exception as e:
    load_error = str(e)

if load_error:
    st.error(f"Could not load recruiter notes: {load_error}")
else:
    rows = notes if isinstance(notes, list) else []

    if len(rows) > 0:
        df = pd.DataFrame(rows)

        display_columns = [
            "NoteID",
            "ApplicationID",
            "CandidateName",
            "EmployerName",
            "PositionTitle",
            "Note_Text",
            "Created_At",
        ]

        available_columns = [col for col in display_columns if col in df.columns]
        df = df[available_columns].copy()

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recruiter notes found.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(notes)