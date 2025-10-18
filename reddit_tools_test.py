"""
Reddit data fetching tools for CrewAI.
Refactored using Repository, Builder, and Value Object patterns.
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from dataclasses import dataclass
from enum import Enum
import praw
from dotenv import load_dotenv
from crewai.tools import BaseTool

load_dotenv()


# ============================================================================
# EXCEPTIONS
# ============================================================================

class RedditAuthenticationError(Exception):
    """Raised when Reddit authentication fails."""
    pass


class RedditFetchError(Exception):
    """Raised when fetching posts fails."""
    pass


# ============================================================================
# VALUE OBJECTS: Domain Entities
# ============================================================================

@dataclass(frozen=True)
class RedditPost:
    """
    Immutable value object representing a Reddit post.
    Encapsulates post data with type safety.
    """
    subreddit: str
    title: str
    content: str
    score: int
    url: str = ""
    author: str = ""
    
    @property
    def word_count(self) -> int:
        """Get word count of post content."""
        return len(self.content.split())
    
    def meets_quality_threshold(self, min_words: int = 50) -> bool:
        """
        Check if post meets quality threshold.
        
        Args:
            min_words: Minimum word count
            
        Returns:
            True if post meets threshold
        """
        return self.word_count >= min_words
    
    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility."""
        return {
            'subreddit': self.subreddit,
            'title': self.title,
            'content': self.content,
            'score': self.score
        }


class PostSortType(Enum):
    """Enumeration of Reddit post sorting types."""
    HOT = "hot"
    NEW = "new"
    TOP = "top"
    RISING = "rising"
    CONTROVERSIAL = "controversial"


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class RedditCredentials:
    """Reddit API credentials."""
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: str
    
    @classmethod
    def from_environment(cls) -> 'RedditCredentials':
        """
        Load credentials from environment variables.
        
        Returns:
            RedditCredentials instance
            
        Raises:
            RedditAuthenticationError: If credentials missing
        """
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        username = os.getenv("REDDIT_USERNAME")
        password = os.getenv("REDDIT_PASSWORD")
        
        if not all([client_id, client_secret, username, password]):
            raise RedditAuthenticationError(
                "Missing Reddit credentials in environment variables"
            )
        
        user_agent = f"COMP301 Agent by u/{username}"
        
        return cls(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )


@dataclass
class FetchConfig:
    """Configuration for fetching posts."""
    num_posts: int = 5
    min_word_count: int = 50
    sort_type: PostSortType = PostSortType.HOT
    include_stickied: bool = False


# ============================================================================
# BUILDER PATTERN: Reddit Client Configuration
# ============================================================================

class RedditClientBuilder:
    """Builder for creating configured PRAW Reddit instances."""
    
    def __init__(self):
        """Initialize builder with None values."""
        self._credentials: Optional[RedditCredentials] = None
        self._read_only: bool = True
    
    def with_credentials(self, credentials: RedditCredentials) -> 'RedditClientBuilder':
        """
        Set Reddit credentials.
        
        Args:
            credentials: Reddit API credentials
            
        Returns:
            Self for method chaining
        """
        self._credentials = credentials
        return self
    
    def with_credentials_from_env(self) -> 'RedditClientBuilder':
        """Load credentials from environment variables."""
        self._credentials = RedditCredentials.from_environment()
        return self
    
    def set_read_only(self, read_only: bool) -> 'RedditClientBuilder':
        """
        Set read-only mode.
        
        Args:
            read_only: Whether to use read-only mode
            
        Returns:
            Self for method chaining
        """
        self._read_only = read_only
        return self
    
    def build(self) -> praw.Reddit:
        """
        Build Reddit client instance.
        
        Returns:
            Configured PRAW Reddit instance
            
        Raises:
            RedditAuthenticationError: If credentials not set
        """
        if not self._credentials:
            raise RedditAuthenticationError("Credentials must be set before building")
        
        try:
            return praw.Reddit(
                client_id=self._credentials.client_id,
                client_secret=self._credentials.client_secret,
                username=self._credentials.username,
                password=self._credentials.password,
                user_agent=self._credentials.user_agent,
                read_only=self._read_only
            )
        except Exception as e:
            raise RedditAuthenticationError(f"Failed to create Reddit client: {e}") from e


