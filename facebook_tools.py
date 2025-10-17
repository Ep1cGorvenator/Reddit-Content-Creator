from facebook import GraphAPI
from dotenv import load_dotenv
import api_keys
import json
import requests
import os
from flask import Flask, redirect, url_for, session, request, render_template

load_dotenv()
# Initialize the Facebook Graph API with the access token from environment variables
api = GraphAPI(access_token=api_keys.facebook_access_token)
#profile = api.get_object('122095381749082092', fields='first_name,location,link,email')

#curl -i -X GET "https://graph.facebook.com/v24.0/809896025009029/accounts?access_token=EAAjgxAUUx4EBPifIJgEFowL556XiJpDsEJnQiRqZB2nSywRBuZB4MMpJTitWxrd5WHXijcdpiPfm9pTUXgDSeifeZCqxNN0QEMU5oUQBF85pJc9zYSvSEL57oEYpeRIBvQYfjfx2SmZCZAzJbtHlefOZCiu6ia2T2ZA3BFbr6qgFFi4bI8ReC21Jv49rxm5DwFRYNRz2xIktwGdkpgwfGr2EqHVJM2HwuMj29Ly"


#print(json.dumps(profile, indent=4))


# --- Replace these placeholder values with your actual data ---
#"122095381749082092"#"809896025009029" # The ID of the Facebook User
#"708804804889961"
#"EAAKEp3qcTWkBPn1wdXUToCQ19qZA33ZBIAfJiQ5ZAohWPlZCgMoN78ebWLBKKSAB8njEQDImuCjnVTlQD7qDwtBYpNjZCQImW4QrIIItZBRLdPk5KJh3zGeuQznF7nkdraXjuWZCesfn283LxollB7mNtZCGnQHd0GXpMb62ptU3kyZButePLWHZBhdMWUK4RY6aDLDJB16Da4DbLR1AFraJUOmTz8F7KGGuF0dRQwktydIDOOLpZCGEJoZAfNNNqBZA0pZA001XrbJ7V73M2pwXVfO7StKJh7fGMWK1QRdhZAgjefNnGNlv64d7ofoq7KKqtZBAj9UZD"#"EAAjgxAUUx4EBPohbJpp7kZCPIzpLhMXQAgbGZBTM3L2Gk0z5H6vHMngZBJ9MtQuOsDVW5v5HtGi7viriVuwaBf7JmM6CboZApiT4ijnNY5rfkr3mKeev6XWrWxgKVmCaR0KEw5Pt5ReZC0q3iJYllpQqmydx90jjkBwUFhZB3AVZC14NeZCMcZAVzUu8gL8l71p4HH78K08XKtRrj3OIhvcFsexNj0E5O0x9tdALQ" # Your User Access Token
#"EAAKEp3qcTWkBPvCZCHTBnCYeQ02hmX6L3dbf8sSFOtzjodklrZC8YhZAnOkXtmSKCbM6jRF7ZChRnCNUc5KAfBC4U2ftsokvtsE9T2QUNvPrrZCFZBaGJVEUVFoTIT9iS4YmCUDwi600Bd9d08JZBWYBPh2rMp9hvNl0nimpE15OsJiZBkCBhKpZCaLa1uND6IHcEf2BKtJltDV8T04Hux6govp4CpZBNhfZA81PuIflZAHqw3121qiKI6gUfNWcZAUMMp1nSAJcIZBzcksG0ThZATy"
#"EAAjgxAUUx4EBPifIJgEFowL556XiJpDsEJnQiRqZB2nSywRBuZB4MMpJTitWxrd5WHXijcdpiPfm9pTUXgDSeifeZCqxNN0QEMU5oUQBF85pJc9zYSvSEL57oEYpeRIBvQYfjfx2SmZCZAzJbtHlefOZCiu6ia2T2ZA3BFbr6qgFFi4bI8ReC21Jv49rxm5DwFRYNRz2xIktwGdkpgwfGr2EqHVJM2HwuMj29Ly"
#"EAAKEp3qcTWkBPuaICaYsZB3fuKQAC2ZA5glNQ3uqVENZAmEqXZA0QjiAgBxMYCkPpKKHEH7ldlGEvhK0hlKUCz3B2Mfk5tch5mXvZCZAoMh8K0MSx7u2RZBjVuYm6wsBrcG826SraXg7OoAwXZCE8gXDmp3KOCX4eH4jZAS7x7N50ThXmVdFHIH5ZClSUHZAwa0ZBZCYfMK5fENkGTkTwWwAFnEtpNdYTDEMl5yaecj3fKR3OlpJZBvCkti5BQduzqGlgtlmAxMtfHgi77H0hq3A9t"



