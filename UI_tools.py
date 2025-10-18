import random
import os
from UI_IntroPrompts import ALL_QUICK_START_PROMPTS

def get_intro_generator(prompt):
    """Generate a random intro phrase for the response that includes the user's prompt"""
    import random
    
    intros = [
        f"**Alright, let's create some content about:** *\"{prompt}\"*\n\n",
        f"**Time to get creative!** You asked for: *\"{prompt}\"*\n\n",
        f"**Gorilla Studios is on it!** Here's your content for: *\"{prompt}\"*\n\n",
        f"**Let me craft something special about:** *\"{prompt}\"*\n\n",
        f"**Perfect! Let's build content around:** *\"{prompt}\"*\n\n",
        f"**Content creation mode activated!** Topic: *\"{prompt}\"*\n\n",
        f"**Here's what I've cooked up for:** *\"{prompt}\"*\n\n",
        f"**Time to make some magic happen!** Your request: *\"{prompt}\"*\n\n",
        f"**Let's crush this content piece about:** *\"{prompt}\"*\n\n",
        f"**Gorilla brain engaged!** Creating content for: *\"{prompt}\"*\n\n",
        f"**Ready to make this viral-worthy?** Topic: *\"{prompt}\"*\n\n",
        f"**Let's turn this into gold:** *\"{prompt}\"*\n\n",
    ]
    
    return random.choice(intros)
# --- CHAT UTILITIES ---
def clear_chat_history(st):
    """
    Clears the message history stored in the Streamlit session state.
    Requires the Streamlit object 'st' to access session_state.
    """
    if "messages" in st.session_state:
        st.session_state.messages = []
    
    if "user_prompt" in st.session_state:
        del st.session_state.user_prompt
        
def display_quick_start_prompts(st):
    st.markdown("---")
    
    # Generate random prompts only once
    if "starter_prompts" not in st.session_state:
        indices = random.sample(range(len(ALL_QUICK_START_PROMPTS)), 3)
        st.session_state.starter_prompts = [ALL_QUICK_START_PROMPTS[i] for i in indices]

    starter_prompts = st.session_state.starter_prompts
    
    st.markdown("<h3 class='quick-start-title'>Quick Start Prompts</h3>", unsafe_allow_html=True)
    cols = st.columns(len(starter_prompts))
    
    for i, prompt in enumerate(starter_prompts):
        with cols[i]:
            if st.button(prompt, key=f"starter_prompt_{i}", use_container_width=True):
                st.session_state.user_prompt = prompt
                st.rerun()

    
# --- AUDIO TESTER IN SIDEBAR ---
def sidebar_audio_tester(st, Audio):
    # Voice selection (now mapped to accents)
    voice_options = Audio.get_available_voices()
    if "selected_voice" not in st.session_state:
        st.session_state.selected_voice = "Charon"
    
    voice_index = voice_options.index(st.session_state.selected_voice) if st.session_state.selected_voice in voice_options else 0
    
    st.session_state.selected_voice = st.selectbox(
        "Voice (Accent)", 
        voice_options, 
        index=voice_index,
        help="Different accents: Australian, British, US, Canadian, Indian"
    )
    
    st.info("🎙️ When enabled, responses will be read aloud automatically.")
    
    # Add divider
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
        
        if st.button("🔊 Test Audio", key="sidebar_test_btn"):
            if test_text.strip():
                st.session_state.audio_handler.generate_and_play(
                    test_text, 
                    st.session_state.selected_voice
                )
            else:
                st.warning("Enter some text to test")
    
def sidebar_video_settings(st):
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

  
# --- SET UP CIRCULAR IMAGE ---
def circular_image(base64, st):
    # Display circular image with pure HTML for fixed sizing
    # Read and encode the image
    with open("bigfoot_vlogs.jpg", "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
    
    st.markdown(f"""
            <div class="logo-container">
                <img src="data:image/jpeg;base64,{img_data}" class="circular-logo">
            </div>
        """, unsafe_allow_html=True)

# --- SETUP GORILLA SLIDER ---
def gorrilla_sideBar_animation(st):
    import streamlit.components.v1 as com
    import json

    # Load your local Lottie JSON file
    with open(r"GorillaHangingAnimation.json", "r") as f:
        lottie_json = json.load(f)

    # Convert JSON to string for embedding in JS
    lottie_str = json.dumps(lottie_json)
    html_code = f"""
    
    <head>
    <!-- Use Lottie Web, not dotlottie-wc -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.10.2/lottie.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: visible;
        }}
        #lottie-container {{
            position: fixed;
            left: -199px;
            top: 65%;
            transform: translateY(-50%) rotate(-90deg);
            width: 480px;
            height: 270px;
            cursor: pointer;
            z-index: 9999;
        }}
    </style>
    </head>
    <body>
    <div id="lottie-container"></div>
    <script>
        var animationData = {lottie_str};
        // Load animation using Lottie Web
        var animation = lottie.loadAnimation({{
        container: document.getElementById('lottie-container'),
        renderer: 'svg',
        loop: true,
        autoplay: false,
        animationData: animationData
        }});
        // Play animation on hover
        const container = document.getElementById('lottie-container');
        container.addEventListener('mouseenter', () => animation.play());
        container.addEventListener('mouseleave', () => animation.stop());
        
        // Toggle sidebar on click
        container.addEventListener('click', () => {{
            try {{
                // Try multiple possible selectors for the sidebar toggle
                const parentDoc = window.parent.document;
                
                // Try different selectors
                let toggle = parentDoc.querySelector('[data-testid="collapsedControl"]') ||
                             parentDoc.querySelector('button[kind="headerNoPadding"]') ||
                             parentDoc.querySelector('section[data-testid="stSidebar"] button');
                
                if (toggle) {{
                    toggle.click();
                    console.log('Sidebar toggle clicked!');
                }} else {{
                    console.log('Sidebar toggle not found');
                }}
            }} catch(e) {{
                console.error('Error accessing parent:', e);
            }}
        }});
    </script>
    </body>
    """
    com.html(html_code, width=500, height=300, scrolling=False)

def show_loading_animation():
    """Display custom loading animation with text using Lottie"""
    import streamlit.components.v1 as com
    import json
    
    with open(r"movingHand.json", "r") as f:
        lottie_json = json.load(f)
    
    lottie_str = json.dumps(lottie_json)
    html_code = f"""
    <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.10.2/lottie.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        #loading-wrapper {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        #loading-text {{
            font-size: 24px;
            font-weight: 600;
            color: #34D399;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            animation: pulse 1.5s ease-in-out infinite;
        }}
        
        #loading-container {{
            width: 150px;
            height: 150px;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.5;
            }}
        }}
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {{
            #loading-text {{
                color: #34D399;
            }}
        }}
    </style>
    </head>
    <body>
    <div id="loading-wrapper">
        <div id="loading-text">Gorilla is thinking...</div>
        <div id="loading-container"></div>
    </div>
    <script>
        var animationData = {lottie_str};
        var animation = lottie.loadAnimation({{
            container: document.getElementById('loading-container'),
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: animationData
        }});
    </script>
    </body>
    """
    
    com.html(html_code, width=400, height=100, scrolling=False)