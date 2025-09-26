#!/usr/bin/env python3
"""
Complete pipeline script for Video-CLI
Downloads a video, separates its audio, and generates subtitles with speaker diarization
"""

import argparse
import os
import sys
import subprocess
from loguru import logger

def run_command(cmd, description):
    """
    Run a command and handle errors
    """
    logger.info(f"Executing: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.success(f"{description} completed successfully")
        if result.stdout:
            logger.debug(f"{description} output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"{description} failed: {e}")
        if e.stdout:
            logger.error(f"{description} stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"{description} stderr: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Complete pipeline: Download video, separate audio, and generate subtitles")
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
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Step 1: Download video
    logger.info("Step 1: Downloading video")
    download_cmd = [
        sys.executable, "core/download/download_video.py",
        args.url,
        "-o", args.output_dir,
        "-r", args.resolution,
        "-n", str(args.num_videos)
    ]
    
    if not run_command(download_cmd, "Video download"):
        logger.error("Pipeline failed at video download step")
        sys.exit(1)
    
    # Step 2: Find the downloaded video
    logger.info("Step 2: Finding downloaded video")
    video_files = []
    for root, dirs, files in os.walk(args.output_dir):
        for file in files:
            if file.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv')):
                video_files.append(os.path.join(root, file))
    
    if not video_files:
        logger.error("No video files found in the download directory")
        sys.exit(1)
    
    # Use the most recently modified video file
    video_path = max(video_files, key=os.path.getmtime)
    logger.info(f"Found video: {video_path}")
    
    # Step 3: Separate audio
    logger.info("Step 3: Separating audio")
    separate_cmd = [
        sys.executable, "core/audio/separate_audio.py",
        video_path,
        "-s", # Separate vocals
        "-d", args.device
    ]
    
    if not run_command(separate_cmd, "Audio separation"):
        logger.error("Pipeline failed at audio separation step")
        # Check if the error is related to CUDA, and try again with CPU
        if args.device == "cuda":
            logger.info("CUDA not available, trying with CPU")
            separate_cmd = [
                sys.executable, "core/audio/separate_audio.py",
                video_path,
                "-s", # Separate vocals
                "-d", "cpu"
            ]
            if not run_command(separate_cmd, "Audio separation with CPU"):
                logger.error("Pipeline failed at audio separation step with CPU too")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Step 4: Find the vocal audio file
    logger.info("Step 4: Finding vocal audio file")
    video_dir = os.path.dirname(video_path)
    vocal_audio_path = os.path.join(video_dir, "vocals.wav")
    
    if not os.path.exists(vocal_audio_path):
        # Try alternative name
        vocal_audio_path = os.path.join(video_dir, "audio_vocals.wav")
        
        if not os.path.exists(vocal_audio_path):
            # Look for download.wav (basic audio extraction when Demucs is not available)
            download_audio_path = os.path.join(video_dir, "download.wav")
            if os.path.exists(download_audio_path):
                vocal_audio_path = download_audio_path
            else:
                # Look for any WAV file as a last resort
                for file in os.listdir(video_dir):
                    if file.endswith('.wav') and file != "vocals.wav" and file != "audio_vocals.wav":
                        vocal_audio_path = os.path.join(video_dir, file)
                        break
    
    if not os.path.exists(vocal_audio_path):
        logger.error("Could not find vocal audio file")
        sys.exit(1)
    
    logger.info(f"Found vocal audio: {vocal_audio_path}")
    
    # Step 5: Generate subtitles
    logger.info("Step 5: Generating subtitles")
    subtitle_cmd = [
        sys.executable, "core/audio/audio_to_subtitle.py",
        vocal_audio_path,
        "-m", args.subtitle_method,
        "--model", args.subtitle_model,
        "-d", args.device
    ]
    # Add diarization options
    if args.no_diarization:
        subtitle_cmd.append("--no-diarization")
    
    if args.min_speakers:
        subtitle_cmd.extend(["--min-speakers", str(args.min_speakers)])
    
    if args.max_speakers:
        subtitle_cmd.extend(["--max-speakers", str(args.max_speakers)])
    
    if not run_command(subtitle_cmd, "Subtitle generation"):
        logger.error("Pipeline failed at subtitle generation step")
        # Check if the error is related to CUDA, and try again with CPU
        if args.device == "cuda":
            logger.info("CUDA not available for subtitle generation, trying with CPU")
            subtitle_cmd = [
                sys.executable, "core/audio/audio_to_subtitle.py",
                vocal_audio_path,
                "-m", args.subtitle_method,
                "--model", args.subtitle_model,
                "-d", "cpu"
            ]
            # Add diarization options
            if args.no_diarization:
                subtitle_cmd.append("--no-diarization")
            
            if args.min_speakers:
                subtitle_cmd.extend(["--min-speakers", str(args.min_speakers)])
            
            if args.max_speakers:
                subtitle_cmd.extend(["--max-speakers", str(args.max_speakers)])
            
            if not run_command(subtitle_cmd, "Subtitle generation with CPU"):
                logger.error("Pipeline failed at subtitle generation step with CPU too")
                sys.exit(1)
        else:
            sys.exit(1)
    
    logger.success("Complete pipeline finished successfully!")
    logger.info(f"Video downloaded to: {video_path}")
    logger.info(f"Audio separated in: {video_dir}")
    logger.info(f"Subtitles generated in: {video_dir}")

if __name__ == "__main__":
    main()
