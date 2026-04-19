##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.title('OfferWatch')
st.write('#### Hi! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button("Act as Alex Chen, a Job Seeker",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student'
    st.session_state['first_name'] = 'Alex'
    st.session_state['user_id'] = 14
    st.switch_page('pages/REPLACE WITH PAGE') #I DONT KNOW PAGE YET SO ...

if st.button("Act as Reece James, a Recruiter",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'recruiter'
    st.session_state['first_name'] = 'Reece'
    st.session_state['user_id'] = 31
    st.switch_page('pages/REPLACE WITH PAGE') #I DONT KNOW PAGE YET SO ...

if st.button("Act as Lisa Rodriguez, a Career Services Director",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'advisor'
    st.session_state['first_name'] = 'Lisa'
    st.session_state['user_id'] = 23
    st.switch_page('pages/REPLACE WITH PAGE') #I DONT KNOW PAGE YET SO ...

if st.button("Act as Dr. Maria Patel, a Career Advisor",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'career_advisor'
    st.session_state['first_name'] = 'Maria'
    st.session_state['user_id'] = 52
    st.switch_page('pages/REPLACE WITH PAGE') #I DONT KNOW PAGE YET SO ...

if st.button("Act as Evan Carter, a System Administrator",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'administrator'
    st.session_state['first_name'] = 'Evan'
    st.session_state['user_id'] = 41
    st.switch_page('pages/30_Admin_Dashboard.py')
    