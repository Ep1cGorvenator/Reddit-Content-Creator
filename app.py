# app.py
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
        time.sleep(2)
        return (
            f"### This is a placeholder response for the topic: '{topic}'\n\n"
            "The full agent crew is not connected. This is a sample of what the "
            "generated post would look like. It would mimic the style and tone "
            "of the posts it analyzed.\n\n- Bullet points might be used.\n"
            "- **Bold text** could emphasize key ideas."
        )

# --- Page Configuration ---
# Sets the page title, icon, and default layout.
st.set_page_config(
    page_title="Gorilla Studios AI",
    page_icon="🦍",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Custom Styling ---
# Injects custom CSS to style the placeholder text for the chat input,
# making it more subtle as requested.
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
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
# Ensures that the message history is preserved across user interactions.
if "messages" not in st.session_state:
    st.session_state.messages = []

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
st.markdown("---") # Visual separator

# 2. Display Chat History
# Iterates through the stored messages and displays them in the chat interface.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. User Input Field
# Creates the chat input box at the bottom of the screen.
if prompt := st.chat_input("ask anything"):
    # Append and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the agent's response
    with st.chat_message("assistant"):
        with st.spinner("Gorilla is thinking..."):
            try:
                # This is where the agent logic is called.
                # It takes the user's prompt and returns the final generated post.
                response = run_crew(prompt)
                st.markdown(response)
            except Exception as e:
                error_message = f"Sorry, an error occurred: {e}"
                st.error(error_message)
                response = error_message

    # Append the agent's response to the history
    st.session_state.messages.append({"role": "assistant", "content": response})