import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# -----------------------------
# Protect page access
# -----------------------------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("Home.py")

SideBarLinks()

API_BASE = "http://api:4000"
STUDENT_ID = 1

st.title("⏰ Student Reminders")
st.write("Track deadlines and follow-up reminders.")


# -----------------------------
# API helper
# -----------------------------
def fetch_json(method: str, endpoint: str, payload=None):
    url = f"{API_BASE}{endpoint}"
    response = requests.request(method, url, json=payload, timeout=10)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


# -----------------------------
# Load reminders
# -----------------------------
reminders = None
load_error = None

try:
    reminders = fetch_json("GET", "/reminders")
except Exception as e:
    load_error = str(e)


# -----------------------------
# Page content
# -----------------------------
st.subheader("Reminder Summary")

if load_error:
    st.error(f"Could not load reminders: {load_error}")
else:
    reminder_rows = reminders if isinstance(reminders, list) else []

    student_reminders = [row for row in reminder_rows if row.get("StudentID") == STUDENT_ID]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Reminders", len(student_reminders))
    with col2:
        st.metric("Upcoming Reminders", len(student_reminders))

    st.markdown("---")
    st.subheader("Current Reminders")

    if len(student_reminders) > 0:
        reminders_df = pd.DataFrame(student_reminders)

        display_columns = [
            "ReminderID",
            "ApplicationID",
            "EmployerName",
            "PositionTitle",
            "Description",
            "DueDate",
        ]

        available_columns = [col for col in display_columns if col in reminders_df.columns]
        reminders_df = reminders_df[available_columns].copy()

        reminders_df = reminders_df.sort_values(by="DueDate", ascending=True)

        st.dataframe(reminders_df, use_container_width=True, hide_index=True)
    else:
        st.info("No reminders found yet.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(reminders)