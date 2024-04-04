import pandas as pd
import streamlit as st
import colorsys

from streamlit_extras.app_logo import add_logo
from streamlit_extras.switch_page_button import switch_page
import streamlit_shadcn_ui as ui

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

DEFAULT_TEXT = """INTERNET AND MOBILE ASSOCIATION OF INDIA v. RESERVE BANK OF INDIA RESPONDENT (Writ Petition (Civil) No. 528 of 2018) MARCH 04, 2020 [R. F. NARIMAN JUDGE, ANIRUDDHA BOSE JUDGE AND V. RAMASUBRAMANIAN JUDGE, JJ.] Reserve Bank of India Act, 1934 PETITIONER – ss.17, 20-22, 26, 38, 45JA, 45L, 45U, 45W, 45Z-45ZO – Reserve Bank of India ORG (RBI ORG) issued a “Statement on Developmental and Regulatory Policies” dtd. 05.04.18 and circular dtd. 06.04.18 respectively, which directed the entities it regulated (i) not to deal with or provide services to any individual/business entities dealing with/settling virtual currencies (VCs) and (ii) to exit the relationship, if they already have one, with such individuals/business entities – Challenged by petitioners (a specialized industry body representing interests of online & digital services industry; companies running online crypto assets exchange platforms; shareholders/founders thereof and individual crypto assets traders) inter alia on the ground that RBI ORG has no power to prohibit the activity of"""

DEFAULT_TEXT = (
    DEFAULT_TEXT
    + """...\n\n-----------------------\n\nstability and (iii) sound economic growth – Public interest permeates all these three areas – This is why s.35A(1)(a) PROVISION is invoked in the impugned Circular. Constitution of India RESPONDENT – Art.19(1)(g) – Reserve Bank of India ORG (RBI ORG) issued circular directing the entities it regulated to not to deal with or provide services to any individual/business entities dealing with/settling virtual currencies (VCs) and to exit the relationship, if they have one, with such individuals/business entities – Plea of the petitioners (a specialized industry body representing interests of online & digital services industry; companies running online crypto assets exchange platforms; shareholders/founders thereof and crypto assets traders) that a total prohibition, especially through a subordinate legislation such as a directive from RBI, of an activity not declared by law to be unlawful, is violative of Art.19(1)(g) PROVISION – Held: Buying and selling of crypto currencies through VC Exchanges can be by way of hobby or as a trade/business – Persons who engage in buying and selling virtual currencies, just as a matter of hobby cannot pitch their claim on Art.19(1)(g) PROVISION, for what is covered therein are only profession, occupation, trade or business – A B C D E F G H 301 Therefore hobbyists, who are one among the three categories of citizens (hobbyists, traders in VCs and VC Exchanges), straightaway go out of the challenge u/Art.19(1)(g) – Second and third categories of citizens namely, those who have made the purchase and sale of VCs as their occupation or trade, and those who are running online platforms and VC exchanges can certainly pitch their claim on the basis of Art.19(1)(g). Words & Phrases - “currency”, “currency notes”, “Indian currency” “money”, “regulate” - Definition & Meaning of – Discussed. Allowing the writ petitions, the Court HELD: 1.1 Role assigned to, functions entrusted to and the powers conferred upon RBI ORG as a Central Bank Reserve Bank of India ORG (RBI) is now vested with the obligation to operate the monetary policy framework in India GPE. After the amendment under Act 28 of 2016, the very task of operating the monetary policy framework has been conferred exclusively upon RBI ORG. The phrase “credit system of the country to its advantage”, as found in paragraph 1 of the Preamble, is repeated in sub-section (1) of Section 45L. PROVISION The only difference between the two is that paragraph 1 of the Preamble speaks about the operation of the credit system, while Section 45L (1) PROVISION speaks about regulation of the credit system. While exercising the power to issue directions conferred by clause (b) of sub-section (1) of Section 45L, RBI ORG is obliged under sub-section (3) of Section 45L PROVISION to have due regard to certain things, one of them being “the effect the business of such financial institution is likely to have on trends in the money and capital markets”. A careful scan of the RBI Act, STATUTE1934 in its entirety would show that the operation/regulation of the credit/financial system of the country to its advantage, is a thread that connects all the provisions which confer powers upon RBI ORG, both to determine policy and to issue directions. [Paras 6.15, 6.16, 6.26 and 6.30][352-C,E; 355-F-G; 356-G-H] 1.2 The RBI Act, 1934 STATUTE, the Banking Regulation Act, 1949 STATUTE and the Payment and Settlement Systems Act, 2007 STATUTE cumulatively recognize and also confer very wide powers upon RBI ORG (i) to operate the currency and credit system of the country to its INTERNET AND MOBILE ASSOCIATION OF INDIA v. RESERVE BANK OF INDIA A B C D E F G H 302 SUPREME COURT REPORTS [2020] 2 S.C.R. advantage (ii) to take over the management of the currency from central government (iii) to have the sole right to make and issue bank notes that would"""
)

