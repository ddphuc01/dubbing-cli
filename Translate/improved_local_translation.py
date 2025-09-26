import srt
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, M2M100Tokenizer, M2M100ForConditionalGeneration
from typing import List, Dict
import time
import logging
from tqdm import tqdm
from character_names import CharacterNameManager
import json
import os

# Set up logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('improved_local_translation.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class ImprovedLocalTranslator:
    """Improved local translator with better models and processing pipeline."""
    
    def __init__(self, model_type: str = "m2m100"):
        """
        Initialize the improved local translator with a specified model.
        
        Args:
            model_type: Type of model to use ("m2m100", "nllb", or "opus")
        """
        self.model_type = model_type
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load appropriate model based on type
        if model_type == "m2m100":
            self.model_name = "facebook/m2m100_418M"
            logger.info(f"Loading M2M100 model: {self.model_name}")
            self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_name)
            self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_name)
        elif model_type == "nllb":
            self.model_name = "facebook/nllb-200-distilled-600M"
            logger.info(f"Loading NLLB model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        else:  # opus (default)
            self.model_name = "Helsinki-NLP/opus-mt-zh-vi"
            logger.info(f"Loading OPUS model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("Model loaded successfully")
    
    def translate_text(self, text: str, src_lang: str = "zh", tgt_lang: str = "vi") -> str:
        """
        Translate a single text from source language to target language.
        
        Args:
            text: Input text in source language
            src_lang: Source language code (default: zh - Chinese)
            tgt_lang: Target language code (default: vi - Vietnamese)
            
        Returns:
            Translated text in target language
        """
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Set language pairs for M2M100 and NLLB
        if self.model_type in ["m2m100", "nllb"]:
            self.tokenizer.src_lang = src_lang
        
        # Tokenize the input text
        inputs = self.tokenizer(processed_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            if self.model_type == "m2m100":
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
                    max_length=512,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False
                )
            else:
                generated_tokens = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False
                )
        
        # Decode the output
        translated_text = self.tokenizer.decode(generated_tokens[0], skip_special_tokens=True)
        
        # Postprocess text
        final_text = self._postprocess_text(translated_text)
        
        return final_text
    
    def translate_batch(self, texts: List[str], src_lang: str = "zh", tgt_lang: str = "vi") -> List[str]:
        """
        Translate a batch of texts from source language to target language.
        
        Args:
            texts: List of input texts in source language
            src_lang: Source language code (default: zh - Chinese)
            tgt_lang: Target language code (default: vi - Vietnamese)
            
        Returns:
            List of translated texts in target language
        """
        # Preprocess texts
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Set language pairs for M2M100 and NLLB
        if self.model_type in ["m2m100", "nllb"]:
            self.tokenizer.src_lang = src_lang
        
        # Tokenize the input texts
        inputs = self.tokenizer(processed_texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        # Generate translations
        with torch.no_grad():
            if self.model_type == "m2m100":
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
                    max_length=512,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False
                )
            else:
                generated_tokens = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True,
                    do_sample=False
                )
        
        # Decode the outputs
        translated_texts = [self.tokenizer.decode(token, skip_special_tokens=True) for token in generated_tokens]
        
        # Postprocess texts
        final_texts = [self._postprocess_text(text) for text in translated_texts]
        
        return final_texts
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before translation.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _postprocess_text(self, text: str) -> str:
        """
        Postprocess text after translation.
        
        Args:
            text: Translated text
            
        Returns:
            Postprocessed text
        """
        # Fix common issues
        text = text.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
        text = text.replace(" :", ":").replace(" ;", ";")
        
        # Strip whitespace
        text = text.strip()
        
        return text

