import streamlit as st

from clients.runpod_client import RunpodClient
from streamlit_extras.app_logo import add_logo

from config import Config, PageConfig

st.set_page_config(
    layout=PageConfig.layout,
    page_title=PageConfig.page_title,
    page_icon=PageConfig.page_icon,
)

SCOTI_AVATAR = "frontend/static/images/chatbot_avatars/scoti.png"
USER_AVATAR = "frontend/static/images/chatbot_avatars/user.png"

SCOTI_GIF_PATH = "frontend/static/gifs/SCOTi_04_Wagging-Tail_V2_cropped.gif"


def get_relation_graph():
    return "Here is the relations for..."

def reset_conversation():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Let's start a new conversation. What would you like to ask me?",
        }
    ]
    
SCOTI_FUNCTIONS = {
    "Show me the relation graph for this document": get_relation_graph
}

add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)
st.title("Chat with SCOTi")

client = RunpodClient()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey! I'm SCOTi. Ask me a question using the box below to get started.",
        }
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = message["role"]

    if role == "user":
        avatar = USER_AVATAR
    else:
        avatar = SCOTI_AVATAR

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=SCOTI_AVATAR):
        if prompt in SCOTI_FUNCTIONS:
            bot_response = SCOTI_FUNCTIONS[prompt.strip()]()
            st.write(bot_response)
        else:
            response_generator = client.queue_async_job(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=Config.STREAM_CHAT,
            )

            bot_response = st.write_stream(response_generator)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
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
