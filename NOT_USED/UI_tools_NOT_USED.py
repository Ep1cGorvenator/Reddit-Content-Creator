#import random
#import os
#from UI_IntroPrompts import ALL_QUICK_START_PROMPTS
#
#def get_intro_generator(prompt):
#    """Generate a random intro phrase for the response that includes the user's prompt"""
#    import random
#    
#    intros = [
#        f"**Alright, let's create some content about:** *\"{prompt}\"*\n\n",
#        f"**Time to get creative!** You asked for: *\"{prompt}\"*\n\n",
#        f"**Gorilla Studios is on it!** Here's your content for: *\"{prompt}\"*\n\n",
#        f"**Let me craft something special about:** *\"{prompt}\"*\n\n",
#        f"**Perfect! Let's build content around:** *\"{prompt}\"*\n\n",
#        f"**Content creation mode activated!** Topic: *\"{prompt}\"*\n\n",
#        f"**Here's what I've cooked up for:** *\"{prompt}\"*\n\n",
#        f"**Time to make some magic happen!** Your request: *\"{prompt}\"*\n\n",
#        f"**Let's crush this content piece about:** *\"{prompt}\"*\n\n",
#        f"**Gorilla brain engaged!** Creating content for: *\"{prompt}\"*\n\n",
#        f"**Ready to make this viral-worthy?** Topic: *\"{prompt}\"*\n\n",
#        f"**Let's turn this into gold:** *\"{prompt}\"*\n\n",
#    ]
#    
#    return random.choice(intros)
#
## --- CHAT UTILITIES ---
#def clear_chat_history(st):
#    """
#    Clears the message history stored in the Streamlit session state.
#    Requires the Streamlit object 'st' to access session_state.
#    """
#    if "messages" in st.session_state:
#        st.session_state.messages = []
#    
#    if "user_prompt" in st.session_state:
#        del st.session_state.user_prompt
#        
#def display_quick_start_prompts(st):
#    st.markdown("---")
#    
#    # Generate random prompts only once
#    if "starter_prompts" not in st.session_state:
#        indices = random.sample(range(len(ALL_QUICK_START_PROMPTS)), 3)
#        st.session_state.starter_prompts = [ALL_QUICK_START_PROMPTS[i] for i in indices]
#
#    starter_prompts = st.session_state.starter_prompts
#    
#    st.markdown("<h3 class='quick-start-title'>Quick Start Prompts</h3>", unsafe_allow_html=True)
#    cols = st.columns(len(starter_prompts))
#    
#    for i, prompt in enumerate(starter_prompts):
#        with cols[i]:
#            if st.button(prompt, key=f"starter_prompt_{i}", use_container_width=True):
#                st.session_state.user_prompt = prompt
#                st.rerun()
#
#    
## --- AUDIO TESTER IN SIDEBAR ---
#def sidebar_audio_tester(st, Audio):
#    # Voice selection (now mapped to accents)
#    voice_options = Audio.get_available_voices()
#    if "selected_voice" not in st.session_state:
#        st.session_state.selected_voice = "Charon"
#    
#    voice_index = voice_options.index(st.session_state.selected_voice) if st.session_state.selected_voice in voice_options else 0
#    
#    st.session_state.selected_voice = st.selectbox(
#        "Voice (Accent)", 
#        voice_options, 
#        index=voice_index,
#        help="Different accents: Australian, British, US, Canadian, Indian"
#    )
#    
#    st.info("🎙️ When enabled, responses will be read aloud automatically.")
#    
#    # Add divider
#    st.markdown("---")
#    
#    # Audio Tester Section
#    with st.expander("🎙️ Audio Tester", expanded=False):
#        st.write("Test audio without generating content")
#        
#        test_text = st.text_area(
#            "Test text:",
#            value="Hello! This is a quick audio test.",
#            height=80,
#            key="sidebar_test_text"
#        )
#        
#        if st.button("🔊 Test Audio", key="sidebar_test_btn"):
#            if test_text.strip():
#                st.session_state.audio_handler.generate_and_play(
#                    test_text, 
#                    st.session_state.selected_voice
#                )
#            else:
#                st.warning("Enter some text to test")
#    
#def sidebar_video_settings(st):
#    st.markdown("---")
#    
#    # Video Settings
#    st.subheader("🎬 Video Settings")
#    
#    # Check if base video exists
#    video_exists = os.path.exists("base_video.mp4")
#    
#    if video_exists:
#        # Get video file size
#        video_size_mb = os.path.getsize("base_video.mp4") / (1024 * 1024)
#        st.success(f"✅ Base video: base_video.mp4 ({video_size_mb:.1f} MB)")
#    else:
#        st.error("❌ base_video.mp4 not found!")
#        st.info("📁 Place your video as 'base_video.mp4' in the same folder as UI.py")
#    
#    # Check for background music
#    bg_music_exists = os.path.exists("bg_music.mp3")
#    
#    if bg_music_exists:
#        # Get music file size
#        music_size_mb = os.path.getsize("bg_music.mp3") / (1024 * 1024)
#        st.success(f"✅ Background music: bg_music.mp3 ({music_size_mb:.1f} MB)")
#        
#        # Background music toggle
#        if "use_bg_music" not in st.session_state:
#            st.session_state.use_bg_music = True
#        
#        st.session_state.use_bg_music = st.checkbox(
#            "Use Background Music",
#            value=st.session_state.use_bg_music,
#            help="Add background music to generated videos"
#        )
#        
#        # Background music volume control (only show if music is enabled)
#        if st.session_state.use_bg_music:
#            if "bg_music_volume" not in st.session_state:
#                st.session_state.bg_music_volume = 0.10  # Default 10%
#            
#            # Volume slider with percentage display
#            volume_percent = int(st.session_state.bg_music_volume * 100)
#            
#            st.session_state.bg_music_volume = st.slider(
#                f"🎵 Music Volume: {volume_percent}%",
#                min_value=0.0,
#                max_value=0.60,
#                value=st.session_state.bg_music_volume,
#                step=0.02,
#                help="Adjust background music volume (0% = silent, 60% = loud)",
#                label_visibility="visible"
#            )
#            
#            # Volume indicator
#            if st.session_state.bg_music_volume == 0:
#                st.caption("🔇 Music muted")
#            elif st.session_state.bg_music_volume < 0.15:
#                st.caption("🔉 Very quiet background")
#            elif st.session_state.bg_music_volume < 0.30:
#                st.caption("🔉 Subtle background")
#            elif st.session_state.bg_music_volume < 0.45:
#                st.caption("🔊 Balanced background")
#            else:
#                st.caption("🔊 Prominent background")
#        else:
#            st.caption("🔇 Background music disabled")
#            if "bg_music_volume" not in st.session_state:
#                st.session_state.bg_music_volume = 0.10
#    else:
#        st.warning("💡 No background music file")
#        with st.expander("ℹ️ How to add background music"):
#            st.markdown("""
#            **Steps to add background music:**
#            1. Download any `.mp3` music file
#            2. Rename it to exactly: `bg_music.mp3`
#            3. Place it in the same folder as `UI.py`
#            
#            **Music sources:**
#            - YouTube Audio Library (free)
#            - Pixabay Music (free)
#            - Incompetech (royalty-free)
#            - Bensound (free with attribution)
#            """)
#        
#        if "bg_music_volume" not in st.session_state:
#            st.session_state.bg_music_volume = 0.10
#        if "use_bg_music" not in st.session_state:
#            st.session_state.use_bg_music = False
#    
#    st.markdown("---")
#    
#    # Video generation options
#    st.session_state.enable_video = st.checkbox(
#        "Enable Video Generation", 
#        value=st.session_state.enable_video,
#        help="Generate video with audio overlay and subtitles",
#        disabled=not video_exists
#    )
#    
#    if st.session_state.enable_video:
#        # Subtitle toggle
#        if "add_subtitles" not in st.session_state:
#            st.session_state.add_subtitles = True
#        
#        st.session_state.add_subtitles = st.checkbox(
#            "Add Subtitles to Video",
#            value=st.session_state.add_subtitles,
#            help="Automatically generate and overlay subtitles using Whisper AI"
#        )
#        
#        if st.session_state.add_subtitles:
#            st.caption("🎯 Using Whisper AI for precise subtitle timing")
#        
#        st.info("🎬 Random segment extracted from base video")
#        
#        # Show what will be in the video
#        features = []
#        features.append("✓ Voice narration")
#        if st.session_state.add_subtitles:
#            features.append("✓ AI-synced subtitles")
#        if bg_music_exists and st.session_state.use_bg_music:
#            features.append(f"✓ Background music ({int(st.session_state.bg_music_volume * 100)}%)")
#        
#        st.caption("Video will include:\n" + "\n".join(features))
#
#
## --- FACEBOOK INTEGRATION ---
#def sidebar_facebook_settings(st):
#    """Facebook integration settings in sidebar"""
#    st.markdown("---")
#    st.subheader("📘 Facebook Integration")
#    
#    # Initialize session state for Facebook
#    if "fb_configured" not in st.session_state:
#        st.session_state.fb_configured = False
#    if "fb_pages" not in st.session_state:
#        st.session_state.fb_pages = []
#    
#    with st.expander("⚙️ Facebook Setup", expanded=not st.session_state.fb_configured):
#        st.markdown("""
#        **Quick Setup:**
#        1. Visit [Facebook Developers](https://developers.facebook.com/)
#        2. Create an app with Facebook Login
#        3. Generate a Page Access Token
#        4. Paste it below
#        """)
#        
#        access_token = st.text_input(
#            "Facebook Access Token",
#            type="password",
#            help="Your Facebook Page Access Token",
#            key="fb_access_token_input"
#        )
#        
#        col1, col2 = st.columns(2)
#        
#        with col1:
#            if st.button("🔗 Connect", use_container_width=True):
#                if access_token:
#                    from facebook_integration import FacebookPoster
#                    fb = FacebookPoster(access_token)
#                    
#                    # Validate token
#                    with st.spinner("Validating token..."):
#                        validation = fb.validate_token()
#                        
#                        if "error" in validation:
#                            st.error(f"❌ Invalid token: {validation.get('error', {}).get('message', 'Unknown error')}")
#                        else:
#                            # Get pages
#                            pages_data = fb.get_pages()
#                            
#                            if "data" in pages_data:
#                                st.session_state.fb_configured = True
#                                st.session_state.fb_access_token = access_token
#                                st.session_state.fb_pages = pages_data["data"]
#                                st.success(f"✅ Connected! Found {len(pages_data['data'])} page(s)")
#                                st.rerun()
#                            else:
#                                st.error("❌ No pages found")
#                else:
#                    st.warning("Please enter an access token")
#        
#        with col2:
#            if st.button("🔓 Disconnect", use_container_width=True):
#                st.session_state.fb_configured = False
#                st.session_state.fb_pages = []
#                if "fb_access_token" in st.session_state:
#                    del st.session_state.fb_access_token
#                st.success("Disconnected")
#                st.rerun()
#    
#    # Show connected status
#    if st.session_state.fb_configured:
#        st.success(f"✅ Connected • {len(st.session_state.fb_pages)} page(s)")
#        
#        # Page selector
#        if st.session_state.fb_pages:
#            page_names = [page["name"] for page in st.session_state.fb_pages]
#            
#            if "selected_fb_page_index" not in st.session_state:
#                st.session_state.selected_fb_page_index = 0
#            
#            st.session_state.selected_fb_page_index = st.selectbox(
#                "Select Page",
#                range(len(page_names)),
#                format_func=lambda i: page_names[i],
#                index=st.session_state.selected_fb_page_index,
#                key="fb_page_selector"
#            )
#    else:
#        st.info("ℹ️ Connect Facebook to enable posting")
#
#
#def display_facebook_post_button(st, message_index):
#    """
#    Display Facebook post button for a specific message.
#    
#    Args:
#        st: Streamlit object
#        message_index: Index of the message in session state
#    """
#    if not st.session_state.get("fb_configured", False):
#        return
#    
#    message = st.session_state.messages[message_index]
#    
#    # Only show for assistant messages
#    if message["role"] != "assistant":
#        return
#    
#    # Create columns for post buttons
#    col1, col2 = st.columns([1, 4])
#    
#    with col1:
#        button_key = f"fb_post_{message_index}_{message.get('timestamp', 0)}"
#        
#        if st.button("📘 Post to Facebook", key=button_key, use_container_width=True):
#            post_to_facebook(st, message_index)
#
#
#def post_to_facebook(st, message_index):
#    """
#    Post content to Facebook.
#    
#    Args:
#        st: Streamlit object
#        message_index: Index of the message to post
#    """
#    from facebook_integration import FacebookPoster
#    
#    message = st.session_state.messages[message_index]
#    content = message["content"]
#    video_path = message.get("video_path")
#    
#    # Get selected page
#    if not st.session_state.fb_pages:
#        st.error("No Facebook pages available")
#        return
#    
#    selected_page = st.session_state.fb_pages[st.session_state.selected_fb_page_index]
#    page_id = selected_page["id"]
#    page_token = selected_page["access_token"]
#    page_name = selected_page["name"]
#    
#    # Initialize Facebook poster
#    fb = FacebookPoster(st.session_state.fb_access_token)
#    
#    # Clean content for Facebook (remove markdown formatting)
#    clean_content = clean_text_for_facebook(content)
#    
#    with st.spinner(f"📤 Posting to {page_name}..."):
#        if video_path and os.path.exists(video_path):
#            # Post with video
#            result = fb.post_to_page(
#                page_id=page_id,
#                message=clean_content,
#                page_access_token=page_token,
#                video_path=video_path
#            )
#        else:
#            # Post text only
#            result = fb.post_to_page(
#                page_id=page_id,
#                message=clean_content,
#                page_access_token=page_token
#            )
#        
#        if result.get("success"):
#            st.success(f"✅ Posted to {page_name}!")
#            
#            # Show post ID
#            post_id = result.get("post_id") or result.get("video_id")
#            if post_id:
#                st.caption(f"Post ID: {post_id}")
#        else:
#            error_msg = result.get("error", {})
#            if isinstance(error_msg, dict):
#                error_text = error_msg.get("message", "Unknown error")
#            else:
#                error_text = str(error_msg)
#            
#            st.error(f"❌ Failed to post: {error_text}")
#
#
#def clean_text_for_facebook(text: str) -> str:
#    """
#    Clean markdown formatting for Facebook posts.
#    
#    Args:
#        text: Text with markdown formatting
#        
#    Returns:
#        Cleaned text suitable for Facebook
#    """
#    import re
#    
#    # Remove markdown bold
#    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
#    
#    # Remove markdown italic
#    text = re.sub(r'\*(.*?)\*', r'\1', text)
#    
#    # Remove markdown headers
#    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
#    
#    # Remove markdown links but keep URL
#    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
#    
#    # Clean up multiple newlines
#    text = re.sub(r'\n{3,}', '\n\n', text)
#    
#    return text.strip()
#
#  
## --- SET UP CIRCULAR IMAGE ---
#def circular_image(base64, st):
#    # Display circular image with pure HTML for fixed sizing
#    # Read and encode the image
#    with open("bigfoot_vlogs.jpg", "rb") as img_file:
#        img_data = base64.b64encode(img_file.read()).decode()
#    
#    st.markdown(f"""
#            <div class="logo-container">
#                <img src="data:image/jpeg;base64,{img_data}" class="circular-logo">
#            </div>
#        """, unsafe_allow_html=True)
#
## --- SETUP GORILLA SLIDER ---
#def gorrilla_sideBar_animation(st):
#    import streamlit.components.v1 as com
#    import json
#    # Load your local Lottie JSON file
#    with open(r"GorillaHangingAnimation.json", "r") as f:
#        lottie_json = json.load(f)
#    # Convert JSON to string for embedding in JS
#    lottie_str = json.dumps(lottie_json)
#    html_code = f"""
#    <head>
#    <!-- Use Lottie Web, not dotlottie-wc -->
#    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.10.2/lottie.min.js"></script>
#    <style>
#        body {{
#            margin: 0;
#            padding: 0;
#            overflow: visible;
#        }}
#        #lottie-container {{
#            position: fixed;
#            left: -199px;
#            top: 65%;
#            transform: translateY(-50%) rotate(-90deg);
#            width: 480px;
#            height: 270px;
#            cursor: pointer;
#            z-index: 9999;
#        }}
#    </style>
#    </head>
#    <body>
#    <div id="lottie-container"></div>
#    <script>
#        var animationData = {lottie_str};
#        // Load animation using Lottie Web
#        var animation = lottie.loadAnimation({{
#        container: document.getElementById('lottie-container'),
#        renderer: 'svg',
#        loop: true,
#        autoplay: false,
#        animationData: animationData
#        }});
#        // Play animation on hover
#        const container = document.getElementById('lottie-container');
#        container.addEventListener('mouseenter', () => animation.play());
#        container.addEventListener('mouseleave', () => animation.stop());
#        
#        // Toggle sidebar on click
#        container.addEventListener('click', () => {{
#            try {{
#                // Try multiple possible selectors for the sidebar toggle
#                const parentDoc = window.parent.document;
#                
#                // Try different selectors
#                let toggle = parentDoc.querySelector('[data-testid="collapsedControl"]') ||
#                             parentDoc.querySelector('button[kind="headerNoPadding"]') ||
#                             parentDoc.querySelector('section[data-testid="stSidebar"] button');
#                
#                if (toggle) {{
#                    toggle.click();
#                    console.log('Sidebar toggle clicked!');
#                }} else {{
#                    console.log('Sidebar toggle not found');
#                }}
#            }} catch(e) {{
#                console.error('Error accessing parent:', e);
#            }}
#        }});
#    </script>
#    </body>
#    """
#    com.html(html_code, width=500, height=300, scrolling=False)
#
#def show_loading_animation():
#    """Display custom loading animation with text using Lottie"""
#    import streamlit.components.v1 as com
#    import json
#    
#    with open(r"movingHand.json", "r") as f:
#        lottie_json = json.load(f)
#    
#    lottie_str = json.dumps(lottie_json)
#    html_code = f"""
#    <head>
#    <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.10.2/lottie.min.js"></script>
#    <style>
#        * {{
#            margin: 0;
#            padding: 0;
#            box-sizing: border-box;
#        }}
#        
#        html, body {{
#            width: 100%;
#            height: 100%;
#            overflow: hidden;
#            background: transparent;
#            display: flex;
#            align-items: center;
#            justify-content: center;
#        }}
#        
#        #loading-wrapper {{
#            display: flex;
#            align-items: center;
#            gap: 20px;
#        }}
#        
#        #loading-text {{
#            font-size: 24px;
#            font-weight: 600;
#            color: #34D399;
#            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
#            animation: pulse 1.5s ease-in-out infinite;
#        }}
#        
#        #loading-container {{
#            width: 150px;
#            height: 150px;
#        }}
#        
#        @keyframes pulse {{
#            0%, 100% {{
#                opacity: 1;
#            }}
#            50% {{
#                opacity: 0.5;
#            }}
#        }}
#        
#        /* Dark mode support */
#        @media (prefers-color-scheme: dark) {{
#            #loading-text {{
#                color: #34D399;
#            }}
#        }}
#    </style>
#    </head>
#    <body>
#    <div id="loading-wrapper">
#        <div id="loading-text">Gorilla is thinking...</div>
#        <div id="loading-container"></div>
#    </div>
#    <script>
#        var animationData = {lottie_str};
#        var animation = lottie.loadAnimation({{
#            container: document.getElementById('loading-container'),
#            renderer: 'svg',
#            loop: true,
#            autoplay: true,
#            animationData: animationData
#        }});
#    </script>
#    </body>
#    """
#    
#    com.html(html_code, width=400, height=100, scrolling=False)