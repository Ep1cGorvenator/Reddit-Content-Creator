import os
import google.generativeai as genai
from dotenv import load_dotenv
import reddit_tools

def run_gemini_prompt(prompt):
    """
    Demonstrates a basic interaction with the Google Gemini API.
    """
    try:
        # 1. CONFIGURE: Load and set up the API key
        setup_gemini()
        
        # 2. INITIALIZE: Select the model
        # gemini-2.5-flash is a fast and versatile model.
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. GENERATE: Create a prompt and get a response
        # PROMPT ENGINEER PROMPT
        
        print(f"Sending prompt to Gemini: '{prompt}'")
        
        response = model.generate_content(prompt)
        
        # The actual text is accessed via the .text attribute
        print("\n--- Gemini's Response ---")
        print(response.text)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check if your API key is valid and has been enabled in your Google Cloud project.")

# 1. CONFIGURE THE API KEY
def setup_gemini():
    """
    Sets up the Gemini API by loading the API key from environment variables.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    
    genai.configure(api_key=api_key)
    print("Gemini API configured successfully.")

# This makes the script runnable
if __name__ == "__main__":
    run_gemini_prompt()