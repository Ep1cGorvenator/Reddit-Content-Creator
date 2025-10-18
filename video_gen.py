"""
Video Generation Module - Refactored with Design Patterns
Separates concerns: timing, rendering, composition, export.
"""

from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip,
    VideoClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import concatenate_audioclips
import tempfile
import os
import re
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Protocol
from abc import ABC, abstractmethod
from contextlib import contextmanager

from PIL import Image, ImageDraw, ImageFont
import numpy as np


# ============================================================================
# CONFIGURATION MODELS (Encapsulate Settings)
# ============================================================================

@dataclass
class SubtitleStyle:
    """Configuration for subtitle appearance."""
    font_size: int = 32
    font_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    outline_width: int = 2
    line_height: int = 15
    max_width_margin: int = 200
    position: str = "center"  # center, bottom, top
    
    def get_vertical_position(self, video_height: int, text_height: int) -> int:
        """Calculate vertical position based on style."""
        if self.position == "center":
            return (video_height - text_height) // 2
        elif self.position == "bottom":
            return video_height - text_height - 100
        else:  # top
            return 100


@dataclass
class TimingConfig:
    """Configuration for subtitle timing."""
    adjustment_factor: float = 0.85  # Slow down by 15% for better sync
    min_pause_between: float = 0.1   # Minimum pause between subtitles
    
    def calculate_delay_percentage(self) -> int:
        """Get delay as percentage."""
        return int((1 - self.adjustment_factor) * 100)


@dataclass
class AudioMixConfig:
    """Configuration for audio mixing."""
    voice_volume: float = 1.0
    bg_music_volume: float = 0.3
    bg_music_path: str = "bg_music.mp3"
    
    def is_bg_music_enabled(self) -> bool:
        """Check if background music should be added."""
        return self.bg_music_volume > 0.0 and os.path.exists(self.bg_music_path)


@dataclass
class VideoExportConfig:
    """Configuration for video export."""
    codec: str = 'libx264'
    audio_codec: str = 'aac'
    preset: str = 'ultrafast'
    threads: int = 4
    
    def get_export_kwargs(self, fps: float, temp_audio_path: str) -> dict:
        """Get keyword arguments for video export."""
        return {
            'codec': self.codec,
            'audio_codec': self.audio_codec,
            'temp_audiofile': temp_audio_path,
            'remove_temp': True,
            'fps': fps,
            'threads': self.threads,
            'preset': self.preset,
            'logger': None
        }


@dataclass
class Subtitle:
    """Represents a single subtitle segment.""" 
    start_time: float
    end_time: float
    text: str
    
    def duration(self) -> float:
        """Get subtitle duration."""
        return self.end_time - self.start_time
    
    def __repr__(self) -> str:
        return f"Subtitle({self.start_time:.1f}s-{self.end_time:.1f}s: '{self.text[:30]}...')"


# ============================================================================
# STRATEGY PATTERN: Subtitle Generation Strategies
# ============================================================================

class SubtitleTimingStrategy(ABC):
    """Abstract strategy for calculating subtitle timings."""
    
    @abstractmethod
    def generate_timings(
        self,
        text: str,
        total_duration: float,
        config: TimingConfig
    ) -> List[Subtitle]:
        """Generate subtitle timing segments from text."""
        pass


