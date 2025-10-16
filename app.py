# app.py
import streamlit as st
import time
import google.generativeai as genai
import os

# --- CONFIGURE GOOGLE API ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Replace with your key or set env var
genai.configure(api_key=GOOGLE_API_KEY)

# --- GOOGLE TTS FUNCTION ---
def generate_speech(text: str, voice="en-US", output_format="mp3") -> bytes:
    """
    Uses Gemini's TTS model to synthesize speech from text.
    Returns audio bytes that can be played in Streamlit.
    """
    model = genai.GenerativeModel("models/tts")
    
    response = model.generate_audio(
        text=text,
        voice=voice,
        audio_format=output_format  # 'mp3' or 'ogg'
    )

    # response.audio is a byte stream (not base64)
    return response.audio  # bytes

# --- Import Your Crew Agent ---
try:
    from main import run_crew
except ImportError:
    def run_crew(topic: str):
        time.sleep(2)
        return (
            f"### This is a placeholder response for the topic: '{topic}'\n\n"
            "The full agent crew is not connected. This is a sample of what the "
            "generated post would look like. It would mimic the style and tone "
            "of the posts it analyzed.\n\n- Bullet points might be used.\n"
            "- **Bold text** could emphasize key ideas."
        )

# --- Streamlit Setup ---
st.set_page_config(
    page_title="Gorilla Studios AI",
    page_icon="🦍",
    layout="centered",
    initial_sidebar_state="auto",
)

st.markdown("""
<style>
    .stChatInput textarea::placeholder {
        color: rgba(0, 0, 0, 0.35);
        opacity: 1;
    }
    [data-theme="dark"] .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Branding ---
st.markdown("<div style='text-align: center;'><h1>🦍 Welcome to Gorilla Studios</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><p>Your personal content generation assistant. Enter a topic to get started!</p></div>", unsafe_allow_html=True)
st.markdown("---")

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input Box ---
if prompt := st.chat_input("ask anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Agent Response ---
    with st.chat_message("assistant"):
        with st.spinner("Gorilla is thinking..."):
            try:
                response = run_crew(prompt)
                st.markdown(response)

                # --- TTS Integration ---
                try:
                    audio_data = generate_speech(response)
                    st.audio(audio_data, format="audio/mp3")
                except Exception as tts_error:
                    st.warning(f"Generated text, but TTS failed: {tts_error}")

            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                response = error_message

    st.session_state.messages.append({"role": "assistant", "content": response})
