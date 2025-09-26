import os
import json
import time
import openai
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_api_key_from_file(file_path: str, key_name: str = None) -> Optional[str]:
    """
    Load API key from various file formats
    """
    if not os.path.exists(file_path):
        logger.warning(f"API key file does not exist: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if key_name:
                # Try to parse as JSON if key_name is provided
                try:
                    data = json.loads(content)
                    return data.get(key_name)
                except json.JSONDecodeError:
                    # If not JSON, try to find the key in the content
                    for line in content.splitlines():
                        if key_name in line and '=' in line:
                            return line.split('=')[1].strip()
            else:
                # Return the entire content if no specific key is requested
                return content
    except Exception as e:
        logger.error(f"Error reading API key file {file_path}: {str(e)}")
        return None

# Import Google Generative AI if available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai not installed. Install it using: pip install google-generativeai")
    GENAI_AVAILABLE = False


class ContextManager:
    """Manage context for different story genres"""
    def __init__(self):
        self.contexts = {
            "quyenluctrungquoc": "Bạn đang dịch một bộ phim/truyện về đề tài Quyền Lực Trung Quốc. Hãy giữ nguyên các tên chức vụ, cơ quan chính phủ, địa danh Trung Quốc và các thuật ngữ chuyên ngành. Ví dụ: Thị trưởng, Tỉnh ủy, Công an tỉnh, Bộ Chính trị, v.v.",
            "tienhiep": "Bạn đang dịch một bộ phim/truyện tiên hiệp (xuyên không, tu chân, tu tiên). Hãy giữ nguyên tên môn phái, cấp bậc tu luyện, thuật ngữ tu chân. Ví dụ: Luyện Khí, Trúc Cơ, Kim Đan, Nguyên Anh, Hóa Thần, v.v.",
            "hienthai": "Bạn đang dịch một bộ phim/truyện hiện đại. Hãy dịch sát nghĩa, giữ nguyên tên người, tên địa danh nếu có.",
            "kinghi": "Bạn đang dịch một bộ phim/truyện kinh dị. Giữ nguyên không khí rùng rợn, âm u trong bản dịch. Không làm giảm tính kinh dị của nội dung gốc.",
            "tinhcam": "Bạn đang dịch một bộ phim/truyện tình cảm. Giữ nguyên cảm xúc, sự lãng mạn trong bản dịch. Dịch với ngôn từ nhẹ nhàng, sâu sắc."
        }
        self.current_context = ""
        self.genre = ""
    
    def set_genre(self, genre: str) -> None:
        """Set the genre for translation context"""
        self.genre = genre.lower().replace(" ", "")
        self.current_context = self.contexts.get(self.genre, "")
        logger.info(f"Set translation genre: {genre}, context: {self.current_context[:100]}...")
    
    def get_context_prompt(self) -> str:
        """Get the context prompt for translation"""
        return self.current_context

class CacheManager:
    """Manage cache for names, locations, etc. to prevent mistranslation"""
    def __init__(self):
        self.name_cache = {}
        self.location_cache = {}
        self.other_cache = {}
        self.processed_entities = set()
    
    def add_name(self, original: str, translated: str = None) -> None:
        """Add a name to cache"""
        if original not in self.name_cache:
            self.name_cache[original] = translated or original
            logger.info(f"Added name to cache: {original} -> {self.name_cache[original]}")
    
    def add_location(self, original: str, translated: str = None) -> None:
        """Add a location to cache"""
        if original not in self.location_cache:
            self.location_cache[original] = translated or original
            logger.info(f"Added location to cache: {original} -> {self.location_cache[original]}")
    
    def get_cached_translation(self, original: str) -> Optional[str]:
        """Get cached translation if exists"""
        if original in self.name_cache:
            return self.name_cache[original]
        if original in self.location_cache:
            return self.location_cache[original]
        if original in self.other_cache:
            return self.other_cache[original]
        return None
    
    def process_text_with_cache(self, text: str) -> str:
        """Process text replacing cached entities"""
        result = text
        # Replace names first
        for original, translated in self.name_cache.items():
            result = result.replace(original, translated)
        # Replace locations
        for original, translated in self.location_cache.items():
            result = result.replace(original, translated)
        # Replace other cached items
        for original, translated in self.other_cache.items():
            result = result.replace(original, translated)
        return result

class TranslationService:
    def __init__(self, genre: str = ""):
        self.openai_client = None
        self.gemini_client = None
        self.qwen_client = None
        self.openrouter_client = None
        self.local_client = None
        self.context_manager = ContextManager()
        self.cache_manager = CacheManager()
        self.genre = genre
        if genre:
            self.context_manager.set_genre(genre)
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients with error handling"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                try:
                    # Try to initialize with newer OpenAI client
                    self.openai_client = openai.OpenAI(api_key=openai_api_key)
                    logger.info("OpenAI client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client with newer version: {e}")
                    try:
                        # Fallback to older OpenAI client initialization
                        import openai as openai_legacy
                        openai_legacy.api_key = openai_api_key
                        self.openai_client = openai_legacy
                        logger.info("OpenAI client initialized successfully with legacy version")
                    except Exception as e2:
                        logger.warning(f"Failed to initialize OpenAI client with legacy version: {e2}")
            else:
                logger.warning("OPENAI_API_KEY not found in environment variables")
            
            # Initialize Gemini client
            self.gemini_client = None  # Initialize as None by default
            if GENAI_AVAILABLE:
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                # Try to load from environment variable first, then from gemini file, then from qwen file as fallback
                if not gemini_api_key:
                    gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.gemini\oauth_creds.json", "access_token")
                if not gemini_api_key:
                    gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "access_token")
                if not gemini_api_key:
                    gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "api_key")
                if gemini_api_key:
                    genai.configure(api_key=gemini_api_key)
                    self.gemini_client = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini client initialized successfully")
                else:
                    logger.warning("GEMINI_API_KEY not found in environment variables, C:\\Users\\ddphu\\.gemini\\oauth_creds.json, or C:\\Users\\ddphu\\.qwen\\oauth_creds.json")
            else:
                logger.warning("Google Generative AI not available. Install with: pip install google-generativeai")
            
            # Initialize Qwen client
            qwen_api_key = os.getenv('QWEN_API_KEY')
            # Try to load from environment variable first, then from file
            if not qwen_api_key:
                qwen_api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "api_key")
            if qwen_api_key:
                # Qwen API key is already loaded, we just need to store it for later use
                self.qwen_api_key = qwen_api_key
                logger.info("Qwen API key loaded successfully")
            else:
                logger.warning("QWEN_API_KEY not found in environment variables or C:\\Users\\ddphu\\.qwen\\oauth_creds.json")
            
            # Initialize OpenRouter client
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if openrouter_api_key:
                try:
                    self.openrouter_client = openai.OpenAI(
                        api_key=openrouter_api_key,
                        base_url="https://openrouter.ai/api/v1",
                    )
                    logger.info("OpenRouter client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenRouter client: {e}")
                    try:
                        # Fallback to older OpenAI client initialization
                        import openai as openai_legacy
                        openai_legacy.api_key = openrouter_api_key
                        self.openrouter_client = openai_legacy
                        logger.info("OpenRouter client initialized successfully with legacy version")
                    except Exception as e2:
                        logger.warning(f"Failed to initialize OpenRouter client with legacy version: {e2}")
            else:
                logger.warning("OPENROUTER_API_KEY not found in environment variables")
            
        except Exception as e:
            logger.error(f"Error initializing clients: {str(e)}")
            raise

    def detect_entities(self, text: str) -> Dict[str, List[str]]:
        """Detect names, locations and other entities to add to cache"""
        entities = {"names": [], "locations": [], "other": []}
        # Simple pattern matching for potential names (capitalized words, Chinese names, etc.)
        import re
        
        # Pattern for potential names (capitalized words, Chinese characters)
        name_pattern = r'\b[A-Z][a-z]+\b|\b[A-Z][a-z]+ [A-Z][a-z]+\b|[\u4e00-\u9fff]{2,4}'
        names = re.findall(name_pattern, text)
        entities["names"] = [name.strip() for name in names if len(name.strip()) > 1]
        
        # Pattern for potential locations (ending with city, province, etc. or Chinese characters)
        location_pattern = r'\b\w+ (?:city|town|village|province|state|country|thành phố|tỉnh|quận|huyện)\b|[\u4e00-\u9fff]{2,4}(?:市|省|县|城)'
        locations = re.findall(location_pattern, text, re.IGNORECASE)
        entities["locations"] = [location.strip() for location in locations if len(location.strip()) > 1]
        
        return entities

    def translate_with_gemini(self, text: str, target_language: str = "vi") -> str:
        """Translate using Gemini API"""
        if not self.gemini_client:
            raise Exception("Gemini client not initialized")
        
        context_prompt = self.context_manager.get_context_prompt()
        full_prompt = f"{context_prompt}\n\nYou are a professional translator. Translate the following text to {target_language}. Maintain the original meaning, tone, and context. Return only the translated text without any additional comments or explanations.\n\nText to translate:\n{text}"
        
        try:
            response = self.gemini_client.generate_content(full_prompt)
            if response.text:
                return response.text.strip()
            else:
                raise Exception("Empty translation response from Gemini")
        except Exception as e:
            logger.error(f"Gemini translation failed: {str(e)}")
            raise

    def translate_with_qwen(self, text: str, target_language: str = "vi") -> str:
        """Translate using Qwen API (via requests)"""
        api_key = getattr(self, 'qwen_api_key', None) or os.getenv('QWEN_API_KEY')
        if not api_key:
            # Try to load from file as fallback
            api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "api_key")
            if not api_key:
                raise Exception("QWEN_API_KEY not found in environment variables or C:\\Users\\ddphu\\.qwen\\oauth_creds.json")
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-max",
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following text to {target_language}. Maintain the original meaning, tone, and context. Return only the translated text without any additional comments or explanations."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            },
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 2000
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"].strip()
            else:
                raise Exception(f"Unexpected response format from Qwen: {result}")
        except Exception as e:
            logger.error(f"Qwen translation failed: {str(e)}")
            raise

    def translate_with_openrouter(self, text: str, target_language: str = "vi") -> str:
        """Translate using OpenRouter API"""
        if not self.openrouter_client:
            raise Exception("OpenRouter client not initialized")
        
        context_prompt = self.context_manager.get_context_prompt()
        try:
            response = self.openrouter_client.chat.completions.create(
                model="openchat/openchat-7b",  # Using a free model as example
                messages=[
                    {
                        "role": "system",
                        "content": f"{context_prompt} You are a professional translator. Translate the following text to {target_language}. Maintain the original meaning, tone, and context. Return only the translated text without any additional comments or explanations."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                timeout=30.0
            )
            
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                raise Exception("Invalid response structure from OpenRouter")
        except Exception as e:
            logger.error(f"OpenRouter translation failed: {str(e)}")
            raise

    def translate_with_local(self, text: str, target_language: str = "vi") -> str:
        """Placeholder for local AI translation"""
        # This would be implemented with local models like Ollama, etc.
        # For now, we'll use a simple fallback
        logger.warning("Local AI translation not implemented, using fallback")
        return text # Return original text as fallback

    def translate_with_gtx_free(self, text: str, target_language: str = "vi") -> str:
        """Placeholder for GTX API Free translation"""
        # This would be implemented with GTX API
        # For now, we'll use a simple fallback
        logger.warning("GTX API Free translation not implemented, using fallback")
        return text  # Return original text as fallback

    def translate_with_retry(self, text: str, target_language: str = "vi", max_retries: int = 3, delay: int = 1, service_priority: Optional[List[str]] = None) -> str:
        """
        Translate text with retry mechanism and error handling
        Supports multiple services with priority order
        """
        if service_priority is None:
            service_priority = ["gemini", "openai", "qwen", "openrouter", "local", "gtx"]

        # Detect and cache entities before translation
        entities = self.detect_entities(text)
        for name in entities["names"]:
            self.cache_manager.add_name(name)
        for location in entities["locations"]:
            self.cache_manager.add_location(location)

        for attempt in range(max_retries):
            for service in service_priority:
                try:
                    logger.info(f"Attempting translation with {service} (attempt {attempt + 1})")
                    
                    if service == "gemini" and self.gemini_client:
                        translated_text = self.translate_with_gemini(text, target_language)
                    elif service == "openai" and self.openai_client:
                        response = self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"{self.context_manager.get_context_prompt()} You are a professional translator. Translate the following text to {target_language}. Maintain the original meaning, tone, and context. Return only the translated text without any additional comments or explanations."
                                },
                                {
                                    "role": "user",
                                    "content": text
                                }
                            ],
                            temperature=0.1,
                            max_tokens=2000,
                            timeout=30.0
                        )
                        translated_text = response.choices[0].message.content.strip()
                    elif service == "qwen":
                        translated_text = self.translate_with_qwen(text, target_language)
                    elif service == "openrouter" and self.openrouter_client:
                        translated_text = self.translate_with_openrouter(text, target_language)
                    elif service == "local":
                        translated_text = self.translate_with_local(text, target_language)
                    elif service == "gtx":
                        translated_text = self.translate_with_gtx_free(text, target_language)
                    else:
                        continue  # Skip this service if not available

                    if translated_text:
                        # Apply cache to the translated text
                        cached_text = self.cache_manager.process_text_with_cache(translated_text)
                        # Add the original->translated mapping to cache
                        text_parts = text.split()
                        cached_text_parts = cached_text.split()
                        if text_parts and cached_text_parts:
                            self.cache_manager.add_name(text_parts[0], cached_text_parts[0])
                        return cached_text
                    else:
                        raise Exception(f"Empty translation response from {service}")

                except Exception as e:
                    logger.warning(f"{service} translation attempt {attempt + 1} failed: {str(e)}")
                    continue  # Try next service in priority list

            # If all services failed in this attempt, wait before retrying
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff

        logger.error(f"All translation services failed after {max_retries} attempts")
        # Return original text as fallback, but still process through cache
        cached_fallback = self.cache_manager.process_text_with_cache(text)
        return cached_fallback

    def translate_subtitles(self, subtitles: List[Dict[str, Any]], target_language: str = "vi", max_batch_size: int = 500) -> List[Dict[str, Any]]:
        """
        Translate a list of subtitle dictionaries with batching and retry mechanism
        """
        if not subtitles:
            return []
        
        translated_subtitles = []
        num_batches = (len(subtitles) + max_batch_size - 1) // max_batch_size  # Ceiling division

        logger.info(f"Translating {len(subtitles)} subtitles in {num_batches} batches of {max_batch_size} each")
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * max_batch_size
            end_idx = min((batch_idx + 1) * max_batch_size, len(subtitles))
            batch = subtitles[start_idx:end_idx]
            
            logger.info(f"Processing batch {batch_idx + 1}/{num_batches} ({len(batch)} subtitles)")
            
            for i, subtitle in enumerate(batch):
                try:
                    # Extract text from subtitle
                    original_text = subtitle.get('text', '')
                    
                    if not original_text.strip():
                        logger.warning(f"Empty subtitle text at index {start_idx + i}, skipping translation")
                        translated_subtitles.append(subtitle)
                        continue
                    
                    # Translate with retry
                    translated_text = self.translate_with_retry(original_text, target_language)
                    
                    # Create new subtitle with translated text
                    translated_subtitle = subtitle.copy()
                    translated_subtitle['text'] = translated_text
                    translated_subtitle['original_text'] = original_text  # Keep original for reference
                    
                    translated_subtitles.append(translated_subtitle)
                    
                    logger.info(f"Translated subtitle {start_idx + i + 1}/{len(subtitles)}: '{original_text[:50]}...' -> '{translated_text[:50]}...'")
                    
                except Exception as e:
                    logger.error(f"Error translating subtitle {start_idx + i}: {str(e)}")
                    # Keep original subtitle if translation fails
                    translated_subtitles.append(subtitle)
        
        return translated_subtitles

    def translate_text_block(self, text_block: str, target_language: str = "vi") -> str:
        """
        Translate a single block of text with retry mechanism
        """
        if not text_block or not text_block.strip():
            return text_block
        
        try:
            translated_text = self.translate_with_retry(text_block, target_language)
            logger.info(f"Text block translated successfully: '{text_block[:100]}...' -> '{translated_text[:100]}...'")
            return translated_text
        except Exception as e:
            logger.error(f"Error translating text block: {str(e)}")
            return text_block  # Return original text as fallback

