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
 
st.title('Flagged Students')
st.caption(f"Logged in as Dr. {st.session_state.get('first_name', 'Maria')} Patel — Career Advisor")
st.write('Students who have been inactive for 14+ days or have zero applications are flagged below.')
st.divider()
 
# ── Fetch flagged students ────────────────────────────────────────────────────
try:
    r = requests.get(f'http://web-api:4000/advisor/{advisor_id}/students/flagged')
    r.raise_for_status()
    flagged = r.json()
except Exception as e:
    st.error(f"Could not load flagged students: {e}")
    st.stop()
 
# ── Summary metric cards ──────────────────────────────────────────────────────
total_flagged   = len(flagged)
zero_apps       = sum(1 for s in flagged if s.get('ApplicationVolume', 0) == 0)
inactive        = sum(1 for s in flagged if s.get('ApplicationVolume', 0) > 0)
 
c1, c2, c3 = st.columns(3)
c1.metric('Total Flagged Students', total_flagged)
c2.metric('Zero Applications', zero_apps)
c3.metric('Inactive 14+ Days', inactive)
 
st.divider()
 
# ── Application volume bar chart ──────────────────────────────────────────────
if flagged:
    df = pd.DataFrame(flagged)
 
    col_left, col_right = st.columns(2)
 
    with col_left:
        st.subheader('Application Volume per Flagged Student')
        chart_df = df.set_index('StudentName')['ApplicationVolume']
        st.bar_chart(chart_df)
 
    with col_right:
        st.subheader('Last Activity Date')
        df_activity = df[['StudentName', 'LastActivityDate']].copy()
        df_activity['LastActivityDate'] = pd.to_datetime(
            df_activity['LastActivityDate'], errors='coerce'
        )
        df_activity = df_activity.sort_values('LastActivityDate')
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
 
    st.divider()
 
    # ── Full flagged student table ────────────────────────────────────────────
    st.subheader('Flagged Student Details')
 
    df_display = df.rename(columns={
        'StudentID':         'ID',
        'StudentName':       'Name',
        'LastActivityDate':  'Last Activity',
        'ApplicationVolume': 'Applications'
    })
 
    # colour-code zero-application rows
    def highlight_zero(row):
        if row['Applications'] == 0:
            return ['background-color: #fff3cd'] * len(row)
        return [''] * len(row)
 
    st.dataframe(
        df_display.style.apply(highlight_zero, axis=1),
        use_container_width=True,
        hide_index=True
    )
 
    st.caption('🟡 Yellow rows = students with zero applications submitted.')
 
    st.divider()
 
    # ── Per-student drill-down ────────────────────────────────────────────────
    st.subheader('Drill Down — Individual Student Application Log')
 
    selected = st.selectbox(
        'Select a student to review their applications:',
        options=df['StudentName'].tolist()
    )
 
    selected_id = int(df.loc[df['StudentName'] == selected, 'StudentID'].values[0])
 
    try:
        r2 = requests.get(
            f'http://web-api:4000/advisor/{advisor_id}/students/{selected_id}/applications'
        )
        r2.raise_for_status()
        apps = r2.json()
    except Exception as e:
        st.error(f"Could not load applications: {e}")
        apps = []
 
    if apps:
        df_apps = pd.DataFrame(apps)
        df_apps = df_apps.rename(columns={
            'ApplicationID':    'App ID',
            'Application_Date': 'Date Applied',
            'Status':           'Status',
            'PositionTitle':    'Position',
            'EmployerName':     'Employer',
            'InterviewDate':    'Interview Date',
            'InterviewType':    'Interview Type',
            'RecruiterFeedback':'Recruiter Feedback',
            'Salary':           'Salary',
            'Deadline':         'Offer Deadline',
            'OfferAccepted':    'Offer Accepted'
        })
        st.dataframe(df_apps, use_container_width=True, hide_index=True)
 
        # ── Add a note ────────────────────────────────────────────────────────
        st.subheader(f'Add a Coaching Note for {selected}')
 
        app_ids = [a['ApplicationID'] for a in apps] if apps else []
        selected_app_id = st.selectbox('Select Application ID to annotate:', app_ids)
 
        note_text = st.text_area('Note', placeholder='e.g. Student should follow up with recruiter...')
 
        if st.button('Save Note', type='primary'):
            if not note_text.strip():
                st.warning('Please enter a note before saving.')
            else:
                try:
                    resp = requests.post(
                        f'http://web-api:4000/advisor/{advisor_id}/students/{selected_id}/applications/{selected_app_id}/notes',
                        json={'note_text': note_text}
                    )
                    if resp.status_code == 201:
                        st.success('Note saved successfully.')
                    else:
                        st.error(f"Failed to save note: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info(f'{selected} has no applications on record.')
 
else:
    st.success('No flagged students — your entire cohort is active and on track!')
 