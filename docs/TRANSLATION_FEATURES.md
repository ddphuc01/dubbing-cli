# Translation Features Documentation

This document describes the translation features integrated from the Translate repository into the project.

## Overview

The translation system provides Chinese to Vietnamese translation capabilities with support for multiple translation methods:
- Local translation using transformer models
- API-based translation via Gemini
- API-based translation via OpenRouter
- Hybrid approach combining multiple methods

## Core Components

### 1. Translation API Module (`core/subtitles/translation_api.py`)

The main module providing translation functionality with the following key classes:

- `TranslationProvider`: Abstract base class for translation providers
- `LocalTranslator`: Uses local transformer models for translation
- `GeminiTranslator`: Uses Google's Gemini API for translation
- `OpenRouterTranslator`: Uses OpenRouter API for translation
- `HybridTranslator`: Combines multiple translation methods

### 2. Character Name Manager (`core/subtitles/character_name_manager.py`)

Manages character names to preserve them during translation:
- Extracts potential character names from text
- Maintains a database of character names
- Preprocesses text to preserve names during translation
- Restores names after translation

## Features

### 1. Multi-Method Translation
The system supports several translation approaches:

#### Local Translation
- Uses Helsinki-NLP/opus-mt-zh-vi model
- Runs entirely locally
- No API keys required
- Good performance on GPU

#### API-Based Translation
- Gemini API: Requires Gemini CLI setup
- OpenRouter API: Requires API key
- Better quality for complex text

#### Hybrid Translation
- Combines multiple approaches
- Automatic fallback between methods
- Optimizes for quality and performance

### 2. Character Name Preservation
- Automatically detects potential character names
- Preserves names during translation process
- Maintains name consistency throughout document
- Supports custom name mappings

### 3. SRT Subtitle Translation
- Full support for SRT subtitle files
- Maintains timing information
- Batch processing for efficiency
- Progress tracking and logging

### 4. Flexible Configuration
- Configurable batch sizes
- Multiple quality settings
- Context-aware translation
- Detailed logging

## Usage Examples

### Translating Text
```python
from core.subtitles.translation_api import translate_text

# Local translation
result = translate_text("你好世界", method="local")

# With character name preservation
result = translate_text("你好刘福生", method="local", preserve_character_names=True)

# With context
result = translate_text("你好", method="local", movie_context="Phim hành động Trung Quốc")
```

### Translating SRT Files
```python
from core.subtitles.translation_api import translate_subtitles

# Local translation of SRT file
translate_subtitles(
    input_file="input.srt",
    output_file="output.srt",
    method="local",
    batch_size=16
)

# API-based translation with context
translate_subtitles(
    input_file="input.srt",
    output_file="output.srt",
    method="openrouter",
    openrouter_api_key="your-api-key",
    movie_context="Bối cảnh phim hoạt hình Trung Quốc",
    batch_size=8
)
```

## Configuration Options

### Translation Methods
- `local`: Uses local transformer model
- `gemini`: Uses Google Gemini API
- `openrouter`: Uses OpenRouter API
- `hybrid`: Uses multiple methods with fallback

### Parameters
- `batch_size`: Number of texts to process at once (default: 16)
- `preserve_character_names`: Whether to preserve character names (default: True)
- `movie_context`: Context information for better translation
- `openrouter_api_key`: API key for OpenRouter method

## Installation Requirements

The following packages are required for translation features:
- torch
- transformers
- srt
- tqdm
- requests
- Flask (for web interface)
- python-dotenv

These are included in the updated `requirements.txt`.

## Performance Considerations

- Local translation performance depends on hardware (CPU/GPU)
- Larger batch sizes improve throughput but require more memory
- Character name extraction adds preprocessing overhead
- API methods may have rate limits

## Error Handling

The system includes robust error handling:
- Automatic fallback between translation methods
- Detailed logging for debugging
- Timeout handling for API requests
- Graceful degradation when resources are unavailable
