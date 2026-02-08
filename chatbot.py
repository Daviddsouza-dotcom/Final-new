import streamlit as st
from google import genai

# 🔑 PUT YOUR API KEY HERE
GEMINI_API_KEY = "AIzaSyAwMTG9UDIi1ngMY4cSMeiirjuvvhVrZKA"

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Gemini Chat", layout="centered")
st.title("🤖 JeevRakshak – Sahaayak")

# ---------- Initialize Gemini Client ----------
if "client" not in st.session_state:
    try:
        st.session_state.client = genai.Client(api_key=GEMINI_API_KEY)

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
        st.error(f"❌ Failed to initialize Gemini: {e}")
        st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    if st.button("🗑 Clear Conversation"):
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
if prompt := st.chat_input("Ask about bites, burns, stings, first aid…"):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    try:
        # System framing for safety + consistency
        system_prompt = (
            "You are JeevRakshak, a first-aid assistant. "
            "Give concise, safe, step-by-step guidance using bullet points and emojis only. "
            "No disclaimers, no graphic content."
        )

        response = st.session_state.chat.send_message(
            system_prompt + "\n\nUser: " + prompt
        )

        # Show assistant reply
        with st.chat_message("assistant"):
            st.markdown(response.text)

        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )

    except Exception as e:
        st.error(f"⚠️ Gemini error: {e}")
