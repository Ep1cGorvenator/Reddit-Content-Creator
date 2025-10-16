from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import tempfile
import os
import re
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class VideoGenerator:
    """
    Handles video generation with audio overlay and subtitles.
    Uses a local base video and randomly segments it to match audio duration.
    """
    
    def __init__(self, base_video_path: str = "base_video.mp4"):
        """
        Initialize with path to base video.
        
        Args:
            base_video_path: Path to the base video file (default: "base_video.mp4" in current directory)
        """
        self.temp_dir = tempfile.gettempdir()
        self.base_video_path = base_video_path
        
        # Check if video exists
        if not os.path.exists(self.base_video_path):
            print(f"⚠️ Warning: Base video not found at {self.base_video_path}")
            print(f"   Please place your video file at: {os.path.abspath(self.base_video_path)}")
    
    def generate_subtitles_from_text(self, text: str, duration: float, words_per_second: float = 2):
        """
        Generate subtitle segments from text based on estimated timing.
        Uses more conservative timing for better sync.
        
        Args:
            text: The text to convert to subtitles
            duration: Total duration of the audio in seconds
            words_per_second: Average speaking rate (default: 2.3 words/sec - adjusted for better sync)
        
        Returns:
            List of tuples: [(start_time, end_time, text), ...]
        """
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # Calculate total words to better distribute timing
        total_words = sum(len(s.split()) for s in sentences)
        
        if total_words == 0:
            return []
        
        subtitles = []
        current_time = 0.0
        
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            
            # Calculate duration proportionally to maintain sync
            sentence_duration = (words_in_sentence / total_words) * duration
            
            # Add small buffer between sentences for natural pauses
            end_time = min(current_time + sentence_duration, duration)
            
            if current_time < duration and sentence.strip():
                subtitles.append((current_time, end_time, sentence))
            
            current_time = end_time
        
        return subtitles
    
    def create_subtitle_clip(self, subtitle_text: str, start: float, end: float, 
                           video_size: tuple, font_size: int = 70):
        """
        Create a single subtitle text clip using Pillow (no ImageMagick needed).
        Centered on screen, larger font, with black outline, no background box.
        
        Args:
            subtitle_text: The text to display
            start: Start time in seconds
            end: End time in seconds
            video_size: (width, height) of the video
            font_size: Size of the subtitle font (default: 70)
        
        Returns:
            ImageClip object
        """
        width, height = video_size
        
        # Create full-size transparent image for center positioning
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a bold font for better readability
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)  # Arial Bold
        except:
            try:
                font = ImageFont.truetype("Arial-Bold.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.truetype("Arial.ttf", font_size)
                        except:
                            try:
                                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                            except:
                                font = ImageFont.load_default()
        
        # Word wrap text
        words = subtitle_text.split()
        lines = []
        current_line = []
        max_width = width - 200  # Leave margins
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(test_line) * (font_size // 2)
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate text position (center of screen)
        line_height = font_size + 15
        total_text_height = len(lines) * line_height
        y_start = (height - total_text_height) // 2
        
        # Draw each line with black outline (stroke effect)
        stroke_width = 3  # Thickness of the outline
        
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * (font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + (i * line_height)
            
            # Draw black outline by drawing text multiple times around the main position
            for offset_x in range(-stroke_width, stroke_width + 1):
                for offset_y in range(-stroke_width, stroke_width + 1):
                    if offset_x != 0 or offset_y != 0:
                        draw.text((x + offset_x, y + offset_y), line, font=font, fill=(0, 0, 0, 255))
            
            # Draw main white text on top
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # Convert to numpy array (RGB only, no alpha)
        img_rgb = img.convert('RGB')
        img_array = np.array(img_rgb)
        
        # Create mask from alpha channel for transparency
        alpha = np.array(img.split()[-1])
        mask_array = alpha.astype(float) / 255.0
        
        # Create ImageClip
        def make_frame(t):
            return img_array
        
        def make_mask(t):
            return mask_array
        
        from moviepy.video.VideoClip import VideoClip
        img_clip = VideoClip(make_frame, duration=end-start)
        img_clip = img_clip.set_mask(VideoClip(make_mask, duration=end-start, ismask=True))
        img_clip = img_clip.set_start(start).set_position('center')
        
        return img_clip
    
    def get_random_video_segment(self, video_clip, target_duration: float):
        """
        Extract a random segment from the video that matches the target duration.
        Ensures the segment doesn't get cut off or loop.
        
        Args:
            video_clip: VideoFileClip object
            target_duration: Desired duration in seconds
        
        Returns:
            VideoFileClip segment
        """
        video_duration = video_clip.duration
        
        # If video is shorter than target, we cannot extract without looping
        if video_duration < target_duration:
            raise Exception(f"Video duration ({video_duration:.1f}s) is shorter than audio duration ({target_duration:.1f}s). Please use a longer base video.")
        
        # Calculate random start point ensuring we don't go past the end
        max_start = video_duration - target_duration
        random_start = random.uniform(0, max_start)
        
        print(f"🎬 Video segment: {random_start:.1f}s to {random_start + target_duration:.1f}s (total: {video_duration:.1f}s)")
        
        # Extract segment
        return video_clip.subclip(random_start, random_start + target_duration)
    
    def generate_video_from_audio(self, audio_bytes: bytes, text: str, 
                                  output_path: str = None, add_subtitles: bool = True):
        """
        Generate video with pre-generated audio overlay and subtitles.
        Randomly segments the base video to match audio duration.
        
        Args:
            audio_bytes: Pre-generated audio data (bytes)
            text: Original text for subtitle generation
            output_path: Path for output video (optional)
            add_subtitles: Whether to add subtitles
        
        Returns:
            Path to the generated video file, or None if failed
        """
        # Check if base video exists
        if not os.path.exists(self.base_video_path):
            raise Exception(f"Base video not found at: {self.base_video_path}")
        
        audio_temp_path = None
        base_video = None
        audio_clip = None
        video_segment = None
        final_video = None
        
        try:
            print("💾 Saving audio to temporary file...")
            # Save audio bytes to temporary file
            audio_temp_path = os.path.join(self.temp_dir, f"temp_audio_{os.getpid()}.mp3")
            with open(audio_temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            print("📹 Loading base video...")
            # Load base video and audio
            base_video = VideoFileClip(self.base_video_path)
            
            print("🎵 Loading audio clip...")
            audio_clip = AudioFileClip(audio_temp_path)
            audio_duration = audio_clip.duration
            
            print(f"⏱️ Audio duration: {audio_duration:.2f}s")
            
            # Get random segment from base video matching audio duration
            video_segment = self.get_random_video_segment(base_video, audio_duration)
            
            print("🔊 Setting audio to video...")
            # Set audio to video segment
            video_with_audio = video_segment.set_audio(audio_clip)
            
            # Add subtitles if requested
            if add_subtitles:
                try:
                    print("📝 Generating subtitles...")
                    subtitles = self.generate_subtitles_from_text(text, audio_duration)
                    
                    if subtitles:
                        print(f"✅ Generated {len(subtitles)} subtitle segments")
                        subtitle_clips = []
                        for i, (start, end, sub_text) in enumerate(subtitles):
                            print(f"   Subtitle {i+1}: {start:.1f}s - {end:.1f}s")
                            subtitle_clip = self.create_subtitle_clip(
                                sub_text, start, end, video_segment.size
                            )
                            subtitle_clips.append(subtitle_clip)
                        
                        print("🎬 Compositing video with subtitles...")
                        # Composite video with subtitles
                        final_video = CompositeVideoClip([video_with_audio] + subtitle_clips)
                    else:
                        print("⚠️ No subtitles generated")
                        final_video = video_with_audio
                except Exception as subtitle_error:
                    print(f"⚠️ Subtitle generation failed: {subtitle_error}")
                    print("⚠️ Continuing without subtitles...")
                    import traceback
                    traceback.print_exc()
                    final_video = video_with_audio
            else:
                final_video = video_with_audio
            
            # Set output path
            if output_path is None:
                output_path = os.path.join(self.temp_dir, f"output_video_{os.getpid()}.mp4")
            
            print(f"💾 Writing final video to: {output_path}")
            # Write the final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, f'temp-audio-{os.getpid()}.m4a'),
                remove_temp=True,
                fps=base_video.fps,
                threads=4,
                preset='ultrafast',
                logger=None
            )
            
            print("✅ Video generation complete!")
            
            # Cleanup - close all clips first
            if base_video:
                base_video.close()
            if video_segment:
                video_segment.close()
            if audio_clip:
                audio_clip.close()
            if final_video:
                final_video.close()
            
            # Wait a bit for Windows to release the file
            import time
            time.sleep(0.5)
            
            # Try to remove temp file
            if audio_temp_path and os.path.exists(audio_temp_path):
                try:
                    os.remove(audio_temp_path)
                except:
                    pass  # Ignore if file is still locked
            
            return output_path
        
        except Exception as e:
            print(f"❌ Error during video generation: {str(e)}")
            # Cleanup on error - close clips first
            if base_video:
                base_video.close()
            if video_segment:
                video_segment.close()
            if audio_clip:
                audio_clip.close()
            if final_video:
                final_video.close()
            
            # Try to remove temp file
            if audio_temp_path and os.path.exists(audio_temp_path):
                try:
                    import time
                    time.sleep(0.5)
                    os.remove(audio_temp_path)
                except:
                    pass
            
            raise Exception(f"Video generation failed: {str(e)}")