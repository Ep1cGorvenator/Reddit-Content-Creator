"""
Audio processing module with TTS capabilities.
Refactored to follow SOLID principles and Strategy pattern.
Supports both gTTS and Coqui TTS providers.
"""

import base64
import io
import tempfile
import os
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Callable
from gtts import gTTS

# Coqui TTS (optional)
try:
    from TTS.api import TTS
    import torch
    import soundfile as sf
    import scipy.signal
    
    # Monkey patch to use soundfile instead of torchaudio (avoids torchcodec issues)
    def load_audio_with_soundfile(audiopath, sr=None):
        """Load audio using soundfile instead of torchaudio"""
        audio_data, sample_rate = sf.read(audiopath)
        
        # Resample if needed
        if sr is not None and sr != sample_rate:
            num_samples = int(len(audio_data) * sr / sample_rate)
            audio_data = scipy.signal.resample(audio_data, num_samples)
            sample_rate = sr
        
        # Convert to torch tensor
        audio = torch.FloatTensor(audio_data)
        
        # Ensure correct shape (channels, samples)
        if len(audio.shape) == 1:
            audio = audio.unsqueeze(0)
        elif len(audio.shape) == 2:
            if audio.shape[0] > audio.shape[1]:
                audio = audio.T
            audio = audio.mean(dim=0, keepdim=True)
        
        return audio
    
    # Patch XTTS load_audio function
    import TTS.tts.models.xtts as xtts_module
    xtts_module.load_audio = load_audio_with_soundfile
    
    _HAS_COQUI = True
except Exception:
    _HAS_COQUI = False
    TTS = None

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


