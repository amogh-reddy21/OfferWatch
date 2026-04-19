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
 
st.title('Industry Status Dashboard')
st.caption(f"Logged in as Dr. {st.session_state.get('first_name', 'Maria')} Patel — Career Advisor")
st.divider()
 
# ── Fetch resume success rates (US3) ─────────────────────────────────────────
try:
    r1 = requests.get(f'http://web-api:4000/advisor/{advisor_id}/resumes/success-rates')
    r1.raise_for_status()
    resume_data = r1.json()
except Exception as e:
    st.error(f"Could not load resume data: {e}")
    resume_data = []
 
# ── Fetch top employers (US4) ─────────────────────────────────────────────────
try:
    r2 = requests.get(f'http://web-api:4000/advisor/{advisor_id}/employers/top-offers')
    r2.raise_for_status()
    employer_data = r2.json()
except Exception as e:
    st.error(f"Could not load employer data: {e}")
    employer_data = []
 
# ── Summary metric cards ──────────────────────────────────────────────────────
st.subheader('Cohort Summary')
 
if resume_data:
    df_r = pd.DataFrame(resume_data)
    df_r['InterviewRate'] = pd.to_numeric(df_r['InterviewRate'], errors='coerce')
    df_r['Applications']  = pd.to_numeric(df_r['Applications'],  errors='coerce')
    df_r['Interviews']    = pd.to_numeric(df_r['Interviews'],    errors='coerce')
    avg_rate         = round(df_r['InterviewRate'].mean(), 1)
    avg_apps         = round(df_r['Applications'].mean(), 0)
    total_industries = df_r['Industry'].nunique()
else:
    avg_rate, avg_apps, total_industries = 0, 0, 0
 
if employer_data:
    total_offers = sum(e['OffersExtended'] for e in employer_data)
else:
    total_offers = 0
 
c1, c2, c3, c4 = st.columns(4)
c1.metric('Avg Interview Rate',            f"{avg_rate}%")
c2.metric('Avg Applications per Resume',   int(avg_apps))
c3.metric('Industries Tracked',            total_industries)
c4.metric('Total Offers Extended',         total_offers)
 
st.divider()
 
# ── Charts row ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)
 
with col_left:
    st.subheader('Market Share by Industry')
    if resume_data:
        df_chart = pd.DataFrame(resume_data)
        df_chart['Applications'] = pd.to_numeric(df_chart['Applications'], errors='coerce')
        industry_apps = df_chart.groupby('Industry')['Applications'].sum()
        st.bar_chart(industry_apps)
    else:
        st.info('No data available.')
 
with col_right:
    st.subheader('Placement Rate per Industry (Interview Rate)')
    if resume_data:
        df_chart2 = pd.DataFrame(resume_data)
        df_chart2['InterviewRate'] = pd.to_numeric(df_chart2['InterviewRate'], errors='coerce')
        industry_rate = df_chart2.groupby('Industry')['InterviewRate'].mean().round(1)
        st.bar_chart(industry_rate)
    else:
        st.info('No data available.')
 
st.divider()
 
# ── Resume version comparison table (US3) ─────────────────────────────────────
st.subheader('Resume Version Success Rates by Industry')
st.caption('Compare which resume version performs best in each industry.')
 
if resume_data:
    df_resume = pd.DataFrame(resume_data)
    df_resume['InterviewRate'] = pd.to_numeric(df_resume['InterviewRate'], errors='coerce')
    df_resume['Applications']  = pd.to_numeric(df_resume['Applications'],  errors='coerce')
    df_resume['Interviews']    = pd.to_numeric(df_resume['Interviews'],    errors='coerce')
    df_resume = df_resume.rename(columns={
        'Version':       'Resume Version',
        'Industry':      'Industry',
        'Applications':  'Applications',
        'Interviews':    'Interviews',
        'InterviewRate': 'Interview Rate (%)'
    })
    st.dataframe(df_resume, use_container_width=True, hide_index=True)
else:
    st.info('No resume data available.')
 
st.divider()
 
# ── Top employers table (US4) ─────────────────────────────────────────────────
st.subheader('Industry Details — Top Employers by Offers')
st.caption('Companies offering the most roles to your students.')
 
if employer_data:
    df_emp = pd.DataFrame(employer_data)
    df_emp = df_emp.rename(columns={
        'Industry':       'Industry',
        'EmployerName':   'Company',
        'Location':       'Location',
        'OffersExtended': 'Offers Extended'
    })
    st.dataframe(df_emp, use_container_width=True, hide_index=True)
else:
    st.info('No employer data available.')
 