#from facebook import GraphAPI
#from dotenv import load_dotenv
#from api_keys import facebook_access_token
#import json
#
#load_dotenv()
## Initialize the Facebook Graph API with the access token from environment variables
#api = GraphAPI(access_token=facebook_access_token)
#profile = api.get_object('me', fields='first_name,location,link,email')
#
#print(json.dumps(profile, indent=4))