import streamlit as st
from google import genai
import os

# Function to safely load the API key
def load_api_key():
    try:
        with open("apikey.txt", "r") as f:
            content = f.read().strip()
            # This looks for the content between the double quotes
            # e.g., key="AIza..." -> AIza...
            if '="' in content:
                api_key = content.split('="')[1].replace('"', '')
                return api_key
            return content # Fallback if format is just the key
    except FileNotFoundError:
        st.error("Error: 'apikey.txt' not found.")
        return None
    except Exception as e:
        st.error(f"Error parsing apikey.txt: {e}")
        return None

st.set_page_config(page_title="Gemini Chat", layout="centered")
st.title("🤖 My Gemini Assistant")

# Sidebar with a Reset Button
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Conversation History"):
        # Reset the chat session in Gemini
        st.session_state.chat = st.session_state.client.chats.create(model="gemini-3-flash")
        # Clear the UI messages
        st.session_state.messages = []
        st.rerun()

# Initialize the Gemini Client
#if "client" not in st.session_state:
#    api_key = load_api_key()
#    if api_key:
#        st.session_state.client = genai.Client(api_key=api_key)
#        st.session_state.chat = st.session_state.client.chats.create(model="gemini-3-flash")
#    else:
#        st.stop() # Stops the app if the key is missing

# Initialize the Gemini Client
if "client" not in st.session_state:
    api_key = load_api_key()
    if api_key:
        st.session_state.client = genai.Client(api_key=api_key)
        # Try 'gemini-3-flash-preview' instead of 'gemini-3-flash'
        try:
            st.session_state.chat = st.session_state.client.chats.create(model="gemini-3-flash-preview")
        except:
            # Fallback to the extremely stable 2.5 version if 3 is restricted on your key
            st.session_state.chat = st.session_state.client.chats.create(model="gemini-2.5-flash")
    else:
        st.stop()


# Initialize Chat History for the UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is on your mind?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response from Gemini
    try:
        response = st.session_state.chat.send_message(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save to history
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"An error occurred: {e}")
