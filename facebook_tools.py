from pyfacebook import GraphAPI
from dotenv import load_dotenv
from api import facebook_access_token

load_dotenv()
# Initialize the Facebook Graph API with the access token from environment variables
api = GraphAPI(access_token=facebook_access_token)

print(api.app_id)