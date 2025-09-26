# Video-CLI

A command-line tool for processing videos, including downloading, audio separation, subtitle generation, and more.

## Features

- Download videos from various platforms using yt-dlp
- Separate vocals from audio using Demucs
- Generate subtitles using WhisperX, FunASR, or NeMo
- Translate subtitles
- Convert SRT subtitles to synchronized audio using TTS
- Support for multiple subtitle formats (SRT, VTT, TXT)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Video-CLI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For WhisperX support (recommended for better results):
   ```bash
   pip install git+https://github.com/m-bain/whisperx.git
   ```

## Usage

### Generate Subtitles

```bash
python audio_to_subtitle.py "path/to/audio.wav" -m FunASR -d cuda
```

### Advanced Subtitle Generation with Speaker Diarization

To enable proper speaker diarization (identifying different speakers like CapCut does), which will create SRT files with more granular timing and speaker identification similar to CapCut output, follow these steps:

1. Get a Hugging Face token for the diarization model (required for speaker separation):
   - Go to https://huggingface.co/
   - Create an account or log in
   - Go to your profile → Settings → Access Tokens
   - Create a new token
   - Accept the user agreement for the pyannote/speaker-diarization-3.1 model at https://huggingface.co/pyannote/speaker-diarization-3.1

2. Create a `.env` file in the Video-CLI directory with your token and speaker range settings:
   ```
   HF_TOKEN=your_token_here
   MIN_SPEAKERS=1
   MAX_SPEAKERS=10
   ```

3. Run subtitle generation with diarization to get CapCut-like granular timing and speaker identification:
   ```bash
   python audio_to_subtitle.py "path/to/audio.wav" -m FunASR -d cuda --min-speakers 1 --max-speakers 10
   ```

## Options

- `-m, --method`: ASR method to use (WhisperX, FunASR, NeMo)
- `-d, --device`: Device to use (auto, cpu, cuda)
- `--model`: Model name (for WhisperX: base, small, medium, large)
- `--min-speakers`, `--max-speakers`: Set speaker range for diarization
- `--no-diarization`: Disable speaker diarization
- `--formats`: Output formats (srt, vtt, txt, json)

## Requirements

- Python 3.8+
- PyTorch with CUDA support (recommended)
- ffmpeg

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

Note: By default, all ASR methods (WhisperX, FunASR, and NeMo) are included in the requirements. If you only want to use specific methods, you can comment out the corresponding lines in `requirements.txt` before running the installation command.

## Environment Setup

To use the audio-to-subtitle functionality with WhisperX and speaker diarization, you need to set up your environment properly:

1. Create a `.env` file in the Video-CLI directory by copying the example file:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Hugging Face token:
   ```
   # Get your token from: https://huggingface.co/settings/tokens
   HF_TOKEN=your_actual_token_here
   ```

3. For speaker diarization, you need to request access to the pyannote/speaker-diarization-3.1 model on Hugging Face at: https://huggingface.co/pyannote/speaker-diarization-3.1

Note: By default, all ASR methods (WhisperX, FunASR, and NeMo) are included in the requirements. If you only want to use specific methods, you can comment out the corresponding lines in `requirements.txt` before running the installation command.

## Usage

### Video Download
```
python download_video.py [URL] [OPTIONS]
```

#### Options
- `-o`, `--output`: Output directory (default: "downloads")
- `-r`, `--resolution`: Video resolution (default: "1080p")
- `-n`, `--num-videos`: Number of videos to download from playlist (default: 5)
- `-h`, `--help`: Show help message

#### Examples

Download a single video:
```
python download_video.py "https://www.youtube.com/watch?v=example"
```

Download a playlist with specific settings:
```
python download_video.py "https://www.youtube.com/playlist?list=example" -o "my_videos" -r "720p" -n 10
```

### Audio Extraction and Vocal Separation
```
python separate_audio.py [VIDEO_PATH] [OPTIONS]
```

