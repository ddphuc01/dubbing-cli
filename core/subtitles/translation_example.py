#!/usr/bin/env python3
"""
Example script demonstrating how to use the translation features
"""

import json
import os
from translate_subtitles import TranslationService, translate_srt_file, translate_json_subtitles

def create_sample_srt():
    """Create a sample SRT file for testing"""
    sample_srt = """1
00:00:01,000 --> 00:00:04,000
Hello, welcome to our show.

2
00:00:05,000 --> 00:00:08,000
Today we'll be discussing artificial intelligence.

3
00:00:09,000 --> 00:00:12,000
人工智能正在改变我们的世界。
"""
    
    with open("sample.srt", "w", encoding="utf-8") as f:
        f.write(sample_srt)
    
    print("Created sample.srt file")

def create_sample_json():
    """Create a sample JSON file for testing"""
    sample_json = [
        {"text": "Hello, welcome to our show.", "start": "00:00:01,000", "end": "00:00:04,000"},
        {"text": "Today we'll be discussing artificial intelligence.", "start": "00:00:05,000", "end": "00:00:08,000"},
        {"text": "人工智能正在改变我们的世界。", "start": "00:00:09,000", "end": "00:00:12,000"}
    ]
    
    with open("sample.json", "w", encoding="utf-8") as f:
        json.dump(sample_json, f, ensure_ascii=False, indent=2)
    
    print("Created sample.json file")

def demonstrate_translation_service():
    """Demonstrate using the TranslationService class directly"""
    print("\n=== Translation Service Demo ===")
    
    # Create translation service
    translator = TranslationService(genre="hienthai")  # Modern content genre
    
    # Test individual text translation
    texts = [
        "Hello, how are you today?",
        "人工智能正在快速发展。",
        "Welcome to our presentation."
    ]
    
    print("Translating individual texts:")
    for text in texts:
        try:
            translated = translator.translate_text_block(text, target_language="vi")
            print(f"  Original: {text}")
            print(f"  Vietnamese: {translated}")
            print()
        except Exception as e:
            print(f"  Error translating '{text}': {e}")
            print()

def demonstrate_srt_translation():
    """Demonstrate SRT file translation"""
    print("\n=== SRT Translation Demo ===")
    
    # Create sample SRT file
    create_sample_srt()
    
    # Translate SRT file
    try:
        translate_srt_file(
            input_file="sample.srt",
            output_file="sample_translated.srt",
            target_language="vi",
            genre="hienthai",
            max_batch_size=100
        )
        print("✓ Successfully translated sample.srt to sample_translated.srt")
        
        # Show the result
        if os.path.exists("sample_translated.srt"):
            with open("sample_translated.srt", "r", encoding="utf-8") as f:
                content = f.read()
                print("Translated content:")
                print(content)
    except Exception as e:
        print(f"✗ Error translating SRT file: {e}")

def demonstrate_json_translation():
    """Demonstrate JSON file translation"""
    print("\n=== JSON Translation Demo ===")
    
    # Create sample JSON file
    create_sample_json()
    
    # Translate JSON file
    try:
        translate_json_subtitles(
            input_file="sample.json",
            output_file="sample_translated.json",
            target_language="vi"
        )
        print("✓ Successfully translated sample.json to sample_translated.json")
        
        # Show the result
        if os.path.exists("sample_translated.json"):
            with open("sample_translated.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print("Translated content:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"✗ Error translating JSON file: {e}")

def cleanup_files():
    """Clean up sample files"""
    files_to_remove = [
        "sample.srt",
        "sample_translated.srt",
        "sample.json",
        "sample_translated.json"
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")

def main():
    """Main demonstration function"""
    print("Translation Features Demonstration")
    print("=" * 40)
    
    try:
        # Demonstrate different translation methods
        demonstrate_translation_service()
        demonstrate_srt_translation()
        demonstrate_json_translation()
        
        print("\n🎉 All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
    finally:
        # Clean up
        print("\nCleaning up sample files...")
        cleanup_files()

if __name__ == "__main__":
    main()