# ============================================================================
# REPOSITORY PATTERN: Data Access Abstraction
# ============================================================================

class RedditRepository(ABC):
    """Abstract repository for Reddit data access."""
    
    @abstractmethod
    def fetch_posts(
        self,
        subreddit_name: str,
        config: FetchConfig
    ) -> List[RedditPost]:
        """
        Fetch posts from a subreddit.
        
        Args:
            subreddit_name: Name of subreddit
            config: Fetch configuration
            
        Returns:
            List of RedditPost objects
        """
        pass


class PrawRedditRepository(RedditRepository):
    """PRAW-based implementation of RedditRepository."""
    
    def __init__(self, reddit_client: praw.Reddit):
        """
        Initialize repository.
        
        Args:
            reddit_client: Configured PRAW client
        """
        self.reddit = reddit_client
    
    def fetch_posts(
        self,
        subreddit_name: str,
        config: FetchConfig
    ) -> List[RedditPost]:
        """
        Fetch posts from subreddit using PRAW.
        
        Args:
            subreddit_name: Subreddit name
            config: Fetch configuration
            
        Returns:
            List of filtered RedditPost objects
            
        Raises:
            RedditFetchError: If fetching fails
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get appropriate submission generator based on sort type
            if config.sort_type == PostSortType.HOT:
                submissions = subreddit.hot(limit=config.num_posts * 2)  # Fetch extra for filtering
            elif config.sort_type == PostSortType.NEW:
                submissions = subreddit.new(limit=config.num_posts * 2)
            elif config.sort_type == PostSortType.TOP:
                submissions = subreddit.top(limit=config.num_posts * 2)
            elif config.sort_type == PostSortType.RISING:
                submissions = subreddit.rising(limit=config.num_posts * 2)
            else:
                submissions = subreddit.hot(limit=config.num_posts * 2)
            
            posts = []
            for submission in submissions:
                # Skip stickied posts if configured
                if not config.include_stickied and submission.stickied:
                    continue
                
                post = RedditPost(
                    subreddit=subreddit_name,
                    title=submission.title,
                    content=submission.selftext,
                    score=submission.score,
                    url=submission.url,
                    author=str(submission.author) if submission.author else "[deleted]"
                )
                
                # Apply quality filter
                if post.meets_quality_threshold(config.min_word_count):
                    posts.append(post)
                
                # Stop when we have enough quality posts
                if len(posts) >= config.num_posts:
                    break
            
            return posts
            
        except Exception as e:
            raise RedditFetchError(
                f"Failed to fetch posts from r/{subreddit_name}: {e}"
            ) from e


# ============================================================================
# SERVICE LAYER: Business Logic
# ============================================================================

class RedditPostService:
    """
    Service layer for Reddit post operations.
    Orchestrates repository and applies business logic.
    """
    
    def __init__(self, repository: RedditRepository):
        """
        Initialize service.
        
        Args:
            repository: Reddit data repository
        """
        self.repository = repository
    
    def fetch_posts_from_multiple_subreddits(
        self,
        subreddit_names: List[str],
        config: FetchConfig
    ) -> List[RedditPost]:
        """
        Fetch posts from multiple subreddits.
        
        Args:
            subreddit_names: List of subreddit names
            config: Fetch configuration
            
        Returns:
            Aggregated list of posts from all subreddits
        """
        all_posts = []
        
        for subreddit_name in subreddit_names:
            print(f"Extracting content from subreddit: r/{subreddit_name}")
            
            try:
                posts = self.repository.fetch_posts(subreddit_name, config)
                all_posts.extend(posts)
                print(f"  ✓ Found {len(posts)} quality posts")
            except RedditFetchError as e:
                print(f"  ⚠️ Skipping r/{subreddit_name}: {e}")
                continue
        
        print(f"Content extraction complete. Found {len(all_posts)} total posts.")
        return all_posts


# ============================================================================
# CREWAI TOOL ADAPTER
# ============================================================================

class RedditTools(BaseTool):
    """
    CrewAI tool for fetching Reddit content.
    Adapter pattern: Adapts RedditPostService to CrewAI tool interface.
    Declares 'service' as a field so assignment is allowed when BaseTool is a pydantic model.
    """
    
    name: str = "Reddit Content Fetcher"
    description: str = "Fetches hot posts from a list of subreddits."
    service: Optional[RedditPostService] = None  # <-- declared field to satisfy pydantic/BaseTool
    
    def __init__(self, service: Optional[RedditPostService] = None):
        """
        Initialize tool.
        
        Args:
            service: Optional custom RedditPostService (creates default if None)
        """
        # Call BaseTool initializer if necessary
        try:
            super().__init__()
        except Exception:
            # Some BaseTool implementations may not require init args; ignore if it fails
            pass
        
        if service:
            self.service = service
        else:
            # Default initialization using environment credentials
            reddit_client = (RedditClientBuilder()
                           .with_credentials_from_env()
                           .set_read_only(True)
                           .build())
            repository = PrawRedditRepository(reddit_client)
            self.service = RedditPostService(repository)
    
    def _run(self, subreddit_names: list, num_posts: int = 5) -> list[dict]:
        """
        CrewAI tool interface implementation.
        
        Args:
            subreddit_names: List of subreddit names
            num_posts: Number of posts to fetch per subreddit
            
        Returns:
            List of post dictionaries (for CrewAI compatibility)
        """
        config = FetchConfig(
            num_posts=num_posts,
            min_word_count=50,
            sort_type=PostSortType.HOT
        )
        
        posts = self.service.fetch_posts_from_multiple_subreddits(
            subreddit_names,
            config
        )
        
        # Convert to dictionaries for backward compatibility
        return [post.to_dict() for post in posts]


# ============================================================================
# FACTORY: Convenience Constructors
# ============================================================================

class RedditToolsFactory:
    """Factory for creating configured RedditTools instances."""
    
    @staticmethod
    def create_default() -> RedditTools:
        """
        Create RedditTools with default configuration.
        
        Returns:
            Configured RedditTools instance
        """
        return RedditTools()
    
    @staticmethod
    def create_with_custom_config(
        credentials: RedditCredentials,
        min_word_count: int = 50
    ) -> RedditTools:
        """
        Create RedditTools with custom configuration.
        
        Args:
            credentials: Reddit API credentials
            min_word_count: Minimum word count for posts
            
        Returns:
            Configured RedditTools instance
        """
        reddit_client = (RedditClientBuilder()
                       .with_credentials(credentials)
                       .set_read_only(True)
                       .build())
        
        repository = PrawRedditRepository(reddit_client)
        service = RedditPostService(repository)
        
        return RedditTools(service)


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

# Global instance for backward compatibility
_default_tool: Optional[RedditTools] = None

def get_default_reddit_tool() -> RedditTools:
    """Get or create default RedditTools instance (singleton pattern)."""
    global _default_tool
    if _default_tool is None:
        _default_tool = RedditToolsFactory.create_default()
    return _default_tool


"""
Design patterns applied and why:
- Builder Pattern (RedditClientBuilder): separates construction of PRAW client with fluent API.
- Repository Pattern (RedditRepository / PrawRedditRepository): isolates data access and makes it testable/mocked.
- Value Object Pattern (RedditPost, RedditCredentials): immutable, typed domain objects.
- Service Layer (RedditPostService): encapsulates business logic and orchestration.
- Factory Pattern (RedditToolsFactory): convenience constructors for different configurations.
- Adapter Pattern (RedditTools -> BaseTool): adapts internal service to CrewAI tool interface.

Fix applied:
- Declared 'service: Optional[RedditPostService] = None' as a class field on RedditTools so assigning
  self.service in __init__ does not raise the pydantic/BaseTool "no field" error.
"""