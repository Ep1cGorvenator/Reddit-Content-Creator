import praw
import random

reddit = praw.Reddit(
    client_id = 'CpT1d5tmU45TS5GQM94Dtw',
    client_secret = 'dxgV5RBN7SyfjZ4jSGCOZQVKEhc9fA',
    user_agent = 'COMP301 Content Creation Agent',
    # username = 'LakeEnvironmental222',
    redirect_uri = 'http://localhost:8501'
    # password = PASSWORD # dont forget to remove from config file
)

state_rand = str(random.randint(0, 65000))
print(reddit.auth.url(duration="permanent", scopes=["submit"], state=state_rand))

# while(reddit)
# print(reddit.auth.authorize(code))
print(reddit.user.me())
# print(reddit.auth.authorize())

subreddit_name = ""
post_title = ""
post = ""
subreddit = reddit.subreddit(subreddit_name)
subreddit.submit_video()

from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/reddit_callback') 
def reddit_callback():
    # 1. Get the 'state' and 'code' from the URL query parameters
    auth_code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return f"Authorization Error: {error}"
    
    return f"Authentication successful! Code: {auth_code}, State: {state}"

if __name__ == '__main__':
    # Ensure this port matches the one in your registered redirect URI
    app.run(debug=True)