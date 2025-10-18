import os
from crewai import Agent, Task, Crew, Process
from litellm import completion
from dotenv import load_dotenv
from reddit_tools_test import RedditTools

load_dotenv()

# --- Robust LiteLLM Wrapper ---
class GeminiLLM:
    def __init__(self, model_name="gemini/gemini-2.5-flash", temperature=0.7):
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
# --- AGENT 1: The Subreddit Analyst ---
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

# --- AGENT 2: The Reddit Researcher ---
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

# --- AGENT 3: The Creative Writer ---
creative_writer = Agent(
    role="Creative Reddit Content Writer",
    goal=(
        "To write a new, engaging, and unique Reddit post that is stylistically similar to a set of provided examples, "
        "while being tailored to a specific user topic."
    ),
    backstory=(
        "You are a master storyteller and viral content creator, known for your ability to analyze writing trends and adapt your style. "
        "You can dissect any piece of text to understand its tone, format, and what makes it engaging. "
        "You then use these insights to craft entirely new content that resonates with specific online communities."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# --- TASKS ---
# --- TASK 1: The Subreddit Identification Task ---
find_subreddits_task = Task(
    description=(
        "Analyze the topic: '{topic}'. "
        "Identify the most relevant and active subreddits where this topic is discussed. "
        "Consider factors like:\n"
        "- Community size and activity\n"
        "- Relevance to the topic\n"
        "- Quality of discussions\n\n"
        "Provide ONLY the subreddit names as a comma-separated list WITHOUT the 'r/' prefix.\n"
        "Example output: python,learnpython,programming,codinghelp"
    ),
    expected_output='Comma-separated list of subreddit names without r/ prefix',
    agent=subreddit_analyst
)

# --- TASK 2: The Reddit Research Task ---
fetch_posts_task = Task(
    description=(
        "You will receive a comma-separated list of subreddit names from the previous task.\n"
        "For EACH subreddit in that list:\n"
        "1. Use your Reddit tool to fetch the top hot posts\n"
        "2. Extract key information: title, score, content\n\n"
        "Present the results in a clear, organized format grouped by subreddit."
    ),
    expected_output=(
        "A well-formatted report showing posts from each subreddit with "
        "title, content and score for each post"
    ),
    agent=reddit_researcher,
    context=[find_subreddits_task]
)

# --- TASK 3: The Writing Task ---
write_post_task = Task(
    description=(
        "You have been provided with a list of successful Reddit posts for research and the user's original topic: '{topic}'.\n"
        "Your mission is to write a new, original Reddit post. Follow these steps carefully:\n\n"
        "1. **Analyze the Style:** First, thoroughly analyze the provided list of posts. Pay close attention to:\n"
        "   - **Tone:** Is it humorous, serious, technical, or casual, etc.?\n"
        "   - **Formatting:** Do they use bullet points, bold text, or long paragraphs, etc.?\n"
        "   - **Sentence Structure:** Are the sentences short and punchy or long and descriptive?\n"
        "   - **Overall Vibe:** What makes these posts 'trendy' or engaging for their audience?\n\n"
        "2. **Understand the User's Goal:** Next, focus on the user's original topic: '{topic}'. This is the core subject your new post MUST be about.\n\n"
        "3. **Synthesize and Create:** Now, combine your findings. Write a complete Reddit post that:\n"
        "   - Is about the user's topic.\n"
        "   - Mimics the writing style, tone, and format you discovered during your analysis.\n"
        "   - Is completely original and not just a summary of the provided posts.\n\n"
        "Your final output MUST be only the new Reddit post, including a compelling title and a well-structured body "
        "with hook words that catch the users attention, and keeping them engaged."
    ),
    expected_output="A complete Reddit post, consisting of a title and the main body text, ready for publishing.",
    agent=creative_writer,
    context=[fetch_posts_task] # This task uses the output of the researcher
)

# --- CREW ---
def run_crew(topic: str):
    """Run the Reddit research crew for a given topic."""
    try:
        crew = Crew(
            agents=[subreddit_analyst, reddit_researcher, creative_writer],
            tasks=[find_subreddits_task, fetch_posts_task, write_post_task],
            process=Process.sequential,
            verbose=True,
            memory=False  # Disable if you don't need conversation memory
        )
        result = crew.kickoff(inputs={'topic': topic})
        return result
    except Exception as e:
        return f"Crew execution failed: {str(e)}"

# This makes the script runnable
if __name__ == "__main__":
    print("=" * 50)
    print("Reddit Content Creator")
    print("=" * 50)
    
    user_topic = input("\nWhat content would you like to create?\n> ")
    
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