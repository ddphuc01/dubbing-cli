#!/usr/bin/env python3
"""
Audio to Subtitle tool for Video-CLI
Converts audio files to subtitles with speaker diarization
Based on approach from Linly-Dubbing project
"""

import argparse
import os
import sys
import json
import time
import re
from typing import List, Dict, Optional, Any
from loguru import logger

try:
    import torch
    import librosa
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError as e:
    TORCH_AVAILABLE = False
    logger.warning(f"PyTorch or related libraries not available. Some features may be limited: {e}")

def format_time(seconds: float) -> str:
    """
    Convert seconds to SRT time format (HH:MM:SS,mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_time_vtt(seconds: float) -> str:
    """
    Convert seconds to VTT time format (HH:MM:SS.mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def save_srt(transcript: List[Dict[str, Any]], output_path: str, show_speaker: bool = False) -> None:
    """
    Save transcript as SRT subtitle file (like CapCut format)
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(transcript, 1):
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            text = segment['text']
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            
            # Option to show/hide speaker like CapCut
            if show_speaker:
                speaker = segment.get('speaker', 'SPEAKER_00')
                f.write(f"[{speaker}] {text}\n\n")
            else:
                f.write(f"{text}\n\n")  # CapCut style - no speaker tags
    
    logger.info(f"Saved SRT subtitles to: {output_path}")

def save_vtt(transcript: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save transcript as VTT subtitle file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for i, segment in enumerate(transcript, 1):
            start_time = format_time_vtt(segment['start'])
            end_time = format_time_vtt(segment['end'])
            speaker = segment.get('speaker', 'SPEAKER_00')
            text = segment['text']
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"<v {speaker}>{text}</v>\n\n")
    
    logger.info(f"Saved VTT subtitles to: {output_path}")

def save_txt(transcript: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save transcript as plain text file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for segment in transcript:
            start_time = format_time(segment['start'])
            speaker = segment.get('speaker', 'SPEAKER_00')
            text = segment['text']
            
            f.write(f"[{start_time}] [{speaker}] {text}\n")
    
    logger.info(f"Saved TXT transcript to: {output_path}")

def save_json(transcript: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save transcript as JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved JSON transcript to: {output_path}")

def optimize_funasr_segments(transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Optimize FunASR segments to match CapCut quality with user requirements:
    - Duration between 0.5s and 2s
    - Maximum 10 characters per segment
    """
    if not transcript:
        return []
    
    optimized = []
    
    for segment in transcript:
        text = segment['text']
        duration = segment['end'] - segment['start']
        speaker = segment['speaker']
        
        # Split long segments (>10s) into shorter ones
        if duration > 10.0:
            sentences = split_chinese_text(text)
            if len(sentences) > 1:
                sentence_duration = duration / len(sentences)
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        optimized.append({
                            'start': segment['start'] + (i * sentence_duration),
                            'end': segment['start'] + ((i + 1) * sentence_duration),
                            'text': sentence.strip(),
                            'speaker': speaker
                        })
            else:
                optimized.append(segment)
        else:
            # Keep segments under 10s as is
            optimized.append(segment)
    
    # Post-process segments to meet user requirements
    optimized = post_process_segments(optimized)
    
    return optimized

def split_chinese_text(text: str, max_length: int = 25) -> List[str]:
    """
    Split Chinese text into shorter segments like CapCut
    """
    # Split by Chinese punctuation first
    sentences = re.split(r'[。！？，；：]', text)
    
    result = []
    current = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If current + sentence is too long, save current and start new
        if len(current + sentence) > max_length and current:
            result.append(current.strip())
            current = sentence
        else:
            current = (current + sentence).strip()
    
    # Add remaining text
    if current:
        result.append(current.strip())
    
    return result if result else [text]


def post_process_segments(transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Post-process segments for better timing with user requirements:
    - Duration between 0.5s and 2s
    - Maximum 10 characters per segment
    """
    if not transcript:
        return []
    
    processed = []
    
    for segment in transcript:
        text = segment['text']
        start_time = segment['start']
        end_time = segment['end']
        duration = end_time - start_time
        speaker = segment['speaker']
        
        # Split text into chunks of max 10 characters
        text_chunks = []
        current_chunk = ""
        
        for char in text:
            if len(current_chunk) >= 10:
                text_chunks.append(current_chunk)
                current_chunk = char
            else:
                current_chunk += char
        
        if current_chunk:  # Add the last chunk if it exists
            text_chunks.append(current_chunk)
        
        # Calculate duration per character to distribute the total duration among chunks
        total_chars = len(text)
        if total_chars > 0:
            # Split the duration based on the number of chunks
            chunk_duration = duration / len(text_chunks) if len(text_chunks) > 0 else duration
            
            # Ensure chunk duration is within 0.5s to 2s range
            if chunk_duration < 0.5:
                chunk_duration = 0.5
            elif chunk_duration > 2.0:
                chunk_duration = 2.0
            
            # If the adjusted duration would exceed the total duration, adjust accordingly
            if chunk_duration * len(text_chunks) > duration:
                chunk_duration = duration / len(text_chunks) if len(text_chunks) > 0 else duration
            
            for i, chunk in enumerate(text_chunks):
                if chunk.strip():  # Only add non-empty chunks
                    chunk_start = start_time + (i * chunk_duration)
                    chunk_end = min(start_time + ((i + 1) * chunk_duration), end_time)
                    
                    processed.append({
                        'start': chunk_start,
                        'end': chunk_end,
                        'text': chunk.strip(),
                        'speaker': speaker
                    })
        else:
            # If no text, just add the original segment
            processed.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': text.strip(),
                'speaker': speaker
            })
    
    return processed


def merge_segments(transcript: List[Dict[str, Any]], ending='!"\').:;?]}~！“”’）。：；？】') -> List[Dict[str, Any]]:
    """
    Merge transcript segments based on punctuation
    """
    if not transcript:
        return []
        
    merged_transcription = []
    buffer_segment = None

    for segment in transcript:
        if buffer_segment is None:
            buffer_segment = segment
        else:
            # Check if the last character of the 'text' field is a punctuation mark
            if buffer_segment['text'][-1] in ending:
                # If it is, add the buffered segment to the merged transcription
                merged_transcription.append(buffer_segment)
                buffer_segment = segment
            else:
                # If it's not, merge this segment with the buffered segment
                buffer_segment['text'] += ' ' + segment['text']
                buffer_segment['end'] = segment['end']

    # Don't forget to add the last buffered segment
    if buffer_segment is not None:
        merged_transcription.append(buffer_segment)

    return merged_transcription

def generate_speaker_audio(audio_path: str, transcript: List[Dict[str, Any]], output_dir: str) -> None:
    """
    Generate separate audio files for each speaker
    """
    audio_data, samplerate = librosa.load(audio_path, sr=24000)
    speaker_dict = dict()
    length = len(audio_data)
    delay = 0.05
    
    for segment in transcript:
        start = max(0, int((segment['start'] - delay) * samplerate))
        end = min(int((segment['end']+delay) * samplerate), length)
        speaker_segment_audio = audio_data[start:end]
        speaker_dict[segment['speaker']] = np.concatenate((speaker_dict.get(
            segment['speaker'], np.zeros((0, ))), speaker_segment_audio))

    speaker_folder = os.path.join(output_dir, 'SPEAKER')
    if not os.path.exists(speaker_folder):
        os.makedirs(speaker_folder)
    
    for speaker, audio in speaker_dict.items():
        speaker_file_path = os.path.join(speaker_folder, f"{speaker}.wav")
        # Save the speaker audio file
        from scipy.io import wavfile
        wavfile.write(speaker_file_path, samplerate, (audio * 32767).astype(np.int16))
    
    logger.info(f"Generated speaker audio files in: {speaker_folder}")

def whisperx_transcribe_audio(wav_path: str, model_name: str = 'large', download_root: str = 'models/ASR/whisper', 
                             device: str = 'auto', batch_size: int = 10, diarization: bool = True, 
                             min_speakers: Optional[int] = None, max_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Transcribe audio using WhisperX with speaker diarization
    Based on Linly-Dubbing's implementation
    """
    try:
        import whisperx
        from dotenv import load_dotenv
        load_dotenv()  # Load environment variables from .env file
        
        if device == 'auto':
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"Loading WhisperX model: {model_name} on {device}")
        
        # Load the model with error handling for authorization issues
        try:
            model = whisperx.load_model(model_name, device=device, download_root=download_root)
        except Exception as e:
            if "401 Client Error" in str(e) or "Unauthorized" in str(e):
                logger.error("Failed to load model from Hugging Face Hub due to authorization error.")
                logger.error("Please ensure you have:")
                logger.error("1. Requested access to the model on Hugging Face (e.g., Systran/faster-whisper-large-v3)")
                logger.error("2. Set your HF_TOKEN in a .env file or environment variables")
                logger.error("3. Or download the model manually to your local download_root directory")
                raise
            elif "Cannot find an appropriate cached snapshot" in str(e):
                logger.error("Model not found in local cache and network access is disabled.")
                logger.error("Please ensure you have:")
                logger.error("1. Downloaded the model to your local download_root directory")
                logger.error("2. Or set up network access to download the model")
                raise
            else:
                raise
        
        # Transcribe with optimized parameters
        logger.info("Transcribing audio...")
        result = model.transcribe(wav_path, batch_size=batch_size)
        
        # Check if language was detected
        if result['language'] == 'nn':
            logger.warning(f'No language detected in {wav_path}')
            return []
        
        # Align with tighter parameters
        logger.info("Aligning transcript...")
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result = whisperx.align(
            result["segments"], 
            model_a, 
            metadata, 
            wav_path, 
            device,
            return_char_alignments=False  # Speed up
        )
        
        # Diarize
        if diarization:
            logger.info("Performing speaker diarization...")
            try:
                # Use the HF token if available for diarization
                hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
                if hf_token:
                    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
                else:
                    logger.warning("HF_TOKEN not found in environment variables.")
                    logger.warning("To enable speaker diarization, please request access to pyannote/speaker-diarization-3.1 on Hugging Face")
                    logger.warning("and set your HF_TOKEN in a .env file or environment variables.")
                    diarize_model = whisperx.DiarizationPipeline(device=device)
                
                diarize_segments = diarize_model(wav_path, min_speakers=min_speakers, max_speakers=max_speakers)
                result = whisperx.assign_word_speakers(diarize_segments, result)
            except Exception as e:
                logger.warning(f"Speaker diarization failed: {str(e)}")
                logger.warning("Continuing without speaker diarization...")
        
        # Format transcript
        transcript = []
        for segment in result['segments']:
            transcript.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'speaker': segment.get('speaker', 'SPEAKER_00')
            })
        
        return transcript
    
    except ImportError:
        logger.error("WhisperX not installed. Please install it with: pip install git+https://github.com/m-bain/whisperx.git")
        raise
    except Exception as e:
        logger.error(f"Error in WhisperX transcription: {str(e)}")
        raise

