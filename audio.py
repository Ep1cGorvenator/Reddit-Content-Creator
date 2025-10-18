"""
Audio processing module with TTS capabilities.
Refactored to follow SOLID principles and Strategy pattern.
"""

import base64
import io
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Callable
from gtts import gTTS

# detect streamlit if available
try:
    import streamlit as st
    _HAS_STREAMLIT = True
except Exception:
    _HAS_STREAMLIT = False


# ============================================================================
# STRATEGY PATTERN: TTS Provider Interface
# ============================================================================

class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""
    
    @abstractmethod
    def generate_speech(self, text: str, voice_config: dict) -> Optional[bytes]:
        """Generate speech from text using provider-specific implementation."""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> Dict[str, dict]:
        """Return available voices for this provider."""
        pass


class GTTSProvider(TTSProvider):
    """Google Text-to-Speech provider implementation."""
    
    VOICE_MAPPING = {
        "Puck": ("en", "com.au"),      # Australian English
        "Charon": ("en", "co.uk"),     # British English
        "Kore": ("en", "us"),          # US English
        "Fenrir": ("en", "ca"),        # Canadian English
        "Aoede": ("en", "co.in")       # Indian English
    }
    
    def generate_speech(self, text: str, voice_config: dict) -> Optional[bytes]:
        """
        Generate speech using gTTS.
        
        Args:
            text: Text to convert to speech
            voice_config: Dictionary with 'name' key for voice selection
            
        Returns:
            Audio bytes or None on failure
        """
        try:
            voice_name = voice_config.get('name', 'Charon')
            lang, tld = self.VOICE_MAPPING.get(voice_name, ("en", "us"))
            
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
            
        except Exception as e:
            raise TTSGenerationError(f"gTTS generation failed: {str(e)}") from e
    
    def get_available_voices(self) -> Dict[str, dict]:
        """Return available gTTS voices."""
        return {
            name: {"lang": lang, "tld": tld}
            for name, (lang, tld) in self.VOICE_MAPPING.items()
        }


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class TTSGenerationError(Exception):
    """Raised when TTS generation fails."""
    pass


class TextTooLongError(Exception):
    """Raised when text exceeds maximum length."""
    pass


# ============================================================================
# ADAPTER PATTERN: Feedback Interface (decouples from Streamlit)
# ============================================================================

class FeedbackAdapter(ABC):
    """Abstract interface for user feedback (UI agnostic)."""
    
    @abstractmethod
    def show_warning(self, message: str):
        """Display warning message."""
        pass
    
    @abstractmethod
    def show_success(self, message: str):
        """Display success message."""
        pass
    
    @abstractmethod
    def show_error(self, message: str):
        """Display error message."""
        pass


class StreamlitFeedbackAdapter(FeedbackAdapter):
    """Streamlit-specific feedback implementation."""
    
    def __init__(self, st_module):
        self.st = st_module
    
    def show_warning(self, message: str):
        self.st.warning(message)
    
    def show_success(self, message: str):
        self.st.success(message)
    
    def show_error(self, message: str):
        self.st.error(message)


class SilentFeedbackAdapter(FeedbackAdapter):
    """No-op feedback for testing or non-UI contexts."""
    
    def show_warning(self, message: str):
        pass
    
    def show_success(self, message: str):
        pass
    
    def show_error(self, message: str):
        pass


# ============================================================================
# TEXT PROCESSING UTILITY (Pure Function)
# ============================================================================

