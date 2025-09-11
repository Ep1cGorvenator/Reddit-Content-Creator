import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your keys securely
reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
google_api_key = os.getenv("GOOGLE_API_KEY")

# You can now use these variables to initialize your APIs
print(f"Loaded Google API Key starting with: {google_api_key[:5]}...")