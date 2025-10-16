from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import tempfile
import os
import re
import io


class VideoGenerator:
    """
    Handles video generation with audio overlay and subtitles.
    Designed to work with pre-generated audio from the Audio class.
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def generate_subtitles_from_text(self, text: str, duration: float, words_per_second: float = 2.5):
        """
        Generate subtitle segments from text based on estimated timing.
        
        Args:
            text: The text to convert to subtitles
            duration: Total duration of the audio in seconds
            words_per_second: Average speaking rate (default: 2.5 words/sec)
        
        Returns:
            List of tuples: [(start_time, end_time, text), ...]
        """
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # Calculate timing for each sentence
        total_words = sum(len(sentence.split()) for sentence in sentences)
        
        subtitles = []
        current_time = 0.0
        
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            
            # Calculate duration for this sentence
            sentence_duration = (words_in_sentence / words_per_second)
            end_time = min(current_time + sentence_duration, duration)
            
            if current_time < duration:
                subtitles.append((current_time, end_time, sentence))
            
            current_time = end_time
        
        return subtitles
    
    def create_subtitle_clip(self, subtitle_text: str, start: float, end: float, 
                           video_size: tuple, font_size: int = 40):
        """
        Create a single subtitle text clip.
        
        Args:
            subtitle_text: The text to display
            start: Start time in seconds
            end: End time in seconds
            video_size: (width, height) of the video
            font_size: Size of the subtitle font
        
        Returns:
            TextClip object
        """
        txt_clip = TextClip(
            subtitle_text,
            fontsize=font_size,
            color='white',
            bg_color='black',
            font='Arial-Bold',
            size=(video_size[0] - 100, None),  # Padding on sides
            method='caption'
        ).set_start(start).set_end(end).set_position(('center', 'bottom'))
        
        return txt_clip
    
    def generate_video_from_audio(self, video_path: str, audio_bytes: bytes, 
                                  text: str, output_path: str = None, 
                                  add_subtitles: bool = True):
        """
        Generate video with pre-generated audio overlay and subtitles.
        
        Args:
            video_path: Path to the input video file
            audio_bytes: Pre-generated audio data (bytes)
            text: Original text for subtitle generation
            output_path: Path for output video (optional)
            add_subtitles: Whether to add subtitles
        
        Returns:
            Path to the generated video file
        """
        try:
            # Save audio bytes to temporary file
            audio_temp_path = os.path.join(self.temp_dir, f"temp_audio_{os.getpid()}.mp3")
            with open(audio_temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Load video and audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_temp_path)
            
            # Adjust video duration to match audio
            audio_duration = audio_clip.duration
            if video_clip.duration < audio_duration:
                # Loop video if it's shorter than audio
                video_clip = video_clip.loop(duration=audio_duration)
            else:
                # Trim video if it's longer than audio
                video_clip = video_clip.subclip(0, audio_duration)
            
            # Set audio
            video_with_audio = video_clip.set_audio(audio_clip)
            
            # Add subtitles if requested
            if add_subtitles:
                subtitles = self.generate_subtitles_from_text(text, audio_duration)
                
                if subtitles:
                    subtitle_clips = []
                    for start, end, sub_text in subtitles:
                        subtitle_clip = self.create_subtitle_clip(
                            sub_text, start, end, video_clip.size
                        )
                        subtitle_clips.append(subtitle_clip)
                    
                    # Composite video with subtitles
                    final_video = CompositeVideoClip([video_with_audio] + subtitle_clips)
                else:
                    final_video = video_with_audio
            else:
                final_video = video_with_audio
            
            # Set output path
            if output_path is None:
                output_path = os.path.join(self.temp_dir, f"output_video_{os.getpid()}.mp4")
            
            # Write the final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, f'temp-audio-{os.getpid()}.m4a'),
                remove_temp=True,
                fps=video_clip.fps,
                logger=None  # Suppress moviepy progress bars
            )
            
            # Cleanup
            video_clip.close()
            audio_clip.close()
            if os.path.exists(audio_temp_path):
                os.remove(audio_temp_path)
            
            return output_path
        
        except Exception as e:
            # Cleanup on error
            if os.path.exists(audio_temp_path):
                os.remove(audio_temp_path)
            raise Exception(f"Video generation failed: {str(e)}")