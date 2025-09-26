#!/usr/bin/env python3
"""
Simple SRT translation module using local models
"""

import os
import json
import time
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTranslator:
    """Simple translator using local models"""
    
    def __init__(self):
        """Initialize the simple translator"""
        self.device = "cpu"  # Default to CPU
        logger.info(f"Simple translator using device: {self.device}")
        
        # Try to import required libraries
        try:
            import torch
            self.torch_available = True
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("CUDA available, using GPU for translation")
            else:
                logger.info("CUDA not available, using CPU for translation")
        except ImportError:
            self.torch_available = False
            logger.warning("PyTorch not available, translation may be slower")
        
        # Try to import transformers
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            self.transformers_available = True
            logger.info("Transformers library available")
        except ImportError:
            self.transformers_available = False
            logger.warning("Transformers library not available, install with: pip install transformers")
        
        # Load model if possible
        self.model = None
        self.tokenizer = None
        if self.torch_available and self.transformers_available:
            self._load_model()
    
    def _load_model(self):
        """Load translation model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            model_name = "Helsinki-NLP/opus-mt-zh-vi"
            logger.info(f"Loading model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            if self.device == "cuda":
                self.model = self.model.cuda()
            
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def translate_text(self, text: str) -> str:
        """
        Translate text from Chinese to Vietnamese using local model
        
        Args:
            text: Input text in Chinese
            
        Returns:
            Translated text in Vietnamese
        """
        if not text or not text.strip():
            return text
        
        # If model is not available, return original text
        if not self.model or not self.tokenizer:
            logger.warning("Translation model not available, returning original text")
            return text
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Move to device if using CUDA
            if self.device == "cuda":
                inputs = {key: value.cuda() for key, value in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode output
            translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated_text.strip()
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text as fallback

def parse_srt_time(time_str: str) -> timedelta:
    """
    Parse SRT time format to timedelta
    
    Args:
        time_str: Time string in SRT format (HH:MM:SS,mmm)
        
    Returns:
        Timedelta object
    """
    hours, minutes, seconds_ms = time_str.split(":")
    seconds, milliseconds = seconds_ms.split(",")
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(milliseconds)
    )

def format_srt_time(td: timedelta) -> str:
    """
    Format timedelta to SRT time format
    
    Args:
        td: Timedelta object
        
    Returns:
        Time string in SRT format (HH:MM:SS,mmm)
    """
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def parse_srt_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse SRT content into list of subtitle entries
    
    Args:
        content: SRT file content as string
        
    Returns:
        List of subtitle dictionaries with index, start, end, and text
    """
    subtitles = []
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Parse index
            index = lines[0] if lines[0].isdigit() else ''
            
            # Parse time
            time_line = lines[1] if '-->' in lines[1] else ''
            if time_line:
                time_parts = time_line.split(' --> ')
                if len(time_parts) == 2:
                    start_time = time_parts[0].strip()
                    end_time = time_parts[1].strip()
                else:
                    start_time = ''
                    end_time = ''
            else:
                start_time = ''
                end_time = ''
            
            # Parse text
            text_lines = lines[2:] if time_line else lines[1:]
            text = '\n'.join(text_lines)
            
            subtitles.append({
                'index': index,
                'start': start_time,
                'end': end_time,
                'text': text
            })
    
    return subtitles

def compose_srt_content(subtitles: List[Dict[str, Any]]) -> str:
    """
    Compose list of subtitle entries into SRT content
    
    Args:
        subtitles: List of subtitle dictionaries
        
    Returns:
        SRT content as string
    """
    srt_blocks = []
    
    for sub in subtitles:
        if sub['index'] and sub['start'] and sub['end'] and sub['text']:
            block = f"{sub['index']}\n{sub['start']} --> {sub['end']}\n{sub['text']}"
            srt_blocks.append(block)
        else:
            # Handle malformed entries
            if sub['text']:
                block = sub['text']
                srt_blocks.append(block)
    
    return '\n\n'.join(srt_blocks)

def translate_srt_file(input_file: str, output_file: str, batch_size: int = 32) -> None:
    """
    Translate SRT file from Chinese to Vietnamese using local model
    
    Args:
        input_file: Path to input SRT file
        output_file: Path to output SRT file
        batch_size: Batch size for translation (default: 32)
    """
    logger.info(f"Starting translation of {input_file}")
    
    # Initialize translator
    translator = SimpleTranslator()
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Read {len(content)} characters from {input_file}")
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        raise
    
    # Parse SRT content
    subtitles = parse_srt_content(content)
    logger.info(f"Parsed {len(subtitles)} subtitle entries")
    
    if not subtitles:
        logger.warning("No subtitles found in file")
        return
    
    # Translate subtitles in batches
    translated_subtitles = []
    total_batches = (len(subtitles) + batch_size - 1) // batch_size
    
    logger.info(f"Translating in {total_batches} batches of {batch_size}")
    
    start_time = time.time()
    
    for batch_idx in range(total_batches):
        start_pos = batch_idx * batch_size
        end_pos = min((batch_idx + 1) * batch_size, len(subtitles))
        batch = subtitles[start_pos:end_pos]
        
        logger.info(f"Processing batch {batch_idx + 1}/{total_batches} ({len(batch)} entries)")
        
        for subtitle in batch:
            try:
                original_text = subtitle.get('text', '')
                if original_text.strip():
                    # Translate text
                    translated_text = translator.translate_text(original_text)
                    
                    # Create translated subtitle
                    translated_subtitle = subtitle.copy()
                    translated_subtitle['text'] = translated_text
                    translated_subtitle['original_text'] = original_text
                    translated_subtitles.append(translated_subtitle)
                    
                    logger.debug(f"Translated: '{original_text[:50]}...' -> '{translated_text[:50]}...'")
                else:
                    # Keep empty subtitles as-is
                    translated_subtitles.append(subtitle)
                    
            except Exception as e:
                logger.error(f"Error translating subtitle: {e}")
                # Keep original subtitle if translation fails
                translated_subtitles.append(subtitle)
        
        # Progress update
        elapsed = time.time() - start_time
        progress = min((batch_idx + 1) * batch_size, len(subtitles))
        estimated_total = elapsed * len(subtitles) / progress
        remaining = estimated_total - elapsed
        
        logger.info(f"Processed {progress}/{len(subtitles)} subtitles. "
                   f"Estimated time remaining: {remaining:.1f}s")
    
    total_time = time.time() - start_time
    logger.info(f"Translation completed in {total_time:.2f}s")
    
    # Compose translated SRT content
    translated_content = compose_srt_content(translated_subtitles)
    
    # Write output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        logger.info(f"Wrote translated content to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        raise
    
    logger.info("Translation process completed successfully")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Translate SRT subtitles from Chinese to Vietnamese")
    parser.add_argument("input_file", help="Input SRT file")
    parser.add_argument("-o", "--output", help="Output SRT file (default: input_vn.srt)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for translation (default: 32)")
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output or input_file.replace('.srt', '_vn.srt')
    batch_size = args.batch_size
    
    try:
        translate_srt_file(input_file, output_file, batch_size)
        print(f"Successfully translated {input_file} to {output_file}")
    except Exception as e:
        print(f"Translation failed: {e}")
        raise

if __name__ == "__main__":
    main()
