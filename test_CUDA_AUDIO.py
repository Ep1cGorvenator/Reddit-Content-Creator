"""
CUDA TTS Test Script
Tests Coqui TTS with GPU acceleration
"""

import torch
import time
import os
from TTS.api import TTS
import soundfile as sf
import numpy as np

# Monkey patch to use soundfile instead of torchaudio
def load_audio_with_soundfile(audiopath, sr=None):
    """Load audio using soundfile instead of torchaudio to avoid torchcodec issues
    
    NOTE: XTTS calls this as: audio = load_audio(file_path, load_sr)
    So it expects ONLY the audio tensor, not a tuple!
    The original load_audio in xtts.py does the unpacking internally.
    """
    print(f"[DEBUG] Loading audio from: {audiopath}, target sr: {sr}")
    
    audio_data, sample_rate = sf.read(audiopath)
    print(f"[DEBUG] Loaded shape: {audio_data.shape}, sr: {sample_rate}")
    
    # Resample if needed
    if sr is not None and sr != sample_rate:
        import scipy.signal as signal
        num_samples = int(len(audio_data) * sr / sample_rate)
        audio_data = signal.resample(audio_data, num_samples)
        sample_rate = sr
        print(f"[DEBUG] Resampled to: {audio_data.shape}, sr: {sample_rate}")
    
    # Convert to torch tensor
    audio = torch.FloatTensor(audio_data)
    
    # Ensure it's the right shape (channels, samples) for XTTS
    if len(audio.shape) == 1:
        # Mono audio - add channel dimension: (samples,) -> (1, samples)
        audio = audio.unsqueeze(0)
        print(f"[DEBUG] Added channel dim: {audio.shape}")
    elif len(audio.shape) == 2:
        # Stereo - ensure shape is (channels, samples)
        if audio.shape[0] > audio.shape[1]:
            # Shape is (samples, channels), transpose it
            audio = audio.T
            print(f"[DEBUG] Transposed to: {audio.shape}")
        # Convert stereo to mono
        audio = audio.mean(dim=0, keepdim=True)
        print(f"[DEBUG] Converted to mono: {audio.shape}")
    
    print(f"[DEBUG] Final audio shape: {audio.shape}, type: {type(audio)}")
    print(f"[DEBUG] Returning ONLY audio tensor (not tuple)")
    
    # Return ONLY the audio tensor, not a tuple
    # The original load_audio function in xtts.py wraps torchaudio.load 
    # but only returns the audio part
    return audio

# Patch the load_audio function in XTTS
import TTS.tts.models.xtts as xtts_module
xtts_module.load_audio = load_audio_with_soundfile

def check_cuda():
    """Check CUDA availability and GPU info"""
    print("=" * 60)
    print("STEP 1: Checking CUDA Setup")
    print("=" * 60)
    
    cuda_available = torch.cuda.is_available()
    print(f"✓ CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"✓ CUDA Version: {torch.version.cuda}")
        print(f"✓ GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        print(f"✓ Current Device: cuda:{torch.cuda.current_device()}")
    else:
        print("❌ CUDA not available - will use CPU (slower)")
    
    print()
    return cuda_available

def test_tts_generation(use_gpu=True):
    """Test TTS model download and audio generation"""
    print("=" * 60)
    print("STEP 2: Loading TTS Model")
    print("=" * 60)
    
    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        # Initialize TTS with XTTS model for voice cloning
        print("\nInitializing Coqui TTS (XTTS-v2)...")
        print("⏳ First run will download ~4GB model - please wait...")
        
        start_time = time.time()
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        load_time = time.time() - start_time
        
        print(f"✓ Model loaded in {load_time:.2f} seconds")
        print()
        
        # Generate test audio
        print("=" * 60)
        print("STEP 3: Generating Test Audio")
        print("=" * 60)
        
        test_text = (
            "Hello! This is a test of CUDA-accelerated text to speech. "
            "If you can hear this clearly, your GPU setup is working perfectly!"
        )
        
        output_file = "test_gpu.wav"
        speaker_file = "Benit.wav"
        
        # Check if speaker file exists
        if not os.path.exists(speaker_file):
            print(f"❌ ERROR: Speaker file '{speaker_file}' not found!")
            print(f"   Please place {speaker_file} in the same directory as this script")
            return False
        
        print(f"Text: '{test_text}'")
        print(f"Speaker Voice: {speaker_file}")
        print(f"Output: {output_file}")
        print("🎤 Generating speech with voice cloning...")
        print("   (This clones the voice from Benit.wav)")
        
        if use_gpu:
            print("💡 TIP: Open another terminal and run 'nvidia-smi' to see GPU usage!")
        
        gen_start = time.time()
        
        # Generate speech with voice cloning from Benit.wav
        tts.tts_to_file(
            text=test_text,
            file_path=output_file,
            speaker_wav=speaker_file,
            language="en"
        )
        
        gen_time = time.time() - gen_start
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024
            print(f"✅ SUCCESS! Audio generated in {gen_time:.2f} seconds")
            print(f"✓ File: {output_file} ({file_size:.2f} KB)")
            print()
            
            # Try to play audio
            print("=" * 60)
            print("STEP 4: Playing Audio")
            print("=" * 60)
            
            try:
                import simpleaudio as sa
                wave_obj = sa.WaveObject.from_wave_file(output_file)
                play_obj = wave_obj.play()
                print("🔊 Playing audio... (wait for it to finish)")
                play_obj.wait_done()
                print("✓ Playback complete!")
            except ImportError:
                print("⚠️ simpleaudio not available - skipping playback")
                print(f"   You can manually play: {output_file}")
            except Exception as e:
                print(f"⚠️ Playback error: {e}")
                print(f"   You can manually play: {output_file}")
            
            return True
        else:
            print("❌ FAILED: Audio file not created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_full_test():
    """Run complete CUDA TTS test"""
    print("\n" + "🦍" * 30)
    print("GORILLA STUDIOS - CUDA TTS TEST")
    print("🦍" * 30 + "\n")
    
    # Check CUDA
    cuda_ok = check_cuda()
    
    # Test TTS
    if cuda_ok:
        print("🚀 Running GPU-accelerated test...\n")
        success = test_tts_generation(use_gpu=True)
    else:
        print("⚠️ Running CPU test (GPU not available)...\n")
        success = test_tts_generation(use_gpu=False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print("✓ CUDA setup is working")
        print("✓ TTS model downloaded and loaded")
        print("✓ Audio generated successfully")
        print("\n📁 Check 'test_gpu.wav' in your current directory")
        
        if cuda_ok:
            print("\n💡 Your GPU is being used for TTS generation!")
            print("   Run 'nvidia-smi' during generation to verify")
    else:
        print("❌ Tests failed - see errors above")
        print("\nTroubleshooting:")
        print("1. Ensure CUDA 12.6 is installed")
        print("2. Check GPU drivers are up to date")
        print("3. Verify torch was installed with CUDA support:")
        print("   python -c \"import torch; print(torch.cuda.is_available())\"")
    
    print("=" * 60)

if __name__ == "__main__":
    run_full_test()