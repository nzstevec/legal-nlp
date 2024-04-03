import streamlit as st
from clients.runpod_client import RunpodClient
from streamlit_extras.app_logo import add_logo
from config import Config

st.set_page_config(layout="wide")
add_logo("frontend/static/images/smartR-AI-logo-RGB_250x90.png", height=65)
st.title("Chat with SCOTi")

# Set OpenAI API key from Streamlit secrets
client = RunpodClient()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):        
        response_generator = client.queue_async_job(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=Config.STREAM_CHAT
        )
        
        bot_response = st.write_stream(response_generator)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})