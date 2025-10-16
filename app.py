import streamlit as st
import time

# To make this runnable, we need to import your main crew function.
# This assumes your main script is named 'main.py' and has a function
# called 'run_crew(topic: str)' that kicks off the agent process and
# returns the final generated text as a string.
try:
    from main import run_crew
except ImportError:
    # This is a placeholder function for UI testing if 'main.py' is not available.
    def run_crew(topic: str):
        # Simulate agent thinking time
        time.sleep(2.5) # Increased time for better UX demonstration
        return (
            f"**✅ Generation Complete**\n\n"
            f"Here is the content draft for the topic: '{topic}'.\n\n"
            "The content crew analyzed top posts and formulated a strategy "
            "to maximize engagement, focusing on a clear hook and strong "
            "call-to-action."
            "\n\n--- Content Draft ---\n\n"
            "This is where the polished, final social media post generated "
            "by the agent system would appear. It uses proper formatting, "
            "emojis, and bolding to mimic a real post."
        )

# --- CONFIGURATION & SETUP ---

st.set_page_config(
    page_title="Gorilla Studios AI Content Generator",
    page_icon="🦍",
    layout="centered",
    initial_sidebar_state="expanded", # Ensure sidebar is visible by default
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Custom Placeholder Style */
    .stChatInput textarea::placeholder {
        color: rgba(0, 0, 0, 0.4); 
        opacity: 1;
    }
    [data-theme="dark"] .stChatInput textarea::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Hiding Streamlit default UI elements 
       NOTE: #MainMenu and header are NOT hidden to ensure the sidebar toggle works.
    */
    footer {visibility: hidden;} 
    
    /* Center the welcome content better for the chat-centric design */
    .center-text { text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI COMPONENTS ---

def clear_chat():
    """
    Clears the message history. Streamlit automatically reruns the script 
    after this on_click function completes to reflect the state change.
    """
    st.session_state.messages = []
    # *** FIX: st.rerun() removed here to eliminate the "no-op" warning. ***

def display_welcome_page():
    """Displays the initial state with branding and starter prompts."""
    st.markdown("<div class='center-text'>", unsafe_allow_html=True)
    st.header("Gorilla Studios AI")
    st.markdown("Your **Content Engine** is ready.")
    st.caption("Enter a topic below or select a starter prompt to generate a polished social media post.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grid for starter prompts (like ChatGPT's suggestions)
    starter_prompts = [
        "Write an engaging LinkedIn post about the future of AI in coding.",
        "Generate a 5-tweet thread summarizing the new space telescope data.",
        "Create an Instagram caption for a picture of a new coffee blend.",
    ]
    
    st.subheader("Quick Start Prompts")
    cols = st.columns(len(starter_prompts))
    
    for i, prompt in enumerate(starter_prompts):
        with cols[i]:
            if st.button(prompt, key=f"starter_prompt_{i}", use_container_width=True):
                # When a button is clicked, set the prompt and re-run the script
                st.session_state.user_prompt = prompt
                st.rerun()

def chat_history_display():
    """Renders the main chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=("🦍" if message["role"] == "assistant" else None)):
            st.markdown(message["content"])

def chat_input_handler():
    """Handles the user input and processes the prompt."""
    
    # 1. Handle Starter Prompt Injection (if applicable)
    if "user_prompt" in st.session_state:
        prompt = st.session_state.user_prompt
        del st.session_state.user_prompt
        
        # Trigger the main processing with the injected prompt
        process_prompt(prompt)

    # 2. User Input Field
    if prompt := st.chat_input("Ask Gorilla to generate a social media post..."):
        process_prompt(prompt)

def process_prompt(prompt: str):
    """Handles the user input, calls the agent, and updates state."""
    
    # Append and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display the agent's response
    with st.chat_message("assistant", avatar="🦍"):
        # Use st.spinner() for perceived thinking time
        with st.spinner(f"Agent crew processing request on: **{prompt[:50]}...**"):
            try:
                # Call the external agent logic
                response = run_crew(prompt)
                st.markdown(response)
            except Exception as e:
                error_message = f"**🚨 Agent Error:** Could not complete the request. Details: `{e}`"
                st.error(error_message)
                response = error_message

    # Append the agent's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- MAIN EXECUTION FLOW ---

# 1. Sidebar for Branding and Utilities
with st.sidebar:
    st.title("🦍 Gorilla Engine")
    st.markdown("### Content Generation Suite")
    st.markdown("---")
    
    st.caption("Manage Conversation")
    # Action is handled by on_click=clear_chat
    st.button("🗑️ Clear Chat", on_click=clear_chat, use_container_width=True)
        
    st.markdown("---")
    st.info("The Gorilla Studios AI uses a multi-agent crew (Planner, Researcher, Writer) to create high-quality, targeted content.")


# 2. Main Content Area Logic
if not st.session_state.messages:
    # If no messages, show the guided welcome screen (Quick Start Prompts)
    display_welcome_page()
else:
    # If messages exist, show the chat history
    chat_history_display()

# 3. Always render the chat input handler at the bottom of the page
chat_input_handler()
