import os
import google.generativeai as genai
# Import the necessary enums for safety settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

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

        # 3. DEFINE SAFETY SETTINGS
        # This is the new part. We are setting all categories to the
        # lowest possible blocking threshold.
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # 3. GENERATE: Create a prompt and get a response
        # PROMPT ENGINEER PROMPT
        
        print(f"Sending prompt to Gemini: '{prompt}'")
        
        response = model.generate_content(prompt_engineer_prompt(prompt), safety_settings=safety_settings)
        
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

# PROMPT ENGINEER PROMPT FUNCTION
def prompt_engineer_prompt(original_prompt):
    """
    Enhances the original prompt to improve the quality of the response.
    """
    engineered_prompt = (
        f"""You are an AI assistant. A user will provide a prompt describing the type of content they want to look for on Reddit.  
            Your task:  
                - Analyze the user's prompt to determine the theme or type of content they are seeking.  
                - Return only a comma-separated list of relevant subreddit names that match the theme/context.  
                - The output must be strictly in the format:  
                    subreddit_1, subreddit_2, subreddit_3, ...  
                - Do not include any explanations, additional text, or formatting outside of the list.  

                User prompt: '{original_prompt}'"""
    )
    return engineered_prompt

# This makes the script runnable
if __name__ == "__main__":
    input_prompt = input("Enter your prompt for Gemini: ")
    run_gemini_prompt(input_prompt)