class TextProcessor:
    """Utility class for text cleaning and processing."""
    
    @staticmethod
    def clean_for_speech(text: str) -> str:
        """
        Remove markdown formatting for cleaner TTS output.
        
        Args:
            text: Raw text with potential markdown
            
        Returns:
            Cleaned text suitable for speech synthesis
        """
        # Remove markdown formatting
        clean_text = (text
                     .replace("#", "")
                     .replace("*", "")
                     .replace("-", "")
                     .replace("`", ""))
        
        # Normalize whitespace
        return " ".join(clean_text.split())
    
    @staticmethod
    def truncate(text: str, max_length: int) -> Tuple[str, bool]:
        """
        Truncate text to maximum length if needed.
        
        Args:
            text: Text to truncate
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        if len(text) <= max_length:
            return text, False
        return text[:max_length] + "...", True


# ============================================================================
# MAIN AUDIO HANDLER (Facade Pattern)
# ============================================================================

class Audio:
    """
    Facade for text-to-speech functionality.
    Handles TTS generation with configurable providers and feedback.
    """
    
    def __init__(
        self,
        max_length: int = 4000,
        tts_provider: Optional[TTSProvider] = None,
        feedback_adapter: Optional[FeedbackAdapter] = None
    ):
        """
        Initialize Audio handler.
        
        Args:
            max_length: Maximum text length for TTS (default: 4000)
            tts_provider: TTS provider instance (defaults to GTTSProvider)
            feedback_adapter: Feedback adapter (defaults to StreamlitFeedbackAdapter if st available, else SilentFeedbackAdapter)
        """
        self.max_length = max_length
        self.tts_provider = tts_provider or GTTSProvider()
        # default to Streamlit feedback when available so users see warnings/success in UI
        if feedback_adapter is None:
            self.feedback_adapter = StreamlitFeedbackAdapter(st) if _HAS_STREAMLIT else SilentFeedbackAdapter()
        else:
            self.feedback_adapter = feedback_adapter
        self.text_processor = TextProcessor()
    
    def text_to_speech(self, text: str, voice_name: str = "Charon") -> Optional[bytes]:
        """
        Convert text to speech with error handling and feedback.
        
        Args:
            text: Text to convert to speech
            voice_name: Voice identifier
            
        Returns:
            Audio bytes if successful, None otherwise
        """
        try:
            # Truncate if necessary
            truncated_text, was_truncated = self.text_processor.truncate(text, self.max_length)
            if was_truncated:
                self.feedback_adapter.show_warning(
                    f"⚠️ Text truncated to {self.max_length} characters"
                )
            
            # Generate audio
            audio_bytes = self.tts_provider.generate_speech(
                truncated_text,
                {'name': voice_name}
            )
            
            if audio_bytes:
                self.feedback_adapter.show_success(
                    f"✅ Audio generated: {len(audio_bytes)} bytes"
                )
            
            return audio_bytes
            
        except TTSGenerationError as e:
            self.feedback_adapter.show_error(f"TTS Error: {str(e)}")
            return None
        except Exception as e:
            self.feedback_adapter.show_error(f"Unexpected error: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Log for debugging
            return None
    
    def autoplay_audio(self, audio_bytes: bytes, render_func: Callable[[str], None] = None):
        """
        Create HTML audio player for autoplay.
        
        Args:
            audio_bytes: Audio data to play
            render_func: Function to render HTML (e.g., st.markdown). If None and Streamlit is available,
                         will default to st.markdown(..., unsafe_allow_html=True)
        """
        if not audio_bytes or len(audio_bytes) == 0:
            self.feedback_adapter.show_warning("No audio data to play")
            return
        
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        """
        if render_func is not None:
            render_func(audio_html)
        elif _HAS_STREAMLIT:
            # default rendering for Streamlit
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            # fallback: no renderer available
            self.feedback_adapter.show_warning("No renderer provided to display audio.")
    
    def clean_text_for_speech(self, text: str) -> str:
        """
        Public wrapper for text cleaning.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        return self.text_processor.clean_for_speech(text)
    
    def generate_and_play(
        self,
        text: str,
        voice_name: str = "Charon",
        render_func: Callable[[str], None] = None,
        spinner_func: Callable = None
    ):
        """
        Convenience method to clean, generate, and play audio.
        
        Args:
            text: Text to convert and play
            voice_name: Voice to use
            render_func: Function to render HTML player (defaults to Streamlit renderer if available)
            spinner_func: Optional spinner context manager factory (e.g., st.spinner)
        """
        # if no render_func provided, default to streamlit renderer when possible
        if render_func is None and _HAS_STREAMLIT:
            render_func = lambda html: st.markdown(html, unsafe_allow_html=True)
        
        def _process():
            clean_text = self.clean_text_for_speech(text)
            audio_bytes = self.text_to_speech(clean_text, voice_name)
            if audio_bytes:
                self.autoplay_audio(audio_bytes, render_func)
        
        if spinner_func and _HAS_STREAMLIT:
            with spinner_func("Generating audio..."):
                _process()
        else:
            _process()
    
    @classmethod
    def get_available_voices(cls) -> list:
        """
        Get list of available voice names.
        Can be called without instantiating Audio class.
        
        Returns:
            List of voice identifiers
        """
        provider = GTTSProvider()
        return list(provider.get_available_voices().keys())