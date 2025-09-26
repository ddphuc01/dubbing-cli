"""
Translation API module that provides Chinese to Vietnamese translation functionality
based on the Translate repository features.
"""
import srt
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict, Optional
import time
import logging
from tqdm import tqdm
from character_name_manager import CharacterNameManager
import json
import os
import subprocess
import requests
from dotenv import load_dotenv

# Set up logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('translation.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class TranslationProvider:
    """Abstract base class for translation providers."""
    
    def __init__(self, name: str):
        self.name = name
    
    def translate_batch(self, texts: List[str], context: Optional[str] = None) -> List[str]:
        """
        Translate a batch of texts.
        
        Args:
            texts: List of input texts in Chinese
            context: Context information to help translation
            
        Returns:
            List of translated texts in Vietnamese
        """
        raise NotImplementedError

class LocalTranslator(TranslationProvider):
    """Translation provider using local model."""
    
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-zh-vi"):
        super().__init__("Local")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Local translator using device: {self.device}")
        
        logger.info(f"Loading local model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("Local model loaded successfully")
    
    def translate_batch(self, texts: List[str], context: Optional[str] = None) -> List[str]:
        """Translate a batch of texts using local model."""
        # Tokenize the input texts
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        # Generate translations
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=5,
                early_stopping=True,
                do_sample=False
            )
        
        # Decode the outputs
        translated_texts = [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        
        return translated_texts

class GeminiTranslator(TranslationProvider):
    """Translation provider using Gemini CLI."""
    
    def __init__(self):
        super().__init__("Gemini")
    
    def translate_batch(self, texts: List[str], context: Optional[str] = None) -> List[str]:
        """Translate a batch of texts using gemini."""
        # Enhanced prompt for better translation quality with context
        prompt = f"""Translate the following Chinese text to Vietnamese. 
Context: {context or 'No specific context provided'}
Follow these guidelines:
1. Preserve the original meaning and tone
2. Use natural, fluent Vietnamese
3. Maintain cultural context appropriately
4. Return only the translated text, one line per original text
5. Do not add any comments, explanations, or formatting

Chinese text to translate:
""" + "\n".join(texts)

        try:
            # Call gemini with the prompt
            result = subprocess.run(
                ['C:\\Users\\ddphuc\\AppData\\Roaming\\npm\\gemini.cmd'],
                input=prompt,
                text=True,
                capture_output=True,
                encoding='utf-8',
                timeout=300  # 5 minutes timeout
            )

            if result.returncode != 0:
                raise Exception(f"gemini failed: {result.stderr}")

            translated_text = result.stdout.strip()
            translated_lines = [line.strip() for line in translated_text.split('\n') if line.strip()]

            # Ensure we have the same number of translations
            if len(translated_lines) != len(texts):
                logger.warning(f"Translation mismatch: expected {len(texts)} lines, got {len(translated_lines)}. Attempting to fix...")
                # Try to handle mismatch by ensuring correct number of lines
                if len(translated_lines) < len(texts):
                    # Pad with original text if we have fewer translations
                    translated_lines.extend(texts[len(translated_lines):])
                else:
                    # Truncate if we have more translations than expected
                    translated_lines = translated_lines[:len(texts)]

            return translated_lines

        except subprocess.TimeoutExpired:
            raise Exception("Translation timed out")
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")

class OpenRouterTranslator(TranslationProvider):
    """Translation provider using OpenRouter API."""
    
    def __init__(self, api_key: str, model: str = "openchat/openchat-7b"):
        super().__init__("OpenRouter")
        self.api_key = api_key
        self.model = model
    
    def translate_batch(self, texts: List[str], context: Optional[str] = None) -> List[str]:
        """Translate a batch of texts using OpenRouter API."""
        # Combine texts with context
        full_text = f"Context: {context or 'No specific context provided'}\n\n" + "\n".join(texts)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a translator. Translate the following Chinese text to Vietnamese. Preserve the original meaning and tone, use natural, fluent Vietnamese, and maintain cultural context appropriately. Return only the translated text, one line per original text."
                },
                {
                    "role": "user",
                    "content": full_text
                }
            ]
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            result = response.json()
            translated_text = result['choices'][0]['message']['content']
            translated_lines = [line.strip() for line in translated_text.split('\n') if line.strip()]
            
            # Ensure we have the same number of translations
            if len(translated_lines) != len(texts):
                logger.warning(f"Translation mismatch: expected {len(texts)} lines, got {len(translated_lines)}. Attempting to fix...")
                if len(translated_lines) < len(texts):
                    translated_lines.extend(texts[len(translated_lines):])
                else:
                    translated_lines = translated_lines[:len(texts)]
            
            return translated_lines
            
        except Exception as e:
            raise Exception(f"OpenRouter translation failed: {str(e)}")

