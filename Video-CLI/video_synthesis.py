"""
Module for video synthesis - combining video, audio, and subtitles
"""
import os
import sys
import argparse
from pathlib import Path
import subprocess
import json
from typing import Optional, List

try:
    import ffmpeg
except ImportError:
    print("ffmpeg-python is required. Install it using: pip install ffmpeg-python")
    sys.exit(1)


def add_audio_to_video(video_path: str, audio_path: str, output_path: str, volume: float = 1.0) -> bool:
    """
    Add audio track to video file
    
    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file
        output_path: Path for output video with audio
        volume: Volume multiplier for the audio (default 1.0)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path).filter('volume', volume)
        
        # Combine video and audio
        output = ffmpeg.output(
            video, 
            audio, 
            output_path,
            vcodec='copy',  # Copy video codec to avoid re-encoding
            acodec='aac',   # Use AAC for audio
            strict='experimental'
        )
        
        # Run the command
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        return True
    except ffmpeg.Error as e:
        print(f"Error adding audio to video: {e}")
        return False


def add_subtitles_to_video(video_path: str, subtitle_path: str, output_path: str, 
                          font_size: int = 24, font_color: str = 'white', 
                          border_color: str = 'black', border_width: int = 1) -> bool:
    """
    Add subtitles to video file using ffmpeg
    
    Args:
        video_path: Path to input video file
        subtitle_path: Path to subtitle file (.srt format)
        output_path: Path for output video with subtitles
        font_size: Size of subtitle font
        font_color: Color of subtitle text
        border_color: Color of subtitle border
        border_width: Width of subtitle border
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Use ffmpeg to burn subtitles into video
        video = ffmpeg.input(video_path)
        
        output = ffmpeg.output(
            video,
            output_path,
            vf=f"subtitles={subtitle_path}:force_style='Fontsize={font_size},Fontcolor={font_color},Outline={border_width},Outlinecolor={border_color}'",
            vcodec='libx264',
            acodec='copy'
        )
        
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        return True
    except ffmpeg.Error as e:
        print(f"Error adding subtitles to video: {e}")
        return False


def add_audio_and_subtitles_to_video(video_path: str, audio_path: str, subtitle_path: str, 
                                   output_path: str, volume: float = 1.0,
                                   font_size: int = 24, font_color: str = 'white', 
                                   border_color: str = 'black', border_width: int = 1) -> bool:
    """
    Add both audio and subtitles to video in a single operation
    
    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file
        subtitle_path: Path to subtitle file (.srt format)
        output_path: Path for output video with audio and subtitles
        volume: Volume multiplier for the audio
        font_size: Size of subtitle font
        font_color: Color of subtitle text
        border_color: Color of subtitle border
        border_width: Width of subtitle border
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a temporary file for the video with audio
        temp_video_with_audio = output_path.rsplit('.', 1)[0] + '_temp_with_audio.' + output_path.rsplit('.', 1)[1]
        
        # First, add audio to video
        if not add_audio_to_video(video_path, audio_path, temp_video_with_audio, volume):
            return False
        
        # Then, add subtitles to the video that already has audio
        success = add_subtitles_to_video(temp_video_with_audio, subtitle_path, output_path, 
                                       font_size, font_color, border_color, border_width)
        
        # Clean up temporary file
        if os.path.exists(temp_video_with_audio):
            os.remove(temp_video_with_audio)
        
        return success
    except Exception as e:
        print(f"Error in combined audio and subtitle addition: {e}")
        return False


def create_video_with_custom_audio_subtitles(video_path: str, audio_path: str, subtitle_path: str, 
                                           output_path: str, volume: float = 1.0,
                                           font_size: int = 24, font_color: str = 'white', 
                                           border_color: str = 'black', border_width: int = 1,
                                           audio_only: bool = False, subtitles_only: bool = False) -> bool:
    """
    Main function to create a video with custom audio and/or subtitles
    
    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file
        subtitle_path: Path to subtitle file (.srt format)
        output_path: Path for output video
        volume: Volume multiplier for the audio
        font_size: Size of subtitle font
        font_color: Color of subtitle text
        border_color: Color of subtitle border
        border_width: Width of subtitle border
        audio_only: If True, only add audio (no subtitles)
        subtitles_only: If True, only add subtitles (no audio)
    
    Returns:
        True if successful, False otherwise
    """
    if audio_only and subtitles_only:
        print("Error: Cannot set both audio_only and subtitles_only to True")
        return False
    
    if audio_only:
        return add_audio_to_video(video_path, audio_path, output_path, volume)
    elif subtitles_only:
        return add_subtitles_to_video(video_path, subtitle_path, output_path, 
                                   font_size, font_color, border_color, border_width)
    else:
        # Add both audio and subtitles
        return add_audio_and_subtitles_to_video(video_path, audio_path, subtitle_path, 
                                              output_path, volume, font_size, font_color, 
                                              border_color, border_width)


def main():
    parser = argparse.ArgumentParser(description='Add audio and/or subtitles to video')
    parser.add_argument('video_path', help='Path to input video file')
    parser.add_argument('--audio', '-a', help='Path to input audio file')
    parser.add_argument('--subtitles', '-s', help='Path to subtitle file (.srt)')
    parser.add_argument('--output', '-o', required=True, help='Path for output video')
    parser.add_argument('--volume', type=float, default=1.0, help='Audio volume multiplier (default: 1.0)')
    parser.add_argument('--font-size', type=int, default=24, help='Subtitle font size (default: 24)')
    parser.add_argument('--font-color', default='white', help='Subtitle font color (default: white)')
    parser.add_argument('--border-color', default='black', help='Subtitle border color (default: black)')
    parser.add_argument('--border-width', type=int, default=1, help='Subtitle border width (default: 1)')
    parser.add_argument('--audio-only', action='store_true', help='Only add audio, no subtitles')
    parser.add_argument('--subtitles-only', action='store_true', help='Only add subtitles, no audio')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.video_path):
        print(f"Error: Video file does not exist: {args.video_path}")
        return
    
    if not args.audio_only and not args.subtitles_only:
        if not args.audio:
            print("Error: Audio file is required when not using --audio-only or --subtitles-only")
            return
        if not args.subtitles:
            print("Error: Subtitle file is required when not using --audio-only or --subtitles-only")
            return
        
        if not os.path.exists(args.audio):
            print(f"Error: Audio file does not exist: {args.audio}")
            return
        if not os.path.exists(args.subtitles):
            print(f"Error: Subtitle file does not exist: {args.subtitles}")
            return
    elif args.audio_only:
        if not args.audio:
            print("Error: Audio file is required when using --audio-only")
            return
        if not os.path.exists(args.audio):
            print(f"Error: Audio file does not exist: {args.audio}")
            return
    elif args.subtitles_only:
        if not args.subtitles:
            print("Error: Subtitle file is required when using --subtitles-only")
            return
        if not os.path.exists(args.subtitles):
            print(f"Error: Subtitle file does not exist: {args.subtitles}")
            return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process the video
    success = create_video_with_custom_audio_subtitles(
        video_path=args.video_path,
        audio_path=args.audio,
        subtitle_path=args.subtitles,
        output_path=args.output,
        volume=args.volume,
        font_size=args.font_size,
        font_color=args.font_color,
        border_color=args.border_color,
        border_width=args.border_width,
        audio_only=args.audio_only,
        subtitles_only=args.subtitles_only
    )
    
    if success:
        print(f"Successfully created video with custom audio/subtitles: {args.output}")
    else:
        print("Failed to create video with custom audio/subtitles")
        sys.exit(1)


if __name__ == "__main__":
    main()
