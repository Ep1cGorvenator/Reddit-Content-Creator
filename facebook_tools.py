import os
from facebook import GraphAPI
from dotenv import load_dotenv
from api import facebook_access_token
import json
import requests
from flask import Flask, redirect, url_for, session, request, render_template

load_dotenv()

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FB_GRAPH_API_URL = "https://graph.facebook.com/v19.0"

SCOPES = "public_profile"

REDIRECT_URL= "https://managerially-unproofread-stefani.ngrok-free.dev/facebook-callback"

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_redirect_uri():
    # In a real app, this should be a fixed, public URL
    # For local testing, ensure this matches your Meta App settings!
    return url_for('facebook_callback', _external=True)

# -----------------------------------------------------
# 1. Initiation Route: Handles the "Sign In" button click
# -----------------------------------------------------
@app.route('/login')
def login():
    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
        return "ERROR: FACEBOOK_APP_ID or FACEBOOK_APP_SECRET not set.", 500

    # Step 1: Construct the URL to redirect the user to Facebook
    auth_url = 'https://www.facebook.com/v19.0/dialog/oauth'
    params = {
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': REDIRECT_URL,
        'scope': SCOPES
    }
    # Facebook is the Identity Provider (IdP), we redirect to its authorization endpoint
    return redirect(f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")

# -----------------------------------------------------
# 2. Callback Route: Handles the response from Facebook
# -----------------------------------------------------
@app.route('/facebook-callback')
def facebook_callback():
    # Check for an error from Facebook (e.g., user denied permission)
    if 'error' in request.args:
        error = request.args.get('error_description', 'Unknown error.')
        return f"Login failed: {error}"

    # Step 2: Receive the Authorization Code from the URL
    code = request.args.get('code')
    if not code:
        return "Missing authorization code."

    # Step 3: Exchange the Code for an Access Token (Server-to-Server)
    token_url = f"{FB_GRAPH_API_URL}/oauth/access_token"
    token_params = {
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': REDIRECT_URL,
        'client_secret': FACEBOOK_APP_SECRET,
        'code': code
    }

    try:
        token_response = requests.get(token_url, params=token_params).json()
        access_token = token_response.get('access_token')
        
        if not access_token:
            return "Failed to get access token: " + str(token_response)

        # Step 4: Use the Access Token to Fetch User Profile Data
        profile_url = f"{FB_GRAPH_API_URL}/me"
        # We request the fields corresponding to our SCOPES
        profile_params = {
            'fields': 'id,name,email,picture',
            'access_token': access_token
        }
        
        profile_response = requests.get(profile_url, params=profile_params).json()
        
        # Step 5: Process and Complete Authentication
        user_id = profile_response.get('id')
        user_name = profile_response.get('name')
        user_email = profile_response.get('email')
        user_picture = profile_response.get('picture', {}).get('data', {}).get('url')

        # In a real application:
        # 1. Look up 'user_id' in your database.
        # 2. If found, log the user in (e.g., set their session).
        # 3. If NOT found, create a new user record using name and email, and THEN log them in.

        # For this example, we'll store data in the Flask session for display
        session['user_id'] = user_id
        session['user_name'] = user_name
        session['user_email'] = user_email
        session['user_picture'] = user_picture
        
        return redirect(url_for('profile'))

    except requests.exceptions.RequestException as e:
        return f"An error occurred during API communication: {e}"

# -----------------------------------------------------
# 3. Application Routes (Home, Profile, Logout)
# -----------------------------------------------------
@app.route('/')
def index():
    # Simple home page with the login link
    if 'user_id' in session:
        return f'Welcome back, {session["user_name"]}! <a href="{url_for("profile")}">View Profile</a> | <a href="{url_for("logout")}">Logout</a>'
    return '<p>Please sign in to continue.</p><a href="/login"><button>Sign in with Facebook</button></a>'

@app.route('/profile')
def profile():
    # Display the user data retrieved from Facebook
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('profile.html', user=session)

@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_picture', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # You MUST set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in your environment!
    # For local development, Flask typically runs on port 5000.
    # The Redirect URI in your Meta App settings should be something like:
    # http://127.0.0.1:5000/facebook-callback or http://localhost:5000/facebook-callback
    app.run(debug=True)

# def get_redirect_url():
#     return url_for('', _external=True)
# 
# # Initialize the Facebook Graph API with the access token from environment variables
# api = GraphAPI(access_token=facebook_access_token)
# 
# 
# profile = api.get_object('/me/accounts', fields='name,location,access_token')
# 
# print(json.dumps(profile, indent=4))
# 
# redirect_url = get_redirect_url()
# print(redirect_url)