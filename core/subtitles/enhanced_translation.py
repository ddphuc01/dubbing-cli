import srt
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict
import time
import logging
from tqdm import tqdm
import json
import os
import re
from pathlib import Path

# Set up logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('enhanced_translation.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class CharacterNameManager:
    """
    Quản lý các tên riêng của nhân vật để tránh dịch sai tên nhân vật.
    """
    
    def __init__(self, storage_file: str = "character_names.json"):
        """
        Khởi tạo quản lý tên nhân vật.
        
        Args:
            storage_file: Tên file lưu trữ các tên nhân vật
        """
        self.storage_file = storage_file
        self.character_names = self.load_character_names()
    
    def load_character_names(self) -> Dict[str, str]:
        """
        Tải danh sách tên nhân vật từ file JSON.
        
        Returns:
            Từ điển chứa tên tiếng Trung và tiếng Việt tương ứng
        """
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_character_names(self):
        """Lưu danh sách tên nhân vật vào file JSON."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.character_names, f, ensure_ascii=False, indent=2)
    
    def add_character_name(self, chinese_name: str, vietnamese_name: str = ""):
        """
        Thêm tên nhân vật mới.
        
        Args:
            chinese_name: Tên nhân vật tiếng Trung
            vietnamese_name: Tên nhân vật tiếng Việt (nếu có)
        """
        self.character_names[chinese_name] = vietnamese_name
        self.save_character_names()
    
    def extract_potential_names(self, texts: List[str]) -> Set[str]:
        """
        Trích xuất các chuỗi có khả năng là tên nhân vật từ danh sách văn bản.
        
        Args:
            texts: Danh sách văn bản để trích xuất tên
            
        Returns:
            Tập hợp các chuỗi có khả năng là tên nhân vật
        """
        potential_names = set()
        
        # Mẫu regex để tìm các chuỗi có thể là tên nhân vật
        # Tên thường ngắn, có thể là 2-4 ký tự Trung Quốc
        name_pattern = r'[\u4e00-\u9fff]{2,4}'
        
        for text in texts:
            matches = re.findall(name_pattern, text)
            for match in matches:
                # Lọc ra các từ phổ biến không phải tên riêng
                if not self.is_common_word(match):
                    potential_names.add(match)
        
        return potential_names
    
    def is_common_word(self, text: str) -> bool:
        """
        Kiểm tra xem một chuỗi có phải là từ phổ biến không (để loại bỏ khỏi tên nhân vật).
        
        Args:
            text: Chuỗi cần kiểm tra
            
        Returns:
            True nếu là từ phổ biến, False nếu có thể là tên riêng
        """
        common_words = {
            '你好', '谢谢', '什么', '怎么', '知道', '可以', '这样', '那样', '这个', '那个',
            '什么', '什么', '现在', '时候', '地方', '事情', '问题', '答案', '朋友', '家人',
            '今天', '明天', '昨天', '时候', '时间', '工作', '生活', '学习', '学生', '老师',
            '医生', '病人', '警察', '罪犯', '男人', '女人', '孩子', '父母', '家庭', '关系',
            '爱情', '友情', '亲情', '感觉', '心情', '想法', '意思', '语言', '文字', '故事',
            '电影', '电视', '节目', '音乐', '歌曲', '舞蹈', '艺术', '文化', '历史', '国家',
            '城市', '乡村', '地方', '位置', '方向', '距离', '大小', '多少', '颜色', '形状',
            '好吃', '好看', '好玩', '重要', '主要', '基本', '一般', '普通', '特殊', '特别',
            '非常', '很', '比较', '相对', '更加', '更加', '更加', '更加', '更加', '更加'
        }
        return text in common_words
    
    def preprocess_text_with_names(self, text: str) -> str:
        """
        Tiền xử lý văn bản để đánh dấu tên nhân vật trước khi dịch.
        
        Args:
            text: Văn bản đầu vào
            
        Returns:
            Văn bản đã được đánh dấu tên nhân vật
        """
        processed_text = text
        for chinese_name in sorted(self.character_names.keys(), key=len, reverse=True):
            # Thay thế tên nhân vật bằng một định dạng đặc biệt để giữ nguyên khi dịch
            processed_text = processed_text.replace(
                chinese_name, 
                f"{{CHARACTER_NAME:{chinese_name}}}"
            )
        return processed_text
    
    def postprocess_text_with_names(self, text: str) -> str:
        """
        Hậu xử lý văn bản sau khi dịch để khôi phục tên nhân vật.
        
        Args:
            text: Văn bản sau khi dịch
            
        Returns:
            Văn bản đã khôi phục tên nhân vật
        """
        processed_text = text
        for chinese_name, vietnamese_name in self.character_names.items():
            if vietnamese_name:  # Nếu có tên tiếng Việt
                # Khôi phục tên nhân vật đã dịch
                processed_text = processed_text.replace(
                    f"{{CHARACTER_NAME:{chinese_name}}}", 
                    vietnamese_name
                )
            else:  # Nếu không có tên tiếng Việt, giữ nguyên tên tiếng Trung
                processed_text = processed_text.replace(
                    f"{{CHARACTER_NAME:{chinese_name}}}", 
                    chinese_name
                )
        return processed_text


class LocalTranslator:
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-zh-vi"):
        """
        Initialize the local translator with a specified model.
        
        Args:
            model_name: Name of the translation model to use
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        logger.info(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("Model loaded successfully")
    
    def translate_text(self, text: str) -> str:
        """
        Translate a single text from Chinese to Vietnamese.
        
        Args:
            text: Input text in Chinese
            
        Returns:
            Translated text in Vietnamese
        """
        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=5,
                early_stopping=True,
                do_sample=False
            )
        
        # Decode the output
        translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translated_text
    
    def translate_batch(self, texts: List[str]) -> List[str]:
        """
        Translate a batch of texts from Chinese to Vietnamese.
        
        Args:
            texts: List of input texts in Chinese
            
        Returns:
            List of translated texts in Vietnamese
        """
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


