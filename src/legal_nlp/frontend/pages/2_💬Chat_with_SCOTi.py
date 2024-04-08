import streamlit as st

from fuzzywuzzy import fuzz
from typing import List

from clients.runpod_client import RunpodClient
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
            "content": "Let's start a new conversation. What would you like to ask me?",
        }
    ]

    st.session_state["messages_hidden"] = []

    st.session_state["current_gif"] = SCOTI_WAITING_GIF
    stop_graph_generation()
    

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
        if '"relation":' in message["content"]:
            # Assume this response includes a relation graph
            st.markdown(message["content"].split("[")[0])
            relation_json = extract_relation_json_from_text(message["content"])
            draw_relation_graph(relation_json)
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
st.session_state["current_gif"] = SCOTI_HAPPY_GIF