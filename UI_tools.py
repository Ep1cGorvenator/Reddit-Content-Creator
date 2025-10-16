# UI_tools.py
import random
import streamlit as st # Need to import st here since we pass it to other functions

# --- PROMPT POOL ---

# A large array of starter prompts for variety (you can expand this to 200)
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
    
    # Technical & How-To
    "Write a simple, step-by-step guide on how to reset a Wi-Fi router.",
    "Draft a 'troubleshooting' section for a software user manual (on login issues).",
    "Generate a code snippet explanation for a basic Python 'for' loop.",
    "Create a list of 5 best practices for cloud security in a small business.",
    "Write a brief summary of the importance of two-factor authentication (2FA).",
    "Develop a comparison table for three different types of video file formats.",
    
    # Social Media Engagement
    "Write a 'Behind the Scenes' post for a startup working late on a project.",
    "Generate 5 ideas for a poll related to weekend activities on X (formerly Twitter).",
    "Compose an energetic caption for a video showcasing a product being unboxed.",
    "Draft a post asking followers for their biggest challenge related to investing.",
    "Create a 'Did You Know?' factoid post about a historical event.",
    "Write a celebratory post for reaching 10,000 followers/subscribers.",
    
    # Sales & Marketing Copy
    "Write three variations of an elevator pitch for a subscription box service.",
    "Draft the opening sentence for a guarantee/return policy page.",
    "Generate a compelling headline for a 'limited-time offer' sale email.",
    "Create a script snippet for a testimonial where the customer solves a pain point.",
    "Develop a set of bullet points detailing the features of a new mobile app.",
    "Write a quick guide on how your product saves the user time or money.",
    "Draft a post segment aimed at overcoming a common customer objection.",

    # Emotional & Story-Focused
    "Write a paragraph designed to evoke a feeling of nostalgia.",
    "Compose a short motivational speech about overcoming creative blocks.",
    "Generate a 'Life Lesson' post based on a common mistake.",
    "Draft a short announcement about a team member's retirement/departure.",
    "Write a short piece on the value of quiet time and reflection.",
    
    # Business Operations & HR
    "Create a draft agenda for a weekly department-head meeting.",
    "Write a professional email requesting a client review/feedback.",
    "Draft a succinct explanation of the company's new remote work policy.",
    "Generate three key performance indicators (KPIs) for a customer support team.",
    "Write a basic job description for an entry-level marketing intern.",
    "Compose a friendly reminder email about an upcoming deadline.",
    
    # Niche & Fun Formats
    "Create a 10-item checklist for launching a successful podcast.",
    "Draft a script for a short, animated explainer video (20 seconds).",
    "Generate a list of 5 popular books and briefly explain why they went viral.",
    "Write a short piece discussing the ethics of using AI in art generation.",
    "Develop a fun, themed 'out-of-office' message for a holiday break.",
    "Create a short recipe post for a simple, healthy weeknight meal.",
    "Write a comparison between two historical figures with opposing views.",
    
    # Education & Summarization
    "Explain the difference between weather and climate in one paragraph.",
    "Summarize the plot of a classic novel (e.g., 'Moby Dick') concisely.",
    "Write a brief tutorial on using a screen-recording tool.",
    "Generate a short list of 5 surprising facts about human psychology.",
    "Draft a curriculum outline for a 4-week introductory photography class.",
    "Write a brief argument supporting the preservation of a national park.",
    
    # Conversational Prompts
    "Ask a fun question about users' favorite childhood movie for an engagement post.",
    "Write an open-ended prompt asking users to share their best career advice.",
    "Compose a 'Fill in the blank' sentence to encourage quick comments.",
    "Draft a post asking for predictions on the next big tech trend.",
    "Generate a post inviting users to vote on a product name or logo design."
]


# --- CHAT UTILITIES ---
def clear_chat_history(st_obj):
    """
    Clears the message history stored in the Streamlit session state.
    Requires the Streamlit object 'st_obj' to access session_state.
    """
    if "messages" in st_obj.session_state:
        st_obj.session_state.messages = []
    
    if "user_prompt" in st_obj.session_state:
        del st_obj.session_state.user_prompt
        
def display_quick_start_prompts(st_obj):
    """
    Renders 3 unique, random quick start prompt buttons on the welcome page.
    Sets 'st_obj.session_state.user_prompt' upon button click to trigger processing.
    """
    st_obj.markdown("---")
    
    # 📌 Key Change: Select 3 unique random prompts from the pool
    try:
        starter_prompts = random.sample(ALL_QUICK_START_PROMPTS, 3)
    except ValueError:
        # Fallback if the array is too small or somehow corrupted
        starter_prompts = ALL_QUICK_START_PROMPTS[:3] 
        
    st_obj.subheader("Quick Start Prompts")
    cols = st_obj.columns(len(starter_prompts))
    
    for i, prompt in enumerate(starter_prompts):
        with cols[i]:
            # Use a lambda function to set the state and trigger rerun
            if st_obj.button(prompt, key=f"starter_prompt_{i}", use_container_width=True):
                # When a button is clicked, set the prompt for ui.py to process
                st_obj.session_state.user_prompt = prompt
                st_obj.rerun() 
    
# --- AUDIO TESTER IN SIDEBAR ---
def sidebar_audio_tester(st_obj, Audio):
    # Voice selection (now mapped to accents)
    voice_options = Audio.get_available_voices()
    if "selected_voice" not in st_obj.session_state:
        st_obj.session_state.selected_voice = "Charon"
    
    voice_index = voice_options.index(st_obj.session_state.selected_voice) if st_obj.session_state.selected_voice in voice_options else 0
    
    st_obj.session_state.selected_voice = st_obj.selectbox(
        "Voice (Accent)", 
        voice_options, 
        index=voice_index,
        help="Different accents: Australian, British, US, Canadian, Indian"
    )
    
    st_obj.info("🎙️ When enabled, responses will be read aloud automatically.")
    
    # Add divider
    st_obj.markdown("---")
    
    # Audio Tester Section
    with st_obj.expander("🎙️ Audio Tester", expanded=False):
        st_obj.write("Test audio without generating content")
        
        test_text = st_obj.text_area(
            "Test text:",
            value="Hello! This is a quick audio test.",
            height=80,
            key="sidebar_test_text"
        )
        
        if st_obj.button("🔊 Test Audio", key="sidebar_test_btn"):
            if test_text.strip():
                st_obj.session_state.audio_handler.generate_and_play(
                    test_text, 
                    st_obj.session_state.selected_voice
                )
            else:
                st_obj.warning("Enter some text to test")

# --- RANDOM INTRO GENERATOR ---
def get_intro_generator(prompt=""):
    intros = [
        f"Here’s the content I’ve crafted for you on **{prompt}**:\n\n",
        f"Alright, let’s bring your idea to life! Here’s my take on **{prompt}**:\n\n",
        f"I’ve put together something special for **{prompt}**. Let’s see what you think:\n\n",
        f"Let’s dive straight into it — here’s your content on **{prompt}** that’s ready to shine:\n\n",
        f"Accessing creative vault... Topic: **{prompt}**\n\nHere’s what I’ve found:\n\n"
    ]
    
    return random.choice(intros)