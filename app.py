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


# 🔑 PUT YOUR API KEY HERE
GEMINI_API_KEY = "API KEY"

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="CareBot", layout="centered")
st.title("🩺 CareBot")
st.caption("Your calm, reliable first-aid companion")

# ---------- Initialize Gemini Client ----------
if "client" not in st.session_state:
    api_key = load_api_key()
    try:
        st.session_state.client = genai.Client(api_key=api_key)

        # Try newer model first, fallback if unavailable
        try:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-3-flash-preview"
            )
        except:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.5-flash"
            )

    except Exception as e:
        st.error(f"❌ Failed to initialize CareBot: {e}")
        st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑  Clear Conversation"):
        st.session_state.chat = st.session_state.client.chats.create(
            model="gemini-2.5-flash"
        )
        st.session_state.messages = []
        st.rerun()

# ---------- Chat History ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- User Input ----------
if prompt := st.chat_input("Describe the injury or situation…"):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    try:
        # 🧠 CareBot system instructions
        system_prompt = (
            "You are CareBot, a calm and friendly first-aid assistant.\n"
            "Rules for your response:\n"
            "- Give ONLY first-aid guidelines\n"
            "- Use concise bullet points with simple emojis\n"
            "- Keep the tone comforting and reassuring\n"
            "- Do NOT ask follow-up questions\n"
            "- Do NOT include disclaimers or warnings\n"
            "- Do NOT include diagnosis or graphic details\n"
            "- Do NOT add extra explanations\n"
        )

        response = st.session_state.chat.send_message(
            system_prompt + "\nUser: " + prompt
        )

        # Show assistant reply
        with st.chat_message("assistant"):
            st.markdown(response.text)

        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )

    except Exception as e:
        st.error(f"⚠️ CareBot error: {e}")