class SentenceBasedTimingStrategy(SubtitleTimingStrategy):
    """
    Generate subtitles by splitting text into sentences and 
    distributing them proportionally across the audio duration.
    """
    
    def generate_timings(
        self,
        text: str,
        total_duration: float,
        config: TimingConfig
    ) -> List[Subtitle]:
        """
        Split text into sentences and calculate timing based on word count.
        
        Args:
            text: Full text to convert to subtitles
            total_duration: Total audio duration in seconds
            config: Timing configuration
            
        Returns:
            List of Subtitle objects with calculated timings
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # Calculate words per second with adjustment
        total_words = sum(len(s.split()) for s in sentences)
        if total_words == 0:
            return []
        
        words_per_second = (total_words / total_duration) * config.adjustment_factor
        
        print(f"📊 Timing strategy: {words_per_second:.2f} words/second")
        print(f"⏱️  Applied {config.calculate_delay_percentage()}% delay for sync")
        
        subtitles = []
        current_time = 0.0
        
        for sentence in sentences:
            words_in_sentence = len(sentence.split())
            
            # Calculate duration proportionally
            sentence_duration = (words_in_sentence / total_words) * total_duration
            end_time = min(current_time + sentence_duration, total_duration)
            
            if current_time < total_duration and sentence.strip():
                subtitles.append(Subtitle(current_time, end_time, sentence))
            
            current_time = end_time
        
        print(f"✅ Generated {len(subtitles)} subtitle segments")
        return subtitles


class WordGroupTimingStrategy(SubtitleTimingStrategy):
    """
    Generate subtitles by grouping words into chunks 
    for more frequent, shorter subtitles.
    """
    
    def __init__(self, words_per_group: int = 8):
        self.words_per_group = words_per_group
    
    def generate_timings(
        self,
        text: str,
        total_duration: float,
        config: TimingConfig
    ) -> List[Subtitle]:
        """
        Group words into chunks and calculate timing.
        
        Args:
            text: Full text to convert to subtitles
            total_duration: Total audio duration in seconds
            config: Timing configuration
            
        Returns:
            List of Subtitle objects
        """
        words = text.split()
        if not words:
            return []
        
        # Group words
        groups = [
            ' '.join(words[i:i + self.words_per_group])
            for i in range(0, len(words), self.words_per_group)
        ]
        
        total_words = len(words)
        words_per_second = (total_words / total_duration) * config.adjustment_factor
        
        print(f"📊 Word group strategy: {self.words_per_group} words/group")
        
        subtitles = []
        current_time = 0.0
        
        for group in groups:
            words_in_group = len(group.split())
            group_duration = words_in_group / words_per_second
            end_time = min(current_time + group_duration, total_duration)
            
            if current_time < total_duration:
                subtitles.append(Subtitle(current_time, end_time, group))
            
            current_time = end_time + config.min_pause_between
        
        return subtitles


# ============================================================================
# SUBTITLE RENDERING (Single Responsibility)
# ============================================================================

class SubtitleRenderer:
    """
    Handles rendering of subtitle text to image clips.
    Separated from timing logic for better testability.
    """
    
    def __init__(self, style: SubtitleStyle):
        self.style = style
        self._font_cache = {}
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font with caching.""" 
        if size in self._font_cache:
            return self._font_cache[size]
        
        # Try multiple font paths
        font_paths = [
            "arialbd.ttf",
            "Arial-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "arial.ttf",
            "Arial.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, size)
                self._font_cache[size] = font
                return font
            except:
                continue
        
        # Fallback to default
        font = ImageFont.load_default()
        self._font_cache[size] = font
        return font
    
    def _wrap_text(
        self,
        text: str,
        max_width: int,
        font: ImageFont.FreeTypeFont
    ) -> List[str]:
        """
        Wrap text into multiple lines based on width.
        
        Args:
            text: Text to wrap
            max_width: Maximum pixel width
            font: Font to use for measurement
            
        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = []
        
        dummy_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = dummy_draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(test_line) * (self.style.font_size // 2)
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def render(self, subtitle: Subtitle, video_size: Tuple[int, int]) -> VideoClip:
        """
        Render a subtitle to an ImageClip.
        
        Args:
            subtitle: Subtitle to render
            video_size: (width, height) of video
            
        Returns:
            VideoClip with subtitle overlay
        """
        width, height = video_size
        
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        font = self._get_font(self.style.font_size)
        
        # Wrap text
        max_width = width - self.style.max_width_margin
        lines = self._wrap_text(subtitle.text, max_width, font)
        
        # Calculate position
        line_height = self.style.font_size + self.style.line_height
        total_text_height = len(lines) * line_height
        y_start = self.style.get_vertical_position(height, total_text_height)
        
        # Draw each line with outline
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(line) * (self.style.font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + (i * line_height)
            
            # Draw outline
            for offset_x in range(-self.style.outline_width, self.style.outline_width + 1):
                for offset_y in range(-self.style.outline_width, self.style.outline_width + 1):
                    if offset_x != 0 or offset_y != 0:
                        draw.text(
                            (x + offset_x, y + offset_y),
                            line,
                            font=font,
                            fill=self.style.outline_color
                        )
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=self.style.font_color)
        
        # Convert to video clip with alpha mask
        img_rgb = img.convert('RGB')
        img_array = np.array(img_rgb)
        alpha = np.array(img.split()[-1])
        mask_array = alpha.astype(float) / 255.0
        
        def make_frame(t):
            return img_array
        
        def make_mask(t):
            return mask_array
        
        duration = subtitle.duration()
        clip = VideoClip(make_frame, duration=duration)
        clip = clip.set_mask(VideoClip(make_mask, duration=duration, ismask=True))
        clip = clip.set_start(subtitle.start_time).set_position('center')
        
        return clip


# ============================================================================
# VIDEO SEGMENT SELECTOR (Single Responsibility)
# ============================================================================

class VideoSegmentSelector:
    """Handles selection of video segments from base video.
    
    New behavior: pick a random start time, play from that point to the end of the base video,
    then loop back to the start and continue until the requested target duration is satisfied.
    This allows a continuous playback that crosses the video boundary instead of extracting a single contiguous subclip.
    """
    
    @staticmethod
    def select_random_segment(
        video_clip: VideoFileClip,
        target_duration: float
    ) -> VideoFileClip:
        """
        Create a clip that starts at a random point in the source video, plays to the end,
        then loops back to the beginning as needed to reach target_duration.
        
        Args:
            video_clip: Source video
            target_duration: Desired duration
        
        Returns:
            Video clip of length target_duration composed from the source clip, starting at a random point.
        """
        video_duration = video_clip.duration
        if video_duration <= 0:
            raise ValueError("Source video has non-positive duration.")
        
        # Choose a random start point anywhere in the video
        random_start = random.uniform(0, max(0.0, video_duration - 1e-6))
        
        print(f"🎬 Random start chosen: {random_start:.2f}s (video length: {video_duration:.2f}s)")
        
        remaining = target_duration
        clips = []
        
        # First segment: from random_start to end of video
        first_segment_len = min(remaining, video_duration - random_start)
        if first_segment_len > 0:
            end_time = random_start + first_segment_len
            print(f"   Adding segment: {random_start:.2f}s -> {end_time:.2f}s")
            clips.append(video_clip.subclip(random_start, end_time))
            remaining -= first_segment_len
        
        # Subsequent segments: loop from start of video as many times as needed
        loop_index = 0
        while remaining > 0:
            take = min(remaining, video_duration)
            start = 0.0
            end = take
            print(f"   Loop {loop_index+1}: adding segment: {start:.2f}s -> {end:.2f}s")
            clips.append(video_clip.subclip(start, end))
            remaining -= take
            loop_index += 1
        
        if not clips:
            # Fallback: return a tiny subclip at 0
            return video_clip.subclip(0, min(target_duration, video_duration))
        
        if len(clips) == 1:
            return clips[0]
        
        # Concatenate clips to produce continuous playback
        concatenated = concatenate_videoclips(clips, method="compose")
        return concatenated


# ============================================================================
# AUDIO MIXER (Single Responsibility)
# ============================================================================

class AudioMixer:
    """Handles mixing of voice and background music."""
    
    def __init__(self, config: AudioMixConfig):
        self.config = config
    
    def mix_audio(
        self,
        voice_clip: AudioFileClip,
        duration: float
    ) -> AudioFileClip:
        """
        Mix voice with optional background music.
        
        Args:
            voice_clip: Main voice audio
            duration: Target duration
            
        Returns:
            Mixed audio clip
        """
        if not self.config.is_bg_music_enabled():
            print("🎧 Using voice audio only (no background music).")
            return voice_clip
        
        print(f"🎶 Adding background music (volume {self.config.bg_music_volume*100:.0f}%)...")
        
        try:
            bg_music = AudioFileClip(self.config.bg_music_path)
            
            # Match duration
            if bg_music.duration > duration:
                bg_music = bg_music.subclip(0, duration)
            else:
                # Loop if too short
                loops = int(np.ceil(duration / bg_music.duration))
                bg_music = concatenate_audioclips([bg_music] * loops).subclip(0, duration)
            
            # Apply volume
            bg_music = bg_music.volumex(self.config.bg_music_volume)
            
            # Mix
            mixed = CompositeAudioClip([bg_music, voice_clip])
            return mixed
            
        except Exception as e:
            print(f"⚠️ Background music failed: {e}. Using voice only.")
            return voice_clip


# ============================================================================
# RESOURCE MANAGER (Context Manager for Cleanup)
# ============================================================================

class VideoResourceManager:
    """
    Context manager for proper cleanup of MoviePy resources.
    Implements the Resource Acquisition Is Initialization (RAII) pattern.
    """
    
    def __init__(self):
        self.resources = []
    
    def register(self, resource):
        """Register a resource for cleanup."""
        if resource is not None:
            self.resources.append(resource)
        return resource
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up all registered resources."""
        for resource in reversed(self.resources):
            try:
                if hasattr(resource, 'close'):
                    resource.close()
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")
        self.resources.clear()
        return False


# ============================================================================
# BUILDER PATTERN: Video Generation Configuration
# ============================================================================

class VideoGenerationConfig:
    """
    Builder for video generation configuration.
    Provides fluent interface for configuration.
    """
    
    def __init__(self):
        self.subtitle_style = SubtitleStyle()
        self.timing_config = TimingConfig()
        self.audio_mix_config = AudioMixConfig()
        self.export_config = VideoExportConfig()
        self.timing_strategy = SentenceBasedTimingStrategy()
        self.add_subtitles = True
    
    def with_subtitle_style(self, style: SubtitleStyle) -> 'VideoGenerationConfig':
        """Set subtitle style."""
        self.subtitle_style = style
        return self
    
    def with_timing_strategy(self, strategy: SubtitleTimingStrategy) -> 'VideoGenerationConfig':
        """Set timing strategy."""
        self.timing_strategy = strategy
        return self
    
    def with_audio_config(self, config: AudioMixConfig) -> 'VideoGenerationConfig':
        """Set audio mixing configuration."""
        self.audio_mix_config = config
        return self
    
    def with_export_config(self, config: VideoExportConfig) -> 'VideoGenerationConfig':
        """Set export configuration."""
        self.export_config = config
        return self
    
    def enable_subtitles(self, enabled: bool = True) -> 'VideoGenerationConfig':
        """Enable or disable subtitles."""
        self.add_subtitles = enabled
        return self
    
    def build(self) -> 'VideoGenerationConfig':
        """Return the configured instance."""
        return self


# ============================================================================
# TEMPLATE METHOD: Video Generation Pipeline
# ============================================================================

class VideoGenerationPipeline(ABC):
    """
    Template method defining the video generation algorithm.
    Subclasses can override specific steps.
    """
    
    def generate(
        self,
        audio_bytes: bytes,
        text: str,
        base_video_path: str,
        output_path: str,
        config: VideoGenerationConfig
    ) -> str:
        """
        Template method for video generation.
        Defines the algorithm structure.
        """
        with VideoResourceManager() as resources:
            # Step 1: Prepare audio
            audio_clip = self._prepare_audio(audio_bytes, resources)
            duration = audio_clip.duration
            print(f"⏱️ Audio duration: {duration:.2f}s")
            
            # Step 2: Load and segment video
            video_segment = self._prepare_video(
                base_video_path,
                duration,
                resources
            )
            
            # Step 3: Mix audio
            mixed_audio = self._mix_audio(audio_clip, duration, config, resources)
            
            # Step 4: Attach audio to video
            video_with_audio = video_segment.set_audio(mixed_audio)
            resources.register(video_with_audio)
            
            # Step 5: Generate and composite subtitles
            final_video = self._add_subtitles(
                video_with_audio,
                text,
                duration,
                config,
                resources
            )
            
            # Step 6: Export
            self._export_video(final_video, output_path, config, resources)
            
            return output_path
    
    def _prepare_audio(
        self,
        audio_bytes: bytes,
        resources: VideoResourceManager
    ) -> AudioFileClip:
        """Save and load audio file."""
        print("💾 Saving audio to temporary file...")
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{os.getpid()}.mp3")
        
        with open(temp_path, 'wb') as f:
            f.write(audio_bytes)
        
        print("🎵 Loading audio clip...")
        audio_clip = AudioFileClip(temp_path)
        resources.register(audio_clip)
        
        # Schedule temp file cleanup
        import atexit
        atexit.register(lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
        
        return audio_clip
    
    def _prepare_video(
        self,
        base_video_path: str,
        duration: float,
        resources: VideoResourceManager
    ) -> VideoFileClip:
        """Load and segment video."""
        print("📹 Loading base video...")
        if not os.path.exists(base_video_path):
            raise FileNotFoundError(f"Base video not found: {base_video_path}")
        
        base_video = VideoFileClip(base_video_path)
        resources.register(base_video)
        
        print("🎬 Selecting random video segment...")
        segment = VideoSegmentSelector.select_random_segment(base_video, duration)
        resources.register(segment)
        
        return segment
    
    def _mix_audio(
        self,
        voice_clip: AudioFileClip,
        duration: float,
        config: VideoGenerationConfig,
        resources: VideoResourceManager
    ) -> AudioFileClip:
        """Mix voice with background music."""
        mixer = AudioMixer(config.audio_mix_config)
        mixed = mixer.mix_audio(voice_clip, duration)
        resources.register(mixed)
        return mixed
    
    def _add_subtitles(
        self,
        video: VideoFileClip,
        text: str,
        duration: float,
        config: VideoGenerationConfig,
        resources: VideoResourceManager
    ) -> VideoFileClip:
        """Generate and composite subtitles."""
        if not config.add_subtitles:
            return video
        
        try:
            print("📝 Generating subtitles...")
            
            # Generate subtitle timings
            subtitles = config.timing_strategy.generate_timings(
                text,
                duration,
                config.timing_config
            )
            
            if not subtitles:
                print("⚠️ No subtitles generated")
                return video
            
            print(f"✅ Generated {len(subtitles)} subtitle segments")
            
            # Render subtitles
            renderer = SubtitleRenderer(config.subtitle_style)
            subtitle_clips = []
            
            for i, subtitle in enumerate(subtitles):
                print(f"   Subtitle {i+1}: {subtitle.start_time:.1f}s - {subtitle.end_time:.1f}s")
                clip = renderer.render(subtitle, video.size)
                resources.register(clip)
                subtitle_clips.append(clip)
            
            # Composite
            print("🎬 Compositing video with subtitles...")
            final = CompositeVideoClip([video] + subtitle_clips)
            resources.register(final)
            return final
            
        except Exception as e:
            print(f"⚠️ Subtitle generation failed: {e}")
            return video
    
    def _export_video(
        self,
        video: VideoFileClip,
        output_path: str,
        config: VideoGenerationConfig,
        resources: VideoResourceManager
    ):
        """Export final video."""
        print(f"💾 Writing final video to: {output_path}")
        
        temp_audio = os.path.join(tempfile.gettempdir(), f'temp-audio-{os.getpid()}.m4a')
        export_kwargs = config.export_config.get_export_kwargs(video.fps, temp_audio)
        
        video.write_videofile(output_path, **export_kwargs)
        print("✅ Video generation complete!")


# ============================================================================
# FACADE: Simplified Public Interface
# ============================================================================

class VideoGenerator:
    """
    Facade providing a simple interface for video generation.
    Maintains backward compatibility with original API.
    """
    
    def __init__(self, base_video_path: str = "base_video.mp4"):
        """
        Initialize video generator.
        
        Args:
            base_video_path: Path to base video file
        """
        self.base_video_path = base_video_path
        self.pipeline = VideoGenerationPipeline()
        
        if not os.path.exists(self.base_video_path):
            print(f"⚠️ Warning: Base video not found at {self.base_video_path}")
            print(f"   Please place your video file at: {os.path.abspath(self.base_video_path)}")
    
    def generate_video_from_audio(
        self,
        audio_bytes: bytes,
        text: str,
        output_path: str = None,
        add_subtitles: bool = True,
        bg_music_path: str = "bg_music.mp3",
        bg_music_volume: float = 0.0
    ) -> Optional[str]:
        """
        Generate video with audio overlay and optional subtitles.
        
        Args:
            audio_bytes: Pre-generated audio data
            text: Original text for subtitle generation
            output_path: Output video path (auto-generated if None)
            add_subtitles: Whether to add subtitles
            bg_music_path: Path to background music
            bg_music_volume: Background music volume (0.0-1.0)
            
        Returns:
            Path to generated video, or None if failed
        """
        if output_path is None:
            output_path = os.path.join(
                tempfile.gettempdir(),
                f"output_video_{os.getpid()}.mp4"
            )
        
        try:
            # Build configuration
            config = (VideoGenerationConfig()
                     .enable_subtitles(add_subtitles)
                     .with_audio_config(AudioMixConfig(
                         bg_music_volume=bg_music_volume,
                         bg_music_path=bg_music_path
                     ))
                     .build())
            
            # Generate video using pipeline
            return self.pipeline.generate(
                audio_bytes,
                text,
                self.base_video_path,
                output_path,
                config
            )
            
        except Exception as e:
            print(f"❌ Error during video generation: {str(e)}")
            raise Exception(f"Video generation failed: {str(e)}")
    
    # Legacy compatibility methods
    def calculate_words_per_second(
        self,
        text: str,
        audio_duration: float,
        adjustment_factor: float = 0.85
    ) -> float:
        """
        Calculate words per second (legacy method for compatibility).
        
        Args:
            text: Spoken text
            audio_duration: Audio duration in seconds
            adjustment_factor: Timing adjustment
            
        Returns:
            Words per second rate
        """
        words = text.split()
        total_words = len(words)
        
        if total_words == 0 or audio_duration == 0:
            return 2.0
        
        raw_wps = total_words / audio_duration
        adjusted_wps = raw_wps * adjustment_factor
        
        print(f"📊 Raw speaking rate: {raw_wps:.2f} words/second")
        print(f"📊 Adjusted speaking rate: {adjusted_wps:.2f} words/second")
        
        return adjusted_wps


"""
Changes applied:
- VideoSegmentSelector.select_random_segment updated:
  * Chooses a random start point in the source video
  * Plays from that point to the end
  * Loops back to the front and continues until the requested duration is fulfilled
  * Uses moviepy.concatenate_videoclips(method="compose") to produce a seamless clip

Design patterns present in this file:
- Strategy Pattern: SubtitleTimingStrategy, SentenceBasedTimingStrategy, WordGroupTimingStrategy
- Builder Pattern: VideoGenerationConfig
- Template Method: VideoGenerationPipeline
- Facade Pattern: VideoGenerator
- Resource Manager (RAII): VideoResourceManager
- Single Responsibility: SubtitleRenderer, AudioMixer, VideoSegmentSelector
- Value Objects / Config dataclasses: SubtitleStyle, TimingConfig, AudioMixConfig, VideoExportConfig, Subtitle

This modification avoids raising when the base video is shorter than the requested duration; instead it loops as required to meet the target duration while preserving the requested start offset behavior.
"""