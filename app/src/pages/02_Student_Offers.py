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

st.title("💼 Student Offers")
st.write("Compare and review your job offers.")


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


def accept_offer(offer_id: int):
    return fetch_json("PATCH", f"/offers/{offer_id}/accept")


# -----------------------------
# Load offers
# -----------------------------
offers = None
load_error = None

try:
    offers = fetch_json("GET", "/offers")
except Exception as e:
    load_error = str(e)


# -----------------------------
# Page content
# -----------------------------
st.subheader("Offer Summary")

if load_error:
    st.error(f"Could not load offers: {load_error}")
else:
    offer_rows = offers if isinstance(offers, list) else []

    # Filter to this student's offers
    student_offers = [row for row in offer_rows if row.get("StudentID") == STUDENT_ID]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Offers", len(student_offers))
    with col2:
        st.metric(
            "Accepted Offers",
            sum(1 for row in student_offers if row.get("OfferAccepted") in [1, True])
        )
    with col3:
        st.metric(
            "Pending Offers",
            sum(1 for row in student_offers if row.get("OfferAccepted") in [0, False, None])
        )

    st.markdown("---")
    st.subheader("Current Offers")

    if len(student_offers) > 0:
        offers_df = pd.DataFrame(student_offers)

        # Save raw accepted status for button logic
        offers_df["OfferAcceptedRaw"] = offers_df["OfferAccepted"]

        display_columns = [
            "OfferID",
            "ApplicationID",
            "EmployerName",
            "PositionTitle",
            "Salary",
            "Location",
            "Deadline",
            "StartDate",
            "OfferAccepted",
        ]

        available_columns = [col for col in display_columns if col in offers_df.columns]
        offers_df = offers_df[available_columns + ["OfferAcceptedRaw"]].copy()

        if "OfferAccepted" in offers_df.columns:
            offers_df["OfferAccepted"] = offers_df["OfferAccepted"].map({
                1: "Yes",
                0: "No",
                True: "Yes",
                False: "No",
                None: "Pending"
            }).fillna("Pending")

        st.subheader("Filter by Offer Status")
        status_options = ["All", "Yes", "No", "Pending"]
        selected_status = st.selectbox("Offer Accepted", status_options)

        filtered_df = (
            offers_df
            if selected_status == "All"
            else offers_df[offers_df["OfferAccepted"] == selected_status]
        )

        st.dataframe(
            filtered_df.drop(columns=["OfferAcceptedRaw"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("Offer Actions")

        pending_or_unaccepted = filtered_df[
            filtered_df["OfferAcceptedRaw"].isin([0, False, None])
        ]

        if len(pending_or_unaccepted) > 0:
            for _, row in pending_or_unaccepted.iterrows():
                offer_id = int(row["OfferID"])
                company = row.get("EmployerName", "Unknown Company")
                role = row.get("PositionTitle", "Unknown Role")

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Offer {offer_id}** — {company} / {role}")
                with col2:
                    if st.button("Accept", key=f"accept_offer_{offer_id}"):
                        try:
                            accept_offer(offer_id)
                            st.success(f"Offer {offer_id} accepted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not accept offer {offer_id}: {e}")
        else:
            st.info("No pending offers available to accept.")

    else:
        st.info("No offers found yet.")

st.markdown("---")

with st.expander("Debug API Response"):
    st.write(offers)