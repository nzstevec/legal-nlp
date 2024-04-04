import streamlit as st
import graphviz
import time

from clients.runpod_client import RunpodClient
from streamlit_extras.app_logo import add_logo

from config import Config, PageConfig

st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

SCOTI_AVATAR = "frontend/static/images/chatbot_avatars/scoti.png"
USER_AVATAR = "🧑‍💻"

SCOTI_GIF_PATH = "frontend/static/gifs/SCOTi_04_Wagging-Tail_V2_cropped.gif"

def get_relation_graph():
    if 'ner_text_tagged' not in st.session_state:
        response = "Please return to the entity extraction page and upload a document first."
        return response, response
    
    visible_response = "Here is the relation graph for your document."
    
    hidden_response = "<hidden_message>Here is a document with entities extracted using NLP. " \
        "The entities are represented using angled bracket tags, for example <DATE>17 December 2020</DATE> represents a detected date. " \
        "Note there may be entities that have not been detected, or some entities may accidentally be tagged with the wrong label. " \
        "Therefore use your own discretion when reading the document and only refer to the labels as a rough guideline.\n\n" \
        + st.session_state['ner_text_tagged'] \
        + "\n</hidden_message>\n" + visible_response + "\n![graph of entity relations](relation_graph.png \"Relationship Graph\")"
    
    # Placeholder sleep
    # time.sleep(5)
    
    # Define the DOT representation of the graph
    dot_graph = """
    digraph G {
        "Carmichael" -> "OneSteel" [label="Contracted_With"];
        "OneSteel" -> "Whyalla" [label="Arranged_For_Shipment"];
        "Whyalla" -> "Mackay" [label="Shipped_To"];
        "BBC" -> "OneSteel" [label="Prepared_Stowage_Plan"];
        "OneSteel" -> "OneSteel's subcontractor" [label="Loaded_Onto_Ship"];
    }
    """

    # Render the graph from the DOT representation
    graph = graphviz.Source(dot_graph)

    # Convert the graph to SVG format
    graph_svg = graph.pipe(format='svg').decode('utf-8')

    # Render the SVG image with a responsive layout
    html = f"""\n<div style="max-width: 100%; overflow-x: auto;">{graph_svg}</div>"""
    
    visible_response += html    
    return visible_response, hidden_response

def reset_conversation():
    st.session_state['messages_visible'] = [
        {
            "role": "assistant",
            "content": "Let's start a new conversation. What would you like to ask me?",
        }
    ]
    
    st.session_state['messages_hidden'] = [
        {
            "role": "assistant",
            "content": "Let's start a new conversation. What would you like to ask me?",
        }
    ]

def add_message_to_both_states(role, message):
    add_visible_message_to_state(role, message)
    add_hidden_message_to_state(role, message)
 
def add_visible_message_to_state(role, message):
    st.session_state.messages_visible.append({"role": role, "content": message})
    
def add_hidden_message_to_state(role, message):
    st.session_state.messages_hidden.append({"role": role, "content": message})

SCOTI_FUNCTIONS = {
    "Show me the relation graph for this document": get_relation_graph
}

add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)
st.title("Chat with SCOTi")

client = RunpodClient()

# Initialize chat history
if "messages_visible" not in st.session_state or "messages_hidden" not in st.session_state:
    reset_conversation()

# Display chat messages from history on app rerun
for message in st.session_state.messages_visible:
    role = message["role"]

    if role == "user":
        avatar = USER_AVATAR
    else:
        avatar = SCOTI_AVATAR

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

# Accept user input
if prompt := st.chat_input("Enter message here..."):
    # Add user message to chat history
    add_message_to_both_states("user", prompt)
    # Display user message in chat message container
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=SCOTI_AVATAR):
        # Handle function call manually
        if prompt in SCOTI_FUNCTIONS:
            with st.spinner():
                bot_visible_response, bot_hidden_response = SCOTI_FUNCTIONS[prompt.strip()]()
                
            st.write(bot_visible_response, unsafe_allow_html=True)
            add_visible_message_to_state("assistant", bot_visible_response)
            add_hidden_message_to_state("assistant", bot_hidden_response)
        else:
            response_generator = client.queue_async_job(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages_hidden
                ],
                stream=Config.STREAM_CHAT,
            )

            bot_response = st.write_stream(response_generator)
            add_message_to_both_states("assistant", bot_response)
    st.button("Clear Conversation", on_click=reset_conversation)


with st.sidebar:
    description = st.markdown(
        f"""
SCOTi **This bit I don't know what we want scoti to be answering questions about** answer questions about your legal documents too.
"""
    )
    scoti_gif_sizing, _ = st.columns((0.5, 0.5), gap="medium")

    with scoti_gif_sizing:
        st.image(SCOTI_GIF_PATH)
