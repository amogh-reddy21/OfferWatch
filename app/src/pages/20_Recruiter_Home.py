import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Recruiter Home")
st.write("Welcome to OfferWatch recruiter tools, Reece.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Candidates", use_container_width=True):
        st.switch_page("pages/21_Candidates.py")

with col2:
    if st.button("Candidate Profile", use_container_width=True):
        st.switch_page("pages/22_Candidate_Profile.py")

with col3:
    if st.button("Recruiter Notes", use_container_width=True):
        st.switch_page("pages/23_Recruiter_Notes.py")
        