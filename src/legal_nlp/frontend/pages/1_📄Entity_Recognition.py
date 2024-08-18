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
SCOTi can extract entities from text with ease. Simply enter your text, and let SCOTi extract key information for you!
"""
    )
    _, scoti_gif_sizing, _ = st.columns((0.25, 0.5, 0.25), gap="medium")

    with scoti_gif_sizing:
        st.image(SCOTI_GIF_PATH)


st.title("Entity Recognition")

# Initialize the API client with the backend URL
api_client = APIClient(Config.NLP_CONNECTION_STRING)

# Can accept multiple files currently
uploaded_files = st.file_uploader(
    label="Upload legal document here or simply enter the text to be processed below:",
    # label_visibility="hidden",
    accept_multiple_files=True,
    type=[".docx", ".pdf", ".txt", ".rtf"],
)
show_processed_text = False
# This needs to be before where the text_area input box is defined
if uploaded_files:
    st.session_state.ner_input = load_file_contents(uploaded_files)

c_1, c_2 = st.columns((0.8, 0.2), gap="medium")
with c_1.expander("🞂 Input Text And Labels", expanded=not show_processed_text):

    col1, col2 = st.columns((0.7, 0.3), gap="medium")
    with col1:
        text_input = st.text_area(
            "Enter text here:",
            value=st.session_state["ner_input"],
            height=250,
        )
        labels_input = st_tags(
            label='Entity labels:',
            text='Press enter to add more',
            value=['person', 'organization', 'location', 'person', 'date', 'law', 'technology', 'number'],
            suggestions=[],
            maxtags = 16,
            key='ner_labels')
    with col2:
        # Show table of entity labels
        ner_labels = split_list_into_df(api_client.get_ner_labels(), 1)

        ner_table_html = ner_labels.to_html(index=False, header=False)
        ner_table_html = ner_table_html.replace(
            "<table",
            '<table style="font-size:.875rem; line-height:1.25rem; border-color:#e5e7eb; border-style:solid;"',
        )
        st.write('<h5 style="margin-top:1rem">Labels</h5>', unsafe_allow_html=True)
        st.write(ner_table_html, unsafe_allow_html=True)

# Process and send to scoti buttons

with c_2:
    if st.button("Process text",help="If you have upload all documents and/or entered all text, click here to process entity extraction."):
        try:
            with st.spinner("Extracting Legal Entities ..."):
                st.session_state["ner_input"] = text_input
                highlight_html, ner_text_tagged = label_text_entities(text_input)
                st.session_state["ner_highlight"] = highlight_html
                st.session_state["ner_text_tagged"] = ner_text_tagged
        except Exception as e:
            st.error(f"Error processing text: {e}")


# Render text with ner label highlights
# Double up new lines to render in markdown, replace 2 space indents with html space tag
display_text = st.session_state['ner_highlight'].replace('\n', '\n\n').replace('  ','&nbsp;&nbsp;')

c_1, c_2 = st.columns((0.8, 0.2), gap="medium")
with c_1.expander("🞂 Processed Text", expanded=show_processed_text):
    st.markdown(display_text, unsafe_allow_html=True)

with c_2:
    if st.button("Generate relation graph",help="Click here to send your text to SCOTi.",):
        switch_page("chat with scoti")
