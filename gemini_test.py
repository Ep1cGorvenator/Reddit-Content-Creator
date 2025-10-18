"""
Gemini API testing module.
Refactored using Strategy, Template Method, and Command patterns.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv


# ============================================================================
# EXCEPTIONS
# ============================================================================

class GeminiConfigurationError(Exception):
    """Raised when Gemini API configuration fails."""
    pass


class GeminiGenerationError(Exception):
    """Raised when content generation fails."""
    pass


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@dataclass
class GeminiConfig:
    """Configuration for Gemini API."""
    api_key: str
    model_name: str = 'gemini-2.5-flash'
    safety_settings: Optional[Dict] = None
    
    @classmethod
    def from_environment(cls) -> 'GeminiConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            GeminiConfig instance
            
        Raises:
            GeminiConfigurationError: If API key not found
        """
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise GeminiConfigurationError(
                "GOOGLE_API_KEY not found in .env file."
            )
        
        # Default safety settings (minimal blocking)
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        return cls(
            api_key=api_key,
            safety_settings=safety_settings
        )


class GeminiAPIClient:
    """Client for interacting with Gemini API."""
    
    def __init__(self, config: GeminiConfig):
        """
        Initialize Gemini client.
        
        Args:
            config: Gemini configuration
        """
        self.config = config
        self._configure_api()
        self.model = genai.GenerativeModel(config.model_name)
    
    def _configure_api(self):
        """Configure the Gemini API with credentials."""
        genai.configure(api_key=self.config.api_key)
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content from prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text response
            
        Raises:
            GeminiGenerationError: If generation fails
        """
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.config.safety_settings
            )
            return response.text
        except Exception as e:
            raise GeminiGenerationError(
                f"Content generation failed: {str(e)}"
            ) from e


# ============================================================================
# STRATEGY PATTERN: Prompt Engineering
# ============================================================================

class PromptStrategy(ABC):
    """Abstract strategy for prompt engineering."""
    
    @abstractmethod
    def engineer_prompt(self, user_input: str) -> str:
        """
        Transform user input into engineered prompt.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Engineered prompt
        """
        pass


class SubredditExtractionPromptStrategy(PromptStrategy):
    """Prompt strategy for extracting subreddit recommendations."""
    
    def engineer_prompt(self, user_input: str) -> str:
        """
        Engineer prompt for subreddit extraction task.
        
        Args:
            user_input: User's topic/query
            
        Returns:
            Engineered prompt for subreddit extraction
        """
        return (
            f"You are an AI assistant. A user will provide a prompt describing "
            f"the type of content they want to look for on Reddit.\n\n"
            f"Your task:\n"
            f"- Analyze the user's prompt to determine the theme or type of content they are seeking.\n"
            f"- Return only a comma-separated list of relevant subreddit names that match the theme/context.\n"
            f"- The output must be strictly in the format:\n"
            f"  subreddit_1, subreddit_2, subreddit_3, ...\n"
            f"- Do not include any explanations, additional text, or formatting outside of the list.\n\n"
            f"User prompt: '{user_input}'"
        )


class GeneralPromptStrategy(PromptStrategy):
    """Pass-through strategy for general queries."""
    
    def engineer_prompt(self, user_input: str) -> str:
        """Return user input as-is."""
        return user_input


# ============================================================================
# COMMAND PATTERN: Test Operations
# ============================================================================

class TestCommand(ABC):
    """Abstract command for test operations."""
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the test command."""
        pass


