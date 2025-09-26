#!/usr/bin/env python3
"""
SRT to Audio tool for Video-CLI
Converts SRT subtitle files to synchronized audio for video dubbing
Based on approaches from SoniTranslate and Linly-Dubbing projects
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
from loguru import logger

try:
    import torch
    import librosa
    import soundfile as sf
    TORCH_AVAILABLE = True
except ImportError as e:
    TORCH_AVAILABLE = False
    logger.warning(f"PyTorch or related libraries not available. Some features may be limited: {e}")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge-tts not available. Install with: pip install edge-tts")

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("TTS (Coqui TTS) not available. Install with: pip install TTS")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available. Install with: pip install gtts")

def parse_srt_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT content into list of subtitle entries
    """
    entries = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for entry in entries:
        if entry.strip():
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = lines[0] if lines[0].isdigit() else ''
                    time_line = lines[1] if '-->' in lines[1] else ''
                    text_lines = lines[2:] if time_line else lines[1:]
                    text = '\n'.join(text_lines)
                    
                    # Parse time codes
                    if time_line:
                        time_parts = time_line.split(' --> ')
                        if len(time_parts) == 2:
                            start_time_str = time_parts[0].strip()
                            end_time_str = time_parts[1].strip()
                            
                            # Convert time format to seconds
                            start_seconds = time_to_seconds(start_time_str)
                            end_seconds = time_to_seconds(end_time_str)
                            
                            subtitles.append({
                                'index': index,
                                'start_time': start_time_str,
                                'end_time': end_time_str,
                                'start_seconds': start_seconds,
                                'end_seconds': end_seconds,
                                'duration': end_seconds - start_seconds,
                                'text': text.strip()
                            })
                except Exception as e:
                    logger.warning(f"Error parsing SRT entry: {e}")
                    continue
    return subtitles

def time_to_seconds(time_str: str) -> float:
    """
    Convert SRT time format (HH:MM:SS,mmm) to seconds
    """
    time_parts = time_str.replace(',', '.').split(':')
    if len(time_parts) == 3:
        hours, minutes, seconds = time_parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return 0.0