USER_ID = "2498932317144961"
USER_ACCESS_TOKEN = "EAAjgxAUUx4EBPpWmQpgMRKvQ759v00xwrr2UNsqucL4Xy9LDho4fgXg0I819G8HhuVeb7tTDxMYMZBMVOg4ptMIgRlHIBfExpTcoK1PqIYMFsNhuVIz2IdcEK8Srw0F1ybG3TJRygQ0DxBSDXmV1IgCwNqOgSYXTVftS04jbqNSLOESoSQDrMY4zteyYLrduzOd7OP8slNEYHiPcoOQsSSvSaUIVrDiAqUvxZAuqS70oZBN1XPJlysPMCVP50wvP6sD21E4e1kZD"
# -----------------------------------------------------------

# Construct the API endpoint URL
API_VERSION = "v24.0" # Use the API version mentioned or the current supported version
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
ENDPOINT = f"/me/accounts"
#
URL = f"{BASE_URL}{ENDPOINT}"
#
# Define the parameters for the GET request
# The access token is usually passed as a query parameter or in the Authorization header
PARAMS = {'access_token': USER_ACCESS_TOKEN}

try:
    # Make the GET request
    response = requests.get(URL, params=PARAMS)

    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()

    # The response content will be in JSON format
    data = response.json()
#
    print("Request Successful! 🎉")
    print("-" * 30)
    print(f"Status Code: {response.status_code}")
    # Print the JSON data in a nicely formatted way
    print("Response Data:")
    print(json.dumps(data, indent=4))
#
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error Occurred: {err}")
    # The response often contains error details in JSON
    try:
        print("\nError Details:")
        print(json.dumps(response.json(), indent=4))
    except (json.JSONDecodeError, UnboundLocalError):
        # Handle cases where response is not JSON or not defined
        print(f"Response text: {response.text}")
except requests.exceptions.RequestException as e:
    # Handle other request errors (e.g., connection issues)
    print(f"An error occurred during the request: {e}")



# --- Replace these placeholder values with your actual data ---
#PAGE_ID = "881618651700453" # The ID of the Facebook Page
#PAGE_ACCESS_TOKEN = "EAAjgxAUUx4EBPv6PJi6ATZAWAdi5ZCS3HZCpm6TQCJ6n8c9CVNdbahNhfLmvh9C9KCZAOV82np91dP12gSPsnCg5PZCuc25VbXfYdStyZC6ZCHsymAwwrWoEvXDbi1tZAGPB8ZAWDjnnpPq8B6EvApq3zjx6Fn7XaL1On4aR8GQd2G50rTQMgHMeZBUn6xIXR8CRiZAp5apKP9q6W1Ka9i9j9Ja9AJg4P7ZBGXjeFDr81LkZD" # The Page Access Token
#MESSAGE_TEXT = "This is a post made using the Facebook Graph API and Python requests library!" # The content of your post
## -----------------------------------------------------------
#
## Define the API endpoint
#API_VERSION = "v24.0"
#BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
#ENDPOINT = f"/{PAGE_ID}/feed"
#
#URL = f"{BASE_URL}{ENDPOINT}"
#
## Define the request body (the data to be sent)
## The access_token and message are sent in the body for a POST request
#PAYLOAD = {
#    'message': MESSAGE_TEXT,
#    'access_token': PAGE_ACCESS_TOKEN
#}
#
## The 'Content-Type: application/json' header is implied when you use the 'json' parameter in requests.post
#HEADERS = {
#    # You generally don't need to explicitly set Content-Type if using the 'json' parameter,
#    # but it's good practice to demonstrate the equivalent of the curl command.
#    'Content-Type': 'application/json'
#}
#
#try:
#    # Make the POST request
#    # Using the 'json' parameter automatically serializes the PAYLOAD dictionary to JSON and sets the appropriate header.
#    response = requests.post(URL, json=PAYLOAD, headers=HEADERS)
#
#    # Raise an exception for bad status codes (4xx or 5xx)
#    response.raise_for_status()
#
#    # The response content will be in JSON format, usually containing the new post ID
#    data = response.json()
#
#    print("Post Successful! 🎉")
#    print("-" * 30)
#    print(f"Status Code: {response.status_code}")
#    print("Response Data (should contain the new post ID):")
#    print(json.dumps(data, indent=4))
#
#except requests.exceptions.HTTPError as err:
#    print(f"HTTP Error Occurred: {err}")
#    try:
#        # The response often contains detailed error information
#        print("\nError Details:")
#        print(json.dumps(response.json(), indent=4))
#    except (json.JSONDecodeError, UnboundLocalError):
#        print(f"Response text: {response.text}")
#except requests.exceptions.RequestException as e:
#    print(f"An error occurred during the request: {e}")
#    