#### Options
- `-o`, `--output-dir`: Output directory for separated audio files
- `-s`, `--separate-vocals`: Separate vocals from instrumental tracks
- `-m`, `--model`: Demucs model to use (default: htdemucs_ft)
- `-d`, `--device`: Device to use for processing (auto, cpu, cuda)
- `-h`, `--help`: Show help message

#### Examples

Extract audio from a video:
```
python separate_audio.py "path/to/video.mp4"
```

Extract audio and separate vocals:
```
python separate_audio.py "path/to/video.mp4" -s
```

Extract audio and separate vocals using GPU:
```
python separate_audio.py "path/to/video.mp4" -s -d cuda
```

### Complete Pipeline (Download and Separate)
```
python pipeline.py [URL] [OPTIONS]
```

#### Options
- `-o`, `--output-dir`: Output directory for downloaded video (default: downloads)
- `-r`, `--resolution`: Video resolution (default: 1080p)
- `-n`, `--num-videos`: Number of videos to download from playlist (default: 5)
- `-d`, `--device`: Device to use for audio separation (auto, cpu, cuda)
- `-h`, `--help`: Show help message

#### Examples

Download a video and separate its audio:
```
python pipeline.py "https://www.youtube.com/watch?v=example"
```

Download a video in 720p and separate its audio using GPU:
```
python pipeline.py "https://www.youtube.com/watch?v=example" -r 720p -d cuda
```

### Subtitle Generation with Speaker Diarization
```bash
python audio_to_subtitle.py [AUDIO_PATH] [OPTIONS]
```

#### Options
- `-f`, `--folder`: Folder containing vocal audio file (alternative to AUDIO_PATH)
- `-m`, `--method`: ASR method to use (WhisperX, FunASR, or NeMo, default: FunASR)
- `--model`: Model name (for WhisperX: base, small, medium, large, default: large)
- `-d`, `--device`: Device to use for processing (auto, cpu, cuda, default: auto)
- `--no-diarization`: Disable speaker diarization
- `--min-speakers`: Minimum number of speakers
- `--max-speakers`: Maximum number of speakers
- `-o`, `--output-dir`: Output directory for subtitle files
- `--formats`: Subtitle formats to generate (srt, vtt, txt, json, default: srt vtt txt)
- `-h`, `--help`: Show help message

#### Examples

Generate subtitles from vocal audio with speaker diarization:
```bash
python audio_to_subtitle.py "path/to/vocals.wav"
```

Generate subtitles using FunASR (default):
```bash
python audio_to_subtitle.py "path/to/vocals.wav" -m FunASR
```

Generate subtitles with GPU processing:
```bash
python audio_to_subtitle.py "path/to/vocals.wav" -d cuda
```

Generate subtitles from vocal audio in a folder:
```bash
python audio_to_subtitle.py -f "path/to/video/folder"
```

### Subtitle Translation
```bash
python translate_subtitles.py [INPUT_SRT] [OPTIONS]
```

#### Options
- `-o`, `--output-path`: Output path for translated .srt file
- `-s`, `--source-lang`: Source language (default: auto)
- `-t`, `--target-lang`: Target language (default: en)
- `-r`, `--translator`: Translator service to use (google, bing, baidu, deepl, default: google)
- `-b`, `--batch-size`: Batch size for translation (default: 10)
- `-h`, `--help`: Show help message

#### Examples

Translate subtitles from auto-detected language to English:
```bash
python translate_subtitles.py "path/to/subtitles.srt"
```

Translate subtitles from Chinese to Vietnamese:
```bash
python translate_subtitles.py "path/to/subtitles.srt" -s zh -t vi
```

Translate subtitles using Bing translator:
```bash
python translate_subtitles.py "path/to/subtitles.srt" -r bing -t es
```

Translate subtitles with custom output path:
```bash
python translate_subtitles.py "path/to/subtitles.srt" -o "path/to/translated_subtitles.srt" -t fr
```

### SRT to Audio Conversion (TTS)
```bash
python srt_to_audio.py [SRT_PATH] [OPTIONS]
```