DEFAULT_TEXT = (
    DEFAULT_TEXT
    + """...\n\n-----------------------\n\nPlaintiff Securities and Exchange Commission (the “Commission” or the “SEC”) files this Complaint against Defendants Xue Samuel Lee a/k/a “Sam” Lee (“Lee”) and Brenda Indah Chunga a/k/a “Bitcoin Beautee” (“Chunga”), and alleges as follows:

SUMMARY
1. This case involves a global, crypto asset-related, multi-level marketing pyramid and Ponzi scheme that raised over $1.7 billion from victims worldwide, including millions from U.S. investors. Defendants and others operated the scheme through a series of projects referred to collectively herein as “HyperFund.” 
2. The HyperTech Group, a purported blockchain technology conglomerate founded by Lee and others (collectively, the “Founders”) launched HyperFund in June 2020. At the outset, HyperFund claimed to be a project dedicated to creating a so-called “decentralized finance (DeFi) ecosystem” for crypto asset market participants. Over time, the project’s stated goals evolved and utilized various names in an effort to capitalize on the buzz words and zeitgeist of the day, including rebranding itself as “HyperVerse” and, later, as “HyperNation,” a version of the project which featured an individual in a mask discussing creating a decentralized government to escape the societal bonds of inequality and injustice through blockchain technology. HyperFund, including its subsequent rebranded iterations, is now defunct. 
3. From 06/2020 through 05/022, HyperFund offered so-called “membership” packages promising exorbitant passive returns, supposedly derived in part from HyperFund’s crypto asset mining operations. For example, HyperFund promised returns of 0.5% to 1% per day, with the prospect of tripling ones’ initial investment in 600 days. HyperFund also implemented a pyramid scheme-like referral system to reward existing members for recruiting new investors."""
)

# Initialize state
if 'ner_input' not in st.session_state:
    st.session_state['ner_input'] = DEFAULT_TEXT
if 'ner_highlight' not in st.session_state:
    st.session_state['ner_highlight'] = ""
if 'ner_text_tagged' not in st.session_state: 
    st.session_state['ner_text_tagged'] = ""


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
    highlighted_text = ""
    current_index = 0
    for entity, label in ner_tags:
        start_index = text.find(entity, current_index)
        end_index = start_index + len(entity)
        highlighted_text += text[current_index:start_index]
        highlighted_text += f'<{label}>{entity}</{label}>'
        current_index = end_index
    highlighted_text += text[current_index:]
    return highlighted_text
    

def label_text_entities(text_input):
    # Call the API client to process the text
    response = api_client.process_text(text_input)
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

col1, col2 = st.columns((0.7, 0.3), gap="medium")
with col1:
    text_input = st.text_area("Enter text here:", value=st.session_state['ner_input'], height=250)
with col2:
    # Show table of entity labels
    ner_labels = split_list_into_df(api_client.get_ner_labels(), 3)

    ner_table_html = ner_labels.to_html(index=False, header=False)
    ner_table_html = ner_table_html.replace(
        "<table",
        '<table style="font-size:.875rem; line-height:1.25rem; border-color:#e5e7eb; border-style:solid;"',
    )
    st.write('<h5 style="margin-top:1rem">Labels</h5>', unsafe_allow_html=True)
    st.write(ner_table_html, unsafe_allow_html=True)

# Process and send to scoti buttons
col1_1, col1_2 = st.columns((0.6, 0.4), gap="medium")
with col1_1:
    if st.button("Process"):
        try:
            with st.spinner("Extracting Legal Entities..."):
                st.session_state['ner_input'] = text_input
                highlight_html, ner_text_tagged = label_text_entities(text_input)
                st.session_state['ner_highlight'] = highlight_html
                st.session_state['ner_text_tagged'] = ner_text_tagged
        except Exception as e:
            st.error(f"Error processing text: {e}")
with col1_2:
    if st.button("Send to SCOTi"):
        switch_page("chat with scoti")

# Render text with ner label highlights
st.markdown(st.session_state['ner_highlight'], unsafe_allow_html=True)