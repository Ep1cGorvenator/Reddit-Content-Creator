import streamlit as st
import base64
from gtts import gTTS
import io


class Audio:
    """
    Handles text-to-speech functionality using gTTS.
    """
    
    # Voice mapping for different accents
    VOICE_MAPPING = {
        "Puck": ("en", "com.au"),      # Australian English
        "Charon": ("en", "co.uk"),     # British English
        "Kore": ("en", "us"),          # US English
        "Fenrir": ("en", "ca"),        # Canadian English
        "Aoede": ("en", "co.in")       # Indian English
    }
    
    def __init__(self, max_length: int = 4000):
        """
        Initialize the Audio handler.
        
        Args:
            max_length: Maximum text length for TTS (default: 4000)
        """
        self.max_length = max_length
    
    def text_to_speech(self, text: str, voice_name: str = "Puck") -> bytes:
        """
        Converts text to speech using gTTS (Google Text-to-Speech - free).
        
        Args:
            text: The text to convert to speech
            voice_name: The voice/accent to use (default: "Puck")
        
        Returns:
            Audio bytes if successful, None otherwise
        """
        try:
            # Truncate text if too long
            if len(text) > self.max_length:
                text = text[:self.max_length] + "..."
                st.warning(f"⚠️ Text truncated to {self.max_length} characters")
            
            # Get language and TLD for the selected voice
            lang, tld = self.VOICE_MAPPING.get(voice_name, ("en", "us"))
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            
            # Save to BytesIO object instead of file
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            
            st.success(f"✅ Audio generated: {len(audio_bytes)} bytes")
            return audio_bytes
        
        except Exception as e:
            st.error(f"TTS Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def autoplay_audio(self, audio_bytes: bytes):
        """
        Creates an audio player that autoplays the generated speech.
        
        Args:
            audio_bytes: The audio data to play
        """
        if audio_bytes and len(audio_bytes) > 0:
            b64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
                <audio controls autoplay>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.warning("No audio data to play")
    
    def clean_text_for_speech(self, text: str) -> str:
        """
        Strip markdown formatting for cleaner speech.
        
        Args:
            text: The text to clean
        
        Returns:
            Cleaned text suitable for TTS
        """
        # Remove markdown formatting
        clean_text = text.replace("#", "").replace("*", "").replace("-", "").replace("`", "")
        
        # Remove extra whitespace
        clean_text = " ".join(clean_text.split())
        
        return clean_text
    
    #MAIN METHOD TO GENERATE AND PLAY AUDIO
    def generate_and_play(self, text: str, voice_name: str = "Puck", show_spinner: bool = True):
        """
        Convenience method to clean text, generate audio, and play it.
        
        Args:
            text: The text to convert and play
            voice_name: The voice/accent to use
            show_spinner: Whether to show a loading spinner
        """
        def _process():
            clean_text = self.clean_text_for_speech(text)
            audio_bytes = self.text_to_speech(clean_text, voice_name)
            if audio_bytes:
                self.autoplay_audio(audio_bytes)
        
        if show_spinner:
            with st.spinner("Generating audio..."):
                _process()
        else:
            _process()
    
    @staticmethod
    def get_available_voices():
        """
        Get list of available voice names.
        
        Returns:
            List of voice names
        """
        return list(Audio.VOICE_MAPPING.keys())
    
    def test_audio(self):
        """
        Interactive test interface for audio functionality.
        Displays controls to test TTS without needing to generate content.
        """
        st.subheader("🎙️ Audio Tester")
        
        # Test text input
        test_text = st.text_area(
            "Enter test text:",
            value="Hello! This is a test of the text-to-speech system. How does it sound?",
            height=100,
            help="Enter any text to test the audio generation"
        )
        
        # Voice selection
        col1, col2 = st.columns(2)
        
        with col1:
            test_voice = st.selectbox(
                "Select Voice:",
                options=self.get_available_voices(),
                help="Choose a voice/accent for testing"
            )
        
        with col2:
            # Display voice info
            lang, tld = self.VOICE_MAPPING.get(test_voice, ("en", "us"))
            accent_names = {
                "com.au": "Australian",
                "co.uk": "British",
                "us": "American",
                "ca": "Canadian",
                "co.in": "Indian"
            }
            st.info(f"🌍 {accent_names.get(tld, 'English')} accent")
        
        # Generate button
        if st.button("🔊 Generate & Play Audio", type="primary"):
            if test_text.strip():
                self.generate_and_play(test_text, test_voice)
            else:
                st.warning("⚠️ Please enter some text to test")
        
        # Quick test buttons
        st.markdown("---")
        st.write("**Quick Tests:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Test Short"):
                self.generate_and_play("This is a short test.", test_voice)
        
        with col2:
            if st.button("Test Medium"):
                self.generate_and_play(
                    "This is a medium length test. It contains multiple sentences to demonstrate how the voice sounds with more content.",
                    test_voice
                )
        
        with col3:
            if st.button("Test Long"):
                long_text = """
                This is a longer test of the text-to-speech system. 
                It includes multiple sentences and different punctuation marks!
                Does it handle questions properly? And what about exclamations!
                Let's also test some numbers like 123 and 456.
                Finally, we'll end with a simple statement.
                """
                self.generate_and_play(long_text, test_voice)


# Example usage and test function
def main():
    """Main function to run the audio tester."""
    st.set_page_config(
        page_title="Audio Tester",
        page_icon="🎙️",
        layout="centered"
    )
    
    st.title("🎙️ Text-to-Speech Audio Tester")
    st.markdown("Test the audio functionality without generating content.")
    st.markdown("---")
    
    # Initialize Audio handler
    audio = Audio()
    
    # Run the tester
    audio.test_audio()


if __name__ == "__main__":
    main()