def translate_srt_file(input_file, output_file, target_language="vi", genre="", max_batch_size=500):
    """
    Translate SRT subtitle file with batching and genre context
    """
    try:
        # Read the SRT file
        with open(input_file, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Parse SRT content (simple parsing for basic SRT files)
        import re
        
        # Split SRT into subtitle entries
        entries = re.split(r'\n\s*\n', srt_content.strip())
        
        # Create translation service with genre context
        translation_service = TranslationService(genre=genre)
        
        # Process entries in batches
        translated_entries = []
        num_batches = (len(entries) + max_batch_size - 1) // max_batch_size  # Ceiling division

        logger.info(f"Translating {len(entries)} SRT entries in {num_batches} batches of {max_batch_size} each")
        
        for batch_idx in range(num_batches):
            start_idx = batch_idx * max_batch_size
            end_idx = min((batch_idx + 1) * max_batch_size, len(entries))
            batch = entries[start_idx:end_idx]
            
            logger.info(f"Processing SRT batch {batch_idx + 1}/{num_batches} ({len(batch)} entries)")
            
            for i, entry in enumerate(batch):
                if entry.strip():
                    lines = entry.strip().split('\n')
                    if len(lines) >= 3:
                        # Format: Index, Time, Text
                        index = lines[0] if lines[0].isdigit() else ''
                        time_line = lines[1] if '-->' in lines[1] else ''
                        text_lines = lines[2:] if time_line else lines[1:]
                        
                        original_text = '\n'.join(text_lines)
                        
                        # Translate the text
                        translated_text = translation_service.translate_text_block(original_text, target_language)
                        
                        # Combine back
                        if index and time_line:
                            translated_entry = f"{index}\n{time_line}\n{translated_text}"
                        else:
                            translated_entry = translated_text
                        
                        translated_entries.append(translated_entry)
                    else:
                        # Not a standard SRT entry, keep as is
                        translated_entries.append(entry)
                else:
                    # Empty entry, keep as is
                    translated_entries.append(entry)
        
        # Write translated content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(translated_entries))
        
        logger.info(f"Successfully translated SRT file: {input_file} -> {output_file}")
        
    except Exception as e:
        logger.error(f"Error translating SRT file: {str(e)}")
        raise

def translate_json_subtitles(input_file: str, output_file: str, target_language: str = "vi") -> None:
    """
    Translate JSON subtitle file
    """
    try:
        # Read JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translation_service = TranslationService()
        
        # Handle different JSON structures
        if isinstance(data, list):
            # If it's a list of subtitle objects
            translated_data = translation_service.translate_subtitles(data, target_language)  # type: ignore
        elif isinstance(data, dict):
            # If it's a dictionary with subtitle data
            if 'segments' in data:
                translated_segments = translation_service.translate_subtitles(data['segments'], target_language)  # type: ignore
                translated_data = {**data, 'segments': translated_segments}
            elif 'subtitles' in data:
                translated_subtitles = translation_service.translate_subtitles(data['subtitles'], target_language)  # type: ignore
                translated_data = {**data, 'subtitles': translated_subtitles}
            else:
                # Try to find subtitle-like keys
                translated_data = {}
                for key, value in data.items():
                    if isinstance(value, list) and value and isinstance(value[0], dict) and 'text' in value[0]:
                        translated_data[key] = translation_service.translate_subtitles(value, target_language)  # type: ignore
                    else:
                        translated_data[key] = value
        else:
            # Single text block
            translated_data = translation_service.translate_text_block(str(data), target_language)
        
        # Write translated JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully translated JSON subtitles: {input_file} -> {output_file}")
        
    except Exception as e:
        logger.error(f"Error translating JSON subtitles: {str(e)}")
        raise

def main():
    """
    Main function to demonstrate translation functionality
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Translate subtitles using AI')
    parser.add_argument('input_file', help='Input subtitle file (SRT or JSON)')
    parser.add_argument('-o', '--output', help='Output translated subtitle file (default: input file with _translated suffix)')
    parser.add_argument('--language', default='vi', help='Target language code (default: vi for Vietnamese)')
    parser.add_argument('--genre', default='', help='Genre of the content (e.g., quyenluctrungquoc, tienhiep, hienthai, kinghi, tinhcam)')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for processing subtitles (default: 500)')
    parser.add_argument('--service-priority', help='Priority order for translation services (comma-separated): gemini, groq, openai, qwen, openrouter, local, gtx')
    
    args = parser.parse_args()
    
    input_file = Path(args.input_file)
    if not input_file.exists():
        logger.error(f"Input file does not exist: {input_file}")
        return
    
    # If no output file is specified, generate one based on the input file
    if args.output:
        output_file = Path(args.output)
    else:
        # Generate output file name based on input file
        output_file = input_file.parent / f"{input_file.stem}_translated{input_file.suffix}"
    
    # Parse service priority if provided
    service_priority = None
    if args.service_priority:
        service_priority = [service.strip() for service in args.service_priority.split(',')]
    
    try:
        if input_file.suffix.lower() == '.srt':
            translate_srt_file(input_file, output_file, args.language, args.genre, args.batch_size)
        elif input_file.suffix.lower() == '.json':
            # For JSON files, we'll need to update the function to accept genre and batch size as well
            translation_service = TranslationService(genre=args.genre)
            # Pass service priority to the translation function if available
            if service_priority:
                # Update the translation methods to use the custom service priority
                original_translate_with_retry = translation_service.translate_with_retry
                def custom_translate_with_retry(text, target_language="vi", max_retries=3, delay=1):
                    return original_translate_with_retry(text, target_language, max_retries, delay, service_priority)
                translation_service.translate_with_retry = custom_translate_with_retry
            
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # If it's a list of subtitle objects
                translated_data = translation_service.translate_subtitles(data, args.language, args.batch_size)
            elif isinstance(data, dict):
                # If it's a dictionary with subtitle data
                if 'segments' in data:
                    translated_segments = translation_service.translate_subtitles(data['segments'], args.language, args.batch_size)
                    translated_data = {**data, 'segments': translated_segments}
                elif 'subtitles' in data:
                    translated_subtitles = translation_service.translate_subtitles(data['subtitles'], args.language, args.batch_size)
                    translated_data = {**data, 'subtitles': translated_subtitles}
                else:
                    # Try to find subtitle-like keys
                    translated_data = {}
                    for key, value in data.items():
                        if isinstance(value, list) and value and 'text' in value[0]:
                            translated_data[key] = translation_service.translate_subtitles(value, args.language, args.batch_size)
                        else:
                            translated_data[key] = value
            else:
                # Single text block
                translated_data = translation_service.translate_text_block(str(data), args.language)
            
            # Write translated JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Successfully translated JSON subtitles: {input_file} -> {output_file}")
        else:
            logger.error(f"Unsupported file format: {input_file.suffix}")
            return
        
        logger.info(f"Translation completed successfully!")
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
