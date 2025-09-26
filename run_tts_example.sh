#!/bin/bash
# Example shell script to run SRT to Audio functionality

echo "Running SRT to Audio example..."
echo

# Check if required arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <srt_file> [output_dir] [method] [voice]"
    echo "Example: $0 example.srt ./output edge en-US-MichelleNeural"
    exit 1
fi

SRT_FILE="$1"
OUTPUT_DIR="${2:-./tts_output}"
METHOD="${3:-edge}"
VOICE="${4:-en-US-MichelleNeural}"

echo "SRT File: $SRT_FILE"
echo "Output Directory: $OUTPUT_DIR"
echo "TTS Method: $METHOD"
echo "Voice: $VOICE"
echo

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Run the Python script
python run_tts_example.py --srt-file "$SRT_FILE" --output-dir "$OUTPUT_DIR" --method "$METHOD" --voice "$VOICE"

echo
echo "Example completed!"
