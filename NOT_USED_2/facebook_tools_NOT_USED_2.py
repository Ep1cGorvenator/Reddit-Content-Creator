# facebook_tools.py (FINALIZED)
#import os
#import time
#import requests
#import uuid
#
## Try to import the token store and config from the Flask app
#try:
#    from flask_app import TOKEN_STORE, APP_ID, REDIRECT_URI
#    print("Facebook Tools: Connected to Flask TOKEN_STORE.")
#except ImportError:
#    # Fallback mock setup (for testing UI without running Flask)
#    TOKEN_STORE = {}
#    APP_ID = "2498932317144961"
#    REDIRECT_URI = "https://managerially-unproofread-stefani.ngrok-free.dev"
#    print("Facebook Tools: WARNING: Flask server not detected. Using Mock.")
#
#
#def get_facebook_login_url(streamlit_session_id: str):
#    """Generates the Facebook OAuth login URL, including the state (session ID)."""
#    
#    # Required scopes for listing and posting to a Page
#    SCOPES = "email,pages_show_list,pages_read_engagement,pages_manage_posts" 
#        
#    oauth_url = (
#        f"https://www.facebook.com/v18.0/dialog/oauth?"
#        f"client_id={APP_ID}&"
#        f"redirect_uri={REDIRECT_URI}&"
#        f"scope={SCOPES}&"
#        f"state={streamlit_session_id}" # Used to match the token back to the Streamlit session
#    )
#    
#    return oauth_url
#
#def get_session_info(streamlit_session_id: str):
#    """Retrieves the stored Page ID and Token for a specific session."""
#    # This is how Streamlit talks to the Flask server's token store
#    return TOKEN_STORE.get(streamlit_session_id)
#
## facebook_tools.py (TEMPORARY DEBUGGING ADDITIONS)
#
#def publish_post(content: str, streamlit_session_id: str):
#    
#    session_info = get_session_info(streamlit_session_id)
#    
#    # ... (Error checking for session_info remains) ...
#
#    token = session_info['page_token']
#    page_id = session_info['page_id'] 
#
#    # 🚨🚨 ADD THESE DEBUG PRINTS 🚨🚨
#    print("-" * 50)
#    print(f"DEBUG: Publishing to Page ID: {page_id}")
#    print(f"DEBUG: Using Page Token (first 10 chars): {token[:10]}...")
#    print(f"DEBUG: Content: {content[:50]}...")
#    print("-" * 50)
#    # 🚨🚨 END DEBUG PRINTS 🚨🚨
#    
#    # --- REAL API CALL to the Page Feed ---
#    URL = f"https://graph.facebook.com/v18.0/{page_id}/feed"
#    # ... (Rest of the function remains the same)
#    payload = {
#        'message': content,
#        'access_token': token
#    }
#    
#    response = requests.post(URL, data=payload)
#    result = response.json()
#    
#    if 'error' in result:
#        raise Exception(f"Facebook API Error: {result['error']['message']}")
#    
#    return result


## facebook_tools.py
#import requests
#
#try:
#    from flask_app import TOKEN_STORE, APP_ID, REDIRECT_URI
#    print("Facebook Tools: Connected to Flask TOKEN_STORE.")
#except ImportError:
#    TOKEN_STORE = {}
#    APP_ID = "2498932317144961"
#    REDIRECT_URI = "https://managerially-unproofread-stefani.ngrok-free.dev/facebook-callback"
#    print("Facebook Tools: WARNING: Flask server not detected. Using Mock.")
#
#
#def get_facebook_login_url(streamlit_session_id: str):
#    """Generates the Facebook OAuth login URL, including the state (session ID)."""
#    
#    # FIXED: Added pages_manage_posts
#    SCOPES = "email,pages_show_list,pages_read_engagement,pages_manage_posts" 
#        
#    oauth_url = (
#        f"https://www.facebook.com/v18.0/dialog/oauth?"
#        f"client_id={APP_ID}&"
#        f"redirect_uri={REDIRECT_URI}&"
#        f"scope={SCOPES}&"
#        f"state={streamlit_session_id}"
#    )
#    
#    return oauth_url
#
#
#def get_session_info(streamlit_session_id: str):
#    """Retrieves the stored Page ID and Token for a specific session."""
#    return TOKEN_STORE.get(streamlit_session_id)
#
#
#def publish_post(content: str, streamlit_session_id: str):
#    """Publishes content to the user's Facebook Page."""
#    
#    session_info = get_session_info(streamlit_session_id)
#    
#    if not session_info:
#        raise Exception("No Facebook session found. Please connect your account first.")
#    
#    token = session_info['page_token']
#    page_id = session_info['page_id']
#    
#    print("-" * 50)
#    print(f"DEBUG: Publishing to Page ID: {page_id}")
#    print(f"DEBUG: Using Page Token (first 10 chars): {token[:10]}...")
#    print(f"DEBUG: Content: {content[:50]}...")
#    print("-" * 50)
#    
#    # Actual API call
#    URL = f"https://graph.facebook.com/v18.0/{page_id}/feed"
#    payload = {
#        'message': content,
#        'access_token': token
#    }
#    
#    response = requests.post(URL, data=payload)
#    result = response.json()
#    
#    print(f"DEBUG: Facebook API Response: {result}")
#    
#    if 'error' in result:
#        raise Exception(f"Facebook API Error: {result['error']['message']}")
#    
#    return result