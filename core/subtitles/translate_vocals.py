"""
Script to translate the vocals.srt file to Vietnamese
"""
from translation_api import translate_subtitles

# Define file paths
input_file = "downloads/浮浮众生_原创/20250925 百日严打/vocals.srt"
output_file = "downloads/浮浮众生_原创/20250925 百日严打/vocals_vn.srt"

# Translate the SRT file
print("Starting translation of vocals.srt to Vietnamese...")
translate_subtitles(
    input_file=input_file,
    output_file=output_file,
    method="local",  # Using local method for privacy and speed
    batch_size=16,   # Appropriate batch size for processing
    preserve_character_names=True  # Preserve character names during translation
)

print(f"Translation completed! Output saved to: {output_file}")
