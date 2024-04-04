import streamlit as st
from streamlit_extras.app_logo import add_logo

from config import PageConfig

st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)

st.write("# Welcome to SCOTi! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
SCOTi™ AI,  your loyal companion by smartR AI, is a powerful, customized AI 
assistant that helps organizations unlock the value in their data. It is built 
using state-of-the-art large language models that can understand context 
and generate human-like responses.

### Key Benefits

| **Benefit**     | **Details**      |
| ------------- | ------------- |
| Data privacy and security | SCOTi keeps data safe and confidential. It is self-hosted for extra security.|
| Cost savings | SCOTi requires far less computing power than other models, saving significantly on costs.|
| Improved efficiency | SCOTi frees up employees from menial tasks so they can focus on more strategic initiatives. This leads to major productivity and efficiency gains. |
| Personalization | SCOTi is customized for each client's unique needs. This ensures high-quality, relevant results tailored to each business. |
| Time savings | SCOTi has extraordinary data and information retrieval abilities, saving teams huge amounts of time digging for information. |
| Easy-to-understand | SCOTi communicates insights from data analysis in straightforward English anyone can understand. No coding or data science expertise required. |
| Ownership | When SCOTi gets trained for you, you own the final model. That’s a refreshing change from the SaaS and license fees you have to pay now |
"""
)
