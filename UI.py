# ui.py
import streamlit as st
import base64 as bs64
import time
import UI_tools
from UI_CSS import setUp_CSS 
from audio import Audio
from video_gen import VideoGenerator
import tempfile
import os

# To make this runnable, we need to import your main crew function.
try:
    from crew import run_crew
except ImportError:
    # This is a placeholder function for UI testing if 'crew.py' is not available.
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
    layout="wide",
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

if "enable_video" not in st.session_state:
    st.session_state.enable_video = False

if "audio_handler" not in st.session_state:
    st.session_state.audio_handler = Audio()

if "video_handler" not in st.session_state:
    st.session_state.video_handler = VideoGenerator(base_video_path="base_video.mp4")

# --- UI Rendering ---
   
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
        
        # Show video if it exists in the message
        if "video_path" in message and message["video_path"]:
            if os.path.exists(message["video_path"]):
                st.video(message["video_path"])
                
                # Download button
                with open(message["video_path"], 'rb') as f:
                    video_bytes = f.read()
                st.download_button(
                    label="⬇️ Download Video",
                    data=video_bytes,
                    file_name=f"gorilla_video_{int(time.time())}.mp4",
                    mime="video/mp4",
                    key=f"download_{message.get('timestamp', time.time())}"
                )
                
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

            # Display the response
            st.markdown(response)
            
            # Generate audio bytes (always generate if TTS or Video is enabled)
            audio_bytes = None
            if st.session_state.enable_tts or st.session_state.enable_video:
                with st.spinner("🎵 Generating audio..."):
                    clean_text = st.session_state.audio_handler.clean_text_for_speech(response)
                    audio_bytes = st.session_state.audio_handler.text_to_speech(
                        clean_text, 
                        st.session_state.selected_voice
                    )
            
            # Play audio if TTS is enabled
            if st.session_state.enable_tts and audio_bytes:
                st.session_state.audio_handler.autoplay_audio(audio_bytes)
            
            # Generate video if enabled
            video_path = None
            if st.session_state.enable_video and audio_bytes:
                if not os.path.exists("base_video.mp4"):
                    st.error("❌ Cannot generate video: base_video.mp4 not found!")
                    st.info("Place your video as 'base_video.mp4' in the same folder as UI.py")
                elif st.session_state.video_handler is None:
                    st.error("❌ Video handler not initialized!")
                else:
                    # Determine background music volume (0 if disabled)
                    bg_vol = st.session_state.bg_music_volume if (
                        st.session_state.use_bg_music and 
                        os.path.exists("bg_music.mp3")
                    ) else 0.0
                    
                    # Build status message
                    status_msg = "🎬 Generating video"
                    if st.session_state.add_subtitles:
                        status_msg += " with AI subtitles"
                    if bg_vol > 0:
                        status_msg += f" and background music ({int(bg_vol * 100)}%)"
                    status_msg += "..."
                    
                    with st.spinner(status_msg):
                        try:
                            output_path = os.path.join(
                                tempfile.gettempdir(),
                                f"gorilla_video_{int(time.time())}.mp4"
                            )
                            
                            clean_text = st.session_state.audio_handler.clean_text_for_speech(response)
                            
                            video_path = st.session_state.video_handler.generate_video_from_audio(
                                audio_bytes=audio_bytes,
                                text=clean_text,
                                output_path=output_path,
                                add_subtitles=st.session_state.add_subtitles,
                                bg_music_volume=bg_vol
                            )
                            
                            # Success message with details
                            success_parts = ["✅ Video generated successfully!"]
                            if st.session_state.add_subtitles:
                                success_parts.append("🎯 Subtitles synced with Whisper AI")
                            if bg_vol > 0:
                                success_parts.append(f"🎵 Background music at {int(bg_vol * 100)}%")
                            
                            st.success(" | ".join(success_parts))
                            
                            # Display the video
                            st.video(video_path)
                            
                            # Download button
                            with open(video_path, 'rb') as f:
                                video_bytes = f.read()
                            
                            st.download_button(
                                label="⬇️ Download Video",
                                data=video_bytes,
                                file_name=f"gorilla_video_{int(time.time())}.mp4",
                                mime="video/mp4",
                                key=f"download_current_{int(time.time())}"
                            )
                            
                        except Exception as e:
                            st.error(f"❌ Video generation error: {str(e)}")
                            import traceback
                            with st.expander("Video Error Details"):
                                st.code(traceback.format_exc())
            # Generate TTS if enabled using the Audio class
            play_audio(response)
            
        except Exception as e:
            error_message = f"Sorry, an error occurred: {e}"
            st.error(error_message)
            import traceback
            st.code(traceback.format_exc())
            response = error_message
            video_path = None

    # Append the agent's response to the history with video path
    message_data = {
        "role": "assistant", 
        "content": response,
        "timestamp": time.time()
    }
    if video_path:
        message_data["video_path"] = video_path
    
    st.session_state.messages.append(message_data)
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
    UI_tools.sidebar_video_settings(st)


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
