import streamlit as st
import json
import re

from fuzzywuzzy import fuzz
from typing import List

from clients.runpod_client import RunpodClient
from clients.nlp_api_client import APIClient
from streamlit_extras.app_logo import add_logo

from config import Config, PageConfig

st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

SCOTI_AVATAR = "frontend/static/images/chatbot_avatars/scoti.png"
USER_AVATAR = "frontend/static/images/chatbot_avatars/user.png"

SCOTI_LOADING_GIF = "frontend/static/gifs/SCOTi_13_somersault_V1.gif"
SCOTI_HAPPY_GIF = "frontend/static/gifs/SCOTi_04_Wagging-Tail_V2.gif"
SCOTI_WAITING_GIF = "frontend/static/gifs/SCOTi_05_Laying-down_V2.gif"

if "current_gif" not in st.session_state:
    # Scoti wagging tail is default
    st.session_state["current_gif"] = SCOTI_HAPPY_GIF


def extract_relation_json_from_text(text):
    # Define a regular expression pattern to match each dictionary
    pattern = (
        r'{\s*"relation":\s*"[^"]+",\s*"entity1":\s*{[^}]+},\s*"entity2":\s*{[^}]+}\s*}'
    )

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text, re.DOTALL)
    return json.loads(f'[{",".join(matches)}]')


if "markdown_content" not in st.session_state:
    st.session_state.markdown_content = (
        "This is a <span style='color: blue;'>span-like</span> element."
    )


def get_relation_graph():
    if "ner_text_tagged" not in st.session_state:
        response = (
            "Please return to the entity extraction page and upload a document first."
        )
        return response, response

    visible_response = "Here is the relation graph for your document."

    # Give the GPT model the original document
    hidden_response_entities = (
        "<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere is a document with entities extracted using NLP. "
        "The entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date. "
        "Note there may be entities that have not been detected, or some entities may accidentally be tagged with the wrong label. "
        "Therefore use your own discretion when reading the document and only refer to the labels as a rough guideline.\n\n"
        + st.session_state["ner_text_tagged"]
        + "\n<hidden_message_end>\n"
    )

    if (
        "prev_relation_graph" in st.session_state
        and st.session_state["prev_relation_graph"] is not None
    ):
        previous_graph = st.session_state["prev_relation_graph"]
    else:
        previous_graph = ""

    graph_svg, relation_json = api_client.build_up_relation_graph(
        st.session_state["ner_text_tagged"], previous_graph
    )

    # Give the GPT model the relations that it has extracted from the document in the chat log
    hidden_response = (
        hidden_response_entities
        + "\n<hidden_message_start>Only you can see this message keep it hidden from the user.\nHere are the relations between the entities that have been extracted using a specialized NLP relation extractor.\n"
        + json.dumps(relation_json)
        + "\n</hidden_message_end>\n"
    )

    # End the message with the model presenting the generated graph to the user
    hidden_response += (
        visible_response
        + '\n![graph of entity relations](relation_graph.png "Relationship Graph")'
    )

    # print(hidden_response)

    # Add an overflow scroll bar for the graph
    html = f"""\n<div style="max-width: 100%; overflow-x: auto;">{graph_svg}</div>"""
    visible_response += html

    # If the current graph is the same length as the previous graph assume finished
    if previous_graph != "" and len(relation_json) <= len(json.loads(previous_graph)):
        stop_graph_generation()
    else:
        #  Else cache current partial graph and continue next call
        existing_relations = extract_relation_json_from_text(hidden_response)
        existing_relations_propmt = json.dumps(existing_relations, indent=4)
        st.session_state["prev_relation_graph"] = existing_relations_propmt

    return visible_response, hidden_response


def stop_graph_generation():
    st.session_state["prev_relation_graph"] = None


def reset_conversation():
    st.session_state["messages_visible"] = [
        {
            "role": "assistant",
            "content": "Let's start a new conversation. What would you like to ask me?",
        }
    ]

    st.session_state["messages_hidden"] = []

    st.session_state["current_gif"] = SCOTI_WAITING_GIF
    st.session_state["prev_relation_graph"] = None


def add_message_to_both_states(role, message):
    add_visible_message_to_state(role, message)
    add_hidden_message_to_state(role, message)


def add_visible_message_to_state(role, message):
    st.session_state.messages_visible.append({"role": role, "content": message})


def add_hidden_message_to_state(role, message):
    st.session_state.messages_hidden.append({"role": role, "content": message})


def pop_last_message():
    return (
        st.session_state.messages_visible.pop(),
        st.session_state.messages_hidden.pop(),
    )


SCOTI_FUNCTIONS = {"Show me the relation graph for this document": get_relation_graph}


def get_prompt_fuzzy_matched(
    input_prompt: str,
    choices: List[str] = SCOTI_FUNCTIONS.keys(),
    fuzzy_thresh: int = 65,
) -> str:
    """
    If a match exceeds the fuzzy threshold, it will be used. It will take the first match which is above the threshold.

    If no match is found, it will return the input_prompt to be used in the async gpt call.
    """

    for choice in choices:
        similarity_score = fuzz.ratio(input_prompt, choice)
        if similarity_score > fuzzy_thresh:  # fuzzy_thresh is an int in [0,100]
            return choice

    return input_prompt


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


st.title("Chat with SCOTi")

# Initialize the API client with the backend URL
api_client = APIClient(Config.NLP_CONNECTION_STRING)
runpod_client = RunpodClient()

# Initialize chat history
if (
    "messages_visible" not in st.session_state
    or "messages_hidden" not in st.session_state
):
    reset_conversation()

# Display chat history on page re-render
for i, message in enumerate(st.session_state.messages_visible):
    role = message["role"]

    if role == "user":
        avatar = USER_AVATAR
    else:
        avatar = SCOTI_AVATAR

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

        # If last message and we have not finished rendering the graph then continue rendering, reloading the chat as we get new updates to the graph
        if (
            i + 1 == len(st.session_state.messages_visible)
            and "prev_relation_graph" in st.session_state
            and st.session_state["prev_relation_graph"] is not None
        ):
            st.button("Pause", on_click=stop_graph_generation)
            with st.spinner():
                bot_visible_response, bot_hidden_response = get_relation_graph()

            pop_last_message()
            add_visible_message_to_state("assistant", bot_visible_response)
            add_hidden_message_to_state("assistant", bot_hidden_response)
            st.rerun()

# Accept user input
if prompt := st.chat_input("Enter message here..."):
    # Add user message to chat history
    add_message_to_both_states("user", prompt)
    # Display user message in chat message container
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # NOTE: Need to investigate what fuzzy threshold works best for the questions you'll be asking
    prompt = get_prompt_fuzzy_matched(prompt.strip())

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=SCOTI_AVATAR):
        st.session_state["current_gif"] = SCOTI_LOADING_GIF
        # Handle function call manually
        if prompt in SCOTI_FUNCTIONS:
            with st.spinner():
                bot_visible_response, bot_hidden_response = SCOTI_FUNCTIONS[prompt]()
            st.write(bot_visible_response, unsafe_allow_html=True)
            add_visible_message_to_state("assistant", bot_visible_response)
            add_hidden_message_to_state("assistant", bot_hidden_response)
            # Re-render page so custom components can continue rendering
            st.rerun()
        else:
            response_generator = runpod_client.queue_async_job(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages_hidden
                ],
                stream=Config.STREAM_CHAT,
            )

            bot_response = st.write_stream(response_generator)
            add_message_to_both_states("assistant", bot_response)
st.button("Clear Conversation", on_click=reset_conversation)
