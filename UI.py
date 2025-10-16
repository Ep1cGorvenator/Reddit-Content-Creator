import streamlit as st
import time
import UI_tools
from audio import Audio

# To make this runnable, we need to import your main crew function.
try:
    from crew import run_crew
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
        color: rgba(255, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False

if "audio_handler" not in st.session_state:
    st.session_state.audio_handler = Audio()

# --- UI Rendering ---

# Sidebar for TTS settings and audio tester(HANDLES AUDIO)
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.enable_tts = st.checkbox("Enable Text-to-Speech", value=st.session_state.enable_tts)

    #ADD AUDIO TESTER TO SIDEBAR
    UI_tools.sidebar_audio_tester(st, Audio)

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

#HELPER AUDIO FUNCTION
def play_audio(response):
    if st.session_state.enable_tts:
        st.session_state.audio_handler.generate_and_play(
            response,
            st.session_state.selected_voice,
            show_spinner=True
        )

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

                # Get a random intro generator
                intro_cycle = str(UI_tools.get_intro_generator(prompt))

                # Convert CrewOutput to string
                if hasattr(crew_response, 'raw'):
                    response = intro_cycle + str(crew_response.raw)
                elif hasattr(crew_response, 'result'):
                    response = intro_cycle + str(crew_response.result)
                else:
                    response = intro_cycle + str(crew_response)

                # Display the response
                st.markdown(response)
                
                # Generate TTS if enabled using the Audio class(HANDLES AUDIO)
                play_audio(response)
                
            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                import traceback
                st.code(traceback.format_exc())
                response = error_message

    # Append the agent's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response})