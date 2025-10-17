import streamlit as st
import time
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
    
    /* Make slider labels more visible */
    .stSlider > label {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

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

# Sidebar for TTS settings, video settings, and audio tester
with st.sidebar:
    st.header("⚙️ Settings")
    
    # TTS Settings
    st.subheader("🎤 Audio Settings")
    st.session_state.enable_tts = st.checkbox(
        "Enable Text-to-Speech", 
        value=st.session_state.enable_tts,
        help="Play generated audio automatically"
    )
    
    # Voice selection (now mapped to accents)
    voice_options = Audio.get_available_voices()
    if "selected_voice" not in st.session_state:
        st.session_state.selected_voice = "Charon"  # Default voice
    
    st.session_state.selected_voice = st.selectbox(
        "Voice (Accent)", 
        voice_options, 
        index=voice_options.index(st.session_state.selected_voice),
        help="Different accents: Australian, British, US, Canadian, Indian"
    )
    
    if st.session_state.enable_tts:
        st.info("🎙️ Responses will be read aloud automatically.")
    
    st.markdown("---")
    
    # Video Settings
    st.subheader("🎬 Video Settings")
    
    # Check if base video exists
    video_exists = os.path.exists("base_video.mp4")
    
    if video_exists:
        # Get video file size
        video_size_mb = os.path.getsize("base_video.mp4") / (1024 * 1024)
        st.success(f"✅ Base video: base_video.mp4 ({video_size_mb:.1f} MB)")
    else:
        st.error("❌ base_video.mp4 not found!")
        st.info("📁 Place your video as 'base_video.mp4' in the same folder as UI.py")
    
    # Check for background music
    bg_music_exists = os.path.exists("bg_music.mp3")
    
    if bg_music_exists:
        # Get music file size
        music_size_mb = os.path.getsize("bg_music.mp3") / (1024 * 1024)
        st.success(f"✅ Background music: bg_music.mp3 ({music_size_mb:.1f} MB)")
        
        # Background music toggle
        if "use_bg_music" not in st.session_state:
            st.session_state.use_bg_music = True
        
        st.session_state.use_bg_music = st.checkbox(
            "Use Background Music",
            value=st.session_state.use_bg_music,
            help="Add background music to generated videos"
        )
        
        # Background music volume control (only show if music is enabled)
        if st.session_state.use_bg_music:
            if "bg_music_volume" not in st.session_state:
                st.session_state.bg_music_volume = 0.10  # Default 10%
            
            # Volume slider with percentage display
            volume_percent = int(st.session_state.bg_music_volume * 100)
            
            st.session_state.bg_music_volume = st.slider(
                f"🎵 Music Volume: {volume_percent}%",
                min_value=0.0,
                max_value=0.60,
                value=st.session_state.bg_music_volume,
                step=0.02,
                help="Adjust background music volume (0% = silent, 60% = loud)",
                label_visibility="visible"
            )
            
            # Volume indicator
            if st.session_state.bg_music_volume == 0:
                st.caption("🔇 Music muted")
            elif st.session_state.bg_music_volume < 0.15:
                st.caption("🔉 Very quiet background")
            elif st.session_state.bg_music_volume < 0.30:
                st.caption("🔉 Subtle background")
            elif st.session_state.bg_music_volume < 0.45:
                st.caption("🔊 Balanced background")
            else:
                st.caption("🔊 Prominent background")
        else:
            st.caption("🔇 Background music disabled")
            if "bg_music_volume" not in st.session_state:
                st.session_state.bg_music_volume = 0.10
    else:
        st.warning("💡 No background music file")
        with st.expander("ℹ️ How to add background music"):
            st.markdown("""
            **Steps to add background music:**
            1. Download any `.mp3` music file
            2. Rename it to exactly: `bg_music.mp3`
            3. Place it in the same folder as `UI.py`
            
            **Music sources:**
            - YouTube Audio Library (free)
            - Pixabay Music (free)
            - Incompetech (royalty-free)
            - Bensound (free with attribution)
            """)
        
        if "bg_music_volume" not in st.session_state:
            st.session_state.bg_music_volume = 0.10
        if "use_bg_music" not in st.session_state:
            st.session_state.use_bg_music = False
    
    st.markdown("---")
    
    # Video generation options
    st.session_state.enable_video = st.checkbox(
        "Enable Video Generation", 
        value=st.session_state.enable_video,
        help="Generate video with audio overlay and subtitles",
        disabled=not video_exists
    )
    
    if st.session_state.enable_video:
        # Subtitle toggle
        if "add_subtitles" not in st.session_state:
            st.session_state.add_subtitles = True
        
        st.session_state.add_subtitles = st.checkbox(
            "Add Subtitles to Video",
            value=st.session_state.add_subtitles,
            help="Automatically generate and overlay subtitles using Whisper AI"
        )
        
        if st.session_state.add_subtitles:
            st.caption("🎯 Using Whisper AI for precise subtitle timing")
        
        st.info("🎬 Random segment extracted from base video")
        
        # Show what will be in the video
        features = []
        features.append("✓ Voice narration")
        if st.session_state.add_subtitles:
            features.append("✓ AI-synced subtitles")
        if bg_music_exists and st.session_state.use_bg_music:
            features.append(f"✓ Background music ({int(st.session_state.bg_music_volume * 100)}%)")
        
        st.caption("Video will include:\n" + "\n".join(features))
    
    st.markdown("---")
    
    # Audio Tester Section
    with st.expander("🎙️ Audio Tester", expanded=False):
        st.write("Test audio without generating content")
        
        test_text = st.text_area(
            "Test text:",
            value="Hello! This is a quick audio test.",
            height=80,
            key="sidebar_test_text"
        )
        
        if st.button("🔊 Test Audio", key="sidebar_test_btn", use_container_width=True):
            if test_text.strip():
                with st.spinner("Generating test audio..."):
                    st.session_state.audio_handler.generate_and_play(
                        test_text, 
                        st.session_state.selected_voice
                    )
            else:
                st.warning("Enter some text to test")

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

# 3. User Input Field
if prompt := st.chat_input("ask anything"):
    # Append and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the agent's response
    with st.chat_message("assistant"):
        with st.spinner("🦍 Gorilla is thinking..."):
            try:
                # Call agent logic
                crew_response = run_crew(prompt)
                
                # Convert CrewOutput to string
                if hasattr(crew_response, 'raw'):
                    response = str(crew_response.raw)
                elif hasattr(crew_response, 'result'):
                    response = str(crew_response.result)
                else:
                    response = str(crew_response)
                
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