class HybridTranslator:
    """Main translator that coordinates multiple translation providers."""
    
    def __init__(self, gemini_enabled: bool = True, openrouter_enabled: bool = True, 
                 local_enabled: bool = True, openrouter_api_key: Optional[str] = None):
        """
        Initialize the hybrid translator.
        
        Args:
            gemini_enabled: Whether to use Gemini translator
            openrouter_enabled: Whether to use OpenRouter translator
            local_enabled: Whether to use local translator
            openrouter_api_key: API key for OpenRouter (required if openrouter_enabled is True)
        """
        self.providers = {}
        
        if gemini_enabled:
            self.providers["gemini"] = GeminiTranslator()
        
        if openrouter_enabled:
            if not openrouter_api_key:
                raise ValueError("OpenRouter API key is required when OpenRouter is enabled")
            self.providers["openrouter"] = OpenRouterTranslator(openrouter_api_key)
        
        if local_enabled:
            self.providers["local"] = LocalTranslator()
        
        if not self.providers:
            raise ValueError("At least one translation provider must be enabled")
        
        self.name_manager = CharacterNameManager()
        logger.info(f"Initialized hybrid translator with providers: {list(self.providers.keys())}")
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts to preserve character names."""
        return [self.name_manager.preprocess_text_with_names(text) for text in texts]
    
    def _postprocess_texts(self, texts: List[str]) -> List[str]:
        """Postprocess texts to restore character names."""
        return [self.name_manager.postprocess_text_with_names(text) for text in texts]
    
    def translate_batch(self, texts: List[str], context: Optional[str] = None) -> List[str]:
        """
        Translate a batch of texts using the most appropriate provider.
        
        Args:
            texts: List of input texts in Chinese
            context: Context information to help translation
            
        Returns:
            List of translated texts in Vietnamese
        """
        # Preprocess to preserve character names
        original_texts = texts.copy()
        processed_texts = self._preprocess_texts(texts)
        
        # For now, use local translator as default, but could implement more sophisticated selection
        provider_name = "local"
        if "local" in self.providers:
            provider_name = "local"
        elif "gemini" in self.providers:
            provider_name = "gemini"
        elif "openrouter" in self.providers:
            provider_name = "openrouter"
        
        provider = self.providers[provider_name]
        
        logger.info(f"Using {provider_name} provider for batch of {len(processed_texts)} texts")
        
        try:
            # Translate using selected provider
            translated_texts = provider.translate_batch(processed_texts, context)
            
            # Postprocess to restore character names
            final_texts = self._postprocess_texts(translated_texts)
            
            return final_texts
            
        except Exception as e:
            logger.error(f"Translation failed with {provider_name}, falling back to local provider: {e}")
            
            # Fallback to local provider if available
            if "local" in self.providers:
                try:
                    translated_texts = self.providers["local"].translate_batch(processed_texts, context)
                    final_texts = self._postprocess_texts(translated_texts)
                    return final_texts
                except Exception as fallback_error:
                    logger.error(f"Fallback translation also failed: {fallback_error}")
                    # If all else fails, return original texts
                    return original_texts
            else:
                # If no fallback available, return original texts
                return original_texts

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
    batch_size: int = 16,
    method: str = "local",
    openrouter_api_key: Optional[str] = None,
    movie_context: Optional[str] = None,
    preserve_character_names: bool = True
):
    """
    Translate SRT subtitles using the specified method.
    
    Args:
        input_file: Path to input SRT file
        output_file: Path to output SRT file
        batch_size: Size of batches for translation
        method: Translation method ('local', 'gemini', 'openrouter', or 'hybrid')
        openrouter_api_key: API key for OpenRouter
        movie_context: Context information about the movie
        preserve_character_names: Whether to preserve character names
    """
    logger.info(f"Starting {method} translation process for {input_file}")
    
    # Parse input SRT file
    logger.info("Parsing input file...")
    subtitles = parse_srt(input_file)
    logger.info(f"Found {len(subtitles)} subtitles")
    
    # Initialize translator based on method
    if method == "local":
        translator = LocalTranslator()
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "gemini":
        translator = GeminiTranslator()
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "openrouter":
        if not openrouter_api_key:
            raise ValueError("OpenRouter API key is required for OpenRouter method")
        translator = OpenRouterTranslator(openrouter_api_key)
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "hybrid":
        translator = HybridTranslator(
            gemini_enabled=True,
            openrouter_enabled=bool(openrouter_api_key),
            local_enabled=True,
            openrouter_api_key=openrouter_api_key
        )
        # For hybrid, we use the name manager from the translator
        name_manager = translator.name_manager if preserve_character_names else None
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Extract potential character names if enabled
    if preserve_character_names and name_manager:
        logger.info("Extracting potential character names...")
        all_texts = [sub['text'] for sub in subtitles]
        potential_names = name_manager.extract_potential_names(all_texts)
        logger.info(f"Found {len(potential_names)} potential character names")
        
        # Add names that aren't already in the database
        for name in potential_names:
            if name not in name_manager.character_names:
                logger.info(f"New potential character name found: {name}")
                name_manager.add_character_name(name)
    
    # Translate subtitles in batches
    logger.info(f"Starting {method} translation...")
    start_time = time.time()
    
    translated_subtitles = []
    
    for i in tqdm(range(0, len(subtitles), batch_size), desc=f"Translating batches ({method})"):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        
        # Preprocess texts to preserve character names if enabled
        if preserve_character_names and name_manager:
            original_texts = texts.copy()
            texts = [name_manager.preprocess_text_with_names(text) for text in texts]
        
        # Translate the batch using the appropriate method
        if method == "hybrid":
            translated_texts = translator.translate_batch(texts, movie_context)
        else:
            translated_texts = translator.translate_batch(texts, movie_context)
        
        # Postprocess texts to restore character names if enabled
        if preserve_character_names and name_manager:
            translated_texts = [name_manager.postprocess_text_with_names(text) for text in translated_texts]
        
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
    
    total_time = time.time() - start_time
    logger.info(f"{method.title()} translation completed in {total_time:.2f}s for {len(subtitles)} subtitles.")
    
    # Write output SRT file
    logger.info("Writing output file...")
    write_srt(translated_subtitles, output_file)
    logger.info("Done!")

def translate_text(text: str, method: str = "local", openrouter_api_key: Optional[str] = None, 
                   movie_context: Optional[str] = None, preserve_character_names: bool = True) -> str:
    """
    Translate a single text string using the specified method.
    
    Args:
        text: Input text in Chinese
        method: Translation method ('local', 'gemini', 'openrouter', or 'hybrid')
        openrouter_api_key: API key for OpenRouter
        movie_context: Context information about the movie
        preserve_character_names: Whether to preserve character names
        
    Returns:
        Translated text in Vietnamese
    """
    # Initialize translator based on method
    if method == "local":
        translator = LocalTranslator()
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "gemini":
        translator = GeminiTranslator()
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "openrouter":
        if not openrouter_api_key:
            raise ValueError("OpenRouter API key is required for OpenRouter method")
        translator = OpenRouterTranslator(openrouter_api_key)
        name_manager = CharacterNameManager() if preserve_character_names else None
    elif method == "hybrid":
        translator = HybridTranslator(
            gemini_enabled=True,
            openrouter_enabled=bool(openrouter_api_key),
            local_enabled=True,
            openrouter_api_key=openrouter_api_key
        )
        # For hybrid, we use the name manager from the translator
        name_manager = translator.name_manager if preserve_character_names else None
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Preprocess text to preserve character names if enabled
    if preserve_character_names and name_manager:
        text = name_manager.preprocess_text_with_names(text)
    
    # Translate the text
    if method == "hybrid":
        translated_text = translator.translate_batch([text], movie_context)[0]
    else:
        translated_text = translator.translate_batch([text], movie_context)[0]
    
    # Postprocess text to restore character names if enabled
    if preserve_character_names and name_manager:
        translated_text = name_manager.postprocess_text_with_names(translated_text)
    
    return translated_text
