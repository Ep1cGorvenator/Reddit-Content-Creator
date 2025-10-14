import os
import praw
from dotenv import load_dotenv
from crewai.tools import BaseTool

# Load environment variables from .env file
load_dotenv()

# --- REDDIT API AUTHENTICATION ---
# Securely get credentials from environment variables
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = "COMP301 Agent by u/DoNotEngage001" # Replace with your actual username

# Initialize the Reddit instance with PRAW
# The 'read_only=True' is important if you only plan to read posts
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD,
    user_agent=USER_AGENT,
    read_only=True 
)

class RedditTools(BaseTool):
    name: str = "Reddit Content Fetcher"
    description: str = "Fetches hot posts from a list of subreddits."

    def _run(self, subreddit_names: list, num_posts: int = 5) -> list[dict]:
        """
        Fetches 'num_posts' hot posts from each subreddit in the list.
        Returns a list of dictionaries, where each dictionary is a post.
        """
        all_posts = []
        for subreddit_name in subreddit_names:
            print(f"Extracting content from subreddit: r/{subreddit_name}")
            try:
                subreddit = reddit.subreddit(subreddit_name)
                hot_posts = subreddit.hot(limit=num_posts)
                
                for post in hot_posts:
                    # Filter for posts with meaningful content
                    if len(post.selftext.split()) > 50:
                        all_posts.append({
                            "subreddit": subreddit_name,
                            "title": post.title,
                            "content": post.selftext,
                            "score": post.score
                        })
            except Exception as e:
                print(f"⚠️ Skipping subreddit '{subreddit_name}' due to error: {e}")
                continue
        
        print(f"Content extraction complete. Found {len(all_posts)} posts.")
        return all_posts