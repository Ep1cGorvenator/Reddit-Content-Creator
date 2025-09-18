import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your keys securely
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
google_api_key = os.getenv("GOOGLE_API_KEY")
facebook_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")   