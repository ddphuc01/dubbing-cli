@echo off
REM Example batch script to run SRT to Audio functionality

setlocal

echo Running SRT to Audio example...
echo.

REM Check if required arguments are provided
if "%~1"=="" (
    echo Usage: %0 ^<srt_file^> [output_dir] [method] [voice]
    echo Example: %0 "example.srt" "./output" "edge" "en-US-MichelleNeural"
    exit /b 1
)

set "SRT_FILE=%~1"
set "OUTPUT_DIR=%~2"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=./tts_output"
set "METHOD=%~3"
if "%METHOD%"=="" set "METHOD=edge"
set "VOICE=%~4"
if "%VOICE%"=="" set "VOICE=en-US-MichelleNeural"

echo SRT File: %SRT_FILE%
echo Output Directory: %OUTPUT_DIR%
echo TTS Method: %METHOD%
echo Voice: %VOICE%
echo.

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Run the Python script
python run_tts_example.py --srt-file "%SRT_FILE%" --output-dir "%OUTPUT_DIR%" --method "%METHOD%" --voice "%VOICE%"

echo.
echo Example completed!
pause
