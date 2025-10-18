"""
CrewAI orchestration module.
Refactored using Builder, Factory, and Strategy patterns.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from crewai import Agent, Task, Crew, Process
from litellm import completion
from dotenv import load_dotenv
from reddit_tools_test import RedditTools

load_dotenv()


# ============================================================================
# STRATEGY PATTERN: LLM Provider Interface
# ============================================================================

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass


class GeminiLLMProvider(LLMProvider):
    """Gemini LLM implementation via LiteLLM."""
    
    def __init__(self, model_name: str = "gemini/gemini-2.5-flash", temperature: float = 0.7):
        """
        Initialize Gemini provider.
        
        Args:
            model_name: Gemini model identifier
            temperature: Sampling temperature (0.0-1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        self._setup_api_key()
    
    def _setup_api_key(self):
        """Configure API key from environment."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        os.environ["GEMINI_API_KEY"] = api_key
    
    def generate(self, prompt: str) -> str:
        """
        Generate response using Gemini.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text response
            
        Raises:
            LLMGenerationError: If generation fails
        """
        try:
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMGenerationError(f"Gemini generation failed: {str(e)}") from e
    
    def __call__(self, prompt: str) -> str:
        """Allow callable interface for CrewAI compatibility."""
        return self.generate(prompt)


class LLMGenerationError(Exception):
    """Raised when LLM generation fails."""
    pass


# ============================================================================
# DATA CLASSES: Configuration Objects
# ============================================================================

@dataclass
class AgentConfig:
    """Configuration for a CrewAI Agent."""
    role: str
    goal: str
    backstory: str
    tools: List = field(default_factory=list)
    verbose: bool = True
    allow_delegation: bool = False


@dataclass
class TaskConfig:
    """Configuration for a CrewAI Task."""
    description: str
    expected_output: str
    agent_role: str  # References agent by role
    context_roles: List[str] = field(default_factory=list)  # Task dependencies


# ============================================================================
# FACTORY PATTERN: Agent and Task Creation
# ============================================================================

class AgentFactory:
    """Factory for creating configured Agents."""
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize factory with LLM provider.
        
        Args:
            llm_provider: LLM implementation to use
        """
        self.llm_provider = llm_provider
        self._agents: Dict[str, Agent] = {}
    
    def create_agent(self, config: AgentConfig) -> Agent:
        """
        Create and register an Agent from configuration.
        
        Args:
            config: Agent configuration
            
        Returns:
            Configured Agent instance
        """
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            llm=self.llm_provider,
            tools=config.tools,
            verbose=config.verbose,
            allow_delegation=config.allow_delegation
        )
        self._agents[config.role] = agent
        return agent
    
    def get_agent(self, role: str) -> Optional[Agent]:
        """Retrieve agent by role."""
        return self._agents.get(role)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all created agents."""
        return list(self._agents.values())


class TaskFactory:
    """Factory for creating configured Tasks."""
    
    def __init__(self, agent_factory: AgentFactory):
        """
        Initialize factory with agent reference.
        
        Args:
            agent_factory: Factory containing agents
        """
        self.agent_factory = agent_factory
        self._tasks: Dict[str, Task] = {}
    
    def create_task(self, config: TaskConfig, topic: str = "") -> Task:
        """
        Create Task from configuration with dynamic variable injection.
        
        Args:
            config: Task configuration
            topic: Runtime topic variable
            
        Returns:
            Configured Task instance
        """
        agent = self.agent_factory.get_agent(config.agent_role)
        if not agent:
            raise ValueError(f"Agent with role '{config.agent_role}' not found")
        
        # Resolve context dependencies
        context_tasks = [
            self._tasks[role] for role in config.context_roles
            if role in self._tasks
        ]
        
        # Format description with topic if provided
        description = config.description.format(topic=topic) if topic else config.description
        
        task = Task(
            description=description,
            expected_output=config.expected_output,
            agent=agent,
            context=context_tasks if context_tasks else None
        )
        
        self._tasks[config.agent_role] = task
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """Get all created tasks."""
        return list(self._tasks.values())


# ============================================================================
# BUILDER PATTERN: Crew Configuration and Assembly
# ============================================================================

class CrewBuilder:
    """Builder for assembling a complete Crew with agents and tasks."""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize builder.
        
        Args:
            llm_provider: LLM provider (defaults to GeminiLLMProvider)
        """
        self.llm_provider = llm_provider or GeminiLLMProvider()
        self.agent_factory = AgentFactory(self.llm_provider)
        self.task_factory = TaskFactory(self.agent_factory)
        self.process = Process.sequential
        self.verbose = True
        self.memory = False
    
    def add_agent(self, config: AgentConfig) -> 'CrewBuilder':
        """
        Add agent to crew.
        
        Args:
            config: Agent configuration
            
        Returns:
            Self for method chaining
        """
        self.agent_factory.create_agent(config)
        return self
    
    def add_task(self, config: TaskConfig) -> 'CrewBuilder':
        """
        Add task to crew (agents must be added first).
        
        Args:
            config: Task configuration
            
        Returns:
            Self for method chaining
        """
        self.task_factory.create_task(config)
        return self
    
    def set_process(self, process: Process) -> 'CrewBuilder':
        """Set execution process type."""
        self.process = process
        return self
    
    def set_verbose(self, verbose: bool) -> 'CrewBuilder':
        """Set verbose logging."""
        self.verbose = verbose
        return self
    
    def set_memory(self, memory: bool) -> 'CrewBuilder':
        """Set conversation memory."""
        self.memory = memory
        return self
    
    def build(self) -> Crew:
        """
        Build final Crew instance.
        
        Returns:
            Configured Crew ready for execution
        """
        return Crew(
            agents=self.agent_factory.get_all_agents(),
            tasks=self.task_factory.get_all_tasks(),
            process=self.process,
            verbose=self.verbose,
            memory=self.memory
        )


