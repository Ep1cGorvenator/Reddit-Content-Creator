import os
import praw
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- REDDIT API AUTHENTICATION ---
# Securely get credentials from environment variables
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = "COMP301 Agent by u/YourRedditUsername" # Replace with your actual username

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

# --- YOUR FIRST TOOL DEFINITION ---
def get_reddit_posts(subreddit_name: str, num_posts: int = 1000000):
    """
    A tool to fetch the top 'num_posts' from a given subreddit.
    
    Args:
        subreddit_name (str): The name of the subreddit to fetch posts from.
        num_posts (int): The number of top posts to retrieve.
        
    Returns:
        str: A formatted string containing the titles and content of the posts,
             or an error message if the subreddit is not found.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.hot(limit=num_posts)
        
        # Format the output for the agent to easily understand
        formatted_posts = ""
        for i, post in enumerate(top_posts):
            formatted_posts += f"--- Post {i+1} ---\n"
            formatted_posts += f"Title: {post.title}\n"
            formatted_posts += f"Content: {post.selftext}\n\n"
            
        return formatted_posts
    except Exception as e:
        return f"An error occurred: Could not find subreddit '{subreddit_name}' or another error happened. Details: {e}"

# --- TESTING THE TOOL ---
# This block allows you to test the function directly by running this file
if __name__ == "__main__":
    # Choose a subreddit to test with
    target_subreddit = "Cyberpunk" 
    print(f"Fetching top posts from r/{target_subreddit}...")
    
    # Call the function
    posts_data = get_reddit_posts(target_subreddit)
    
    # Print the results
    print("\n--- RESULTS ---")
    print(posts_data)