import streamlit as st
from datetime import datetime
import json
import asyncio

from fuzzywuzzy import fuzz
from typing import List

from clients.runpod_client import RunpodClient
from clients.inference_client import InferenceClient
from clients.nlp_api_client import APIClient
from streamlit_extras.app_logo import add_logo

from config import Config, PageConfig
from components.relation_graph import draw_relation_graph, extract_relation_json_from_text, get_relation_graph

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


def stop_graph_generation():
    if "graph_building_cache" in st.session_state:
        del st.session_state["graph_building_cache"]


def reset_conversation():
    st.session_state["messages_visible"] = [
        {
            "role": "assistant",
            "content": "I'm generating a relation graph for your document. Please wait...",
        }
    ]

    if st.session_state.get('ner_text_tagged') is not None:
        st.session_state["messages_hidden"] = [
            {
                "role": "user",
                "content": "Here is a document with entities extracted using NLP that I will ask you questions about. " \
                        "The entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date. " \
                        "Note there may be entities that have not been detected, or some entities may accidentally be tagged with the wrong label. " \
                        "Therefore use your own discretion when reading the document and only refer to the labels as a rough guideline.\n\n" \
                        + st.session_state['ner_text_tagged']
            },
            {
                "role": "assistant",
                "content":  "Great I see your document regarding a court case with labelled named entities. What would you like to know about it?"   
            }
        ]
    else:
        st.session_state["messages_hidden"] = []

    st.session_state["current_gif"] = SCOTI_WAITING_GIF
    stop_graph_generation()


def save_graph(graph):
    filename = "relation-graph-" + datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"
    file_contents = json.dumps(graph, indent=4)
    with open(filename, 'w') as file:
        file.write(file_contents) 
    st.download_button(
        label="Download file",
        data=file_contents,
        file_name=filename,
        mime="text/plain",
    )


def delete_last_message():
    deleted_message = st.session_state["messages_visible"].pop()
    if st.session_state["messages_hidden"][-1]['role'] == deleted_message['role']:
        st.session_state["messages_hidden"].pop()
            

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


SCOTI_FUNCTIONS = {"Hey SCOTi, can you show me the relation graph for this document?": get_relation_graph}


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
if Config.RUNPOD_SERVERLESS:
    gpt_client = RunpodClient()
else:
    gpt_client = InferenceClient()

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
        if '"relation":' in message["content"]:
            # Assume this response includes a relation graph
            st.markdown(message["content"].split("[")[0])
            relation_json = extract_relation_json_from_text(message["content"])
            draw_relation_graph(relation_json, 4)
            # st.button("Save Graph", on_click=save_graph, kwargs={"graph": relation_json})
            filename = "relation-graph-" + datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt"
            file_contents = json.dumps(relation_json, indent=4) 
            st.download_button(
                label="Download file",
                data=file_contents,
                file_name=filename,
                mime="text/plain",
            )
        else:
            # Assume this is just a text response
            st.markdown(message["content"], unsafe_allow_html=True)

        # If last message and we have not finished rendering the graph then continue rendering, reloading the chat as we get new updates to the graph
        if i+1 == len(st.session_state.messages_visible) and st.session_state.get('graph_building_cache') is not None:
            st.button("Pause", on_click=stop_graph_generation)            
            with st.spinner():
                bot_visible_response, bot_hidden_response = get_relation_graph(api_client)
                
            pop_last_message()
            add_visible_message_to_state("assistant", bot_visible_response)
            add_hidden_message_to_state("assistant", bot_hidden_response)
            st.rerun()

# First entry with pre-defined prompt
if "not_first_entry" not in st.session_state:
    st.session_state["not_first_entry"] = True
    prompt = "Hey SCOTi, can you show me the relation graph for this document?"
    with st.spinner():
            bot_visible_response, bot_hidden_response = SCOTI_FUNCTIONS[prompt](api_client)
    st.write(bot_visible_response, unsafe_allow_html=True)
    add_visible_message_to_state("assistant", bot_visible_response)
    add_hidden_message_to_state("assistant", bot_hidden_response)
    # Re-render page so custom components can continue rendering
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
                bot_visible_response, bot_hidden_response = SCOTI_FUNCTIONS[prompt](api_client)
            st.write(bot_visible_response, unsafe_allow_html=True)
            add_visible_message_to_state("assistant", bot_visible_response)
            add_hidden_message_to_state("assistant", bot_hidden_response)
            # Re-render page so custom components can continue rendering
            st.rerun()
        else:
            response_generator = gpt_client.queue_async_job(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages_hidden
                ],
                stream=Config.STREAM_CHAT,
            )

            if Config.STREAM_CHAT:
                bot_response = st.write_stream(response_generator)
            else:
                with st.spinner():
                    bot_response = st.write_stream(response_generator)
                
            add_message_to_both_states("assistant", bot_response)


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

# Chat Buttons
col1, col2, _ = st.columns((1, 1, 1), gap="small")
with col1:  
    st.button("Clear Conversation", on_click=reset_conversation)
with col2:
    st.button("Delete last message", on_click=delete_last_message)
    
st.session_state["current_gif"] = SCOTI_HAPPY_GIF