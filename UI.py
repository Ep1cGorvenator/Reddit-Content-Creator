"""
Streamlit UI Module - Refactored with MVP Pattern
Separates presentation, business logic, and state management.
"""

import streamlit as st
import base64 as bs64
import time
import tempfile
import os
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Protocol
from abc import ABC, abstractmethod

import UI_tools
from audio import Audio
from video_gen import VideoGenerator

# Import crew functionality
try:
    from crew import run_crew
except ImportError:
    def run_crew(topic: str):
        time.sleep(2)
        return (
            f"### This is a placeholder response for the topic: '{topic}'\n\n"
            "The full agent crew is not connected. This is a sample of what the "
            "generated post would look like."
        )


# ============================================================================
# DATA MODELS (Following Single Responsibility Principle)
# ============================================================================

@dataclass
class Message:
    """Immutable message data structure."""
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    video_path: Optional[str] = None
    
    def is_assistant(self) -> bool:
        return self.role == "assistant"
    
    def is_user(self) -> bool:
        return self.role == "user"
    
    def has_video(self) -> bool:
        return self.video_path is not None and os.path.exists(self.video_path)


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    enable_video: bool = False
    add_subtitles: bool = False
    use_bg_music: bool = False
    bg_music_volume: float = 0.1
    
    def is_enabled(self) -> bool:
        return self.enable_video
    
    def get_bg_volume(self) -> float:
        """Returns 0 if bg music disabled, volume otherwise."""
        return self.bg_music_volume if self.use_bg_music else 0.0


@dataclass
class TTSConfig:
    """Configuration for text-to-speech."""
    enabled: bool = False
    selected_voice: str = "Charon"


# ============================================================================
# REPOSITORY PATTERN (Centralized State Management)
# ============================================================================

class MessageRepository:
    """
    Repository for managing conversation messages.
    Encapsulates Streamlit session state access.
    """
    
    def __init__(self, session_state):
        self._state = session_state
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Initialize messages list if not exists."""
        if "messages" not in self._state:
            self._state.messages = []
    
    def add_message(self, message: Message):
        """Add a message to the conversation history."""
        self._state.messages.append(message)

    def get_all_messages(self) -> List[Message]:
        """Retrieve all messages."""
        return [Message(**msg) if isinstance(msg, dict) else msg 
                for msg in self._state.messages]

    def clear_all(self):
        """Clear all messages."""
        self._state.messages = []

    def has_messages(self) -> bool:
        """Check if conversation has any messages."""
        return len(self._state.messages) > 0

    def update_last_message(self, *, content: Optional[str] = None, video_path: Optional[str] = None):
        """Update the last message in-session (content and/or video_path)."""
        if not self._state.messages:
            return
        last = self._state.messages[-1]
        # handle stored dicts or Message objects
        if isinstance(last, dict):
            if content is not None:
                last['content'] = content
            if video_path is not None:
                last['video_path'] = video_path
        else:
            if content is not None:
                last.content = content
            if video_path is not None:
                last.video_path = video_path


class ConfigRepository:
    """
    Repository for managing application configuration.
    Provides type-safe access to settings.
    """
    
    def __init__(self, session_state):
        self._state = session_state
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Initialize default configurations."""

        if "enable_tts" not in self._state:
            self._state.enable_tts = False
        if "enable_video" not in self._state:
            self._state.enable_video = False
        if "selected_voice" not in self._state:
            self._state.selected_voice = "Charon"
        if "add_subtitles" not in self._state:
            self._state.add_subtitles = False
        if "use_bg_music" not in self._state:
            self._state.use_bg_music = False
        if "bg_music_volume" not in self._state:
            self._state.bg_music_volume = 0.3
    
    def get_tts_config(self) -> TTSConfig:
        """Get current TTS configuration.""" 
        return TTSConfig(
            enabled=self._state.enable_tts,
            selected_voice=self._state.selected_voice
        )
    
    def get_video_config(self) -> VideoConfig:
        """Get current video configuration.""" 
        return VideoConfig(
            enable_video=self._state.enable_video,
            add_subtitles=self._state.add_subtitles,
            use_bg_music=self._state.use_bg_music,
            bg_music_volume=self._state.bg_music_volume
        )
    
    def update_tts_enabled(self, enabled: bool):
        """Update TTS enabled state.""" 
        self._state.enable_tts = enabled


# ============================================================================
# SERVICE LAYER (Business Logic)
# ============================================================================

