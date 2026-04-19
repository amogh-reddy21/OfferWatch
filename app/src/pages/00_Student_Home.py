import streamlit as st
from modules.nav import SideBarLinks

SideBarLinks()

st.title("Student Home")
st.write("Welcome to OfferWatch, Alex.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Applications", use_container_width=True):
        st.switch_page("pages/01_Student_Applications.py")

with col2:
    if st.button("Offers", use_container_width=True):
        st.switch_page("pages/02_Student_Offers.py")

with col3:
    if st.button("Reminders", use_container_width=True):
        st.switch_page("pages/03_Student_Reminders.py")