import streamlit as st

# ---- General ------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")

def about_page_nav():
    st.sidebar.page_link("pages/99_About.py", label="About", icon="🧠")


# ---- Role: Student ------------------------------------------------------

def student_home_nav():
    st.sidebar.page_link("pages/00_Student_Home.py", label="Student Home", icon="🎓")

def student_applications_nav():
    st.sidebar.page_link("pages/01_Student_Applications.py", label="Student Applications", icon="📄")

def student_offers_nav():
    st.sidebar.page_link("pages/02_Student_Offers.py", label="Student Offers", icon="💼")

def student_reminders_nav():
    st.sidebar.page_link("pages/03_Student_Reminders.py", label="Student Reminders", icon="⏰")


# ---- Role: Analyst ------------------------------------------------------

def analyst_home_nav():
    st.sidebar.page_link("pages/10_Analyst_Home.py", label="Analyst Home", icon="📊")

def analytics_dashboard_nav():
    st.sidebar.page_link("pages/17_Analytics_Dashboard.py", label="Analytics Dashboard", icon="📈")

def trends_nav():
    st.sidebar.page_link("pages/12_Trends.py", label="Trends", icon="📉")

def salary_nav():
    st.sidebar.page_link("pages/13_Salary_Insights.py", label="Salary Insights", icon="💰")


# ---- Role: Recruiter ----------------------------------------------------

def recruiter_home_nav():
    st.sidebar.page_link("pages/20_Recruiter_Home.py", label="Recruiter Home", icon="🤝")

def candidates_nav():
    st.sidebar.page_link("pages/21_Candidates.py", label="Candidates", icon="🧑‍💼")

def candidate_profile_nav():
    st.sidebar.page_link("pages/22_Candidate_Profile.py", label="Candidate Profile", icon="👤")

def recruiter_notes_nav():
    st.sidebar.page_link("pages/23_Recruiter_Notes.py", label="Recruiter Notes", icon="📝")


# ---- Role: Administrator -----------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/30_Admin_Home.py", label="Admin Home", icon="🖥️")

def system_logs_nav():
    st.sidebar.page_link("pages/31_System_Logs.py", label="System Logs", icon="📋")

def health_metrics_nav():
    st.sidebar.page_link("pages/32_Health_Metrics.py", label="Health Metrics", icon="❤️")

def user_management_nav():
    st.sidebar.page_link("pages/33_User_Management.py", label="User Management", icon="👥")


# ---- Sidebar Builder ----------------------------------------------------

def SideBarLinks(show_home=False):
    st.sidebar.image("assets/logo.png", width=150)

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if show_home:
        home_nav()

    if not st.session_state["authenticated"]:
        about_page_nav()
        return

    role = st.session_state.get("role", "")

    if role == "student":
        student_home_nav()
        student_applications_nav()
        student_offers_nav()
        student_reminders_nav()

    elif role == "analyst":
        analyst_home_nav()
        analytics_dashboard_nav()
        trends_nav()
        salary_nav()

    elif role == "recruiter":
        recruiter_home_nav()
        candidates_nav()
        candidate_profile_nav()
        recruiter_notes_nav()

    elif role == "administrator":
        admin_home_nav()
        system_logs_nav()
        health_metrics_nav()
        user_management_nav()

    about_page_nav()

    if st.sidebar.button("Logout", key=f"logout_{role or 'guest'}"):
        st.session_state.clear()
        st.switch_page("Home.py")