def format_time(seconds: float) -> str:
    """
    Convert seconds to SRT time format (HH:MM:SS,mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def load_srt_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Load and parse SRT file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_srt_content(content)

def clean_text(text: str) -> str:
    """
    Clean subtitle text for TTS processing
    """
    # Remove content within square brackets
    text = re.sub(r'\[.*?\]', '', text)
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove "♫" and "♪" content
    text = re.sub(r'♫.*?♫', '', text)
    text = re.sub(r'♪.*?♪', '', text)
    # Replace newline characters with spaces
    text = text.replace("\n", " ")
    # Remove double quotation marks
    text = text.replace('"', '')
    # Collapse multiple spaces and replace with a single space
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def stretch_audio_to_duration(audio_path: str, target_duration: float, output_path: str):
    """
    Stretch audio to match target duration using librosa
    """
    try:
        audio, sr = librosa.load(audio_path, sr=24000)
        current_duration = librosa.get_duration(y=audio, sr=sr)
        
        if current_duration > 0:
            speed_factor = current_duration / target_duration
            # Use librosa to time-stretch
            stretched_audio = librosa.effects.time_stretch(audio, rate=speed_factor)
            
            # Trim or pad to exact duration
            target_samples = int(target_duration * sr)
            if len(stretched_audio) > target_samples:
                stretched_audio = stretched_audio[:target_samples]
            elif len(stretched_audio) < target_samples:
                # Pad with zeros
                padding = target_samples - len(stretched_audio)
                stretched_audio = np.pad(stretched_audio, (0, padding), mode='constant')
            
            sf.write(output_path, stretched_audio, sr)
        else:
            # If audio is empty, create silent audio of target duration
            sr = 24000
            silent_audio = np.zeros(int(target_duration * sr))
            sf.write(output_path, silent_audio, sr)
    except Exception as e:
        logger.error(f"Error stretching audio: {e}")
        # If stretching fails, create silent audio
        sr = 24000
        silent_audio = np.zeros(int(target_duration * sr))
        sf.write(output_path, silent_audio, sr)

async def generate_edge_tts_audio(text: str, output_path: str, voice: str = "en-US-MichelleNeural"):
    """
    Generate audio using Edge TTS
    """
    if not EDGE_TTS_AVAILABLE:
        raise ImportError("edge-tts is not installed. Please install with: pip install edge-tts")
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        logger.info(f"Generated audio with Edge TTS: {output_path}")
    except Exception as e:
        logger.error(f"Edge TTS generation failed: {e}")
        raise

def generate_gtts_audio(text: str, output_path: str, lang: str = "en", speed: float = 1.0):
    """
    Generate audio using gTTS as fallback
    """
    if not GTTS_AVAILABLE:
        raise ImportError("gTTS is not installed. Please install with: pip install gtts")
    
    try:
        # gTTS doesn't have a direct speed parameter, so we'll need to handle it differently
        # For now, we'll just use the default speed, but we could post-process the audio to change speed
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        logger.info(f"Generated audio with gTTS: {output_path}")
    except Exception as e:
        logger.error(f"gTTS generation failed: {e}")
        raise

def generate_xtts_audio(text: str, output_path: str, speaker_wav: str, language: str = "en"):
    """
    Generate audio using XTTS
    """
    if not TTS_AVAILABLE:
        raise ImportError("TTS (Coqui TTS) is not installed. Please install with: pip install TTS")
    
    try:
        # Initialize TTS with XTTS model
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        
        # Generate speech with voice cloning
        wav = tts.tts(text, speaker_wav=speaker_wav, language=language)
        
        # Save the generated audio
        sf.write(output_path, wav, 24000)
        logger.info(f"Generated audio with XTTS: {output_path}")
    except Exception as e:
        logger.error(f"XTTS generation failed: {e}")
        raise

def srt_to_audio(srt_path: str, output_dir: Optional[str] = None, tts_method: str = "edge", 
                 voice: str = "en-US-MichelleNeural", speaker_wav: Optional[str] = None, 
                 language: str = "en", stretch_audio: bool = True) -> List[str]:
    """
    Convert SRT file to synchronized audio files
    """
    if not output_dir:
        # Create an output folder with the same name as the input SRT file
        srt_filename = Path(srt_path).stem  # Get the filename without extension
        output_dir = os.path.join(os.path.dirname(srt_path) or '.', srt_filename + '_tts_output')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and parse SRT file
    logger.info(f"Loading SRT file: {srt_path}")
    subtitles = load_srt_file(srt_path)
    
    if not subtitles:
        logger.error(f"No subtitles found in {srt_path}")
        return []
    
    logger.info(f"Loaded {len(subtitles)} subtitle entries")
    
    # Generate audio for each subtitle
    audio_files = []
    
    for i, subtitle in enumerate(subtitles):
        text = clean_text(subtitle['text'])
        
        # Skip empty subtitles
        if not text.strip():
            logger.info(f"Skipping empty subtitle at index {subtitle['index']}")
            continue
        
        # Create output filename based on start time
        start_time_formatted = format_time(subtitle['start_seconds']).replace(':', '_').replace(',', '_')
        output_filename = f"audio_{start_time_formatted}.wav"
        output_path = os.path.join(output_dir, output_filename)
        
        logger.info(f"Processing subtitle {i+1}/{len(subtitles)}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        try:
            # Generate audio based on selected TTS method
            if tts_method == "edge" and EDGE_TTS_AVAILABLE:
                import asyncio
                try:
                    asyncio.run(generate_edge_tts_audio(text, output_path, voice))
                except Exception as e:
                    logger.warning(f"Edge TTS failed for text: '{text[:50]}...', trying gTTS as fallback: {e}")
                    # Determine language automatically based on text content
                    detected_lang = "zh" if any(ord(char) > 127 for char in text) else language
                    generate_gtts_audio(text, output_path, detected_lang)
            elif tts_method == "xtts" and TTS_AVAILABLE and speaker_wav:
                generate_xtts_audio(text, output_path, speaker_wav, language)
            elif tts_method == "gtts" and GTTS_AVAILABLE:
                generate_gtts_audio(text, output_path, language)
            else:
                # Default to gTTS if available, otherwise raise error
                if GTTS_AVAILABLE:
                    # Determine language automatically based on text content
                    detected_lang = "zh" if any(ord(char) > 127 for char in text) else language
                    generate_gtts_audio(text, output_path, detected_lang)
                else:
                    raise ImportError("No TTS engine available. Please install at least one: edge-tts, TTS, or gtts")
            # Stretch audio to match subtitle duration if requested
            if stretch_audio and subtitle['duration'] > 0:
                stretched_path = output_path.replace('.wav', '_stretched.wav')
                stretch_audio_to_duration(output_path, subtitle['duration'], stretched_path)
                
                # Replace original with stretched version
                os.remove(output_path)
                os.rename(stretched_path, output_path)
            
            audio_files.append(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate audio for subtitle {subtitle['index']}: {e}")
            # Create silent audio as fallback
            sr = 24000
            silent_audio = np.zeros(int(subtitle['duration'] * sr))
            sf.write(output_path, silent_audio, sr)
            audio_files.append(output_path)
    
    logger.success(f"TTS conversion completed! Generated {len(audio_files)} audio files in {output_dir}")
    return audio_files

def combine_audio_files(audio_files: List[str], output_path: str):
    """
    Combine multiple audio files into a single audio file
    """
    if not audio_files:
        logger.warning("No audio files to combine")
        return
    
    combined_audio = np.array([])
    sr = 24000
    
    for audio_file in audio_files:
        audio, file_sr = librosa.load(audio_file, sr=sr)
        combined_audio = np.concatenate([combined_audio, audio])
    
    sf.write(output_path, combined_audio, sr)
    logger.info(f"Combined audio saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert SRT subtitle files to synchronized audio for video dubbing")
    parser.add_argument("srt_path", help="Path to the SRT subtitle file")
    parser.add_argument("-o", "--output-dir", help="Output directory for generated audio files")
    parser.add_argument("--method", default="edge", choices=["edge", "xtts", "gtts"], 
                        help="TTS method to use (default: edge)")
    parser.add_argument("--voice", default="en-US-MichelleNeural", 
                        help="Voice to use for Edge TTS (default: en-US-MichelleNeural)")
    parser.add_argument("--speaker-wav", 
                        help="Path to speaker reference audio file for XTTS voice cloning")
    parser.add_argument("--language", default="en", 
                        help="Language code for TTS (default: en)")
    parser.add_argument("--no-stretch", action="store_true", 
                        help="Disable audio stretching to match subtitle duration")
    parser.add_argument("--combine", action="store_true", 
                        help="Combine all generated audio files into a single file")
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.srt_path):
        logger.error(f"SRT file not found: {args.srt_path}")
        sys.exit(1)
    
    if args.method == "xtts" and not args.speaker_wav:
        logger.error("XTTS method requires a speaker reference audio file (--speaker-wav)")
        sys.exit(1)
    
    if args.method == "xtts" and not os.path.exists(args.speaker_wav):
        logger.error(f"Speaker reference file not found: {args.speaker_wav}")
        sys.exit(1)
    
    try:
        # Generate audio files
        audio_files = srt_to_audio(
            srt_path=args.srt_path,
            output_dir=args.output_dir,
            tts_method=args.method,
            voice=args.voice,
            speaker_wav=args.speaker_wav,
            language=args.language,
            stretch_audio=not args.no_stretch
        )
        
        # Combine audio files if requested
        if args.combine and audio_files:
            output_dir = args.output_dir or os.path.dirname(args.srt_path)
            combined_path = os.path.join(output_dir, "combined_audio.wav")
            combine_audio_files(audio_files, combined_path)
        
        logger.success("SRT to audio conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"SRT to audio conversion failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