# ============================================================================
# TEMPLATE METHOD: Crew Execution Strategy
# ============================================================================

class CrewExecutor:
    """Executes crew with standardized error handling and logging."""
    
    def __init__(self, crew: Crew):
        """
        Initialize executor.
        
        Args:
            crew: Configured Crew instance
        """
        self.crew = crew
    
    def execute(self, inputs: Dict[str, str]) -> str:
        """
        Execute crew with error handling.
        
        Args:
            inputs: Input variables for tasks
            
        Returns:
            Execution result as string
        """
        try:
            result = self.crew.kickoff(inputs=inputs)
            return self._format_result(result)
        except Exception as e:
            return self._handle_error(e)
    
    def _format_result(self, result) -> str:
        """Format crew result for display."""
        if hasattr(result, 'raw'):
            return str(result.raw)
        elif hasattr(result, 'result'):
            return str(result.result)
        return str(result)
    
    def _handle_error(self, error: Exception) -> str:
        """Handle execution errors."""
        return f"Crew execution failed: {str(error)}"


# ============================================================================
# FACADE: High-Level Reddit Content Creator
# ============================================================================

class RedditContentCreator:
    """
    Facade for Reddit content generation workflow.
    Encapsulates crew configuration and execution.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize content creator.
        
        Args:
            llm_provider: Optional custom LLM provider
        """
        self.llm_provider = llm_provider or GeminiLLMProvider()
        self.reddit_tool = RedditTools()
        self._crew: Optional[Crew] = None
    
    def _build_crew(self) -> Crew:
        """Build the Reddit research crew configuration."""
        builder = CrewBuilder(self.llm_provider)
        
        # Define agent configurations
        subreddit_analyst = AgentConfig(
            role="Subreddit Analyst",
            goal="Identify relevant and active subreddits for a given topic.",
            backstory=(
                "You are an expert in online communities with deep knowledge of Reddit's ecosystem. "
                "You know which subreddits are active, well-moderated, and relevant for specific topics."
            )
        )
        
        reddit_researcher = AgentConfig(
            role="Reddit Data Researcher",
            goal="Fetch and organize hot posts from specified subreddits.",
            backstory=(
                "You are a diligent researcher skilled at gathering data from Reddit. "
                "You use tools effectively and present information in a clear, organized manner."
            ),
            tools=[self.reddit_tool],
            allow_delegation=False
        )
        
        creative_writer = AgentConfig(
            role="Creative Reddit Content Writer",
            goal=(
                "To write a new, engaging, and unique Reddit post that is stylistically similar to "
                "a set of provided examples, while being tailored to a specific user topic."
            ),
            backstory=(
                "You are a master storyteller and viral content creator, known for your ability to "
                "analyze writing trends and adapt your style. You can dissect any piece of text to "
                "understand its tone, format, and what makes it engaging."
            ),
            allow_delegation=False
        )
        
        # Define task configurations
        find_subreddits = TaskConfig(
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
            agent_role="Subreddit Analyst"
        )
        
        fetch_posts = TaskConfig(
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
            agent_role="Reddit Data Researcher",
            context_roles=["Subreddit Analyst"]
        )
        
        write_post = TaskConfig(
            description=(
                "You have been provided with a list of successful Reddit posts for research and "
                "the user's original topic: '{topic}'.\n"
                "Your mission is to write a new, original Reddit post. Follow these steps carefully:\n\n"
                "1. **Analyze the Style:** First, thoroughly analyze the provided list of posts.\n"
                "2. **Understand the User's Goal:** Focus on the user's original topic: '{topic}'.\n"
                "3. **Synthesize and Create:** Write a complete Reddit post that mimics the style "
                "while being completely original.\n\n"
                "Your final output MUST be only the new Reddit post, including a compelling title "
                "and a well-structured body with hook words that catch the users attention."
            ),
            expected_output="A complete Reddit post, consisting of a title and the main body text, ready for publishing.",
            agent_role="Creative Reddit Content Writer",
            context_roles=["Reddit Data Researcher"]
        )
        
        # Build crew
        return (builder
                .add_agent(subreddit_analyst)
                .add_agent(reddit_researcher)
                .add_agent(creative_writer)
                .add_task(find_subreddits)
                .add_task(fetch_posts)
                .add_task(write_post)
                .set_process(Process.sequential)
                .set_verbose(True)
                .set_memory(False)
                .build())
    
    def create_content(self, topic: str) -> str:
        """
        Generate Reddit content for a given topic.
        
        Args:
            topic: Content topic/theme
            
        Returns:
            Generated Reddit post
        """
        if not self._crew:
            self._crew = self._build_crew()
        
        executor = CrewExecutor(self._crew)
        return executor.execute({'topic': topic})


# ============================================================================
# PUBLIC API: Backward Compatibility
# ============================================================================

def run_crew(topic: str) -> str:
    """
    Run the Reddit research crew for a given topic.
    
    This function maintains backward compatibility with the original API.
    
    Args:
        topic: Content topic to research
        
    Returns:
        Generated content result
    """
    creator = RedditContentCreator()
    return creator.create_content(topic)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

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