class ContentGenerationService:
    """
    Service for orchestrating content generation.
    Coordinates between crew, audio, and video subsystems.
    """
    
    def __init__(
        self,
        crew_executor: Callable[[str], any],
        audio_handler: Audio,
        video_generator: Optional[VideoGenerator] = None
    ):
        self.crew_executor = crew_executor
        self.audio_handler = audio_handler
        self.video_generator = video_generator
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using crew AI.
        
        Args:
            prompt: User input prompt
            
        Returns:
            Generated content string
        """
        crew_response = self.crew_executor(prompt)
        
        # Extract text from CrewOutput
        if hasattr(crew_response, 'raw'):
            return str(crew_response.raw)
        elif hasattr(crew_response, 'result'):
            return str(crew_response.result)
        else:
            return str(crew_response)
    
    def generate_audio(self, text: str, voice_name: str) -> Optional[bytes]:
        """
        Generate audio from text.
        
        Args:
            text: Text to convert
            voice_name: Voice identifier
            
        Returns:
            Audio bytes or None
        """
        clean_text = self.audio_handler.clean_text_for_speech(text)
        return self.audio_handler.text_to_speech(clean_text, voice_name)
    
    def generate_video(
        self,
        audio_bytes: bytes,
        text: str,
        video_config: VideoConfig
    ) -> Optional[str]:
        """
        Generate video with audio and optional subtitles.
        
        Args:
            audio_bytes: Pre-generated audio
            text: Original text for subtitles
            video_config: Video generation configuration
            
        Returns:
            Path to generated video or None
        """
        if not self.video_generator:
            raise Exception("Video generator not initialized")
        
        if not os.path.exists("base_video.mp4"):
            raise FileNotFoundError("base_video.mp4 not found")
        
        output_path = os.path.join(
            tempfile.gettempdir(),
            f"gorilla_video_{int(time.time())}.mp4"
        )
        
        clean_text = self.audio_handler.clean_text_for_speech(text)
        
        return self.video_generator.generate_video_from_audio(
            audio_bytes=audio_bytes,
            text=clean_text,
            output_path=output_path,
            add_subtitles=video_config.add_subtitles,
            bg_music_volume=video_config.get_bg_volume()
        )


# ============================================================================
# PRESENTER (MVP Pattern)
# ============================================================================

class ChatPresenter:
    """
    Presenter component for chat interface.
    Orchestrates business logic and view updates.
    """
    
    def __init__(
        self,
        message_repo: MessageRepository,
        config_repo: ConfigRepository,
        content_service: ContentGenerationService,
        view: 'ChatView'
    ):
        self.message_repo = message_repo
        self.config_repo = config_repo
        self.content_service = content_service
        self.view = view
    
    def process_user_input(self, prompt: str):
        """
        Main orchestration method for handling user input.
        Follows the Template Method pattern for consistent flow.
        """
        # 1. Save user message
        user_message = Message(role="user", content=prompt)
        self.message_repo.add_message(user_message)
        self.view.display_user_message(user_message)
        
        # 2. Generate content (blocking, but we display text ASAP)
        try:
            response_text = self._generate_response(prompt)
            intro_text = str(UI_tools.get_intro_generator(prompt))
            
            # Immediately create and display assistant message (so text is visible while media is created)
            assistant_message = Message(role="assistant", content=intro_text+response_text)
            self.message_repo.add_message(assistant_message)
            self.view.display_message(assistant_message)   # show text quickly
            
            # 3. Generate multimedia if needed (audio/video)
            audio_bytes = self._handle_audio_generation(response_text)
            video_path = self._handle_video_generation(response_text, audio_bytes)
            
            # 4. If video produced, update last assistant message and show the video
            if video_path:
                self.message_repo.update_last_message(video_path=video_path)
                # Display video once now (display_message no longer auto-displays video)
                self.view.display_video(video_path)
            
        except Exception as e:
            self._handle_error(e)
    
    def _generate_response(self, prompt: str) -> str:
        """Generate text response using content service."""
        with self.view.show_spinner("Gorilla is thinking..."):
            return self.content_service.generate_content(prompt)
    
    def _handle_audio_generation(self, text: str) -> Optional[bytes]:
        """Generate audio if TTS or video is enabled."""
        tts_config = self.config_repo.get_tts_config()
        video_config = self.config_repo.get_video_config()
        
        if not (tts_config.enabled or video_config.is_enabled()):
            return None
        
        with self.view.show_spinner("🎵 Generating audio..."):
            audio_bytes = self.content_service.generate_audio(
                text,
                tts_config.selected_voice
            )
            
            if tts_config.enabled and audio_bytes:
                self.view.play_audio(audio_bytes)
            
            return audio_bytes
    
    def _handle_video_generation(
        self,
        text: str,
        audio_bytes: Optional[bytes]
    ) -> Optional[str]:
        """Generate video if enabled and audio available."""
        video_config = self.config_repo.get_video_config()
        
        if not video_config.is_enabled() or not audio_bytes:
            return None
        
        try:
            status_msg = self._build_video_status_message(video_config)
            
            with self.view.show_spinner(status_msg):
                video_path = self.content_service.generate_video(
                    audio_bytes,
                    text,
                    video_config
                )
                
                success_msg = self._build_video_success_message(video_config)
                self.view.show_success(success_msg)
                # do not call display_video here — presenter will call it after updating last message
                return video_path
                
        except FileNotFoundError:
            self.view.show_error(
                "❌ Cannot generate video: base_video.mp4 not found!\n"
                "Place your video as 'base_video.mp4' in the same folder as UI.py"
            )
            return None
        except Exception as e:
            self.view.show_error(f"❌ Video generation error: {str(e)}")
            return None
    
    def _build_video_status_message(self, config: VideoConfig) -> str:
        """Build status message for video generation."""
        msg = "🎬 Generating video"
        if config.add_subtitles:
            msg += " with AI subtitles"
        if config.use_bg_music:
            msg += f" and background music ({int(config.bg_music_volume * 100)}%)"
        return msg + "..."
    
    def _build_video_success_message(self, config: VideoConfig) -> str:
        """Build success message after video generation."""
        parts = ["✅ Video generated successfully!"]
        if config.add_subtitles:
            parts.append("🎯 Subtitles synced with Whisper AI")
        if config.use_bg_music:
            parts.append(f"🎵 Background music at {int(config.bg_music_volume * 100)}%")
        return " | ".join(parts)
    
    def _handle_error(self, error: Exception):
        """Handle and display errors."""
        error_message = f"Sorry, an error occurred: {error}"
        self.view.show_error(error_message)
        
        import traceback
        self.view.show_code(traceback.format_exc())
        
        # Save error message
        error_msg = Message(role="assistant", content=error_message)
        self.message_repo.add_message(error_msg)
    
    def display_conversation_history(self):
        """Display all messages in the conversation."""
        for message in self.message_repo.get_all_messages():
            self.view.display_message(message)
    
    def clear_conversation(self):
        """Clear all messages."""
        self.message_repo.clear_all()


# ============================================================================
# VIEW ABSTRACTION (Interface for UI Operations)
# ============================================================================

class ChatView(Protocol):
    """Protocol defining the chat view interface."""
    
    def display_message(self, message: Message):
        """Display a chat message."""
        ...
    
    def display_user_message(self, message: Message):
        """Display user message."""
        ...
    
    def show_spinner(self, text: str):
        """Show loading spinner with text.""" 
        ...
    
    def play_audio(self, audio_bytes: bytes):
        """Play audio in the UI.""" 
        ...
    
    def display_video(self, video_path: str):
        """Display video player.""" 
        ...
    
    def show_success(self, message: str):
        """Show success message.""" 
        ...
    
    def show_error(self, message: str):
        """Show error message.""" 
        ...
    
    def show_code(self, code: str):
        """Display code block.""" 
        ...


class StreamlitChatView:
    """Concrete implementation of ChatView for Streamlit."""
    
    def __init__(self, st_module, audio_handler: Audio):
        self.st = st_module
        self.audio_handler = audio_handler
    
    def display_message(self, message: Message):
        """Display a complete message with potential video (text-only)."""
        avatar = "🦍" if message.is_assistant() else None
        
        with self.st.chat_message(message.role, avatar=avatar):
            # Show message text only; video is displayed via display_video to avoid duplication
            self.st.markdown(message.content)
    
    def display_user_message(self, message: Message):
        """Display user message immediately."""
        with self.st.chat_message("user"):
            self.st.markdown(message.content)
    
    def show_spinner(self, text: str):
        """Return spinner context manager."""
        return self.st.spinner(text)
    
    def play_audio(self, audio_bytes: bytes):
        """Play audio using autoplay."""
        self.audio_handler.autoplay_audio(
            audio_bytes,
            lambda html: self.st.markdown(html, unsafe_allow_html=True)
        )
    
    def display_video(self, video_path: str):
        """Display video player with download button (unique download key)."""
        # Display the video
        self.st.video(video_path)
        
        # Read bytes for download
        try:
            with open(video_path, 'rb') as f:
                video_bytes = f.read()
        except Exception:
            self.show_error("Could not read generated video for download.")
            return
        
        # Use UUID to ensure unique widget key across reruns/calls
        unique_key = f"download_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
        
        self.st.download_button(
            label="⬇️ Download Video",
            data=video_bytes,
            file_name=f"gorilla_video_{int(time.time())}.mp4",
            mime="video/mp4",
            key=unique_key
        )
    
    def show_success(self, message: str):
        """Show success message."""
        self.st.success(message)
    
    def show_error(self, message: str):
        """Show error message."""
        self.st.error(message)
    
    def show_code(self, code: str):
        """Display code in expander."""
        with self.st.expander("Error Details"):
            self.st.code(code)


# ============================================================================
# APPLICATION FACADE (Simplified Entry Point)
# ============================================================================

class GorillaStudioApp:
    """
    Facade for the entire application.
    Simplifies initialization and coordinates all components.
    """
    
    def __init__(self, st_module):
        self.st = st_module
        self._setup_page_config()
        self._apply_custom_styling()
        self._initialize_components()
    
    def _setup_page_config(self):
        """Configure Streamlit page settings."""
        self.st.set_page_config(
            page_title="Gorilla Studios AI",
            page_icon="🦍",
            layout="wide",
            initial_sidebar_state="auto",
        )
    
    def _apply_custom_styling(self):
        """Apply custom CSS."""
        self.st.markdown("""
        <style>
            .stChatInput textarea::placeholder {
                color: rgba(0, 0, 0, 0.35);
                opacity: 1;
            }
            [data-theme="dark"] .stChatInput textarea::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
            .stSlider > label {
                font-weight: 600;
            }
        </style>
        """, unsafe_allow_html=True)
        UI_tools.setUp_CSS(self.st)
    
    def _initialize_components(self):
        """Initialize all application components.""" 
        # Repositories
        self.message_repo = MessageRepository(self.st.session_state)
        self.config_repo = ConfigRepository(self.st.session_state)
        
        # Handlers
        if "audio_handler" not in self.st.session_state:
            self.st.session_state.audio_handler = Audio()
        
        if "video_handler" not in self.st.session_state:
            self.st.session_state.video_handler = VideoGenerator(
                base_video_path="base_video.mp4"
            )
        
        # Service
        self.content_service = ContentGenerationService(
            crew_executor=run_crew,
            audio_handler=self.st.session_state.audio_handler,
            video_generator=self.st.session_state.video_handler
        )
        
        # View
        self.view = StreamlitChatView(
            self.st,
            self.st.session_state.audio_handler
        )
        
        # Presenter
        self.presenter = ChatPresenter(
            self.message_repo,
            self.config_repo,
            self.content_service,
            self.view
        )
    
    def render_sidebar(self):
        """Render sidebar with settings.""" 
        with self.st.sidebar:
            self.st.title("🦍 Gorilla Engine")
            self.st.markdown("### Content Generation Suite")
            self.st.markdown("---")
            
            self.st.caption("Manage Conversation")
            self.st.button(
                "🗑️ Clear Chat",
                on_click=lambda: self.presenter.clear_conversation(),
                use_container_width=True
            )
            self.st.markdown("---")
            
            self.st.header("⚙️ Settings")
            
            # TTS Settings
            enabled = self.st.checkbox(
                "Enable Text-to-Speech",
                value=self.config_repo.get_tts_config().enabled
            )
            self.config_repo.update_tts_enabled(enabled)
            
            UI_tools.sidebar_audio_tester(self.st, Audio)
            UI_tools.sidebar_video_settings(self.st)
    
    def render_welcome_screen(self):
        """Render welcome screen for new conversations.""" 
        UI_tools.circular_image(bs64, self.st)
        
        self.st.markdown("""
            <div class="welcome-container">
                <h1>🦍 Welcome to Gorilla Studios</h1>
                <p>Your personal content generation assistant. Enter a topic to get started!</p>
            </div>
        """, unsafe_allow_html=True)
        
        UI_tools.display_quick_start_prompts(self.st)
    
    def run(self):
        """Main application loop.""" 
        self.render_sidebar()
        
        # Handle quick start prompts
        if "user_prompt" in self.st.session_state:
            prompt = self.st.session_state.user_prompt
            del self.st.session_state.user_prompt
            self.presenter.process_user_input(prompt)
            self.st.rerun()
        
        # Display conversation or welcome screen
        if not self.message_repo.has_messages():
            self.render_welcome_screen()
        else:
            self.presenter.display_conversation_history()
        
        # Handle user input
        if prompt := self.st.chat_input("ask anything"):
            self.presenter.process_user_input(prompt)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Application entry point.""" 
    app = GorillaStudioApp(st)
    app.run()


if __name__ == "__main__":
    main()