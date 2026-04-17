import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.markdown("""
    <style>
        .stApp {
            background-color: #FAF9F6;
        }
    </style>
""", unsafe_allow_html=True)

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
        added_input = {
            "FirstName": first_name,
            "LastName": last_name,
            "Email": email,
            "RoleID": role_id,
            "InstitutionID": institution_id
        }
        added_result = requests.post(f"{API_BASE}/admin/users", json=added_input)

        if added_result.status_code == 201:
            st.success("User created successfully!")
            st.rerun()
        else:
            st.error("Something went wrong. Was not able to create you user")
    else:
        st.warning("Please fill in all the fields.")

st.subheader("Update User")

col1, col2 = st.columns(2)
with col1:
    update_id = st.number_input("User ID to Update", min_value=1, step=1)
    new_role_id = st.selectbox("New Role", options=[1, 2, 3, 4],format_func=role_options.get)
with col2:
    new_institution_id = st.selectbox("New Institution", options=[1, 2, 3],format_func=institution_options.get)

if st.button("Update User", type="primary"):
    update_input = {
        "RoleID": new_role_id,
        "InstitutionID": new_institution_id
    }
    update_result = requests.put(f"{API_BASE}/admin/users/{update_id}", json=update_input)
    if update_result.status_code == 200:
        st.success("User updated successfully!")
        st.rerun()
    else:
        st.error("User not found.")

st.subheader("Deactivate User")

deactivate_id = st.number_input("User ID to Deactivate", min_value=1, step=1)

if st.button("Deactivate User", type="primary"):
    deactivate_result = requests.delete(f"{API_BASE}/admin/users/{deactivate_id}")
    if deactivate_result.status_code == 200:
        st.success("User deactivated successfully!")
        st.rerun()
    else:
        st.error("User not found.")