def funasr_transcribe_audio(wav_path: str, device: str = 'auto', batch_size: int = 1, diarization: bool = True) -> List[Dict[str, Any]]:
    """
    Transcribe audio using FunASR with optimized segmentation like CapCut
    """
    try:
        from funasr import AutoModel
        import torch
        from dotenv import load_dotenv
        load_dotenv() # Load environment variables from .env file
        
        if device == 'auto':
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"Loading FunASR model on {device}")
        
        # Define model file paths
        model_path = "models/ASR/FunASR/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
        vad_model_path = "models/ASR/FunASR/speech_fsmn_vad_zh-cn-16k-common-pytorch"
        punc_model_path = "models/ASR/FunASR/punc_ct-transformer_cn-en-common-vocab471067-large"
        spk_model_path = "models/ASR/FunASR/speech_campplus_sv_zh-cn_16k-common"
        
        # Load models, using local paths if they exist, otherwise use default online models
        model = AutoModel(
            model=model_path if os.path.isdir(model_path) else "paraformer-zh",
            vad_model=vad_model_path if os.path.isdir(vad_model_path) else "fsmn-vad",
            punc_model=punc_model_path if os.path.isdir(punc_model_path) else "ct-punc",
            spk_model=spk_model_path if os.path.isdir(spk_model_path) else "cam++",
        )
        logger.info("Transcribing audio...")
        result = model.generate(
            wav_path,
            device=device, 
            return_spk_res=True if diarization else False,
            sentence_timestamp=True,
            return_raw_text=True,
            is_final=True,
            batch_size_s=30,  # Even shorter batch for better segmentation
            batch_size_threshold_s=20,  # Lower threshold
            merge_vad=True,  # Enable VAD merging
            merge_length_s=5  # Merge segments longer than 5s (shorter than before)
        )[0]
        
        # Extract and optimize segments
        transcript = []
        for sentence in result['sentence_info']:
            # Fix timing calculation (was /100, should be /1000)
            start_time = sentence['timestamp'][0][0] / 1000
            end_time = sentence['timestamp'][-1][-1] / 1000
            text = sentence['text'].strip()
            
            # Skip empty segments
            if not text:
                continue
            
            # Extract speaker if diarization enabled
            speaker_id = sentence.get('spk', 0) if diarization and 'spk' in sentence else 0
            speaker = f"SPEAKER_{speaker_id:02d}" if diarization else "SPEAKER_00"
            
            # Create initial segment
            segment = {
                'start': start_time,
                'end': end_time,
                'text': text,
                'speaker': speaker
            }
            
            transcript.append(segment)
        
        # Post-process segments for better timing and more segments
        transcript = optimize_funasr_segments(transcript)
        
        return transcript
    
    except ImportError:
        logger.error("FunASR not installed. Please install it with: pip install funasr")
        raise
    except Exception as e:
        logger.error(f"Error in FunASR transcription: {str(e)}")
        raise