def parse_srt(file_path: str) -> List[Dict]:
    """Parse SRT file and return list of subtitle entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    subtitles = srt.parse(content)
    result = []

    for subtitle in subtitles:
        result.append({
            'index': subtitle.index,
            'start': subtitle.start,
            'end': subtitle.end,
            'text': subtitle.content
        })

    return result

def write_srt(subtitles: List[Dict], output_path: str):
    """Write translated subtitles to SRT file."""
    srt_subtitles = []

    for sub in subtitles:
        srt_sub = srt.Subtitle(
            index=sub['index'],
            start=sub['start'],
            end=sub['end'],
            content=sub['text']
        )
        srt_subtitles.append(srt_sub)

    content = srt.compose(srt_subtitles)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def translate_subtitles(
    input_file: str, 
    output_file: str, 
    batch_size: int = 32,
    model_type: str = "m2m100",
    src_lang: str = "zh",
    tgt_lang: str = "vi"
):
    """
    Translate SRT subtitles from source language to target language using improved local model.
    
    Args:
        input_file: Path to input SRT file
        output_file: Path to output SRT file
        batch_size: Size of batches for translation
        model_type: Type of model to use ("m2m100", "nllb", or "opus")
        src_lang: Source language code (default: zh - Chinese)
        tgt_lang: Target language code (default: vi - Vietnamese)
    """
    logger.info(f"Starting improved local translation process for {input_file}")
    logger.info(f"Using model type: {model_type}")
    
    # Parse input SRT file
    logger.info("Parsing input file...")
    subtitles = parse_srt(input_file)
    logger.info(f"Found {len(subtitles)} subtitles")
    
    # Initialize improved translator
    translator = ImprovedLocalTranslator(model_type=model_type)
    
    # Translate subtitles in batches
    logger.info("Starting translation...")
    start_time = time.time()
    
    translated_subtitles = []
    
    for i in tqdm(range(0, len(subtitles), batch_size), desc="Translating batches"):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        
        # Translate the batch
        try:
            translated_texts = translator.translate_batch(texts, src_lang=src_lang, tgt_lang=tgt_lang)
            
            # Update the subtitles with translated text
            for j, sub in enumerate(batch):
                translated_sub = sub.copy()
                translated_sub['text'] = translated_texts[j]
                translated_subtitles.append(translated_sub)
            
            # Progress update
            elapsed_time = time.time() - start_time
            progress = min(i + batch_size, len(subtitles))
            estimated_total_time = elapsed_time * len(subtitles) / progress
            estimated_remaining = estimated_total_time - elapsed_time
            
            logger.info(f"Processed {progress}/{len(subtitles)} subtitles. "
                       f"Estimated time remaining: {estimated_remaining:.2f}s")
                       
        except Exception as e:
            logger.error(f"Error translating batch {i//batch_size + 1}: {e}")
            # If translation fails, keep original text
            translated_subtitles.extend(batch)
    
    total_time = time.time() - start_time
    logger.info(f"Translation completed in {total_time:.2f}s for {len(subtitles)} subtitles.")
    
    # Write output SRT file
    logger.info("Writing output file...")
    write_srt(translated_subtitles, output_file)
    logger.info("Done!")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Translate SRT subtitles using improved local model")
    parser.add_argument("input_file", help="Path to input SRT file")
    parser.add_argument("-o", "--output", help="Path to output SRT file (default: input_file_vn.srt)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for translation (default: 32)")
    parser.add_argument("--model-type", choices=["m2m100", "nllb", "opus"], default="m2m100", 
                        help="Type of model to use (default: m2m100)")
    parser.add_argument("--src-lang", default="zh", help="Source language code (default: zh)")
    parser.add_argument("--tgt-lang", default="vi", help="Target language code (default: vi)")
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output or input_file.replace('.srt', '_vn.srt')
    batch_size = args.batch_size
    model_type = args.model_type
    src_lang = args.src_lang
    tgt_lang = args.tgt_lang
    
    translate_subtitles(
        input_file, output_file, batch_size,
        model_type=model_type,
        src_lang=src_lang,
        tgt_lang=tgt_lang
    )
