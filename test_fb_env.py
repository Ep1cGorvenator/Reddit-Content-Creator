# test_facebook_env.py
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv('FB_ACCESS_TOKEN')

if token:
    print(f"✅ Token loaded successfully!")
    print(f"Token preview: {token[:20]}...{token[-10:]}")
else:
    print("❌ Token not found. Check your .env file.")