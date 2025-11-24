# 🦍 Gorilla Studios: AI Content Creation Agent

This project is a multi-modal AI content generation assistant built for the COMP301 module. It uses a crew of AI agents (powered by CrewAI and Google's Gemini models) to research, write, and create content based on a user's prompt.

The application features a fully interactive web interface built with Streamlit, supporting not only text generation but also integrated text-to-speech (TTS) and video generation.

## 🛠️ Tech Stack

- **Python 3.10+**
- **Agent Framework:** CrewAI
- **LLM:** Google Gemini
- **Web UI:** Streamlit
- **Tools:** PRAW (Reddit API), Coqui-TTS (Voice Clone), FFMPEG (Video)

---

## 🚀 Setup & Installation

Follow these steps to set up the project locally.

### 1. Create and Activate a Virtual Environment

It is essential to use a virtual environment to manage dependencies.

**On macOS/Linux:**

```bash
# Create the environment
python3 -m venv venv
# Activate the environment
source venv/bin/activate
```

**On Windows:**

```bash
# Create the environment
python -m venv venv
# Activate the environment
.\venv\Scripts\activate
```

### 2. Install Dependencies

With your virtual environment active, install all required libraries from the `libraries.txt` file.

```bash
pip install -r libraries.txt
```

_Note: This project requires API keys to be set in a `.env` file to function correctly. Ensure your `.env` file is in place before running the application._

---

## 🏃 How to Use the Application

### 1. Launch the App

Ensure your virtual environment is active.

```bash
# If your environment is not active, activate it first:
# On Windows: .\venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Run the Streamlit application
streamlit run ./UI.py
```

This will automatically open the application in your default web browser.

### 2. Navigating the Interface

The application is divided into a main chat area and a sidebar for advanced settings.

#### Main Chat Screen

This is the primary interface for interacting with the AI.

- **Welcome Message:** You will be greeted by the "Welcome to Gorilla Studios" homepage.
- **Quick Start Prompts:** You can click one of the three "Quick Start Prompts" (e.g., "Draft a post...") to send a pre-defined message to the agent.
- **Chat Input:** At the very bottom of the screen is the main chat box. Type your topic or request (e.g., "Write a post about the future of AI in healthcare") and press Enter to send. The agent's response will appear in this window.

#### Sidebar: Settings & Tools

The sidebar on the left (click the `>` arrow to open it or the hanging Gorrila) contains controls to customize your content generation.

- **Gorilla Engine:**

  - **Clear Chat:** Click this button to erase the current conversation history from the main screen.
  - **Enable Text-to-Speech:** Check this box to have the agent's text responses read aloud automatically as they are generated.
  - **Voice (Accent):** Select your preferred voice for the TTS from this dropdown menu (e.g., "Coqui - Voice Clone").

- **Audio Tester:**

  - This section lets you sample the selected voice _before_ generating content.
  - **Play Default/Regenerate:** Listen to a pre-defined audio sample.
  - **Custom Text Test:** Type any text into the box and click "Test Custom Text" to hear it spoken in the selected voice.

- **Video Settings:**
  - **Enable Video Generation:** Check this box if you want the agent to generate a video file based on the text content.
  - **Use Background Music:** This toggle becomes active with video generation, allowing you to include pre-loaded background music in the final video.

## NOTE: API keys are private, to utilise this system, place your relevant API keys in the .env file
