#!/usr/bin/env python3
"""
Audio separation tool for Video-CLI
Extracts audio from video files and separates vocals from instrumental tracks
"""

import argparse
import os
import sys
import time
import gc
from loguru import logger

try:
    from demucs.api import Separator
    import torch
    import numpy as np
    from scipy.io import wavfile
    DEMUCS_AVAILABLE = True
except ImportError:
    DEMUCS_AVAILABLE = False
    logger.warning("Demucs not available. Only basic audio extraction will be supported.")

def extract_audio_from_video(video_path, output_path=None):
    """
    Extract audio from video file using ffmpeg
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(os.path.dirname(video_path), f"{base_name}.wav")
    
    logger.info(f"Extracting audio from: {video_path}")
    logger.info(f"Saving audio to: {output_path}")
    
    # Use ffmpeg to extract audio
    cmd = f'ffmpeg -loglevel error -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{output_path}" -y'
    result = os.system(cmd)
    
    if result != 0:
        raise RuntimeError("Failed to extract audio from video")
    
    time.sleep(1)
    logger.success("Audio extraction completed")
    return output_path

def save_wav(wav: np.ndarray, output_path: str, sample_rate=44100):
    """
    Save numpy array as WAV file
    """
    wav_norm = wav * 32767
    wavfile.write(output_path, sample_rate, wav_norm.astype(np.int16))

def load_demucs_model(model_name: str = "htdemucs_ft", device: str = 'auto'):
    """
    Load Demucs model for vocal separation
    """
    if not DEMUCS_AVAILABLE:
        raise RuntimeError("Demucs is not available. Please install Demucs to use this feature.")
    
    logger.info(f"Loading Demucs model: {model_name}")
    t_start = time.time()
    
    # Check if CUDA is available and supported by PyTorch
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        try:
            # Test if CUDA actually works
            torch.tensor([1.0]).cuda()
        except Exception:
            cuda_available = False
            logger.warning("CUDA is available but not working properly. Falling back to CPU.")
    
    auto_device = torch.device('cuda' if cuda_available else 'cpu')
    
    # If user specifically requested CUDA but it's not available, warn and fallback to CPU
    if device == 'cuda' and not cuda_available:
        logger.warning("CUDA requested but not available. Falling back to CPU.")
        device_to_use = 'cpu'
    elif device == 'auto':
        device_to_use = auto_device
    else:
        device_to_use = device
    
    separator = Separator(model_name, device=device_to_use, progress=True, shifts=1)
    
    t_end = time.time()
    logger.info(f"Demucs model loaded in {t_end - t_start:.2f} seconds on {device_to_use}")
    
    return separator

def separate_audio(audio_path, output_dir=None, model_name: str = "htdemucs_ft", device: str = 'auto'):
    """
    Separate vocals from instrumental tracks using Demucs
    """
    if not DEMUCS_AVAILABLE:
        raise RuntimeError("Demucs is not available. Please install Demucs to use this feature.")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)
    
    vocal_output_path = os.path.join(output_dir, "vocals.wav")
    instruments_output_path = os.path.join(output_dir, "instruments.wav")
    
    # Check if separation already exists
    if os.path.exists(vocal_output_path) and os.path.exists(instruments_output_path):
        logger.info("Audio already separated")
        return vocal_output_path, instruments_output_path
    
    logger.info(f"Separating audio: {audio_path}")
    
    # Load model
    separator = load_demucs_model(model_name, device)
    
    try:
        t_start = time.time()
        origin, separated = separator.separate_audio_file(audio_path)
        t_end = time.time()
        logger.info(f"Audio separation completed in {t_end - t_start:.2f} seconds")
        
        # Extract vocals
        vocals = separated['vocals'].numpy().T
        save_wav(vocals, vocal_output_path, sample_rate=44100)
        logger.info(f"Saved vocals to: {vocal_output_path}")
        
        # Combine all non-vocal tracks for instrumental
        instruments = None
        for k, v in separated.items():
            if k == 'vocals':
                continue
            if instruments is None:
                instruments = v
            else:
                instruments += v
        instruments = instruments.numpy().T
        save_wav(instruments, instruments_output_path, sample_rate=44100)
        logger.info(f"Saved instruments to: {instruments_output_path}")
        
        # Clean up
        del separator
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return vocal_output_path, instruments_output_path
    
    except Exception as e:
        logger.error(f"Audio separation failed: {str(e)}")
        raise

def process_video(video_path, separate_vocals=False, model_name: str = "htdemucs_ft", device: str = 'auto'):
    """
    Process video file: extract audio and optionally separate vocals
    """
    logger.info(f"Processing video: {video_path}")
    
    # Extract audio
    audio_path = extract_audio_from_video(video_path)
    
    if separate_vocals and DEMUCS_AVAILABLE:
        # Separate vocals from instruments
        vocal_path, instrumental_path = separate_audio(audio_path, model_name=model_name, device=device)
        logger.success("Vocal separation completed")
        return audio_path, vocal_path, instrumental_path
    elif separate_vocals and not DEMUCS_AVAILABLE:
        logger.warning("Demucs not available. Skipping vocal separation.")
        return audio_path, None
    else:
        return audio_path, None

def main():
    parser = argparse.ArgumentParser(description="Extract audio from video and separate vocals from instrumental tracks")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("-o", "--output-dir", help="Output directory for separated audio files")
    parser.add_argument("-s", "--separate-vocals", action="store_true", help="Separate vocals from instrumental tracks")
    parser.add_argument("-m", "--model", default="htdemucs_ft", help="Demucs model to use (default: htdemucs_ft)")
    parser.add_argument("-d", "--device", default="auto", choices=["auto", "cpu", "cuda"], help="Device to use for processing")
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.video_path):
        logger.error(f"Video file not found: {args.video_path}")
        sys.exit(1)
    
    # Set output directory
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        output_dir = args.output_dir
    else:
        output_dir = os.path.dirname(args.video_path)
    
    try:
        result = process_video(
            args.video_path, 
            separate_vocals=args.separate_vocals,
            model_name=args.model,
            device=args.device
        )
        
        logger.success("Processing completed successfully!")
        if args.separate_vocals:
            audio_path, vocal_path, instrumental_path = result
            logger.info(f"Extracted audio: {audio_path}")
            if vocal_path and instrumental_path:
                logger.info(f"Separated vocals: {vocal_path}")
                logger.info(f"Separated instruments: {instrumental_path}")
        else:
            audio_path = result[0] if isinstance(result, tuple) else result
            logger.info(f"Extracted audio: {audio_path}")
    
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