class CoquiTTSProvider(TTSProvider):
    """Coqui TTS provider implementation with GPU support and voice cloning."""
    
    COQUI_MODEL_MAP = {
        "Coqui - Voice Clone (GPU, best quality)": "tts_models/multilingual/multi-dataset/xtts_v2",
        "Coqui - LJSpeech (CPU, fast)": "tts_models/en/ljspeech/tacotron2-DDC",
        "Coqui - GlowTTS (CPU, natural)": "tts_models/en/ljspeech/glow-tts",
    }
    
    def __init__(self, prefer_gpu: bool = True, speaker_wav: str = "Benit.wav", 
                 feedback_adapter: Optional['FeedbackAdapter'] = None):
        """
        Initialize Coqui TTS provider.
        
        Args:
            prefer_gpu: If True, use CUDA for models
            speaker_wav: Path to WAV file for voice cloning
            feedback_adapter: Optional feedback adapter for user notifications
        """
        if not _HAS_COQUI:
            raise ImportError("Coqui TTS not available. Install with: pip install TTS torch soundfile scipy")
        
        self.prefer_gpu = prefer_gpu
        self.speaker_wav = speaker_wav
        self.feedback_adapter = feedback_adapter
        self.model_cache = {}  # model_name -> TTS instance
        self.audio_cache = {}  # cache_key -> audio bytes
        
        # Check if speaker file exists
        if speaker_wav and not os.path.exists(speaker_wav):
            if self.feedback_adapter:
                self.feedback_adapter.show_warning(
                    f"⚠️ Speaker file '{speaker_wav}' not found. Voice cloning will be disabled."
                )
            self.speaker_wav = None
    
    def generate_speech(self, text: str, voice_config: dict) -> Optional[bytes]:
        """
        Generate speech using Coqui TTS.
        
        Args:
            text: Text to convert to speech
            voice_config: Dictionary with 'name' key for voice/model selection
            
        Returns:
            Audio bytes or None on failure
        """
        try:
            voice_name = voice_config.get('name', 'Coqui - Voice Clone (GPU, best quality)')
            model_name = self.COQUI_MODEL_MAP.get(voice_name)
            
            if not model_name:
                raise TTSGenerationError(f"Unknown Coqui model: {voice_name}")
            
            # Check cache
            cache_key = self._hash_text(text, model_name)
            if cache_key in self.audio_cache:
                return self.audio_cache[cache_key]
            
            # Load model
            tts = self._load_model(model_name)
            if tts is None:
                return None
            
            # Generate audio to temp file
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_path = tmp.name
            tmp.close()
            
            try:
                # Check if this is XTTS (voice cloning model)
                is_xtts = "xtts" in model_name.lower()
                
                if is_xtts and self.speaker_wav:
                    # Voice cloning with speaker file
                    if self.feedback_adapter:
                        self.feedback_adapter.show_success("🎤 Using voice cloning from speaker file...")
                    tts.tts_to_file(
                        text=text,
                        file_path=tmp_path,
                        speaker_wav=self.speaker_wav,
                        language="en"
                    )
                else:
                    # Standard TTS without cloning
                    tts.tts_to_file(text=text, file_path=tmp_path)
                
                # Read generated audio
                with open(tmp_path, "rb") as f:
                    audio_bytes = f.read()
                
                # Cache it
                self.audio_cache[cache_key] = audio_bytes
                return audio_bytes
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                        
        except Exception as e:
            raise TTSGenerationError(f"Coqui generation failed: {str(e)}") from e
    
    def get_available_voices(self) -> Dict[str, dict]:
        """Return available Coqui models."""
        return {
            name: {"model_path": path}
            for name, path in self.COQUI_MODEL_MAP.items()
        }
    
    def _load_model(self, model_name: str):
        """Load and cache Coqui TTS model."""
        # Return cached if already loaded
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        try:
            # Show loading message if feedback available
            if self.feedback_adapter and _HAS_STREAMLIT:
                with st.spinner(f"🔥 Loading {model_name.split('/')[-1]}..."):
                    tts = TTS(model_name)
            else:
                tts = TTS(model_name)
            
            # Move to GPU if available and preferred
            if self.prefer_gpu and hasattr(tts, "to"):
                try:
                    if torch.cuda.is_available():
                        tts = tts.to("cuda")
                        if self.feedback_adapter:
                            gpu_name = torch.cuda.get_device_name(0)
                            self.feedback_adapter.show_success(f"✅ Model loaded on GPU: {gpu_name}")
                    else:
                        if self.feedback_adapter:
                            self.feedback_adapter.show_warning("ℹ️ CUDA not available, using CPU (slower)")
                except Exception as e:
                    if self.feedback_adapter:
                        self.feedback_adapter.show_warning(f"⚠️ Could not move to GPU: {e}. Using CPU.")
            
            # Cache the model
            self.model_cache[model_name] = tts
            return tts
            
        except Exception as e:
            if self.feedback_adapter:
                self.feedback_adapter.show_error(f"❌ Failed to load Coqui model: {e}")
            return None
    
    @staticmethod
    def _hash_text(text: str, model_name: str) -> str:
        """Generate cache key from text and model."""
        h = hashlib.sha256()
        h.update((model_name or "none").encode())
        h.update(text.encode("utf-8"))
        return h.hexdigest()


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
    Supports both gTTS and Coqui TTS providers.
    """
    
    def __init__(
        self,
        max_length: int = 4000,
        tts_provider: Optional[TTSProvider] = None,
        feedback_adapter: Optional[FeedbackAdapter] = None,
        prefer_gpu: bool = True,
        speaker_wav: str = "Benit.wav"
    ):
        """
        Initialize Audio handler.
        
        Args:
            max_length: Maximum text length for TTS (default: 4000)
            tts_provider: TTS provider instance (defaults to GTTSProvider)
            feedback_adapter: Feedback adapter (defaults to StreamlitFeedbackAdapter if st available)
            prefer_gpu: If True, use CUDA for Coqui models (default: True)
            speaker_wav: Path to WAV file for voice cloning (default: "Benit.wav")
        """
        self.max_length = max_length
        self.prefer_gpu = prefer_gpu
        self.speaker_wav = speaker_wav
        
        # default to Streamlit feedback when available
        if feedback_adapter is None:
            self.feedback_adapter = StreamlitFeedbackAdapter(st) if _HAS_STREAMLIT else SilentFeedbackAdapter()
        else:
            self.feedback_adapter = feedback_adapter
        
        # Initialize providers
        self.gtts_provider = GTTSProvider()
        self.coqui_provider = None
        if _HAS_COQUI:
            try:
                self.coqui_provider = CoquiTTSProvider(
                    prefer_gpu=prefer_gpu,
                    speaker_wav=speaker_wav,
                    feedback_adapter=self.feedback_adapter
                )
            except ImportError:
                pass
        
        # Use provided provider or default to gTTS
        self.tts_provider = tts_provider or self.gtts_provider
        self.text_processor = TextProcessor()
    
    def text_to_speech(self, text: str, voice_name: str = "Charon") -> Optional[bytes]:
        """
        Convert text to speech with error handling and feedback.
        
        Args:
            text: Text to convert to speech
            voice_name: Voice identifier (supports both gTTS and Coqui voices)
            
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
            
            # Route to appropriate provider
            provider = self._select_provider(voice_name)
            
            # Generate audio
            audio_bytes = provider.generate_speech(
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
    
    def _select_provider(self, voice_name: str) -> TTSProvider:
        """Select the appropriate TTS provider based on voice name."""
        # Check if it's a Coqui voice
        if self.coqui_provider and voice_name in CoquiTTSProvider.COQUI_MODEL_MAP:
            return self.coqui_provider
        # Default to gTTS
        return self.gtts_provider
    
    def autoplay_audio(self, audio_bytes: bytes, render_func: Callable[[str], None] = None):
        """
        Create HTML audio player for autoplay or use Streamlit's native audio player.
        
        Args:
            audio_bytes: Audio data to play
            render_func: Function to render HTML (e.g., st.markdown). If None and Streamlit is available,
                         will use st.audio for better compatibility
        """
        if not audio_bytes or len(audio_bytes) == 0:
            self.feedback_adapter.show_warning("No audio data to play")
            return
        
        if render_func is not None:
            # Custom render function provided
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio controls autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            """
            render_func(audio_html)
        elif _HAS_STREAMLIT:
            # Use Streamlit's native audio player (better compatibility)
            # Detect format by header
            if audio_bytes[:4] == b"RIFF":
                st.audio(audio_bytes, format="audio/wav")
            else:
                st.audio(audio_bytes, format="audio/mp3")
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
        show_spinner: bool = True
    ):
        """
        Convenience method to clean, generate, and play audio.
        
        Args:
            text: Text to convert and play
            voice_name: Voice to use (supports both gTTS and Coqui voices)
            render_func: Function to render HTML player (defaults to Streamlit renderer if available)
            show_spinner: Whether to show a spinner during generation (default: True)
        """
        def _process():
            clean_text = self.clean_text_for_speech(text)
            audio_bytes = self.text_to_speech(clean_text, voice_name)
            if audio_bytes:
                self.autoplay_audio(audio_bytes, render_func)
        
        if show_spinner and _HAS_STREAMLIT:
            with st.spinner("🎤 Generating audio..."):
                _process()
        else:
            _process()
    
    @classmethod
    def get_available_voices(cls) -> list:
        """
        Get list of all available voice names (gTTS + Coqui if available).
        Can be called without instantiating Audio class.
        
        Returns:
            List of voice identifiers
        """
        voices = list(GTTSProvider.VOICE_MAPPING.keys())
        if _HAS_COQUI:
            voices += list(CoquiTTSProvider.COQUI_MODEL_MAP.keys())
        return voices