#### Options
- `-o`, `--output-dir`: Output directory for generated audio files
- `--method`: TTS method to use (edge, xtts, gtts, default: edge)
- `--voice`: Voice to use for Edge TTS (default: en-US-MichelleNeural)
- `--speaker-wav`: Path to speaker reference audio file for XTTS voice cloning
- `--language`: Language code for TTS (default: en)
- `--no-stretch`: Disable audio stretching to match subtitle duration
- `--combine`: Combine all generated audio files into a single file
- `-h`, `--help`: Show help message

#### TTS Speed Information
The default TTS speed varies by engine:
- **Edge TTS**: Normal human speaking speed (~150 words per minute)
- **gTTS**: Normal speaking speed
- **XTTS**: Configurable speed through the underlying model

Currently, the TTS engines don't expose direct speed controls through the API. To adjust the speed of the generated audio, you can use audio editing software or command-line tools like FFmpeg after generation. For example:
```bash
ffmpeg -i input.wav -filter:a atempo=1.2 output.wav  # Increase speed by 20%
ffmpeg -i input.wav -filter:a atempo=0.8 output.wav  # Decrease speed by 20%
```

#### Examples

Convert SRT to audio using Edge TTS (default):
```bash
python srt_to_audio.py "path/to/subtitles.srt"
```

Convert SRT to audio with specific voice and language:
```bash
python srt_to_audio.py "path/to/subtitles.srt" --voice "en-US-RogerNeural" --language "en" --output-dir "./audio_output"
```

Convert SRT to audio using XTTS with voice cloning (requires speaker reference audio):
```bash
python srt_to_audio.py "path/to/subtitles.srt" --method xtts --speaker-wav "path/to/speaker.wav" --language "en"
```

Convert SRT to audio and combine all segments into a single file:
```bash
python srt_to_audio.py "path/to/subtitles.srt" --combine
```

### Pipeline (Download and Separate)
```bash
python pipeline.py [URL] [OPTIONS]
```

#### Options
- `-o`, `--output-dir`: Output directory for downloaded video (default: downloads)
- `-r`, `--resolution`: Video resolution (default: 1080p)
- `-n`, `--num-videos`: Number of videos to download from playlist (default: 5)
- `-d`, `--device`: Device to use for audio separation (auto, cpu, cuda, default: auto)
- `-h`, `--help`: Show help message

#### Examples

Download a video and separate its audio:
```bash
python pipeline.py "https://www.youtube.com/watch?v=example"
```

Download a video in 720p and separate its audio using GPU:
```bash
python pipeline.py "https://www.youtube.com/watch?v=example" -r 720p -d cuda
```

### Model Download

To download the required FunASR models locally for offline use, run the following command:
```bash
python download_models.py --model-type funasr
```

This will download all necessary FunASR models to the `models/ASR/FunASR/` directory. The audio_to_subtitle.py script will automatically use these local models if they exist, falling back to online models if needed.

## Supported Platforms

- YouTube
- Bilibili
- And other platforms supported by yt-dlp

## Dependencies

- yt-dlp
- loguru
- ffmpeg (for audio extraction)
- torch (for vocal separation)
- numpy (for vocal separation)
- scipy (for vocal separation)
- demucs (for vocal separation)
- edge-tts (for TTS functionality)
- TTS (for XTTS functionality)
- gTTS (for basic TTS functionality)

## Setting up Git and Pushing to GitHub

To prepare this project for uploading to GitHub, follow these steps:

1. Remove unnecessary data directories before committing:
   ```bash
   # Remove download and test output directories that shouldn't be committed
   rm -rf downloads/
   rm -rf test_output/
   rm -rf models/ # Only if the models directory is too large to commit
   ```

2. Make sure your `.env` file (containing sensitive information like API keys) is not committed. It should already be in `.gitignore`.

3. Initialize Git repository and add remote origin:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Add Video-CLI project"
   git branch -M main
   git remote add origin <your-github-repository-url>
   git push -u origin main
   ```

Alternatively, you can use the provided setup scripts in this repository to automate the process:
- On Linux/Mac: `setup_git.sh` (make sure to chmod +x before running)
- On Windows: `setup_git.bat`
#   d u b b i n g - c l i  
 