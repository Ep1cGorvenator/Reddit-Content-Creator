# ui.py (FINALIZED)
import streamlit as st
import time
import facebook_tools 
import UI_tools 
from urllib.parse import urlparse, parse_qs
import uuid

# --- MOCK IMPORTS FOR RUNNABILITY ---
# (Keep your mock imports here)
class MockAudio:
    @staticmethod
    def get_available_voices(): return ["Charon", "Aurora", "Echo"]
    def generate_and_play(self, text, voice, show_spinner=False): st.caption(f"🔊 Mocking audio for: {voice}")

try:
    from audio import Audio
except ImportError:
    Audio = MockAudio 

try:
    from crew import run_crew
except ImportError:
    def run_crew(topic: str):
        time.sleep(2)
        return (f"### Placeholder Content for: '{topic}'\n\nGenerated content will go here.")
# ------------------------------------


# --- Page Configuration ---
st.set_page_config(
    page_title="Gorilla Studios AI",
    page_icon="🦍",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Styling and State Initialization ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Styling placeholder

if "messages" not in st.session_state: st.session_state.messages = []
if "enable_tts" not in st.session_state: st.session_state.enable_tts = False
if "audio_handler" not in st.session_state: st.session_state.audio_handler = Audio()

# --- Facebook Authentication State ---
if "facebook_token_ready" not in st.session_state: st.session_state.facebook_token_ready = False 
if "unique_session_id" not in st.session_state:
    st.session_state.unique_session_id = str(uuid.uuid4())
if "facebook_page_id" not in st.session_state:
    st.session_state.facebook_page_id = None
        
# --- CORE PROCESSING & HELPER FUNCTIONS ---
def play_audio(response):
    if st.session_state.enable_tts:
        # ... (audio playback logic) ...
        pass

def process_prompt(prompt: str):
    """Handles user input, calls the agent, and updates state."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🦍"):
        with st.spinner("Gorilla is thinking..."):
            try:
                crew_response = run_crew(prompt)
                intro_cycle = str(UI_tools.get_intro_generator(prompt))

                response = intro_cycle + (str(getattr(crew_response, 'raw', None) or getattr(crew_response, 'result', None) or crew_response))

                st.markdown(response)
                play_audio(response)
                
            except Exception as e:
                response = f"Sorry, an error occurred: {e}"
                st.error(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})


# --- URL Parameter Handler (Runs at the top of the app) ---
def handle_oauth_redirect():
    """Checks the URL for the auth_status parameter after Flask redirects."""
    
    query_params = st.query_params
    auth_status = query_params.get("auth_status")
    session_id = query_params.get("session_id")
    
    print(query_params)
    print(auth_status)
    print(session_id)
    print()
    # Check if we have an authentication signal
    if auth_status:
        # Clear the parameters from the URL bar
        
        st.query_params.clear() 
        
        if auth_status == "success" and session_id:
            # Token found and stored in Flask, retrieve info for UI display
            
            session_info = facebook_tools.get_session_info(session_id)
            if session_info:
                
                st.session_state.facebook_token_ready = True
                st.session_state.facebook_page_id = session_info['page_id']
                # The success message is now dynamically displayed in the sidebar
            else:
                st.error("Authentication success signaled, but token not found. Server error.")
        
        elif auth_status == "no_page":
            st.error("Connection successful, but your account manages no eligible Facebook Pages (or required permissions were not granted).")
        
        elif auth_status in ["failed", "token_error", "server_error"]:
            st.error(f"❌ Facebook authorization failed with status: {auth_status}")
        
        # Force a rerun to clean the URL and display the updated state
        st.rerun()

handle_oauth_redirect()
# -------------------------------------------------------------


# --- UI RENDERING (Sidebar) ---

with st.sidebar:
    st.title("🦍 Gorilla Engine")
    st.markdown("### Content Generation Suite")
    st.markdown("---") 
    
    st.caption("Manage Conversation")
    st.button("🗑️ Clear Chat", on_click=lambda: UI_tools.clear_chat_history(st), use_container_width=True)
    st.markdown("---")
    st.header("⚙️ Settings")
    st.session_state.enable_tts = st.checkbox("Enable Text-to-Speech", value=st.session_state.enable_tts)
    UI_tools.sidebar_audio_tester(st, Audio)


    # --- Publish/Connect to Facebook ---
    if st.session_state.messages and any(msg["role"] == "assistant" for msg in st.session_state.messages):
        st.markdown("---")
        st.subheader("📤 Publishing")
        
        if not st.session_state.facebook_token_ready:
            
            # --- STAGE 1: CONNECT BUTTON ---
            if st.button("🔗 Connect Facebook Account", use_container_width=True):
                with st.spinner("Generating login URL..."):
                    try:
                        # Pass the unique session ID to the login URL
                        login_url = facebook_tools.get_facebook_login_url(st.session_state.unique_session_id)
                        
                        st.session_state.facebook_login_url = login_url 
                        st.info("A link to the Facebook login page is ready below.")
                        
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Error generating login link: {e}")
                
        else:
            # --- STAGE 2: PUBLISH BUTTON (Token is ready) ---
            page_id_display = st.session_state.facebook_page_id if st.session_state.facebook_page_id else "..."
            st.success(f"✅ Facebook Connected! Publishing to Page ID: **{page_id_display}**")
            
            assistant_messages = [msg["content"] for msg in st.session_state.messages if msg["role"] == "assistant"]
            #post_content = assistant_messages[-1] if assistant_messages else "No content generated yet."
            post_content = "Hello there" 
            if st.button("🚀 Publish Generated Post", use_container_width=True):
                with st.spinner(f"Publishing to Page {page_id_display}...") as s:
                    try:
                        # Pass the unique session ID to the publish function
                        facebook_tools.publish_post(post_content, st.session_state.unique_session_id) 
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

# 2. Handle the Redirect Link Display
if "facebook_login_url" in st.session_state:
    st.markdown("---")
    st.link_button(
        "Click here to Authorize on Facebook", 
        st.session_state.facebook_login_url, 
        type="primary", 
        help="Opens Facebook login in a new tab."
    )
    del st.session_state.facebook_login_url
#    handle_oauth_redirect()

# 3. Display Welcome/History
if not st.session_state.messages:
    st.markdown("<div class='center-text'>", unsafe_allow_html=True)
    st.header("🦍 Welcome to Gorilla Studios")
    st.markdown("Your personal content generation assistant. Enter a topic to get started!")
    st.markdown("</div>", unsafe_allow_html=True)
    UI_tools.display_quick_start_prompts(st)

else:
    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=("🦍" if message["role"] == "assistant" else None)):
            st.markdown(message["content"])

# 4. User Input Field
if prompt := st.chat_input("ask anything"):
    process_prompt(prompt)