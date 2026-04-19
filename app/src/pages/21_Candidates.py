import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("Home.py")

SideBarLinks()

API_BASE = "http://api:4000"

st.title("🧑‍💼 Candidates")
st.write("View and filter recruiter candidate pipelines.")


def fetch_json(method: str, endpoint: str, payload=None):
    url = f"{API_BASE}{endpoint}"
    response = requests.request(method, url, json=payload, timeout=10)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


candidates = None
load_error = None

try:
    candidates = fetch_json("GET", "/recruiter/candidates")
except Exception as e:
    load_error = str(e)

st.subheader("Candidate Summary")

if load_error:
    st.error(f"Could not load candidates: {load_error}")
else:
    candidate_rows = candidates if isinstance(candidates, list) else []

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applications", len(candidate_rows))
    with col2:
        st.metric(
            "Interview Scheduled",
            sum(1 for row in candidate_rows if row.get("Status") == "Interview Scheduled")
        )
    with col3:
        st.metric(
            "Offers Sent / Accepted",
            sum(1 for row in candidate_rows if row.get("Status") in ["Offer Sent", "Accepted"])
        )

    st.markdown("---")
    st.subheader("Candidate Pipeline")

    if len(candidate_rows) > 0:
        df = pd.DataFrame(candidate_rows)

        display_columns = [
            "ApplicationID",
            "CandidateName",
            "InstitutionName",
            "MajorName",
            "PositionTitle",
            "EmployerName",
            "Status",
            "Application_Date",
        ]

        available_columns = [col for col in display_columns if col in df.columns]
        df = df[available_columns].copy()

        st.subheader("Filters")

        if "Status" in df.columns:
            status_options = ["All"] + sorted(df["Status"].dropna().unique().tolist())
            selected_status = st.selectbox("Status", status_options)
        else:
            selected_status = "All"

        if "InstitutionName" in df.columns:
            school_options = ["All"] + sorted(df["InstitutionName"].dropna().unique().tolist())
            selected_school = st.selectbox("Institution", school_options)
        else:
            selected_school = "All"

        filtered_df = df.copy()

        if selected_status != "All":
            filtered_df = filtered_df[filtered_df["Status"] == selected_status]

        if selected_school != "All":
            filtered_df = filtered_df[filtered_df["InstitutionName"] == selected_school]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("No candidate applications found.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(candidates)