#import requests
#import os # For securely storing credentials as environment variables
#
## --- Your app credentials and configuration ---
#APP_ID =       api.facebook_app_id
#APP_SECRET = api.facebook_app_secret
#REDIRECT_URI = "http://localhost:8501/"  # Must match the one in your Facebook App settings
#AUTH_CODE = "..."  # This is the temporary code you receive in the redirect from Step 2
#
## --- Step 3: Exchange the 'code' for an Access Token ---
#TOKEN_EXCHANGE_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
#
#params = {
#    "client_id": APP_ID,
#    "redirect_uri": REDIRECT_URI,
#    "client_secret": APP_SECRET,
#    "code": AUTH_CODE
#}
#
#try:
#    response = requests.get(TOKEN_EXCHANGE_URL, params=params)
#    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
#
#    token_data = response.json()
#    
#    # The crucial piece of data: the User Access Token!
#    user_access_token = token_data.get("access_token")
#    
#    if user_access_token:
#        print(f"Successfully obtained User Access Token: {user_access_token}")
#        
#        # --- Step 4: Example API Call (Using the new token) ---
#        GRAPH_API_URL = "https://graph.facebook.com/v18.0/me"
#        
#        user_info_params = {
#            "fields": "id,name,email", # Request specific fields/data
#            "access_token": user_access_token
#        }
#        
#        user_response = requests.get(GRAPH_API_URL, params=user_info_params)
#        user_response.raise_for_status()
#        
#        user_info = user_response.json()
#        print(f"User Info: {user_info}")
#
#    else:
#        print("Token exchange failed: 'access_token' not found in response.")
#        
#except requests.exceptions.HTTPError as e:
#    print(f"HTTP Error during token exchange: {e}")
#except requests.exceptions.RequestException as e:
#    print(f"Request failed: {e}")
#

import requests
import json
import os # Used to check if the file exists and to get the file size

# --- Replace these placeholder values with your actual data ---
PAGE_ID = "859866000537287"
PAGE_ACCESS_TOKEN = "EAAjgxAUUx4EBPlRRZAV4AYRZCdqnJ6K5HuhUS6JbFTZBvTAhL6WYVhXGeh8VOp0wLELT0KzYoZBBKDbVmqpZCsLY0JCVdaLcQFVAXrjrWU2j0BKgFsM6znGak0VaDlTVKPAQ6tuyucKtjwE0xdHhPIdRZBXbi4Q7CSZBDnmniJUtDeq5EV8vL2CHnPzunE7DalInGiqr0YSP44RPlUaEfQEYc2vQwQTLkaGhTn2FkAZD"
VIDEO_FILE_PATH = "../Comp301/videoplayback.mp4" # <--- CHANGE THIS to your video file's actual path
VIDEO_TITLE = "Gorilla"
VIDEO_DESCRIPTION = "Video tester"
# -----------------------------------------------------------

# Define the API endpoint for video uploads
API_VERSION = "v24.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
# NOTE: We change the endpoint from /feed to /videos
ENDPOINT = f"/{PAGE_ID}/videos"

URL = f"{BASE_URL}{ENDPOINT}"

# 1. Check if the video file exists
if not os.path.exists(VIDEO_FILE_PATH):
    print(f"Error: Video file not found at '{VIDEO_FILE_PATH}'")
    exit()

# 2. Define the parameters (fields) for the video post
# The access_token, title, and description are sent as form fields.
FIELDS = {
    'title': VIDEO_TITLE,
    'description': VIDEO_DESCRIPTION,
    'access_token': PAGE_ACCESS_TOKEN
}

# 3. Define the file to be uploaded
# 'file' is the key Facebook expects for the video content.
# The tuple format is: ('filename', file_object, 'content_type')
try:
    with open(VIDEO_FILE_PATH, 'rb') as video_file:
        FILES = {
            'file': (os.path.basename(VIDEO_FILE_PATH), video_file, 'video/mp4')
        }

        print(f"Attempting to upload video: {os.path.basename(VIDEO_FILE_PATH)}...")

        # 4. Make the POST request
        # We use the 'files' parameter for the video content and the 'data' parameter for the fields.
        response = requests.post(URL, data=FIELDS, files=FILES)

    # 5. Process the response
    response.raise_for_status()

    # The response will contain the ID of the new video post (e.g., {"id": "1234567890"})
    data = response.json()

    print("\nVideo Post Successful! 🎥")
    print("-" * 30)
    print(f"Status Code: {response.status_code}")
    print("Response Data (should contain the new video ID):")
    print(json.dumps(data, indent=4))

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error Occurred: {err}")
    try:
        print("\nError Details:")
        print(json.dumps(response.json(), indent=4))
    except (json.JSONDecodeError, UnboundLocalError):
        print(f"Response text: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")










#FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
#FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
#FB_GRAPH_API_URL = "https://graph.facebook.com/v19.0"
#
#SCOPES = "public_profile"
#
#REDIRECT_URL= "https://managerially-unproofread-stefani.ngrok-free.dev/facebook-callback"
#
#app = Flask(__name__)
#app.secret_key = os.urandom(24)
#
#def get_redirect_uri():
#    # In a real app, this should be a fixed, public URL
#    # For local testing, ensure this matches your Meta App settings!
#    return url_for('facebook_callback', _external=True)
#
## -----------------------------------------------------
## 1. Initiation Route: Handles the "Sign In" button click
## -----------------------------------------------------
#@app.route('/login')
#def login():
#    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
#        return "ERROR: FACEBOOK_APP_ID or FACEBOOK_APP_SECRET not set.", 500
#
#    # Step 1: Construct the URL to redirect the user to Facebook
#    auth_url = 'https://www.facebook.com/v19.0/dialog/oauth'
#    params = {
#        'client_id': FACEBOOK_APP_ID,
#        'redirect_uri': REDIRECT_URL,
#        'scope': SCOPES
#    }
#    # Facebook is the Identity Provider (IdP), we redirect to its authorization endpoint
#    return redirect(f"{auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
#
## -----------------------------------------------------
## 2. Callback Route: Handles the response from Facebook
## -----------------------------------------------------
#@app.route('/facebook-callback')
#def facebook_callback():
#    # Check for an error from Facebook (e.g., user denied permission)
#    if 'error' in request.args:
#        error = request.args.get('error_description', 'Unknown error.')
#        return f"Login failed: {error}"
#
#    # Step 2: Receive the Authorization Code from the URL
#    code = request.args.get('code')
#    if not code:
#        return "Missing authorization code."
#
#    # Step 3: Exchange the Code for an Access Token (Server-to-Server)
#    token_url = f"{FB_GRAPH_API_URL}/oauth/access_token"
#    token_params = {
#        'client_id': FACEBOOK_APP_ID,
#        'redirect_uri': REDIRECT_URL,
#        'client_secret': FACEBOOK_APP_SECRET,
#        'code': code
#    }
#
#    try:
#        token_response = requests.get(token_url, params=token_params).json()
#        access_token = token_response.get('access_token')
#        
#        if not access_token:
#            return "Failed to get access token: " + str(token_response)
#
#        # Step 4: Use the Access Token to Fetch User Profile Data
#        profile_url = f"{FB_GRAPH_API_URL}/me"
#        # We request the fields corresponding to our SCOPES
#        profile_params = {
#            'fields': 'id,name,email,picture',
#            'access_token': access_token
#        }
#        
#        profile_response = requests.get(profile_url, params=profile_params).json()
#        
#        # Step 5: Process and Complete Authentication
#        user_id = profile_response.get('id')
#        user_name = profile_response.get('name')
#        user_email = profile_response.get('email')
#        user_picture = profile_response.get('picture', {}).get('data', {}).get('url')
#
#        # In a real application:
#        # 1. Look up 'user_id' in your database.
#        # 2. If found, log the user in (e.g., set their session).
#        # 3. If NOT found, create a new user record using name and email, and THEN log them in.
#
#        # For this example, we'll store data in the Flask session for display
#        session['user_id'] = user_id
#        session['user_name'] = user_name
#        session['user_email'] = user_email
#        session['user_picture'] = user_picture
#        
#        return redirect(url_for('profile'))
#
#    except requests.exceptions.RequestException as e:
#        return f"An error occurred during API communication: {e}"
#
## -----------------------------------------------------
## 3. Application Routes (Home, Profile, Logout)
## -----------------------------------------------------
#@app.route('/')
#def index():
#    # Simple home page with the login link
#    if 'user_id' in session:
#        return f'Welcome back, {session["user_name"]}! <a href="{url_for("profile")}">View Profile</a> | <a href="{url_for("logout")}">Logout</a>'
#    return '<p>Please sign in to continue.</p><a href="/login"><button>Sign in with Facebook</button></a>'
#
#@app.route('/profile')
#def profile():
#    # Display the user data retrieved from Facebook
#    if 'user_id' not in session:
#        return redirect(url_for('index'))
#    
#    return render_template('profile.html', user=session)
#
#@app.route('/logout')
#def logout():
#    # Clear the session data
#    session.pop('user_id', None)
#    session.pop('user_name', None)
#    session.pop('user_email', None)
#    session.pop('user_picture', None)
#    return redirect(url_for('index'))
#
#if __name__ == '__main__':
#    # You MUST set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in your environment!
#    # For local development, Flask typically runs on port 5000.
#    # The Redirect URI in your Meta App settings should be something like:
#    # http://127.0.0.1:5000/facebook-callback or http://localhost:5000/facebook-callback
#    app.run(debug=True)
#