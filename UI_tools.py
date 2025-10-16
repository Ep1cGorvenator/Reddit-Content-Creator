# UI_tools.py
import random

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
    """
    Renders the quick start prompt buttons on the welcome page.
    Sets 'st.session_state.user_prompt' upon button click to trigger processing.
    """
    st.markdown("---")
    
    # Grid for starter prompts (copied from your original design)
    starter_prompts = [
        "Write an engaging LinkedIn post about the future of AI in coding.",
        "Generate a 5-tweet thread summarizing the new space telescope data.",
        "Create an Instagram caption for a picture of a new coffee blend.",
    ]
    
    st.subheader("Quick Start Prompts")
    cols = st.columns(len(starter_prompts))
    
    for i, prompt in enumerate(starter_prompts):
        with cols[i]:
            # Use a lambda function to set the state and trigger rerun
            if st.button(prompt, key=f"starter_prompt_{i}", use_container_width=True):
                # When a button is clicked, set the prompt for ui.py to process
                st.session_state.user_prompt = prompt
                st.rerun() # Immediately rerun the script to jump to processing
    
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