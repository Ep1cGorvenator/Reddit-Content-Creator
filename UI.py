# ui.py
import streamlit as st
import time
# Note: Streamlit uses standard library for external browser opening
import facebook_tools 
import UI_tools 

# --- MOCK IMPORTS FOR RUNNABILITY ---
# Create mock classes if your actual files aren't available for testing
class MockAudio:
    @staticmethod
    def get_available_voices(): return ["Charon", "Aurora", "Echo"]
    def generate_and_play(self, text, voice, show_spinner=False): 
        st.caption(f"🔊 Mocking audio for: {voice}")

try:
    from audio import Audio
except ImportError:
    Audio = MockAudio # Use mock if not found

try:
    from crew import run_crew
except ImportError:
    def run_crew(topic: str):
        time.sleep(2)
        return (f"### Placeholder response for topic: '{topic}'\n\nContent generated successfully.")
# ------------------------------------


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
    .center-text { text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "enable_tts" not in st.session_state:
    st.session_state.enable_tts = False

if "audio_handler" not in st.session_state:
    st.session_state.audio_handler = Audio()
        
# --- Facebook Authentication State ---
# This must be set to True by your separate Flask/OAuth callback logic 
if "facebook_token_ready" not in st.session_state:
    st.session_state.facebook_token_ready = False 


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
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🦍"):
        with st.spinner("Gorilla is thinking..."):
            try:
                crew_response = run_crew(prompt)
                intro_cycle = str(UI_tools.get_intro_generator(prompt))

                # Handle crew output conversion
                if hasattr(crew_response, 'raw'):
                    response = intro_cycle + str(crew_response.raw)
                elif hasattr(crew_response, 'result'):
                    response = intro_cycle + str(crew_response.result)
                else:
                    response = intro_cycle + str(crew_response)

                st.markdown(response)
                play_audio(response)
                
            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                import traceback
                st.code(traceback.format_exc())
                response = error_message
    
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

    # Note: Using the initialized Audio handler
    UI_tools.sidebar_audio_tester(st, Audio)


    # --- Publish/Connect to Facebook (Visible After First Response) ---
    if st.session_state.messages and any(msg["role"] == "assistant" for msg in st.session_state.messages):
        st.markdown("---")
        st.subheader("📤 Publishing")
        
        # Logic to decide which button to show: Connect or Publish
        if not st.session_state.facebook_token_ready:
            
            # --- STAGE 1: CONNECT BUTTON (Triggers state-driven redirect) ---
            if st.button("🔗 Connect Facebook Account", use_container_width=True):
                with st.spinner("Generating login URL..."):
                    try:
                        # 1. Get the OAuth URL from your facebook_tools.py
                        login_url = facebook_tools.get_facebook_login_url()
                        
                        # 2. Store the URL and force a rerun to display the st.link_button (THE FIX)
                        st.session_state.facebook_login_url = login_url 
                        st.info("A link to the Facebook login page is ready below.")
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Error generating login link: {e}")
                
        else:
            # --- STAGE 2: PUBLISH BUTTON (Token is ready) ---
            st.success("✅ Facebook Connected! Ready to publish.")
            
            # Get the most recent assistant response
            assistant_messages = [msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"]
            post_content = assistant_messages[-1] if assistant_messages else "No content generated yet."

            if st.button("🚀 Publish Generated Post", use_container_width=True):
                with st.spinner("Publishing to Facebook..."):
                    try:
                        # Call the synchronous publish function
                        facebook_tools.publish_post(post_content) 
                        st.success("Post successfully published! 🎉")
                        
                    except Exception as e:
                        st.error(f"Publishing failed. Error: {e}")


# --- MAIN CONTENT LOGIC ---

# 1. Handle Quick Start Prompt Injection
if "user_prompt" in st.session_state:
    prompt = st.session_state.user_prompt
    del st.session_state.user_prompt
    process_prompt(prompt)
    st.rerun() 

# 2. Display Welcome/History
if not st.session_state.messages:
    # --- HANDLE PENDING REDIRECT LINK AFTER STAGE 1 BUTTON PRESS ---
    if "facebook_login_url" in st.session_state:
        # Display the link button immediately and clear state
        st.link_button(
            "Click here to Authorize on Facebook", 
            st.session_state.facebook_login_url, 
            type="primary", 
            help="Opens Facebook login in a new tab."
        )
        del st.session_state.facebook_login_url
    # -------------------------------------------------------------
        
    st.markdown("<div class='center-text'>", unsafe_allow_html=True)
    st.header("🦍 Welcome to Gorilla Studios")
    st.markdown("Your personal content generation assistant. Enter a topic to get started!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    UI_tools.display_quick_start_prompts(st)

else:
    # --- HANDLE PENDING REDIRECT LINK AFTER STAGE 1 BUTTON PRESS ---
    if "facebook_login_url" in st.session_state:
        st.link_button(
            "Click here to Authorize on Facebook", 
            st.session_state.facebook_login_url, 
            type="primary", 
            help="Opens Facebook login in a new tab."
        )
        del st.session_state.facebook_login_url
    # -------------------------------------------------------------
    
    # If messages exist, display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=("🦍" if message["role"] == "assistant" else None)):
            st.markdown(message["content"])

# 3. User Input Field
if prompt := st.chat_input("ask anything"):
    process_prompt(prompt)