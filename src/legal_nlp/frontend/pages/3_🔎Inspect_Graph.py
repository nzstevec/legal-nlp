import streamlit as st
import json
from streamlit_extras.app_logo import add_logo

from config import PageConfig
from components.relation_graph import draw_relation_graph


def load_graph(filepath):
    graph_json = json.load(filepath)
    return graph_json


st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)

with st.sidebar:
    description = st.markdown(
        f"""
Chat with SCOTi directly and ask any questions about your legal documents!
"""
    )
    _, scoti_gif_sizing, _ = st.columns((0.25, 0.5, 0.25), gap="medium")

    with scoti_gif_sizing:
        st.image(st.session_state["current_gif"])


st.title("Load Relation Graph")

uploaded_files = st.file_uploader(
    label="File Uploader",
    label_visibility="hidden",
    accept_multiple_files=False,
    type=[".txt"],
)

if uploaded_files:
    st.session_state.inspecting_graph = load_graph(uploaded_files)

if st.session_state.get('inspecting_graph') is not None:
    draw_relation_graph(st.session_state.inspecting_graph, 4)