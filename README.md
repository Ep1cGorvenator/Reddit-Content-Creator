# Reddit-Content-Creator

A multi-agent AI system for automated content generation using web supplementation. Agents gather Reddit posts, analyze and create unique stories, convert them to speech, and potentially publish to social media. Built with Python, CrewAI, Ollama, Hugging Face, Reddit APIs, and Streamlit.

Added the libraries.txt which contains the list of libraries used in the venv.

To install these libraries easily <NB>:

1. setup the venv
2. activate venv
3. run this command "pip install -r libraries.txt"

After venv is setup(run these commands to setup CUDA sound) <NB>:

1. pip install torchaudio==2.9.0+cu126 --index-url https://download.pytorch.org/whl/cu126
2. pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
