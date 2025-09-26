import srt
import subprocess
import json
import hashlib
import os
import time
import logging
from typing import List, Dict, Optional

# Import Google Generative AI if available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def load_api_key_from_file(file_path: str, key_name: str = None) -> Optional[str]:
    """
    Load API key from various file formats
    """
    if not os.path.exists(file_path):
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
    except Exception:
        return None

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

def get_cache_dir():
    """Get the cache directory path."""
    cache_dir = os.path.join(os.path.dirname(__file__), '.translation_cache')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_text_hash(texts: List[str]) -> str:
    """Generate a hash for a list of texts to use as cache key."""
    text_str = "\n".join(texts)
    return hashlib.md5(text_str.encode('utf-8')).hexdigest()

def load_from_cache(texts: List[str]) -> List[str] or None:
    """Load translation from cache if available."""
    cache_dir = get_cache_dir()
    cache_key = get_text_hash(texts)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Verify that the cached data matches the input
                if cached_data['input'] == texts:
                    print(f"Cache hit for batch with {len(texts)} texts")
                    return cached_data['output']
        except Exception:
            pass  # If cache reading fails, proceed with normal translation
    
    return None

def save_to_cache(texts: List[str], translations: List[str]):
    """Save translation to cache."""
    cache_dir = get_cache_dir()
    cache_key = get_text_hash(texts)
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    cache_data = {
        'input': texts,
        'output': translations
    }
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # If cache saving fails, continue without caching

def translate_with_gemini(text: str, target_language: str = "vi", context_prompt: str = "") -> str:
    """Translate using Gemini API with file-based API key loading"""
    # Try multiple methods to get the API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.gemini\oauth_creds.json", "access_token")
    if not gemini_api_key:
        gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "access_token")
    if not gemini_api_key:
        gemini_api_key = load_api_key_from_file(r"C:\Users\ddphu\.qwen\oauth_creds.json", "api_key")
    
    if not gemini_api_key:
        # Fallback to the original subprocess method if no API key is found
        return translate_with_subprocess(text)
    
    if GENAI_AVAILABLE:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            full_prompt = f"{context_prompt}\n\nYou are a professional translator. Translate the following text to {target_language}. Maintain the original meaning, tone, and context. Return only the translated text without any additional comments or explanations.\n\nText to translate:\n{text}"
            
            response = model.generate_content(full_prompt)
            if response.text:
                return response.text.strip()
            else:
                raise Exception("Empty translation response from Gemini")
        except Exception as e:
            logging.error(f"Gemini API translation failed: {str(e)}, falling back to subprocess method")
            return translate_with_subprocess(text)
    else:
        # Fallback to the original subprocess method if genai is not available
        return translate_with_subprocess(text)

def translate_with_subprocess(text: str) -> str:
    """Translate using the original subprocess method"""
    # Enhanced prompt for better translation quality
    prompt = """Translate the following Chinese text to Vietnamese. 
Follow these guidelines:
1. Preserve the original meaning and tone
2. Use natural, fluent Vietnamese
3. Maintain cultural context appropriately
4. Return only the translated text, one line per original text
5. Do not add any comments, explanations, or formatting

Chinese text to translate:
""" + text

    try:
        # Call gemini with the prompt
        result = subprocess.run(
            ['C:\\Users\\ddphu\\AppData\\Roaming\\npm\\gemini.cmd'],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',
            timeout=300  # 5 minutes timeout
        )

        if result.returncode != 0:
            raise Exception(f"gemini failed: {result.stderr}")

        translated_text = result.stdout.strip()
        return translated_text

    except subprocess.TimeoutExpired:
        raise Exception("Translation timed out")
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

def translate_batch(texts: List[str]) -> List[str]:
    """Translate a batch of texts using gemini with caching."""
    # Check cache first
    cached_result = load_from_cache(texts)
    if cached_result:
        return cached_result

    # Enhanced prompt for better translation quality
    context_prompt = "Bạn đang dịch một bộ phim/truyện hiện đại. Hãy dịch sát nghĩa, giữ nguyên tên người, tên địa danh nếu có."
    translated_lines = []
    
    for text in texts:
        translated_text = translate_with_gemini(text, context_prompt=context_prompt)
        translated_lines.append(translated_text)

    # Ensure we have the same number of translations
    if len(translated_lines) != len(texts):
        print(f"Warning: Translation mismatch: expected {len(texts)} lines, got {len(translated_lines)}. Attempting to fix...")
        # Try to handle mismatch by ensuring correct number of lines
        if len(translated_lines) < len(texts):
            # Pad with original text if we have fewer translations
            translated_lines.extend(texts[len(translated_lines):])
        else:
            # Truncate if we have more translations than expected
            translated_lines = translated_lines[:len(texts)]
    
    # Save to cache before returning
    save_to_cache(texts, translated_lines)
        
    return translated_lines

