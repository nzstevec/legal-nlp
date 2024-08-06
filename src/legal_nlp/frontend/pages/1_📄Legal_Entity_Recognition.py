import pandas as pd
import streamlit as st
import colorsys

from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page
import streamlit_shadcn_ui as ui
from streamlit_tags import st_tags

from utils.text_extraction import load_file_contents
from clients.nlp_api_client import APIClient
from config import Config, PageConfig

SCOTI_GIF_PATH = "frontend/static/gifs/SCOTi_10_Sniffing-Clues_V2.gif"

# Define a limited color palette
COLOR_PALETTE = [
    "#97E5D7",
    "#B5E8D8",
    "#D2EBD8",
    "#E7EEDB",
    "#FCF1DD",
    "#FEE3CB",
    "#FFD4B8",
]

DEFAULT_TEXT = ""

# Initialize state
if "ner_input" not in st.session_state:
    st.session_state["ner_input"] = DEFAULT_TEXT
if "ner_highlight" not in st.session_state:
    st.session_state["ner_highlight"] = ""
if "ner_text_tagged" not in st.session_state:
    st.session_state["ner_text_tagged"] = ""


def saturate_lighten_color(hex_color, percentage):
    # Remove the "#" symbol and parse the hex color
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert RGB to HSL
    hls = colorsys.rgb_to_hls(*[component / 255.0 for component in rgb])
    h, l, s = hls

    # Increase the saturation
    s = min(1, s * (1 + percentage / 100))
    # Increase the lightness
    l = min(1, l * (1 + percentage / 100))

    # Convert back to RGB
    rgb = colorsys.hls_to_rgb(h, l, s)
    rgb = tuple(int(component * 255) for component in rgb)

    # Convert the saturated RGB values back to hex color
    saturated_hex = "#{:02x}{:02x}{:02x}".format(*rgb)
    return saturated_hex


def highlight_ner(text, ner_tags, label_colors):
    highlighted_text = ""
    current_index = 0
    for entity, label in ner_tags:
        start_index = text.find(entity, current_index)
        end_index = start_index + len(entity)
        label_color = label_colors.get(label, "yellow")
        label_tag_color = saturate_lighten_color(label_color, -20)
        highlighted_text += text[current_index:start_index]
        highlighted_text += f'<mark style="background-color: {label_color};">{entity} <span style="font-size:.75rem; line-height:1rem; font-weight:600; border-radius:0.25rem; background-color:{label_tag_color}; padding-left:0.25rem; padding-right:0.25rem">{label}</span></mark>'
        current_index = end_index
    highlighted_text += text[current_index:]
    return highlighted_text


def add_plaintext_tags(text, ner_tags):
    tagged_text = ""
    current_index = 0
    for entity, label in ner_tags:
        start_index = text.find(entity, current_index)
        end_index = start_index + len(entity)
        tagged_text += text[current_index:start_index]
        tagged_text += f"<{label}>{entity}</{label}>"
        current_index = end_index
    tagged_text += text[current_index:]
    return tagged_text


def label_text_entities(text_input):
    # Call the API client to process the text
    response = api_client.process_text(text_input, labels_input)
    ner_tags = response["ner_tags"]

    # Assign colors from the color palette to each label
    unique_tags = set([sublist[1] for sublist in ner_tags])
    label_colors = {}
    for i, label in enumerate(unique_tags):
        label_colors[label] = COLOR_PALETTE[
            i % len(COLOR_PALETTE)
        ]  # Use modulus to cycle through the color palette

    # Highlight NER tags using dynamic labels and colors
    highlighted_html = highlight_ner(text_input, ner_tags, label_colors)
    tagged_plaintext = add_plaintext_tags(text_input, ner_tags)

    return highlighted_html, tagged_plaintext


def split_list_into_df(my_list, num_columns):
    # Calculate the number of rows needed for the DataFrame
    num_rows = -(-len(my_list) // num_columns)
    # Pad the list if necessary to make sure it's evenly divisible
    my_list += [None] * (num_rows * num_columns - len(my_list))
    # Reshape the list into a 2D array
    data = [my_list[i : i + num_columns] for i in range(0, len(my_list), num_columns)]

    df = pd.DataFrame(data, columns=[f"Column{i+1}" for i in range(num_columns)])
    df.style.hide()
    return df


st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)

with st.sidebar:
    description = st.markdown(
        f"""
SCOTi can extract legal entities from text with ease. Simply enter your text, and let SCOTi extract key information for you!
"""
    )
    _, scoti_gif_sizing, _ = st.columns((0.25, 0.5, 0.25), gap="medium")

    with scoti_gif_sizing:
        st.image(SCOTI_GIF_PATH)


st.title("Legal Entity Recognition")

# Initialize the API client with the backend URL
api_client = APIClient(Config.NLP_CONNECTION_STRING)

# Can accept multiple files currently
uploaded_files = st.file_uploader(
    label="File Uploader",
    label_visibility="hidden",
    accept_multiple_files=True,
    type=[".docx", ".pdf", ".txt", ".rtf"],
)

# This needs to be before where the text_area input box is defined
if uploaded_files:
    st.session_state.ner_input = load_file_contents(uploaded_files)


labels_input = st_tags(
    label='Entity labels:',
    text='Press enter to add more',
    value=['person', 'company'],
    suggestions=[],
    maxtags = 16,
    key='ner_labels')

text_input = st.text_area(
    "Enter text here:",
    value=st.session_state["ner_input"],
    height=250,
)

# Evenly space columns
st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)

# Process and send to scoti buttons
col1_1, col1_2, _ = st.columns((1,1,1), gap="small")
with col1_1:
    if st.button("Process"):
        try:
            with st.spinner("Extracting Legal Entities..."):
                st.session_state["ner_input"] = text_input
                highlight_html, ner_text_tagged = label_text_entities(text_input)
                st.session_state["ner_highlight"] = highlight_html
                st.session_state["ner_text_tagged"] = ner_text_tagged
        except Exception as e:
            st.error(f"Error processing text: {e}")
with col1_2:
    if st.button("Send to SCOTi"):
        switch_page("chat with scoti")

# Render text with ner label highlights
# Double up new lines to render in markdown, replace 2 space indents with html space tag
display_text = st.session_state['ner_highlight'].replace('\n', '\n\n').replace('  ','&nbsp;&nbsp;')
st.markdown(display_text, unsafe_allow_html=True)
