import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("User Management")
st.write("Add, Update, or Deactivate user accounts")

st.subheader("All Users")

response = requests.get(f"{API_BASE}/admin/users")
users = response.json()
st.dataframe(users, use_container_width=True)

st.subheader("Add New User")

col1, col2 = st.columns(2)

role_options = {
    1: "Student",
    2: "Advisor",
    3: "Recruiter",
    4: "Admin"
}

with col1:
    first_name = st.text_input("First Name")
    email = st.text_input("Email")
    role_id = st.selectbox("Role", options=[1, 2, 3, 4], format_func=role_options.get)

institution_options = {
    1: "Northeastern University", 
    2: "Boston University", 
    3: "University of Alberta"
}

with col2:
    last_name = st.text_input("Last Name")
    institution_id = st.selectbox("Institution", options=[1, 2, 3], format_func=institution_options.get)

if st.button("Add User", type="primary"):
    if first_name and last_name and email:
        input = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "RoleID": role_id,
            "InstitutionID": institution_id
        }
        result = requests.post(f"{API_BASE}/admin/users", json=input)

        if result.status_code == 201:
            st.success("User created successfully!")
            st.rerun()
        else:
            st.error("Something went wrong. Was not able to create you user")
    else:
        st.warning("Please fill in all the fields.")
