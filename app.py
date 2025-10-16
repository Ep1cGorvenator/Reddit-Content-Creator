# app.py
import streamlit as st
import time
import os
import base64
from google import genai

# To make this runnable, we need to import your main crew function.
try:
    from main import run_crew
except ImportError:
    # This is a placeholder function for UI testing if 'main.py' is not available.
    def run_crew(topic: str):
        # Simulate agent thinking time
        time.sleep(2)
        return (
            f"### This is a placeholder response for the topic: '{topic}'\n\n"
            "The full agent crew is not connected. This is a sample of what the "
            "generated post would look like. It would mimic the style and tone "
            "of the posts it analyzed.\n\n- Bullet points might be used.\n"
            "- **Bold text** could emphasize key ideas."
        )

# --- Initialize Gemini Client ---
# Set your API key here or use environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def text_to_speech(text: str) -> bytes:
    """
    Converts text to speech using Gemini 2.5 Pro TTS API.
    Returns audio bytes.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Configure TTS with Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=text,
            config={
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Puck"  # Options: Puck, Charon, Kore, Fenrir, Aoede
                        }
                    }
                }
            }
        )
        
        # Extract audio from response
        audio_data = b""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                if part.inline_data.mime_type.startswith("audio/"):
                    audio_data = part.inline_data.data
                    break
        
        return audio_data
    
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

def autoplay_audio(audio_bytes: bytes):
    """
    Creates an audio player that autoplays the generated speech.
    """
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
    page_title="Gorilla Studios AI",
    page_icon="🦍",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Light Mode Placeholder */
    .stChatInput textarea::placeholder {
        color: rgba(0, 0, 0, 0.35);
        opacity: 1;
    }
    /* Dark Mode Placeholder */
    [data-theme="dark"] .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False

# --- UI Rendering ---

# Sidebar for TTS settings
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.enable_tts = st.checkbox("Enable Text-to-Speech", value=st.session_state.enable_tts)
    st.info("🎙️ When enabled, responses will be read aloud automatically.")

# 1. Branding & Welcome Message
st.markdown(
    "<div style='text-align: center;'><h1>🦍 Welcome to Gorilla Studios</h1></div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='text-align: center;'><p>Your personal content generation assistant. Enter a topic to get started!</p></div>",
    unsafe_allow_html=True
)
st.markdown("---")

# 2. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. User Input Field
if prompt := st.chat_input("ask anything"):
    # Append and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the agent's response
    with st.chat_message("assistant"):
        with st.spinner("Gorilla is thinking..."):
            try:
                # Call agent logic
                crew_response = run_crew(prompt)
                
                # Convert CrewOutput to string
                # CrewOutput has multiple ways to access the content
                if hasattr(crew_response, 'raw'):
                    response = str(crew_response.raw)
                elif hasattr(crew_response, 'result'):
                    response = str(crew_response.result)
                else:
                    response = str(crew_response)
                
                st.markdown(response)
                
                # Generate TTS if enabled
                if st.session_state.enable_tts:
                    with st.spinner("Generating audio..."):
                        # Strip markdown formatting for cleaner speech
                        clean_text = response.replace("#", "").replace("*", "").replace("-", "")
                        audio_bytes = text_to_speech(clean_text)
                        
                        if audio_bytes:
                            autoplay_audio(audio_bytes)
                
            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                response = error_message

    # Append the agent's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response})