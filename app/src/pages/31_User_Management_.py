# import logging
# logger = logging.getLogger(__name__)

# import streamlit as st
# import requests
# from modules.nav import SideBarLinks

# st.set_page_config(layout='wide')
# SideBarLinks()

# API_BASE = "http://web-api:4000"

# st.title("User Management")
# st.write("Add, Update, or Deactivate user accounts")

# # ---- User Table -------------------------------------------------------------
# st.subheader("All Users")

# response = requests.get(f"{API_BASE}/admin/users")
# users = response.json()
# st.dataframe(users, use_container_width=True)

# # ---- Add New User -----------------------------------------------------------
# st.subheader("Add New User")

# col1, col2 = st.columns(2)
# with col1:
#     first_name = st.text_input("First Name")
#     email      = st.text_input("Email")
#     role_id    = st.selectbox("Role", options=[1, 2, 3, 4], 
#                                format_func=lambda x: {1: "Student", 2: "Advisor", 3: "Recruiter", 4: "Admin"}[x])
# with col2:
#     last_name      = st.text_input("Last Name")
#     institution_id = st.selectbox("Institution", options=[1, 2, 3],
#                                    format_func=lambda x: {1: "Northeastern University", 2: "Boston University", 3: "Duke University"}[x])

# if st.button("Add User", type="primary"):
#     if first_name and last_name and email:
#         payload = {
#             "FirstName":     first_name,
#             "LastName":      last_name,
#             "Email":         email,
#             "RoleID":        role_id,
#             "InstitutionID": institution_id
#         }
#         result = requests.post(f"{API_BASE}/admin/users", json=payload)
#         if result.status_code == 201:
#             st.success("User created successfully!")
#             st.rerun()
#         else:
#             st.error("Something went wrong.")
#     else:
#         st.warning("Please fill in all fields.")

# # ---- Update User ------------------------------------------------------------
# st.subheader("Update User")

# col1, col2 = st.columns(2)
# with col1:
#     update_id   = st.number_input("User ID to Update", min_value=1, step=1)
#     new_role_id = st.selectbox("New Role", options=[1, 2, 3, 4],
#                                 format_func=lambda x: {1: "Student", 2: "Advisor", 3: "Recruiter", 4: "Admin"}[x])
# with col2:
#     new_institution_id = st.selectbox("New Institution", options=[1, 2, 3],
#                                        format_func=lambda x: {1: "Northeastern University", 2: "Boston University", 3: "Duke University"}[x])

# if st.button("Update User", type="primary"):
#     payload = {
#         "RoleID":        new_role_id,
#         "InstitutionID": new_institution_id
#     }
#     result = requests.put(f"{API_BASE}/admin/users/{update_id}", json=payload)
#     if result.status_code == 200:
#         st.success("User updated successfully!")
#         st.rerun()
#     else:
#         st.error("User not found.")

# # ---- Deactivate User --------------------------------------------------------
# st.subheader("Deactivate User")

# deactivate_id = st.number_input("User ID to Deactivate", min_value=1, step=1)

# if st.button("Deactivate User", type="primary"):
#     result = requests.delete(f"{API_BASE}/admin/users/{deactivate_id}")
#     if result.status_code == 200:
#         st.success("User deactivated successfully!")
#         st.rerun()
#     else:
#         st.error("User not found.")

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

# ---- User Table -------------------------------------------------------------
st.subheader("All Users")

col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    role_filter = st.selectbox("Filter by Role", 
                                options=["All", "Student", "Advisor", "Recruiter", "Admin"])
with col2:
    institution_filter = st.selectbox("Filter by Institution",
                                       options=["All", "Northeastern University", 
                                                "Boston University", "Duke University"])
with col3:
    status_filter = st.selectbox("Filter by Status",
                                  options=["All", "Active", "Inactive"])

params = {}
if role_filter != "All":
    params["role"] = role_filter
if institution_filter != "All":
    params["institution"] = institution_filter
if status_filter != "All":
    params["status"] = status_filter

response = requests.get(f"{API_BASE}/admin/users", params=params)
users = response.json()
st.dataframe(users, use_container_width=True)

# ---- Add New User -----------------------------------------------------------
st.subheader("Add New User")

col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First Name")
    email      = st.text_input("Email")
    role_id    = st.selectbox("Role", options=[1, 2, 3, 4], 
                               format_func=lambda x: {1: "Student", 2: "Advisor", 
                                                       3: "Recruiter", 4: "Admin"}[x])
with col2:
    last_name      = st.text_input("Last Name")
    institution_id = st.selectbox("Institution", options=[1, 2, 3],
                                   format_func=lambda x: {1: "Northeastern University", 
                                                           2: "Boston University", 
                                                           3: "Duke University"}[x])

if st.button("Add User", type="primary"):
    if first_name and last_name and email:
        payload = {
            "FirstName":     first_name,
            "LastName":      last_name,
            "Email":         email,
            "RoleID":        role_id,
            "InstitutionID": institution_id
        }
        result = requests.post(f"{API_BASE}/admin/users", json=payload)
        if result.status_code == 201:
            st.success("User created successfully!")
            st.rerun()
        else:
            st.error("Something went wrong.")
    else:
        st.warning("Please fill in all fields.")

# ---- Update User ------------------------------------------------------------
st.subheader("Update User")

col1, col2 = st.columns(2)
with col1:
    update_id   = st.number_input("User ID to Update", min_value=1, step=1)
    new_role_id = st.selectbox("New Role", options=[1, 2, 3, 4],
                                format_func=lambda x: {1: "Student", 2: "Advisor", 
                                                        3: "Recruiter", 4: "Admin"}[x])
with col2:
    new_institution_id = st.selectbox("New Institution", options=[1, 2, 3],
                                       format_func=lambda x: {1: "Northeastern University", 
                                                               2: "Boston University", 
                                                               3: "Duke University"}[x])

if st.button("Update User", type="primary"):
    payload = {
        "RoleID":        new_role_id,
        "InstitutionID": new_institution_id
    }
    result = requests.put(f"{API_BASE}/admin/users/{int(update_id)}", json=payload)
    if result.status_code == 200:
        st.success("User updated successfully!")
        st.rerun()
    else:
        st.error("User not found.")

# ---- Deactivate User --------------------------------------------------------
st.subheader("Deactivate User")

deactivate_id = st.number_input("User ID to Deactivate", min_value=1, step=1)

if st.button("Deactivate User", type="primary"):
    result = requests.delete(f"{API_BASE}/admin/users/{int(deactivate_id)}")
    if result.status_code == 200:
        st.success("User deactivated successfully!")
        st.rerun()
    else:
        st.error("User not found.")