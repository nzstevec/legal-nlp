import streamlit as st
from streamlit_extras.app_logo import add_logo

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

add_logo("frontend\\static\\images\\smartR-AI-logo-RGB_250x90.png", height=65)

st.write("# Welcome to SCOTi! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    SCOTi is ...
"""
)