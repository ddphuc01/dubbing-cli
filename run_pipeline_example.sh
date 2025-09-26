#!/bin/bash
# Example usage script for Video-CLI pipeline

echo "Video-CLI Pipeline Usage Examples"
echo "================================"

echo ""
echo "Example 1: Download a single video and process its audio"
echo "------------------------------------------------------"
echo "python run_pipeline.py \"https://www.youtube.com/watch?v=jNQXAC9IVRw\" -o \"examples/single_video\" -r 360p -d cpu"
echo ""

echo "Example 2: Download a playlist and process all videos"
echo "---------------------------------------------------"
echo "python run_pipeline.py \"https://www.youtube.com/playlist?list=PLw02K2RyJZ5b4B4n4C9n3n9n9\" -o \"examples/playlist\" -r 720p -n 3 -d cuda"
echo ""

echo "Example 3: Download a video and process its audio with speaker diarization"
echo "------------------------------------------------------------------------"
echo "python run_pipeline.py \"https://www.bilibili.com/video/BV1m5aGzVEaj/\" -o \"examples/bilibili_video\" -r 1080p -d cuda --subtitle-method WhisperX --subtitle-model large --min-speakers 2 --max-speakers 4"
echo ""

echo "Example 4: Download a video and process its audio with FunASR"
echo "-----------------------------------------------------------"
echo "python run_pipeline.py \"https://www.youtube.com/watch?v=example\" -o \"examples/funasr_video\" -r 720p -d cpu --subtitle-method FunASR"
echo ""

echo "To run any of these examples, copy the command and paste it in your terminal."
