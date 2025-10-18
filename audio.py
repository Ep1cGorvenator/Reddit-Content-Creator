# audio.py
import streamlit as st
import base64
import io
import tempfile
import os
import hashlib
from typing import Optional
import torch
import soundfile as sf

# existing gTTS fallback
from gtts import gTTS

# Coqui TTS (optional; will raise nicely if not installed)
try:
    from TTS.api import TTS
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
    
    COQUI_AVAILABLE = True
except Exception as e:
    COQUI_AVAILABLE = False
    TTS = None

class Audio:
    """
    Audio handler supporting:
      - gTTS fallback voices (fast, simple)
      - Coqui TTS models (GPU/CPU, high quality with voice cloning)
    """

    # gTTS mapping (your existing voices)
    VOICE_MAPPING = {
        "Puck": ("en", "com.au"),      # Australian English
        "Charon": ("en", "co.uk"),     # British English
        "Kore": ("en", "us"),          # US English
        "Fenrir": ("en", "ca"),        # Canadian English
        "Aoede": ("en", "co.in")       # Indian English
    }

    # Coqui voice models
    COQUI_MODEL_MAP = {
        "Coqui - Voice Clone (GPU, best quality)": "tts_models/multilingual/multi-dataset/xtts_v2",
        "Coqui - LJSpeech (CPU, fast)": "tts_models/en/ljspeech/tacotron2-DDC",
        "Coqui - GlowTTS (CPU, natural)": "tts_models/en/ljspeech/glow-tts",
    }

    def __init__(self, max_length: int = 4000, prefer_gpu: bool = True, speaker_wav: str = "Benit.wav"):
        """
        prefer_gpu: if True, use CUDA for Coqui models
        speaker_wav: path to WAV file for voice cloning (used with XTTS-v2)
        """
        self.max_length = max_length
        self.prefer_gpu = prefer_gpu
        self.speaker_wav = speaker_wav
        self.coqui_models = {}   # model_name -> TTS instance
        self.cache = {}          # simple in-memory cache
        
        # Check if speaker file exists
        if not os.path.exists(self.speaker_wav):
            st.warning(f"⚠️ Speaker file '{self.speaker_wav}' not found. Voice cloning will be disabled.")
            self.speaker_wav = None

    @staticmethod
    def get_available_voices():
        """Return list of all available voices"""
        voices = list(Audio.VOICE_MAPPING.keys())
        if COQUI_AVAILABLE:
            voices += list(Audio.COQUI_MODEL_MAP.keys())
        return voices

    def generate_and_play(self, text: str, voice_name: str = "Charon", show_spinner: bool = True):
        """Clean text, synthesize, and play inside Streamlit"""
        def _work():
            clean_text = self.clean_text_for_speech(text)
            
            # Route to Coqui if voice_name is a Coqui model
            if voice_name in self.COQUI_MODEL_MAP:
                audio_bytes = self._synthesize_coqui(clean_text, voice_name)
            else:
                audio_bytes = self._synthesize_gtts(clean_text, voice_name)

            if audio_bytes:
                self._play_audio_bytes(audio_bytes)

        if show_spinner:
            with st.spinner("🎤 Generating audio..."):
                _work()
        else:
            _work()

    def clean_text_for_speech(self, text: str) -> str:
        """Remove markdown and limit length"""
        clean_text = text.replace("#", "").replace("*", "").replace("-", "").replace("`", "")
        clean_text = " ".join(clean_text.split())
        if len(clean_text) > self.max_length:
            clean_text = clean_text[: self.max_length] + "..."
            st.warning(f"⚠️ Text truncated to {self.max_length} characters for TTS")
        return clean_text

    def _synthesize_gtts(self, text: str, voice_name: str) -> Optional[bytes]:
        """Generate audio using gTTS (fast, simple)"""
        try:
            lang, tld = self.VOICE_MAPPING.get(voice_name, ("en", "us"))
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            st.error(f"gTTS Error: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None

    def _synthesize_coqui(self, text: str, friendly_voice: str) -> Optional[bytes]:
        """Generate audio using Coqui TTS (GPU-accelerated, high quality)"""
        if not COQUI_AVAILABLE:
            st.error("⚠️ Coqui TTS not available. Install with: pip install TTS torch soundfile scipy")
            return None

        model_name = self.COQUI_MODEL_MAP.get(friendly_voice)
        if not model_name:
            st.error("Unknown Coqui model.")
            return None

        # Check cache
        cache_key = self._hash_text(text, model_name)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Load model
        tts = self._load_coqui_model(model_name)
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
                st.info("🎤 Using voice cloning from speaker file...")
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
            self.cache[cache_key] = audio_bytes
            return audio_bytes
            
        except Exception as e:
            st.error(f"❌ Coqui synthesis error: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _play_audio_bytes(self, audio_bytes: bytes):
        """Play audio in Streamlit"""
        # Detect format by header
        if audio_bytes[:4] == b"RIFF":
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.audio(audio_bytes, format="audio/mp3")

    def _load_coqui_model(self, model_name: str):
        """Load and cache Coqui TTS model"""
        # Return cached if already loaded
        if model_name in self.coqui_models:
            return self.coqui_models[model_name]

        try:
            # Load model
            with st.spinner(f"📥 Loading {model_name.split('/')[-1]}..."):
                tts = TTS(model_name)
            
            # Move to GPU if available and preferred
            if self.prefer_gpu and hasattr(tts, "to"):
                try:
                    if torch.cuda.is_available():
                        tts = tts.to("cuda")
                        gpu_name = torch.cuda.get_device_name(0)
                        st.success(f"✅ Model loaded on GPU: {gpu_name}")
                    else:
                        st.info("ℹ️ CUDA not available, using CPU (slower)")
                except Exception as e:
                    st.warning(f"⚠️ Could not move to GPU: {e}. Using CPU.")
            
            # Cache the model
            self.coqui_models[model_name] = tts
            return tts
            
        except Exception as e:
            st.error(f"❌ Failed to load Coqui model: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None

    @staticmethod
    def _hash_text(text: str, model_name: str) -> str:
        """Generate cache key from text and model"""
        h = hashlib.sha256()
        h.update((model_name or "none").encode())
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    # Backward compatibility methods
    def text_to_speech(self, text: str, voice_name: str = "Charon") -> Optional[bytes]:
        """Generate audio and return bytes (for video generation)"""
        clean_text = self.clean_text_for_speech(text)
        
        if voice_name in self.COQUI_MODEL_MAP:
            return self._synthesize_coqui(clean_text, voice_name)
        else:
            return self._synthesize_gtts(clean_text, voice_name)
    
    def autoplay_audio(self, audio_bytes: bytes):
        """Auto-play audio (uses st.audio)"""
        self._play_audio_bytes(audio_bytes)