class SubredditExtractionTest(TestCommand):
    """Test command for subreddit extraction workflow."""
    
    def __init__(
        self,
        api_client: GeminiAPIClient,
        prompt_strategy: PromptStrategy,
        reddit_fetcher: Any,
        user_input: str,
        num_posts: int = 3
    ):
        """
        Initialize test command.
        
        Args:
            api_client: Gemini API client
            prompt_strategy: Prompt engineering strategy
            reddit_fetcher: Reddit data fetcher (dependency injection)
            user_input: User's input prompt
            num_posts: Number of posts to fetch per subreddit
        """
        self.api_client = api_client
        self.prompt_strategy = prompt_strategy
        self.reddit_fetcher = reddit_fetcher
        self.user_input = user_input
        self.num_posts = num_posts
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute subreddit extraction and content fetching.
        
        Returns:
            Dictionary containing results
        """
        # Step 1: Engineer prompt
        engineered_prompt = self.prompt_strategy.engineer_prompt(self.user_input)
        print(f"Sending prompt to Gemini: '{self.user_input}'")
        
        # Step 2: Get subreddit recommendations
        response = self.api_client.generate_content(engineered_prompt)
        print("\n--- Gemini's Response ---")
        print(response)
        
        # Step 3: Parse subreddit list
        subreddit_list = self._parse_subreddits(response)
        print(f"\nExtracted Subreddits: {subreddit_list}")
        
        # Step 4: Fetch Reddit content
        reddit_content = self.reddit_fetcher(subreddit_list, num_posts=self.num_posts)
        print("\n--- Reddit Content ---")
        print(reddit_content)
        
        return {
            'prompt': self.user_input,
            'engineered_prompt': engineered_prompt,
            'subreddits': subreddit_list,
            'reddit_content': reddit_content
        }
    
    def _parse_subreddits(self, response: str) -> List[str]:
        """
        Parse comma-separated subreddit list from response.
        
        Args:
            response: API response text
            
        Returns:
            List of cleaned subreddit names
        """
        return [
            sub.strip().removeprefix("r/")
            for sub in response.split(",")
            if sub.strip()
        ]


# ============================================================================
# TEMPLATE METHOD: Test Execution Workflow
# ============================================================================

class GeminiTestRunner(ABC):
    """
    Abstract base class defining test execution workflow.
    Template Method pattern.
    """
    
    def __init__(self, api_client: GeminiAPIClient):
        """
        Initialize test runner.
        
        Args:
            api_client: Configured Gemini API client
        """
        self.api_client = api_client
    
    def run_test(self, user_input: str) -> Any:
        """
        Template method defining test workflow.
        
        Args:
            user_input: User input for testing
            
        Returns:
            Test results
        """
        try:
            self._setup()
            command = self._create_command(user_input)
            result = command.execute()
            self._teardown()
            return result
        except GeminiGenerationError as e:
            self._handle_error(e)
            return None
        except Exception as e:
            self._handle_error(e)
            return None
    
    def _setup(self):
        """Hook for pre-test setup."""
        print("Gemini API configured successfully.")
    
    @abstractmethod
    def _create_command(self, user_input: str) -> TestCommand:
        """
        Create test command (must be implemented by subclass).
        
        Args:
            user_input: User input
            
        Returns:
            TestCommand instance
        """
        pass
    
    def _teardown(self):
        """Hook for post-test cleanup."""
        pass
    
    def _handle_error(self, error: Exception):
        """Handle test errors."""
        print(f"\nAn error occurred: {error}")
        print("Please check if your API key is valid and has been enabled in your Google Cloud project.")


class SubredditTestRunner(GeminiTestRunner):
    """Concrete test runner for subreddit extraction tests."""
    
    def __init__(self, api_client: GeminiAPIClient, reddit_fetcher: Any):
        """
        Initialize subreddit test runner.
        
        Args:
            api_client: Gemini API client
            reddit_fetcher: Function to fetch Reddit posts
        """
        super().__init__(api_client)
        self.reddit_fetcher = reddit_fetcher
    
    def _create_command(self, user_input: str) -> TestCommand:
        """Create subreddit extraction test command."""
        prompt_strategy = SubredditExtractionPromptStrategy()
        return SubredditExtractionTest(
            api_client=self.api_client,
            prompt_strategy=prompt_strategy,
            reddit_fetcher=self.reddit_fetcher,
            user_input=user_input,
            num_posts=3
        )


# ============================================================================
# FACADE: High-Level Test Interface
# ============================================================================

class GeminiTester:
    """
    Facade providing simple interface for Gemini testing.
    """
    
    def __init__(self, config: Optional[GeminiConfig] = None):
        """
        Initialize tester.
        
        Args:
            config: Optional Gemini configuration (loads from env if None)
        """
        self.config = config or GeminiConfig.from_environment()
        self.api_client = GeminiAPIClient(self.config)
    
    def test_subreddit_extraction(
        self,
        user_prompt: str,
        reddit_fetcher: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Test subreddit extraction workflow.
        
        Args:
            user_prompt: User's query/topic
            reddit_fetcher: Function to fetch Reddit data
            
        Returns:
            Test results or None if failed
        """
        runner = SubredditTestRunner(self.api_client, reddit_fetcher)
        return runner.run_test(user_prompt)
    
    def test_general_prompt(self, prompt: str) -> Optional[str]:
        """
        Test general prompt (no specific workflow).
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response or None
        """
        try:
            return self.api_client.generate_content(prompt)
        except GeminiGenerationError as e:
            print(f"Error: {e}")
            return None


# ============================================================================
# BACKWARD COMPATIBILITY: Original Function Interface
# ============================================================================

def run_gemini_prompt(prompt: str):
    """
    Original function interface maintained for backward compatibility.
    
    Args:
        prompt: User prompt for Gemini
    """
    try:
        # Import here to avoid circular dependency
        from old_reddit_tools import get_reddit_posts
        
        tester = GeminiTester()
        tester.test_subreddit_extraction(prompt, get_reddit_posts)
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check if your API key is valid.")


def setup_gemini():
    """Legacy function for backward compatibility."""
    config = GeminiConfig.from_environment()
    genai.configure(api_key=config.api_key)
    print("Gemini API configured successfully.")


def prompt_engineer_prompt(original_prompt: str) -> str:
    """Legacy function for backward compatibility."""
    strategy = SubredditExtractionPromptStrategy()
    return strategy.engineer_prompt(original_prompt)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    input_prompt = input("Enter your prompt for Gemini: ")
    
    if not input_prompt.strip():
        print("Error: Please provide a valid prompt.")
    else:
        run_gemini_prompt(input_prompt)