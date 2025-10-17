# facebook_tools.py
import os
import time
# import requests # Uncomment this if you use the requests library for API calls

# --- Mock Configuration/Credentials ---
APP_ID = "2498932317144961"
REDIRECT_URI = "https://managerially-unproofread-stefani.ngrok-free.dev" 
SCOPES = "email,pages_show_list,pages_read_engagement" 
MOCK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN", "MOCK_TOKEN_READY") # Assume a token exists after OAuth


def get_facebook_login_url():
    """
    Generates the Facebook OAuth login URL.
    """
    if APP_ID == "2498932317144961":
        # In a real app, this should be a proper logging/error handler
        print("Warning: Using mock APP_ID. Login URL will not work with Facebook.")
        
    oauth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope={SCOPES}"
    )
    
    return oauth_url

def publish_post(content: str):
    """
    Publishes the content to Facebook using a stored access token.
    This function must be synchronous and is called from the Streamlit thread.
    """
    token = MOCK_ACCESS_TOKEN
    
    if token == "MOCK_TOKEN_READY":
        # Simulate a successful publishing action for the UI demo
        print(f"MOCK: Publishing content: {content[:50]}...")
        time.sleep(1) 
        return {"post_id": f"mock_published_{int(time.time())}"}
    
    # --- Replace the mock above with your actual API call logic below ---
    # Example:
    # PAGE_ID = "YOUR_PAGE_ID_HERE"
    # URL = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
    # payload = { 'message': content, 'access_token': token }
    # response = requests.post(URL, data=payload)
    # response.raise_for_status()
    # return response.json()