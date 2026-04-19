import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("About OfferWatch")
st.markdown("---")

st.markdown(
    """
    OfferWatch is a data driven job search platform that brings structure, clarity, and useful data to the recruiting process for students, advisors, recruiters, and administrators. OfferWatch combines the employment process into a single platform with a common relational database, reducing the need for several documents and emails.
    """
)

st.markdown("---")

st.subheader("Team GOATS")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("**Ansh Vats**")
    st.write("vats.an@northeastern.edu")

with col2:
    st.markdown("**Vansh Kumar**")
    st.write("kumar.van@northeastern.edu")

with col3:
    st.markdown("**Rudra Patel**")
    st.write("patel.rudra4@northeastern.edu")

with col4:
    st.markdown("**Amogh Peddapothla**")
    st.write("peddapothla.a@northeastern.edu")

with col5:
    st.markdown("**Brian Skiles**")
    st.write("skiles.b@northeastern.edu")

st.markdown("---")

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
