## flask_app.py (FINALIZED PROFESSIONAL VERSION)
#from flask import Flask, request, redirect, session, url_for
#import requests
#import os
#import uuid 
#
#app = Flask(__name__)
## Replace with a real, strong secret key
#app.secret_key = os.environ.get("FLASK_SECRET_KEY", 'a_robust_and_secure_secret_key_987654321!') 
#
## --- Config (Ensure these match your actual credentials) ---
#APP_ID = "2498932317144961"
#APP_SECRET = "55ad6b318c52bbcf7b18b8e97b70357a"
## The final URL where Streamlit is running (usually 8501)
#STREAMLIT_URL = "https://managerially-unproofread-stefani.ngrok-free.app" 
#
## NOTE: REPLACE WITH YOUR SECURE NGROK HTTPS URL (e.g., https://<id>.ngrok-free.app)
## If testing locally, keep http://127.0.0.1:5000/
#SECURE_DOMAIN = "https://managerially-unproofread-stefani.ngrok-free.app" 
#REDIRECT_URI = f"{SECURE_DOMAIN}/facebook-callback"
#
## --- Global Token Storage (Maps Session ID to Token Data) ---
## Key: Unique Streamlit Session ID (UUID)
## Value: {'page_id': '...', 'page_token': '...'}
#TOKEN_STORE = {} 
#
## --- Helper Functions ---
#
#def get_page_info(user_access_token):
#    """Retrieves the first Page ID and its Page Access Token."""
#    # This requires 'pages_show_list' and 'pages_read_engagement' scopes
#    pages_url = f"https://graph.facebook.com/me/accounts?access_token={user_access_token}"
#    pages_response = requests.get(pages_url).json()
#    
#    if pages_response.get('data'):
#        # We take the first available page as requested
#        first_page = pages_response['data'][0]
#        return {
#            'page_id': first_page.get('id'),
#            'page_token': first_page.get('access_token')
#        }
#    return None
#
## --- Flask Routes ---
#
#@app.route('/facebook-callback')
#def facebook_callback():
#    code = request.args.get('code')
#    state_id = request.args.get('state') # The unique Streamlit Session ID
#
#    if not code:
#        # User denied access or an error occurred
#        return redirect(f"{STREAMLIT_URL}/?auth_status=failed")
#
#    # 1. Exchange the code for a User Access Token
#    token_url = f"https://graph.facebook.com/v18.0/oauth/access_token?" \
#                f"client_id={APP_ID}&" \
#                f"redirect_uri={REDIRECT_URI}&" \
#                f"client_secret={APP_SECRET}&" \
#                f"code={code}"
#
#    try:
#        response = requests.get(token_url).json()
#        user_access_token = response.get('access_token')
#        
#        if not user_access_token:
#            print(f"Flask Error: Failed to get user token: {response}")
#            return redirect(f"{STREAMLIT_URL}/?auth_status=token_error")
#
#        # 2. Get the first Page ID and Page Token
#        page_info = get_page_info(user_access_token)
#        
#        if page_info and page_info.get('page_token'):
#            # 3. Store the token data using the Streamlit-provided state ID
#            TOKEN_STORE[state_id] = page_info
#            
#            # 4. Redirect the user back to Streamlit with the success signal
#            return redirect(f"{STREAMLIT_URL}/?auth_status=success&session_id={state_id}")
#        else:
#            # Failed to get page info (e.g., app lacks permissions or user has no pages)
#            return redirect(f"{STREAMLIT_URL}/?auth_status=no_page")
#
#    except Exception as e:
#        print(f"Flask Unhandled Error: {e}")
#        return redirect(f"{STREAMLIT_URL}/?auth_status=server_error")
#
#if __name__ == '__main__':
#    print(f"*** Starting Flask OAuth Server on {SECURE_DOMAIN} ***")
#    # In production, this must be running over HTTPS (e.g., via ngrok)
#    app.run(port=5000, debug=True, use_reloader=False)


# flask_app.py (WITH TWO NGROK TUNNELS)
from flask import Flask, request, redirect, session, url_for
import requests
import os
import uuid 

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", 'a_robust_and_secure_secret_key_987654321!') 

# --- Config with TWO separate ngrok URLs ---
APP_ID = "2498932317144961"
APP_SECRET = "55ad6b318c52bbcf7b18b8e97b70357a"

