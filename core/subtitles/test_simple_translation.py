#!/usr/bin/env python3
"""
Test script for simple translation functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test that we can import the translation module"""
    try:
        import simple_translation
        print("✓ Successfully imported simple_translation")
        return True
    except Exception as e:
        print(f"✗ Failed to import simple_translation: {e}")
        return False

def test_translator_class():
    """Test translator class instantiation"""
    try:
        from simple_translation import SimpleTranslator
        translator = SimpleTranslator()
        print("✓ Successfully instantiated SimpleTranslator")
        print(f"  Torch available: {translator.torch_available}")
        print(f"  Transformers available: {translator.transformers_available}")
        print(f"  Device: {translator.device}")
        return True
    except Exception as e:
        print(f"✗ Failed to instantiate SimpleTranslator: {e}")
        return False

def test_srt_function():
    """Test SRT translation function"""
    try:
        # Create a simple test SRT file
        test_srt_content = """1
00:00:01,000 --> 00:00:04,000
Hello world

2
00:00:05,000 --> 00:00:08,000
This is a test subtitle
"""
        
        with open("test_input.srt", "w", encoding="utf-8") as f:
            f.write(test_srt_content)
        
        # Test importing the function
        from simple_translation import translate_srt_file
        
        print("✓ SRT translation function imported successfully")
        print("  Created test SRT file")
        return True
    except Exception as e:
        print(f"✗ Failed to test SRT translation function: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_input.srt",
        "test_output.srt"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  Cleaned up {file}")
            except Exception as e:
                print(f"  Warning: Could not remove {file}: {e}")

def main():
    """Main test function"""
    print("Testing simple_translation.py...\n")
    
    # Run tests
    tests = [
        test_import,
        test_translator_class,
        test_srt_function
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
    
    # Cleanup
    print("\nCleaning up test files...")
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
