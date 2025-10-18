import random
from UI_IntroPrompts import ALL_QUICK_START_PROMPTS

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
    with open(r"C:\UnityProjects\301Project\Reddit-Content-Creator\GorillaHangingAnimation.json", "r") as f:
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