# CHANGE 1: Streamlit now has its OWN public ngrok URL
STREAMLIT_URL = "https://managerially-unproofread-stefani.ngrok-free.dev"  # NEW ngrok tunnel for port 8501

# CHANGE 2: Flask has its OWN ngrok URL  
SECURE_DOMAIN = "https://managerially-unproofread-stefani.ngrok-free.dev"  # ngrok tunnel for port 5000
REDIRECT_URI = f"{SECURE_DOMAIN}/facebook-callback"

# --- Global Token Storage ---
TOKEN_STORE = {} 

# --- Helper Functions (NO CHANGES) ---
def get_page_info(user_access_token):
    """Retrieves the first Page ID and its Page Access Token."""
    pages_url = f"https://graph.facebook.com/me/accounts?access_token={user_access_token}"
    pages_response = requests.get(pages_url).json()
    
    if pages_response.get('data'):
        first_page = pages_response['data'][0]
        return {
            'page_id': first_page.get('id'),
            'page_token': first_page.get('access_token')
        }
    return None

# --- Flask Routes (NO CHANGES) ---
#@app.route('/facebook-callback')
#def facebook_callback():
#    code = request.args.get('code')
#    state_id = request.args.get('state')
#
#    if not code:
#        return redirect(f"{STREAMLIT_URL}/?auth_status=failed")
#
#    token_url = f"https://graph.facebook.com/v18.0/oauth/access_token?" \
#                f"client_id={APP_ID}&" \
#                f"redirect_uri={REDIRECT_URI}&" \
#                f"client_secret={APP_SECRET}&" \
#                f"code={code}"
#
#    try:
#        response = requests.get(token_url).json()
#        user_access_token = response.get('access_token')
#        
#        if not user_access_token:
#            print(f"Flask Error: Failed to get user token: {response}")
#            return redirect(f"{STREAMLIT_URL}/?auth_status=token_error")
#
#        page_info = get_page_info(user_access_token)
#        
#        if page_info and page_info.get('page_token'):
#            TOKEN_STORE[state_id] = page_info
#            
#            # REDIRECTS to the Streamlit ngrok URL (not localhost)
#            return redirect(f"{STREAMLIT_URL}/?auth_status=success&session_id={state_id}")
#        else:
#            return redirect(f"{STREAMLIT_URL}/?auth_status=no_page")
#
#    except Exception as e:
#        print(f"Flask Unhandled Error: {e}")
#        return redirect(f"{STREAMLIT_URL}/?auth_status=server_error")
#
#if __name__ == '__main__':
#    print(f"*** Starting Flask OAuth Server on {SECURE_DOMAIN} ***")
#    app.run(port=5000, debug=True, use_reloader=False)

@app.route('/facebook-callback')
def facebook_callback():
    code = request.args.get('code')
    state_id = request.args.get('state')

    if not code:
        return redirect(f"{STREAMLIT_URL}/?auth_status=failed")

    token_url = f"https://graph.facebook.com/v18.0/oauth/access_token?" \
                f"client_id={APP_ID}&" \
                f"redirect_uri={REDIRECT_URI}&" \
                f"client_secret={APP_SECRET}&" \
                f"code={code}"

    try:
        response = requests.get(token_url).json()
        user_access_token = response.get('access_token')
        
        if not user_access_token:
            print(f"Flask Error: Failed to get user token: {response}")
            return redirect(f"{STREAMLIT_URL}/?auth_status=token_error")

        page_info = get_page_info(user_access_token)
        
        if page_info and page_info.get('page_token'):
            TOKEN_STORE[state_id] = page_info
            
            # DEBUG: Print what we're storing
            print(f"✅ Stored token for session: {state_id}")
            print(f"✅ TOKEN_STORE now contains: {list(TOKEN_STORE.keys())}")
            print(f"✅ Page ID: {page_info['page_id']}")
            
            # Make sure the redirect URL is properly formatted
            redirect_url = f"{STREAMLIT_URL}/?auth_status=success&session_id={state_id}"
            print(f"✅ Redirecting to: {redirect_url}")
            
            return redirect(redirect_url)
        else:
            return redirect(f"{STREAMLIT_URL}/?auth_status=no_page")

    except Exception as e:
        print(f"Flask Unhandled Error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(f"{STREAMLIT_URL}/?auth_status=server_error")
    
if __name__=="__main__":
    app.run(debug=True)