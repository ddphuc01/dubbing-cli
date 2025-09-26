#!/usr/bin/env python3
"""
Example script to demonstrate the SRT to Audio functionality
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Example script for SRT to Audio functionality")
    parser.add_argument("--srt-file", required=True, help="Path to the SRT file to convert")
    parser.add_argument("--output-dir", default="./tts_output", help="Output directory for generated audio files")
    parser.add_argument("--method", default="edge", choices=["edge", "gtts"], 
                        help="TTS method to use (default: edge)")
    parser.add_argument("--voice", default="en-US-MichelleNeural", 
                        help="Voice to use for Edge TTS (default: en-US-MichelleNeural)")
    parser.add_argument("--language", default="en", 
                        help="Language code for TTS (default: en)")
    
    args = parser.parse_args()
    
    # Verify the SRT file exists
    if not os.path.exists(args.srt_file):
        print(f"Error: SRT file does not exist: {args.srt_file}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Converting SRT file: {args.srt_file}")
    print(f"Output directory: {args.output_dir}")
    print(f"TTS method: {args.method}")
    print(f"Voice: {args.voice}")
    print(f"Language: {args.language}")
    
    # Import and run the srt_to_audio functionality
    try:
        from srt_to_audio import srt_to_audio
        
        audio_files = srt_to_audio(
            srt_path=args.srt_file,
            output_dir=args.output_dir,
            tts_method=args.method,
            voice=args.voice,
            language=args.language
        )
        
        print(f"\nSuccessfully generated {len(audio_files)} audio files:")
        for audio_file in audio_files:
            print(f" - {audio_file}")
        
        # Optionally combine all audio files into one
        from srt_to_audio import combine_audio_files
        if audio_files:
            combined_path = os.path.join(args.output_dir, "combined_audio.wav")
            combine_audio_files(audio_files, combined_path)
            print(f"\nCombined audio saved to: {combined_path}")
        
    except ImportError as e:
        print(f"Error importing srt_to_audio: {e}")
        print("Make sure you're running this script from the Video-CLI directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error during SRT to audio conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
