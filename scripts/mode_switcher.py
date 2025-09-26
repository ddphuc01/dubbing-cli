#!/usr/bin/env python3
"""
Script tự động chuyển đổi chế độ dựa trên nội dung yêu cầu
"""
import json
import re
import sys
from pathlib import Path

def load_mode_config():
    """Tải cấu hình chuyển đổi chế độ từ file MODE_CONFIG.json"""
    config_path = Path("MODE_CONFIG.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Cấu hình mặc định nếu không tìm thấy file
        return {
            "modeAutoSwitch": {
                "enabled": True,
                "rules": [
                    {
                        "keywords": ["plan", "design", "architecture", "structure", "overview", "strategy", "planning", "designing"],
                        "mode": "architect",
                        "description": "Chuyển sang chế độ kiến trúc khi làm việc liên quan đến lập kế hoạch, thiết kế hệ thống"
                    },
                    {
                        "keywords": ["code", "implement", "function", "class", "module", "script", "development", "create", "write code", "programming"],
                        "mode": "code",
                        "description": "Chuyển sang chế độ code khi làm việc liên quan đến viết code, implement chức năng"
                    },
                    {
                        "keywords": ["test", "testing", "unit test", "integration test", "pytest", "unittest", "verify", "validation"],
                        "mode": "test-engineer",
                        "description": "Chuyển sang chế độ test khi làm việc liên quan đến viết test, kiểm thử"
                    },
                    {
                        "keywords": ["debug", "fix", "bug", "error", "issue", "troubleshoot", "problem", "error handling"],
                        "mode": "debug",
                        "description": "Chuyển sang chế độ debug khi làm việc liên quan đến sửa lỗi, gỡ rối"
                    },
                    {
                        "keywords": ["review", "analyze", "analysis", "check", "examine", "inspect", "code review"],
                        "mode": "code-reviewer",
                        "description": "Chuyển sang chế độ review khi cần phân tích, kiểm tra code"
                    },
                    {
                        "keywords": ["document", "documentation", "readme", "guide", "manual", "write documentation"],
                        "mode": "docs-specialist",
                        "description": "Chuyển sang chế độ tài liệu khi làm việc liên quan đến viết tài liệu"
                    }
                ]
            },
            "defaultMode": "code",
            "contextAwareSwitching": True
        }

def detect_mode(user_input):
    """Phát hiện chế độ phù hợp dựa trên nội dung yêu cầu của người dùng"""
    config = load_mode_config()
    
    if not config["modeAutoSwitch"]["enabled"]:
        return config["defaultMode"]
    
    user_input_lower = user_input.lower()
    rules = config["modeAutoSwitch"]["rules"]
    
    # Tạo từ điển để đếm số lượng từ khóa khớp cho mỗi chế độ
    mode_scores = {}
    
    for rule in rules:
        mode = rule["mode"]
        keywords = rule["keywords"]
        score = 0
        
        for keyword in keywords:
            # Sử dụng regex để tìm từ khóa, không phân biệt hoa thường
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', user_input_lower):
                score += 1
        
        if score > 0:
            mode_scores[mode] = mode_scores.get(mode, 0) + score
    
    # Trả về chế độ có điểm cao nhất, nếu không có thì trả về mặc định
    if mode_scores:
        return max(mode_scores, key=mode_scores.get)
    else:
        return config["defaultMode"]

def main():
    """Hàm chính để chạy script từ dòng lệnh"""
    if len(sys.argv) < 2:
        print("Usage: python mode_switcher.py \"<user_input>\"")
        print("Ví dụ: python mode_switcher.py \"Hãy giúp tôi lập kế hoạch hệ thống dịch thuật\"")
        return
    
    user_input = sys.argv[1]
    detected_mode = detect_mode(user_input)
    
    print(f"Input: {user_input}")
    print(f"Detected Mode: {detected_mode}")
    
    # Trả về chế độ để có thể sử dụng trong các script khác
    return detected_mode

if __name__ == "__main__":
    main()