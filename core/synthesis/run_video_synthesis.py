"""
Script to demonstrate video synthesis functionality
"""
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the path so we can import video_synthesis
sys.path.insert(0, str(Path(__file__).parent))

from video_synthesis import create_video_with_custom_audio_subtitles, add_audio_to_video, add_subtitles_to_video


def main():
    parser = argparse.ArgumentParser(description='Video Synthesis - Add audio and/or subtitles to video')
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