def translate_subtitles(input_file: str, output_file: str, batch_size: int = 32, preserve_character_names: bool = True):
    """
    Translate SRT subtitles from Chinese to Vietnamese using local model.
    
    Args:
        input_file: Path to input SRT file
        output_file: Path to output SRT file
        batch_size: Size of batches for translation
        preserve_character_names: Whether to preserve character names during translation
    """
    logger.info(f"Starting translation process for {input_file}")
    
    # Parse input SRT file
    logger.info("Parsing input file...")
    subtitles = parse_srt(input_file)
    logger.info(f"Found {len(subtitles)} subtitles")
    
    # Initialize translator and character name manager
    translator = LocalTranslator()
    name_manager = CharacterNameManager() if preserve_character_names else None
    
    # Extract potential character names if enabled
    if preserve_character_names:
        logger.info("Extracting potential character names...")
        all_texts = [sub['text'] for sub in subtitles]
        potential_names = name_manager.extract_potential_names(all_texts)
        logger.info(f"Found {len(potential_names)} potential character names")
        
        # Add names that aren't already in the database
        for name in potential_names:
            if name not in name_manager.character_names:
                logger.info(f"New potential character name found: {name}")
                # For now, we'll add them without Vietnamese translation
                # In a real scenario, you might want to prompt the user for translation
                name_manager.add_character_name(name)
    
    # Translate subtitles in batches
    logger.info("Starting translation...")
    start_time = time.time()
    
    translated_subtitles = []
    
    for i in tqdm(range(0, len(subtitles), batch_size), desc="Translating batches"):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        
        # Preprocess texts to preserve character names if enabled
        if preserve_character_names:
            original_texts = texts.copy()
            texts = [name_manager.preprocess_text_with_names(text) for text in texts]
        
        # Translate the batch
        translated_texts = translator.translate_batch(texts)
        
        # Postprocess texts to restore character names if enabled
        if preserve_character_names:
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
    logger.info(f"Translation completed in {total_time:.2f}s for {len(subtitles)} subtitles.")
    
    # Write output SRT file
    logger.info("Writing output file...")
    write_srt(translated_subtitles, output_file)
    logger.info("Done!")


