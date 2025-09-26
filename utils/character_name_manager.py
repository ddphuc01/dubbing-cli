import json
import os
import re
from typing import Dict, List, Set

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
