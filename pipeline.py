#!/usr/bin/env python3
"""
Pipeline script for Video-CLI
Downloads a video, separates its audio into vocals and instrumental tracks, and generates subtitles
"""

import argparse
import os
import sys
import subprocess
from typing import Optional, List, Tuple
from loguru import logger

def run_download_video(url: str, output_dir: str = "downloads", resolution: str = "1080p", num_videos: int = 5) -> bool:
    """
    Run the download_video.py script
    """
    logger.info(f"Starting video download: {url}")
    
    cmd: List[str] = [
        sys.executable, "download_video.py",
        url,
        "-o", output_dir,
        "-r", resolution,
        "-n", str(num_videos)
    ]
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.success("Video download completed successfully")
        if result.stdout:
            logger.info(f"Download output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Video download failed: {e}")
        if e.stdout:
            logger.error(f"Download stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Download stderr: {e.stderr}")
        return False

def find_downloaded_video(output_dir: str) -> Optional[str]:
    """
    Find the most recently downloaded video file
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']
    
    # Walk through the directory tree to find video files
    video_files: List[str] = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if any(file.endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))
    
    # Return the most recently modified video file
    if video_files:
        latest_video = max(video_files, key=os.path.getmtime)
        logger.info(f"Found latest downloaded video: {latest_video}")
        return latest_video
    
    logger.error("No video files found in the download directory")
    return None

def run_separate_audio(video_path: str, separate_vocals: bool = True, device: str = "auto") -> bool:
    """
    Run the separate_audio.py script
    """
    logger.info(f"Starting audio separation for: {video_path}")
    
    cmd: List[str] = [
        sys.executable, "separate_audio.py",
        video_path
    ]
    
    if separate_vocals:
        cmd.append("-s")
    
    cmd.extend(["-d", device])
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.success("Audio separation completed successfully")
        if result.stdout:
            logger.info(f"Separation output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Audio separation failed: {e}")
        if e.stdout:
            logger.error(f"Separation stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Separation stderr: {e.stderr}")
        return False

def run_generate_subtitles(audio_path: str, method: str = 'WhisperX', model_name: str = 'large', device: str = 'auto', 
                          diarization: bool = True, min_speakers: Optional[int] = None, max_speakers: Optional[int] = None, 
                          output_dir: Optional[str] = None) -> bool:
    """
    Run the audio_to_subtitle.py script
    """
    logger.info(f"Starting subtitle generation for: {audio_path}")
    
    # Adjust device parameter for subtitle generation
    # If CUDA is not available, force CPU processing
    import torch
    if device == 'cuda' and not torch.cuda.is_available():
        logger.warning("CUDA requested but not available. Falling back to CPU for subtitle generation.")
        device_to_use = 'cpu'
    elif device == 'auto':
        device_to_use = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device_to_use = device
    
    cmd: List[str] = [
        sys.executable, "audio_to_subtitle.py",
        audio_path,
        "-m", method,
        "--model", model_name,
        "-d", device_to_use
    ]
    # Note: The CLI argument is --no-diarization, so we append it when diarization is False
    if not diarization:
        cmd.append("--no-diarization")
    
    if min_speakers:
        cmd.extend(["--min-speakers", str(min_speakers)])
    
    if max_speakers:
        cmd.extend(["--max-speakers", str(max_speakers)])
    
    if output_dir:
        cmd.extend(["-o", output_dir])
    
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.success("Subtitle generation completed successfully")
        if result.stdout:
            logger.info(f"Subtitle generation output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Subtitle generation failed: {e}")
        if e.stdout:
            logger.error(f"Subtitle generation stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Subtitle generation stderr: {e.stderr}")
        return False

def find_vocal_audio(video_dir: str) -> Optional[str]:
    """
    Find the vocal audio file in the video directory
    """
    vocal_files = ['vocals.wav', 'audio_vocals.wav']
    
    for filename in vocal_files:
        filepath = os.path.join(video_dir, filename)
        if os.path.exists(filepath):
            logger.info(f"Found vocal audio file: {filepath}")
            return filepath
    
    # If not found, check for any WAV file
    for file in os.listdir(video_dir):
        if file.endswith('.wav'):
            filepath = os.path.join(video_dir, file)
            logger.info(f"Using audio file: {filepath}")
            return filepath
    
    logger.error("No vocal audio file found")
    return None

def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline for downloading video, separating audio, and generating subtitles")
    parser.add_argument("url", help="URL of the video to download")
    parser.add_argument("-o", "--output-dir", default="downloads", help="Output directory for downloaded video")
    parser.add_argument("-r", "--resolution", default="1080p", 
                        choices=['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p'],
                        help="Video resolution")
    parser.add_argument("-n", "--num-videos", type=int, default=5, help="Number of videos to download from playlist")
    parser.add_argument("-d", "--device", default="auto", choices=["auto", "cpu", "cuda"], 
                        help="Device to use for audio separation and subtitle generation")
    parser.add_argument("-m", "--subtitle-method", default="FunASR", choices=["WhisperX", "FunASR", "NeMo"],
                        help="ASR method to use for subtitle generation")
    parser.add_argument("--subtitle-model", default="large", help="Model name for subtitle generation")
    parser.add_argument("--no-diarization", action="store_true", help="Disable speaker diarization for subtitles")
    parser.add_argument("--min-speakers", type=int, help="Minimum number of speakers for diarization")
    parser.add_argument("--max-speakers", type=int, help="Maximum number of speakers for diarization")
    
    args = parser.parse_args()
    
    # Step 1: Download video
    if not run_download_video(args.url, args.output_dir, args.resolution, args.num_videos):
        logger.error("Pipeline failed at video download step")
        sys.exit(1)
    
    # Step 2: Find the downloaded video
    video_path = find_downloaded_video(args.output_dir)
    if not video_path:
        logger.error("Could not find downloaded video file")
        sys.exit(1)
    
    # Step 3: Separate audio
    if not run_separate_audio(video_path, separate_vocals=True, device=args.device):
        logger.error("Pipeline failed at audio separation step")
        sys.exit(1)
    
    # Step 4: Find the vocal audio file
    video_dir = os.path.dirname(video_path)
    vocal_audio_path = find_vocal_audio(video_dir)
    if not vocal_audio_path:
        logger.error("Could not find vocal audio file")
        sys.exit(1)
    
    # Step 5: Generate subtitles
    if not run_generate_subtitles(
        audio_path=vocal_audio_path,
        method=args.subtitle_method,
        model_name=args.subtitle_model,
        device=args.device,
        diarization=not args.no_diarization,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        output_dir=video_dir
    ):
        logger.error("Pipeline failed at subtitle generation step")
        sys.exit(1)
    
    logger.success("Pipeline completed successfully!")
    logger.info(f"Video downloaded to: {video_path}")
    logger.info(f"Audio separated in the same directory as the video")
    logger.info(f"Subtitles generated in the same directory as the video")

if __name__ == "__main__":
    main()