def translate_subtitles(subtitles: List[Dict], batch_size: int = 500) -> List[Dict]:
    """Translate all subtitles in batches."""
    translated_subtitles = []
    total_batches = (len(subtitles) + batch_size - 1) // batch_size

    logger.info(f"Total subtitles: {len(subtitles)}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Total batches: {total_batches}")
    
    start_time = time.time()

    for i in range(0, len(subtitles), batch_size):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        batch_num = i//batch_size + 1

        batch_start_time = time.time()
        logger.info(f"Translating batch {batch_num}/{total_batches} ({len(texts)} subtitles)...")

        # Retry up to 3 times
        for attempt in range(3):
            try:
                translated_texts = translate_batch(texts)

                for j, sub in enumerate(batch):
                    translated_sub = sub.copy()
                    translated_sub['text'] = translated_texts[j]
                    translated_subtitles.append(translated_sub)
                
                elapsed_time = time.time() - batch_start_time
                total_elapsed = time.time() - start_time
                estimated_remaining = (total_batches - batch_num) * (total_elapsed / batch_num)
                
                logger.info(f"Batch {batch_num}/{total_batches} completed in {elapsed_time:.2f}s. "
                            f"Progress: {len(translated_subtitles)}/{len(subtitles)} "
                            f"({100*len(translated_subtitles)/len(subtitles):.1f}%). "
                            f"Estimated time remaining: {estimated_remaining:.2f}s")
                
                # Print to console as well for immediate feedback
                print(f"Batch {batch_num}/{total_batches} completed in {elapsed_time:.2f}s. "
                      f"Progress: {len(translated_subtitles)}/{len(subtitles)} "
                      f"({100*len(translated_subtitles)/len(subtitles):.1f}%). "
                      f"Estimated time remaining: {estimated_remaining:.2f}s")
                break  # Success, exit retry loop

            except Exception as e:
                if attempt < 2:  # Not the last attempt
                    logger.warning(f"Attempt {attempt + 1} failed for batch {batch_num}: {e}. Retrying...")
                    # Add a small delay before retry to avoid overwhelming the API
                    time.sleep(2)
                else:
                    logger.error(f"Failed to translate batch {batch_num} after 3 attempts: {e}")
                    # Keep original text if all retries fail
                    translated_subtitles.extend(batch)

    total_time = time.time() - start_time
    logger.info(f"Translation completed in {total_time:.2f}s for {len(subtitles)} subtitles across {total_batches} batches.")
    print(f"Translation completed in {total_time:.2f}s for {len(subtitles)} subtitles across {total_batches} batches.")
    return translated_subtitles

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

# Set up logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('translation.log', encoding='utf-8'),
            logging.StreamHandler()  # Changed from sys.stdout to allow proper output
        ]
    )
    return logging.getLogger(__name__)

if __name__ == "__main__":
    import argparse
    import sys
    import os

    try:
        # Fix Unicode encoding for Windows console
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')

        # Set up logging
        logger = setup_logging()

        parser = argparse.ArgumentParser(description="Translate SRT subtitles from Chinese to Vietnamese using Gemini CLI")
        parser.add_argument("input_file", help="Path to input SRT file")
        parser.add_argument("-o", "--output", help="Path to output SRT file (default: input_file_vn.srt)")
        parser.add_argument("--batch-size", type=int, default=500, help="Batch size for translation (default: 500)")
        parser.add_argument("--clear-cache", action="store_true", help="Clear translation cache before starting")

        args = parser.parse_args()

        input_file = args.input_file
        output_file = args.output or input_file.replace('.srt', '_vn.srt')
        batch_size = args.batch_size

        logger.info(f"Starting translation process for {input_file}")
        
        # Clear cache if requested
        if args.clear_cache:
            cache_dir = get_cache_dir()
            import shutil
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            logger.info("Cache cleared")

        logger.info("Parsing input file...")
        subtitles = parse_srt(input_file)
        logger.info(f"Found {len(subtitles)} subtitles")

        logger.info("Translating...")
        translated_subtitles = translate_subtitles(subtitles, batch_size=batch_size)

        logger.info("Writing output file...")
        write_srt(translated_subtitles, output_file)

        logger.info("Done!")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
