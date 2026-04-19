import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'career_advisor'
    st.session_state['advisor_id'] = 1
    st.session_state['first_name'] = 'Maria'

SideBarLinks()

advisor_id = st.session_state.get('advisor_id', 1)
 
st.title('Application Status Dashboard')
st.caption(f"Logged in as Dr. {st.session_state.get('first_name', 'Maria')} Patel — Career Advisor")
st.divider()
 
# ── Fetch dashboard summary ──────────────────────────────────────────────────
try:
    r = requests.get(f'http://web-api:4000/advisor/{advisor_id}/dashboard')
    r.raise_for_status()
    data = r.json()
except Exception as e:
    st.error(f"Could not load dashboard data: {e}")
    st.stop()
 
# ── Fetch YoY placement for charts ───────────────────────────────────────────
try:
    r2 = requests.get(f'http://web-api:4000/advisor/{advisor_id}/analytics/placement')
    r2.raise_for_status()
    placement = r2.json()
except Exception:
    placement = []
 
# ── Fetch top employers for bar chart ────────────────────────────────────────
try:
    r3 = requests.get(f'http://web-api:4000/advisor/{advisor_id}/employers/top-offers')
    r3.raise_for_status()
    employers = r3.json()
except Exception:
    employers = []
 
# ── Fetch student application log for table ──────────────────────────────────
try:
    r4 = requests.get(f'http://web-api:4000/advisor/{advisor_id}/students/flagged')
    r4.raise_for_status()
    students = r4.json()
except Exception:
    students = []
 
# ── Metric cards (row 1) ─────────────────────────────────────────────────────
st.subheader('Week of Summary')
c1, c2, c3, c4 = st.columns(4)
 
c1.metric(
    label='Total Interviews',
    value=data.get('TotalInterviews', 0)
)
c2.metric(
    label='Offers Extended',
    value=data.get('TotalOffers', 0)
)
c3.metric(
    label='Applied → Interview Rate',
    value=f"{data.get('AppliedToInterviewRate', 0)}%"
)
c4.metric(
    label='Interview → Offer Rate',
    value=f"{data.get('InterviewToOfferRate', 0)}%"
)
 
st.divider()
 
# ── Charts row ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)
 
with col_left:
    st.subheader('Students Placed per Year')
    if placement:
        df_place = pd.DataFrame(placement)
        df_place = df_place.rename(columns={
            'ApplicationYear': 'Year',
            'StudentsPlaced': 'Students Placed'
        })
        st.line_chart(df_place.set_index('Year')['Students Placed'])
    else:
        st.info('No placement data available.')
 
with col_right:
    st.subheader('Offers Extended per Employer')
    if employers:
        df_emp = pd.DataFrame(employers)
        df_emp = df_emp.rename(columns={
            'EmployerName': 'Employer',
            'OffersExtended': 'Offers'
        })
        st.bar_chart(df_emp.set_index('Employer')['Offers'])
    else:
        st.info('No employer offer data available.')
 
st.divider()
 
# ── Student details table ────────────────────────────────────────────────────
st.subheader('Student Details')
 
if students:
    df_students = pd.DataFrame(students)
    df_students = df_students.rename(columns={
        'StudentName': 'Name',
        'LastActivityDate': 'Last Activity',
        'ApplicationVolume': 'Applications'
    })
    st.dataframe(df_students, use_container_width=True, hide_index=True)
else:
    st.success('All students are active — no flags at this time.')
 