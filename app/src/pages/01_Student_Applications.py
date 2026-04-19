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

st.title("📄 Student Applications")
st.write("View and manage your submitted job applications.")


# -----------------------------
# API helpers
# -----------------------------
def fetch_json(method: str, endpoint: str, payload=None):
    url = f"{API_BASE}{endpoint}"
    response = requests.request(method, url, json=payload, timeout=10)
    response.raise_for_status()
    if response.text:
        return response.json()
    return None


def create_application(student_id: int, position_id: int, notes: str):
    payload = {
        "StudentID": student_id,
        "PositionID": position_id,
        "Notes": notes,
    }
    return fetch_json("POST", "/applications", payload)


# -----------------------------
# Form state
# -----------------------------
if "show_form" not in st.session_state:
    st.session_state["show_form"] = False


# -----------------------------
# New application button
# -----------------------------
if st.button("➕ New Application"):
    st.session_state["show_form"] = not st.session_state["show_form"]


# -----------------------------
# New application form
# -----------------------------
if st.session_state.get("show_form"):
    with st.form("new_application", clear_on_submit=True):
        st.subheader("Submit New Application")

        position_id = st.number_input(
            "Position ID",
            min_value=1,
            step=1,
            format="%d"
        )
        notes = st.text_area("Notes", placeholder="e.g. Applied via LinkedIn")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Submit")
        with col2:
            cancelled = st.form_submit_button("Cancel")

        if cancelled:
            st.session_state["show_form"] = False
            st.rerun()

        if submitted:
            try:
                create_application(
                    student_id=STUDENT_ID,
                    position_id=int(position_id),
                    notes=notes.strip(),
                )
                st.success("Application submitted successfully!")
                st.session_state["show_form"] = False
                st.rerun()

            except requests.exceptions.HTTPError as e:
                details = ""
                if e.response is not None:
                    try:
                        details = e.response.json()
                    except Exception:
                        details = e.response.text

                st.error(f"Failed to submit application: {e} | Details: {details}")

            except Exception as e:
                st.error(f"Failed to submit application: {e}")


# -----------------------------
# Load applications
# -----------------------------
applications = None
load_error = None

try:
    applications = fetch_json("GET", "/applications")
except Exception as e:
    load_error = str(e)


# -----------------------------
# Summary and tables
# -----------------------------
st.subheader("Application Summary")

if load_error:
    st.error(f"Could not load applications: {load_error}")
else:
    app_rows = applications if isinstance(applications, list) else []

    # Filter to this student's applications
    student_apps = [row for row in app_rows if row.get("StudentID") == STUDENT_ID]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applications", len(student_apps))
    with col2:
        st.metric(
            "Active Applications",
            sum(1 for row in student_apps if row.get("IsArchived") == 0)
        )
    with col3:
        st.metric(
            "Archived Applications",
            sum(1 for row in student_apps if row.get("IsArchived") == 1)
        )

    st.markdown("---")
    st.subheader("Current Applications")

    if len(student_apps) > 0:
        apps_df = pd.DataFrame(student_apps)

        display_columns = [
            "ApplicationID",
            "PositionID",
            "ResumeID",
            "Status",
            "Application_Date",
            "IsArchived",
            "Notes",
        ]

        available_columns = [col for col in display_columns if col in apps_df.columns]
        apps_df = apps_df[available_columns].copy()

        if "IsArchived" in apps_df.columns:
            apps_df["IsArchived"] = apps_df["IsArchived"].map({0: "No", 1: "Yes"})

        st.subheader("Filter by Status")

        if "Status" in apps_df.columns:
            status_options = ["All"] + sorted(
                apps_df["Status"].dropna().unique().tolist()
            )
            selected_status = st.selectbox("Status", status_options)

            filtered_df = (
                apps_df
                if selected_status == "All"
                else apps_df[apps_df["Status"] == selected_status]
            )
        else:
            filtered_df = apps_df

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    else:
        st.info("No applications found yet.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(applications)