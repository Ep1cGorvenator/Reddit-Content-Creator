import os
from crewai import Agent, Task, Crew, Process
from litellm import completion
from dotenv import load_dotenv
from reddit_tools_test import RedditTools

load_dotenv()

# --- Robust LiteLLM Wrapper ---
class GeminiLLM:
    def __init__(self, model_name="gemini/gemini-2.0-flash-exp", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        # Set API key in environment
        os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
    def __call__(self, prompt: str) -> str:
        try:
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return f"Error generating response: {str(e)}"

llm = GeminiLLM()

# Instantiate custom tool
reddit_tool = RedditTools()

# --- AGENTS ---
subreddit_analyst = Agent(
    role="Subreddit Analyst",
    goal="Identify 3-5 relevant and active subreddits for a given topic.",
    backstory=(
        "You are an expert in online communities with deep knowledge of Reddit's ecosystem. "
        "You know which subreddits are active, well-moderated, and relevant for specific topics."
    ),
    llm=llm,
    verbose=True
)

reddit_researcher = Agent(
    role="Reddit Data Researcher",
    goal="Fetch and organize hot posts from specified subreddits.",
    backstory=(
        "You are a diligent researcher skilled at gathering data from Reddit. "
        "You use tools effectively and present information in a clear, organized manner."
    ),
    llm=llm,
    tools=[reddit_tool],
    verbose=True,
    allow_delegation=False  # Prevents unnecessary complexity
)

# --- TASKS ---
find_subreddits_task = Task(
    description=(
        "Analyze the topic: '{topic}'. "
        "Identify 3-5 most relevant and active subreddits where this topic is discussed. "
        "Consider factors like:\n"
        "- Community size and activity\n"
        "- Relevance to the topic\n"
        "- Quality of discussions\n\n"
        "Provide ONLY the subreddit names as a comma-separated list WITHOUT the 'r/' prefix.\n"
        "Example output: python,learnpython,programming,codinghelp"
    ),
    expected_output='Comma-separated list of 3-5 subreddit names without r/ prefix',
    agent=subreddit_analyst
)

fetch_posts_task = Task(
    description=(
        "You will receive a comma-separated list of subreddit names from the previous task.\n"
        "For EACH subreddit in that list:\n"
        "1. Use your Reddit tool to fetch the top 3 hot posts\n"
        "2. Extract key information: title, score, URL, number of comments\n\n"
        "Present the results in a clear, organized format grouped by subreddit."
    ),
    expected_output=(
        "A well-formatted report showing posts from each subreddit with "
        "title, score, comments, and URL for each post"
    ),
    agent=reddit_researcher,
    context=[find_subreddits_task]
)

# --- CREW ---
def run_crew(topic: str):
    """Run the Reddit research crew for a given topic."""
    try:
        crew = Crew(
            agents=[subreddit_analyst, reddit_researcher],
            tasks=[find_subreddits_task, fetch_posts_task],
            process=Process.sequential,
            verbose=True,
            memory=False  # Disable if you don't need conversation memory
        )
        result = crew.kickoff(inputs={'topic': topic})
        return result
    except Exception as e:
        return f"Crew execution failed: {str(e)}"

if __name__ == "__main__":
    print("=" * 50)
    print("Reddit Content Research Crew")
    print("=" * 50)
    
    user_topic = input("\nWhat topic would you like to research?\n> ")
    
    if not user_topic.strip():
        print("Error: Please provide a valid topic.")
    else:
        print(f"\nResearching: {user_topic}")
        print("-" * 50)
        
        crew_result = run_crew(user_topic)
        
        print("\n" + "=" * 50)
        print("Research Complete")
        print("=" * 50)
        print(crew_result)