def translate_with_context(input_file: str, output_file: str, batch_size: int = 32, genre: str = "", preserve_character_names: bool = True):
    """
    Enhanced translation function with genre context and character name preservation.
    
    Args:
        input_file: Path to input SRT file
        output_file: Path to output SRT file
        batch_size: Size of batches for translation
        genre: Genre of the content (for context)
        preserve_character_names: Whether to preserve character names during translation
    """
    logger.info(f"Starting enhanced translation process for {input_file} with genre: {genre}")
    
    # Parse input SRT file
    logger.info("Parsing input file...")
    subtitles = parse_srt(input_file)
    logger.info(f"Found {len(subtitles)} subtitles")
    
    # Initialize translator and character name manager
    translator = LocalTranslator()
    name_manager = CharacterNameManager() if preserve_character_names else None
    
    # Add genre-specific context to character names if needed
    if genre.lower() == "quyenluctrungquoc":
        # For Chinese power dramas, we might want to add specific character titles
        pass  # The character name manager handles this automatically
    
    # Extract potential character names if enabled
    if preserve_character_names:
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
    logger.info("Starting translation...")
    start_time = time.time()
    
    translated_subtitles = []
    
    for i in tqdm(range(0, len(subtitles), batch_size), desc="Translating batches"):
        batch = subtitles[i:i + batch_size]
        texts = [sub['text'] for sub in batch]
        
        # Preprocess texts to preserve character names if enabled
        if preserve_character_names:
            original_texts = texts.copy()
            texts = [name_manager.preprocess_text_with_names(text) for text in texts]
        
        # Translate the batch
        translated_texts = translator.translate_batch(texts)
        
        # Postprocess texts to restore character names if enabled
        if preserve_character_names:
            translated_texts = [name_manager.postprocess_text_with_names(text) for text in translated_texts]
        
        # Update the subtitles with translated text
        for j, sub in enumerate(batch):
            translated_sub = sub.copy()
            translated_sub['text'] = translated_texts[j]
            translated_sub['original_text'] = sub['text']  # Keep original for reference
            translated_subtitles.append(translated_sub)
        
        # Progress update
        elapsed_time = time.time() - start_time
        progress = min(i + batch_size, len(subtitles))
        estimated_total_time = elapsed_time * len(subtitles) / progress
        estimated_remaining = estimated_total_time - elapsed_time
        
        logger.info(f"Processed {progress}/{len(subtitles)} subtitles. "
                   f"Estimated time remaining: {estimated_remaining:.2f}s")
    
    total_time = time.time() - start_time
    logger.info(f"Enhanced translation completed in {total_time:.2f}s for {len(subtitles)} subtitles.")
    
    # Write output SRT file
    logger.info("Writing output file...")
    write_srt(translated_subtitles, output_file)
    logger.info("Done!")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Translate SRT subtitles from Chinese to Vietnamese using local model with enhanced features")
    parser.add_argument("input_file", help="Path to input SRT file")
    parser.add_argument("-o", "--output", help="Path to output SRT file (default: input_file_vn.srt)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for translation (default: 32)")
    parser.add_argument("--no-preserve-names", action="store_true", help="Disable preservation of character names")
    parser.add_argument("--genre", default="", help="Genre of the content for context (e.g., quyenluctrungquoc, tienhiep, hienthai, kinghi, tinhcam)")
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output or input_file.replace('.srt', '_vn.srt')
    batch_size = args.batch_size
    preserve_character_names = not args.no_preserve_names
    genre = args.genre
    
    if genre:
        translate_with_context(input_file, output_file, batch_size, genre, preserve_character_names)
    else:
        translate_subtitles(input_file, output_file, batch_size, preserve_character_names)
