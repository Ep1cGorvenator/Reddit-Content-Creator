# ui.py
import streamlit as st
import base64 as bs64
import time
import UI_tools
from UI_CSS import setUp_CSS 
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
setUp_CSS(st)

#--- ADD MONKEY SIDE BAR ---
#add animated Iframe
UI_tools.gorrilla_sideBar_animation(st)


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False

if "audio_handler" not in st.session_state:
    st.session_state.audio_handler = Audio()

# --- CORE PROCESSING & HELPER FUNCTIONS ---

def play_audio(response):
    if st.session_state.enable_tts:
        if "selected_voice" not in st.session_state:
             st.session_state.selected_voice = "Charon" 
             
        st.session_state.audio_handler.generate_and_play(
            response,
            st.session_state.selected_voice,
            show_spinner=True
        )

def process_prompt(prompt: str):
    """Handles the user input, calls the agent, and updates state."""
    
    # Append and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the agent's response
    with st.chat_message("assistant", avatar="🦍"):
        # Create a placeholder for custom loading animation
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            # Show custom loading animation
            UI_tools.show_loading_animation()
        
        try:
            # Call agent logic
            crew_response = run_crew(prompt)

            # Clear the loading animation
            loading_placeholder.empty()

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
            
            # Generate TTS if enabled using the Audio class
            play_audio(response)
            
        except Exception as e:
            loading_placeholder.empty()
            error_message = f"Sorry, an error occurred: {e}"
            st.error(error_message)
            import traceback
            st.code(traceback.format_exc())
            response = error_message

    # Append the agent's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- UI RENDERING ---

# Sidebar for TTS settings and audio tester, including Clear Chat Button
with st.sidebar:
    st.title("🦍 Gorilla Engine")
    st.markdown("### Content Generation Suite")
    st.markdown("---") 
    
    st.caption("Manage Conversation")
    st.button(
        "🗑️ Clear Chat", 
        on_click=lambda: UI_tools.clear_chat_history(st), 
        use_container_width=True
    )
    st.markdown("---")
    
    st.header("⚙️ Settings")
    st.session_state.enable_tts = st.checkbox("Enable Text-to-Speech", value=st.session_state.enable_tts)

    #ADD VOICE SELECTION DROPDOWN
    UI_tools.sidebar_audio_tester(st, Audio)


# --- MAIN CONTENT LOGIC ---

# 1. Handle Quick Start Prompt Injection
if "user_prompt" in st.session_state:
    # A quick start button was clicked, process it and clear the state key
    prompt = st.session_state.user_prompt
    del st.session_state.user_prompt
    process_prompt(prompt)
    st.rerun() # Rerun to properly display the new messages

# 2. Display Welcome/History
if not st.session_state.messages:
    # If no messages, show the guided welcome screen (Branding + Quick Start Prompts)
    
    # Display circular image with pure HTML for fixed sizing
    UI_tools.circular_image(bs64,st)
    
    st.markdown("""
        <div class="welcome-container">
            <h1>🦍 Welcome to Gorilla Studios</h1>
            <p>Your personal content generation assistant. Enter a topic to get started!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Use the UI_tools function to render the prompt buttons
    UI_tools.display_quick_start_prompts(st)

else:
    # If messages exist, display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=("🦍" if message["role"] == "assistant" else None)):
            st.markdown(message["content"])

# 3. User Input Field
if prompt := st.chat_input("ask anything"):
    process_prompt(prompt)