def transcribe_audio(audio_path: str, method: str = 'WhisperX', model_name: str = 'large', 
                     download_root: str = 'models/ASR/whisper', device: str = 'auto', 
                     batch_size: int = 10, diarization: bool = True, 
                     min_speakers: Optional[int] = None, max_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Transcribe audio file using specified method
    """
    logger.info(f"Starting transcription of: {audio_path}")
    logger.info(f"Method: {method}, Model: {model_name}, Device: {device}")
    logger.info(f"Diarization: {diarization}")
    
    if method == 'WhisperX':
        transcript = whisperx_transcribe_audio(
            audio_path, model_name, download_root, device, batch_size, diarization, min_speakers, max_speakers
        )
    elif method == 'FunASR':
        transcript = funasr_transcribe_audio(
            audio_path, device, batch_size, diarization
        )
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return transcript

def audio_to_subtitle(audio_path: str, output_dir: Optional[str] = None, method: str = 'WhisperX', 
                      model_name: str = 'large', download_root: str = 'models/ASR/whisper', 
                      device: str = 'auto', batch_size: int = 10, diarization: bool = True, 
                      min_speakers: Optional[int] = None, max_speakers: Optional[int] = None,
                      formats: List[str] = ['srt', 'vtt', 'txt', 'json'], merge_segments_flag: bool = True,
                      generate_speaker_audio_flag: bool = False, show_speaker_flag: bool = False) -> List[Dict[str, Any]]:
    """
    Convert audio file to subtitle files in multiple formats
    """
    if not output_dir:
        output_dir = os.path.dirname(audio_path) or '.'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Transcribe audio
    transcript = transcribe_audio(
        audio_path, method, model_name, download_root, device, batch_size, diarization, 
        min_speakers, max_speakers
    )
    
    # Merge segments if requested
    if merge_segments_flag:
        transcript = merge_segments(transcript)
    
    # Apply optimization for FunASR segments to match CapCut-style quality
    if method == 'FunASR':
        transcript = optimize_funasr_segments(transcript)
        transcript = post_process_segments(transcript)
    # Generate speaker audio files if requested
    if generate_speaker_audio_flag:
        generate_speaker_audio(audio_path, transcript, output_dir)
    
    # Save transcript in various formats
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    if 'json' in formats:
        json_path = os.path.join(output_dir, f'{base_name}_transcript.json')
        save_json(transcript, json_path)
    
    if 'srt' in formats:
        srt_path = os.path.join(output_dir, f'{base_name}.srt')
        save_srt(transcript, srt_path, show_speaker_flag)
    
    if 'vtt' in formats:
        vtt_path = os.path.join(output_dir, f'{base_name}.vtt')
        save_vtt(transcript, vtt_path)
    
    if 'txt' in formats:
        txt_path = os.path.join(output_dir, f'{base_name}_transcript.txt')
        save_txt(transcript, txt_path)
    
    logger.success(f"Audio to subtitle conversion completed successfully!")
    logger.info(f"Generated {len(transcript)} segments with {len(set(seg['speaker'] for seg in transcript))} speakers")
    
    return transcript

def main():
    parser = argparse.ArgumentParser(description="Convert audio files to subtitles with speaker diarization (Linly-Dubbing approach)")
    parser.add_argument("audio_path", help="Path to the audio file")
    parser.add_argument("-o", "--output-dir", help="Output directory for subtitle files")
    parser.add_argument("-m", "--method", default="FunASR", choices=["WhisperX", "FunASR"], 
                        help="ASR method to use")
    parser.add_argument("--model", default="large", help="Model name (for WhisperX: base, small, medium, large)")
    parser.add_argument("--download-root", default="models/ASR/whisper", help="Download root for Whisper models")
    parser.add_argument("-d", "--device", default="auto", choices=["auto", "cpu", "cuda"], 
                        help="Device to use for processing")
    parser.add_argument("-b", "--batch-size", type=int, default=10, help="Batch size for processing")
    parser.add_argument("--no-diarization", action="store_true", 
                        help="Disable speaker diarization")
    parser.add_argument("--min-speakers", type=int, help="Minimum number of speakers")
    parser.add_argument("--max-speakers", type=int, help="Maximum number of speakers")
    parser.add_argument("--formats", nargs='+', default=['srt', 'vtt', 'txt', 'json'], 
                        choices=['srt', 'vtt', 'txt', 'json'],
                        help="Subtitle formats to generate")
    parser.add_argument("--no-merge-segments", action="store_true", 
                        help="Disable merging segments based on punctuation")
    parser.add_argument("--generate-speaker-audio", action="store_true", 
                        help="Generate separate audio files for each speaker")
    parser.add_argument("--show-speaker", action="store_true", 
                        help="Show speaker labels in subtitles (default: hide like CapCut)")
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.audio_path):
        logger.error(f"Audio file not found: {args.audio_path}")
        sys.exit(1)
    
    # Check if file is audio
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.opus']
    if not any(args.audio_path.lower().endswith(ext) for ext in audio_extensions):
        logger.warning(f"File {args.audio_path} doesn't have a recognized audio extension, but will attempt to process it")
    
    # Set output directory
    output_dir = args.output_dir or os.path.dirname(args.audio_path) or '.'
    
    try:
        transcript = audio_to_subtitle(
            audio_path=args.audio_path,
            output_dir=output_dir,
            method=args.method,
            model_name=args.model,
            download_root=args.download_root,
            device=args.device,
            batch_size=args.batch_size,
            diarization=not args.no_diarization,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            formats=args.formats,
            merge_segments_flag=not args.no_merge_segments,
            generate_speaker_audio_flag=args.generate_speaker_audio,
            show_speaker_flag=args.show_speaker
        )
        
        logger.success("Audio to subtitle conversion completed successfully!")
        logger.info(f"Generated {len(transcript)} segments with {len(set(seg['speaker'] for seg in transcript))} speakers")
        
    except Exception as e:
        logger.error(f"Audio to subtitle conversion failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
