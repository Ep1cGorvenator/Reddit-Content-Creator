import random

# --- FULL LIST OF QUICK START PROMPTS ---
ALL_QUICK_START_PROMPTS = [
    # --- Original 50 Prompts (Retained) ---
    "Write an engaging LinkedIn post about the future of AI in coding.",
    "Generate a 5-tweet thread summarizing the new space telescope data.",
    "Create an Instagram caption for a picture of a new coffee blend.",
    "Draft a short blog post intro on the benefits of remote work.",
    "Develop a Facebook ad copy promoting a new fitness app.",
    "Create three catchy headlines for an article about blockchain.",
    "Generate a 1-minute script for a TikTok video on sustainable fashion.",
    "Write an email newsletter segment about upcoming tech conferences.",
    "Compose a professional rejection email for a job candidate.",
    "Create a press release announcing a company's new funding round.",
    "Summarize the key takeaways from the latest quarterly earnings report.",
    "Write a short product description for a smart home gadget.",
    "Develop a motivational quote for a Twitter post.",
    "Outline a webinar presentation on mastering public speaking.",
    "Craft a compelling call-to-action for a landing page.",
    "Generate a quick tutorial on using a popular Excel function.",
    "Write a humorous post about the challenges of working from home.",
    "Design a customer testimonial for a B2B software service.",
    "Create a short video description and tags for a YouTube gaming clip.",
    "Write a speculative post about what cities will look like in 2050.",
    "Generate a list of 10 keywords for a new SEO campaign on hydroponics.",
    "Draft a compelling subject line and opening paragraph for a cold outreach email.",
    "Create a short comparison (pros/cons) of two popular marketing automation tools.",
    "Write a brief script for an instructional voice-over on a software feature.",
    "Develop a 7-day social media content calendar focusing on brand awareness.",
    "Write a public apology statement for a minor product launch delay.",
    "Generate three unique value propositions for a custom furniture company.",
    "Write a 100-word flash fiction story based on the prompt: 'The last library.'",
    "Describe the color blue without using the words 'sky' or 'water'.",
    "Develop a fictional character profile for a graphic novelist.",
    "Compose a poem about the sound of rain on a tin roof.",
    "Generate five alternate titles for a documentary about deep-sea exploration.",
    "Write a short, engaging riddle about the internet.",
    "Draft three bullet points for a performance review self-assessment.",
    "Create a concise mission statement for a non-profit organization focused on education.",
    "Write a brief explanation of quantum computing for a non-technical audience.",
    "Generate three interview questions for a mid-level project manager role.",
    "Write a thank-you note to a colleague who helped you finish a big project.",
    "Create a simple project timeline for a website redesign.",
    "Write a short post highlighting the benefits of a specific LinkedIn skill.",
    "Draft an Instagram Story poll asking followers about their favorite productivity hack.",
    "Generate five highly engaging questions to start a discussion on a Reddit thread.",
    "Create a list of 10 relevant hashtags for a travel blogger's post about Japan.",
    "Write a template for an 'Ask Me Anything' (AMA) session on Twitter.",
    "Develop the perfect title and thumbnail text for a self-help podcast episode.",
    "Explain the concept of 'supply chain' using a simple, real-world analogy.",
    "Write a summary of the Federalist Papers (No. 10) in modern language.",
    "Create a quick guide to composting for beginners.",
    "Generate a fact-based argument for increasing minimum wage.",
    "Outline the four key steps in the scientific method.",

    # --- 50 NEW PROMPTS ADDED HERE ---
    "Write a simple, step-by-step guide on how to reset a Wi-Fi router.",
    "Draft a 'troubleshooting' section for a software user manual (on login issues).",
    "Generate a code snippet explanation for a basic Python 'for' loop.",
    "Create a list of 5 best practices for cloud security in a small business.",
    "Write a brief summary of the importance of two-factor authentication (2FA).",
    "Develop a comparison table for three different types of video file formats.",
    "Write a 'Behind the Scenes' post for a startup working late on a project.",
    "Generate 5 ideas for a poll related to weekend activities on X (formerly Twitter).",
    "Compose an energetic caption for a video showcasing a product being unboxed.",
    "Draft a post asking followers for their biggest challenge related to investing.",
    "Create a 'Did You Know?' factoid post about a historical event.",
    "Write a celebratory post for reaching 10,000 followers/subscribers.",
    "Write three variations of an elevator pitch for a subscription box service.",
    "Draft the opening sentence for a guarantee/return policy page.",
    "Generate a compelling headline for a 'limited-time offer' sale email.",
    "Create a script snippet for a testimonial where the customer solves a pain point.",
    "Develop a set of bullet points detailing the features of a new mobile app.",
    "Write a quick guide on how your product saves the user time or money.",
    "Draft a post segment aimed at overcoming a common customer objection.",
    "Write a paragraph designed to evoke a feeling of nostalgia.",
    "Compose a short motivational speech about overcoming creative blocks.",
    "Generate a 'Life Lesson' post based on a common mistake.",
    "Draft a short announcement about a team member's retirement/departure.",
    "Write a short piece on the value of quiet time and reflection.",
    "Create a draft agenda for a weekly department-head meeting.",
    "Write a professional email requesting a client review/feedback.",
    "Draft a succinct explanation of the company's new remote work policy.",
    "Generate three key performance indicators (KPIs) for a customer support team.",
    "Write a basic job description for an entry-level marketing intern.",
    "Compose a friendly reminder email about an upcoming deadline.",
    "Create a 10-item checklist for launching a successful podcast.",
    "Draft a script for a short, animated explainer video (20 seconds).",
    "Generate a list of 5 popular books and briefly explain why they went viral.",
    "Write a short piece discussing the ethics of using AI in art generation.",
    "Develop a fun, themed 'out-of-office' message for a holiday break.",
    "Create a short recipe post for a simple, healthy weeknight meal.",
    "Write a comparison between two historical figures with opposing views.",
    "Explain the difference between weather and climate in one paragraph.",
    "Summarize the plot of a classic novel (e.g., 'Moby Dick') concisely.",
    "Write a brief tutorial on using a screen-recording tool.",
    "Generate a short list of 5 surprising facts about human psychology.",
    "Draft a curriculum outline for a 4-week introductory photography class.",
    "Write a brief argument supporting the preservation of a national park.",
    "Ask a fun question about users' favorite childhood movie for an engagement post.",
    "Write an open-ended prompt asking users to share their best career advice.",
    "Compose a 'Fill in the blank' sentence to encourage quick comments.",
    "Draft a post asking for predictions on the next big tech trend.",
    "Generate a post inviting users to vote on a product name or logo design."
]

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

