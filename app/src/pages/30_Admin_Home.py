import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Administrator Home")
st.write("Welcome to OfferWatch admin tools, Evan.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("System Logs", use_container_width=True):
        st.switch_page("pages/31_System_Logs.py")

with col2:
    if st.button("Health Metrics", use_container_width=True):
        st.switch_page("pages/32_Health_Metrics.py")

with col3:
    if st.button("User Management", use_container_width=True):
        st.switch_page("pages/33_User_Management.py")