#ADD CSS STYLES WITH TROPICAL LEAVES ANIMATION
def setUp_CSS(st):
    st.markdown("""
        <style>
            /* --- Correct Placeholder Styling for Chat Input --- */
            /* Light Mode */
            .stChatInput input::placeholder,
            .stChatInput div[data-baseweb="input"] input::placeholder {
                color: rgba(120, 120, 120, 0.7) !important;
            }

            /* Dark Mode */
            [data-theme="dark"] .stChatInput input::placeholder,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"] input::placeholder {
                color: rgba(200, 200, 200, 0.5) !important;
            }

            /* Optional: Adjust input text color too */
            .stChatInput input {
                color: rgba(0, 0, 0, 0.85) !important;
            }
            [data-theme="dark"] .stChatInput input {
                color: rgba(255, 255, 255, 0.9) !important;
            }

            /* Center Text Class */  
            .center-text { text-align: center; }
                
            /* Circular Image Styling for Welcome Logo */
            .logo-container img {
                border-radius: 50%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 250px !important;
                height: 250px !important;
                object-fit: cover;
                display: block;
                margin: 0 auto;
            }
            
            /* Center entire welcome section vertically and horizontally */
            .welcome-container {
                display: flex;
                flex-direction: column;
                align-items: center;       /* horizontal centering */
                text-align: center;
            }

            /* Style text for better visual hierarchy */
            .welcome-container h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: rgba(255, 255, 255, 1);
            }

            .welcome-container p {
                font-size: 1.2rem;
                color: rgba(255, 255, 255, 0.9);
            }
                
            [data-theme="dark"] .welcome-container p {
                color: rgba(220, 220, 220, 0.8);
            }
                
            .quick-start-title {
                text-align: center;
                margin-top: 2rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }

            /* ========================================= */
            /* TROPICAL LEAVES ANIMATION FOR CHAT INPUT */
            /* ========================================= */
            
            /* Container wrapper for the chat input with leaves */
            .stChatInput {
                position: relative;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            /* Scale up the entire chat input on hover/focus */
            .stChatInput:hover {
                transform: scale(1.02);
            }

            .stChatInput:focus-within {
                transform: scale(1.03);
            }

            /* Create tropical leaf elements using pseudo-elements */
            .stChatInput::before,
            .stChatInput::after {
                content: '🌿';
                position: absolute;
                font-size: 2rem;
                opacity: 0;
                transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                z-index: -1; /* Keep leaves behind to avoid interfering */
            }

            /* Left leaf - positioned safely away from text box */
            .stChatInput::before {
                left: -45px;
                top: 50%;
                transform: translateY(-50%) rotate(-45deg) scale(0.5);
            }

            /* Right leaf - positioned safely away from text box */
            .stChatInput::after {
                right: -45px;
                top: 50%;
                transform: translateY(-50%) rotate(45deg) scale(0.5);
            }

            /* Animate leaves on hover */
            .stChatInput:hover::before {
                opacity: 0.8;
                left: -35px;
                transform: translateY(-50%) rotate(-25deg) scale(1);
            }

            .stChatInput:hover::after {
                opacity: 0.8;
                right: -35px;
                transform: translateY(-50%) rotate(25deg) scale(1);
            }

            /* Animate leaves when input is focused */
            .stChatInput:focus-within::before {
                opacity: 1;
                left: -30px;
                transform: translateY(-50%) rotate(-15deg) scale(1.1);
                animation: leafSway 3s ease-in-out infinite;
            }

            .stChatInput:focus-within::after {
                opacity: 1;
                right: -30px;
                transform: translateY(-50%) rotate(15deg) scale(1.1);
                animation: leafSway 3s ease-in-out infinite reverse;
            }

            /* Gentle swaying animation */
            @keyframes leafSway {
                0%, 100% {
                    transform: translateY(-50%) rotate(-15deg) scale(1.1);
                }
                50% {
                    transform: translateY(-55%) rotate(-10deg) scale(1.15);
                }
            }

            /* Add a subtle glow effect to the input on focus */
            .stChatInput:focus-within input {
                box-shadow: 0 0 0 2px rgba(52, 211, 153, 0.3),
                            0 0 20px rgba(52, 211, 153, 0.1) !important;
                transition: box-shadow 0.3s ease;
            }

            /* Enhance the tropical vibe with additional leaf decorations */
            .stChatInput:focus-within input {
                background: linear-gradient(
                    to right,
                    rgba(52, 211, 153, 0.02),
                    transparent 20%,
                    transparent 80%,
                    rgba(52, 211, 153, 0.02)
                ) !important;
            }

            /* Smooth transition for the input border */
            .stChatInput input {
                transition: all 0.3s ease !important;
            }

            /* Remove red border on hover/focus - target all possible selectors */
            .stChatInput:hover input,
            .stChatInput input:hover,
            .stChatInput input:focus,
            .stChatInput:focus-within input,
            .stChatInput textarea:hover,
            .stChatInput textarea:focus,
            .stChatInput div[data-baseweb="input"]:hover,
            .stChatInput div[data-baseweb="input"]:focus-within {
                border-color: rgba(52, 211, 153, 0.3) !important;
                outline: none !important;
            }

            /* Target the actual input wrapper */
            .stChatInput > div:hover,
            .stChatInput > div:focus-within {
                border-color: rgba(52, 211, 153, 0.3) !important;
            }

                        /* Dark mode border adjustments */
            [data-theme="dark"] .stChatInput:hover input,
            [data-theme="dark"] .stChatInput input:hover,
            [data-theme="dark"] .stChatInput input:focus,
            [data-theme="dark"] .stChatInput:focus-within input,
            [data-theme="dark"] .stChatInput textarea:hover,
            [data-theme="dark"] .stChatInput textarea:focus,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"]:hover,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"]:focus-within,
            [data-theme="dark"] .stChatInput > div:hover,
            [data-theme="dark"] .stChatInput > div:focus-within {
                border-color: rgba(52, 211, 153, 0.4) !important;
                outline: none !important;
            }

            /* ========================================= */
            /* ANIMATED SIDEBAR TOGGLE ARROW */
            /* ========================================= */
            
            /* Target the sidebar collapse/expand button - try multiple selectors */
            button[kind="header"],
            button[data-testid="collapsedControl"],
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"],
            section[data-testid="stSidebar"] > button,
            .css-1544g2n,
            div[data-testid="collapsedControl"] button,
            button[aria-label*="sidebar"] {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                transform-origin: center !important;
            }

            /* Hover effect - slide right and grow */
            button[kind="header"]:hover,
            button[data-testid="collapsedControl"]:hover,
            [data-testid="collapsedControl"]:hover,
            [data-testid="stSidebarCollapsedControl"]:hover,
            section[data-testid="stSidebar"] > button:hover,
            .css-1544g2n:hover,
            div[data-testid="collapsedControl"] button:hover,
            button[aria-label*="sidebar"]:hover {
                transform: translateX(8px) scale(1.15) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            /* Active/click effect - keep it functional */
            button[kind="header"]:active,
            button[data-testid="collapsedControl"]:active,
            [data-testid="collapsedControl"]:active,
            [data-testid="stSidebarCollapsedControl"]:active,
            section[data-testid="stSidebar"] > button:active,
            .css-1544g2n:active,
            div[data-testid="collapsedControl"] button:active,
            button[aria-label*="sidebar"]:active {
                transform: translateX(8px) scale(1.1) !important;
            }
        

            /* Dark mode adjustments for leaves */
            [data-theme="dark"] .stChatInput:focus-within input {
                box-shadow: 0 0 0 2px rgba(52, 211, 153, 0.4),
                            0 0 25px rgba(52, 211, 153, 0.15) !important;
            }

            /* ========================================= */
            /* ANIMATED SIDEBAR TOGGLE ARROW */
            /* ========================================= */
            
            /* Target all possible sidebar toggle button selectors */
            [data-testid="stSidebarNav"] + div button,
            [data-testid="collapsedControl"],
            section[data-testid="stSidebar"] ~ button,
            div[data-testid="stSidebarUserContent"] button:first-child,
            button[kind="header"],
            .stApp > header button,
            button[aria-label="Open sidebar navigation"],
            button[aria-label="Close sidebar navigation"] {
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                transform-origin: center center !important;
            }

            /* Hover effect - slide right and grow */
            [data-testid="stSidebarNav"] + div button:hover,
            [data-testid="collapsedControl"]:hover,
            section[data-testid="stSidebar"] ~ button:hover,
            div[data-testid="stSidebarUserContent"] button:first-child:hover,
            button[kind="header"]:hover,
            .stApp > header button:hover,
            button[aria-label="Open sidebar navigation"]:hover,
            button[aria-label="Close sidebar navigation"]:hover {
                transform: translateX(10px) scale(1.2) !important;
            }

            /* Active/click state */
            [data-testid="stSidebarNav"] + div button:active,
            [data-testid="collapsedControl"]:active,
            section[data-testid="stSidebar"] ~ button:active,
            div[data-testid="stSidebarUserContent"] button:first-child:active,
            button[kind="header"]:active,
            .stApp > header button:active,
            button[aria-label="Open sidebar navigation"]:active,
            button[aria-label="Close sidebar navigation"]:active {
                transform: translateX(10px) scale(1.15) !important;
            }

            /* More aggressive targeting - catch any button in the top left */
            .stApp > div > div > div > button:first-of-type,
            header button:first-of-type {
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                transform-origin: center center !important;
            }

            .stApp > div > div > div > button:first-of-type:hover,
            header button:first-of-type:hover {
                transform: translateX(10px) scale(1.2) !important;
            }

            .stApp > div > div > div > button:first-of-type:active,
            header button:first-of-type:active {
                transform: translateX(10px) scale(1.15) !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
#SET UP CIRCULAR IMAGE
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

# --- RANDOM INTRO GENERATOR ---
def get_intro_generator(prompt=""):
    intros = [
        f"Here's the content I've crafted for you on **{prompt}**:\n\n",
        f"Alright, let's bring your idea to life! Here's my take on **{prompt}**:\n\n",
        f"I've put together something special for **{prompt}**. Let's see what you think:\n\n",
        f"Let's dive straight into it — here's your content on **{prompt}** that's ready to shine:\n\n",
        f"Accessing creative vault... Topic: **{prompt}**\n\nHere's what I've found:\n\n"
    ]
    
    return random.choice(intros)