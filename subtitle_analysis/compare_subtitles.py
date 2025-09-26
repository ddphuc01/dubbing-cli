#!/usr/bin/env python3
"""
Script to compare two SRT subtitle files and analyze their differences
"""
import re
import difflib
from pathlib import Path

def parse_srt_content(content):
    """Parse SRT content into list of subtitle entries"""
    # Split by double newlines
    entries = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for entry in entries:
        if entry.strip():
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
                # Format: Index, Time, Text
                try:
                    index = lines[0] if lines[0].isdigit() else ''
                    time_line = lines[1] if '-->' in lines[1] else ''
                    text_lines = lines[2:] if time_line else lines[1:]
                    text = '\n'.join(text_lines)
                    
                    subtitles.append({
                        'index': index,
                        'time': time_line,
                        'text': text.strip()
                    })
                except:
                    continue
    return subtitles

def load_srt_file(filepath):
    """Load and parse SRT file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_srt_content(content)

def calculate_similarity(text1, text2):
    """Calculate similarity ratio between two texts"""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def compare_subtitles(raw_file, vocals_file):
    """Compare two subtitle files"""
    print("Comparing Subtitle Files")
    print("=" * 60)
    
    # Load both files
    raw_subtitles = load_srt_file(raw_file)
    vocals_subtitles = load_srt_file(vocals_file)
    
    print(f"Raw.srt: {len(raw_subtitles)} entries")
    print(f"vocals.srt: {len(vocals_subtitles)} entries")
    print()
    
    # Compare each entry
    total_similarity = 0
    matched_entries = 0
    mismatches = []
    
    min_len = min(len(raw_subtitles), len(vocals_subtitles))
    
    for i in range(min_len):
        raw_text = raw_subtitles[i]['text']
        vocals_text = vocals_subtitles[i]['text']
        
        similarity = calculate_similarity(raw_text, vocals_text)
        total_similarity += similarity
        matched_entries += 1
        
        if similarity < 0.8:  # Consider as mismatch if similarity < 80%
            mismatches.append({
                'index': i + 1,
                'raw_text': raw_text,
                'vocals_text': vocals_text,
                'similarity': similarity
            })
    
    # Calculate overall statistics
    avg_similarity = total_similarity / matched_entries if matched_entries > 0 else 0
    accuracy_rate = (matched_entries - len(mismatches)) / matched_entries * 100 if matched_entries > 0 else 0
    
    print("STATISTICS:")
    print(f"Average similarity: {avg_similarity:.2%}")
    print(f"Accuracy rate (80%+ match): {accuracy_rate:.2f}%")
    print(f"Total mismatches: {len(mismatches)} out of {matched_entries} entries")
    print()
    
    # Show mismatches
    if mismatches:
        print("MISMATCHES (similarity < 80%):")
        print("-" * 60)
        for mismatch in mismatches[:10]:  # Show first 10 mismatches
            print(f"Entry {mismatch['index']}:")
            print(f"  Raw:     '{mismatch['raw_text'][:100]}{'...' if len(mismatch['raw_text']) > 10 else ''}'")
            print(f"  Vocals:  '{mismatch['vocals_text'][:100]}{'...' if len(mismatch['vocals_text']) > 100 else ''}'")
            print(f"  Similarity: {mismatch['similarity']:.2%}")
            print()
        
        if len(mismatches) > 10:
            print(f"... and {len(mismatches) - 10} more mismatches")
        print()
    
    # Show detailed comparison for first few entries
    print("DETAILED COMPARISON (first 5 entries):")
    print("-" * 60)
    for i in range(min(5, min_len)):
        raw_text = raw_subtitles[i]['text']
        vocals_text = vocals_subtitles[i]['text']
        similarity = calculate_similarity(raw_text, vocals_text)
        
        print(f"Entry {i + 1} (similarity: {similarity:.2%}):")
        print(f"  Raw:    {raw_subtitles[i]['time']}")
        print(f"         '{raw_text}'")
        print(f"  Vocals: {vocals_subtitles[i]['time']}")
        print(f"         '{vocals_text}'")
        print()
    
    # Analyze segmentation differences
    print("SEGMENTATION ANALYSIS:")
    print("-" * 60)
    print(f"Difference in entry count: {len(vocals_subtitles) - len(raw_subtitles)}")
    
    if len(vocals_subtitles) > len(raw_subtitles):
        print("vocals.srt has more entries - ASR may have over-segmented")
    elif len(vocals_subtitles) < len(raw_subtitles):
        print("vocals.srt has fewer entries - ASR may have under-segmented")
    else:
        print("Same number of entries - segmentation is consistent")
    
    print()
    
    # Show some specific examples of differences
    print("SPECIFIC EXAMPLES:")
    print("-" * 60)
    
    # Find examples of different segmentation
    if len(vocals_subtitles) != len(raw_subtitles):
        print("Segmentation differences found:")
        print(f"Raw entries: {len(raw_subtitles)}")
        print(f"Vocals entries: {len(vocals_subtitles)}")
        
        # Show some combined text to see if meaning is preserved
        raw_combined = " ".join([s['text'] for s in raw_subtitles])
        vocals_combined = " ".join([s['text'] for s in vocals_subtitles])
        
        combined_similarity = calculate_similarity(raw_combined, vocals_combined)
        print(f"Combined text similarity: {combined_similarity:.2%}")
        print()
    
    # Quality assessment
    print("QUALITY ASSESSMENT:")
    print("-" * 60)
    if avg_similarity >= 0.9:
        quality = "EXCELLENT"
    elif avg_similarity >= 0.8:
        quality = "GOOD"
    elif avg_similarity >= 0.7:
        quality = "FAIR"
    else:
        quality = "POOR"
    
    print(f"Overall quality: {quality}")
    print(f"Average similarity: {avg_similarity:.2%}")
    print(f"Accuracy rate: {accuracy_rate:.2f}%")
    
    return {
        'avg_similarity': avg_similarity,
        'accuracy_rate': accuracy_rate,
        'total_entries': matched_entries,
        'mismatches': len(mismatches),
        'quality': quality
    }

def main():
    """Main function to compare the two subtitle files"""
    raw_file = "Video-CLI/downloads/浮浮众生_原创/Raw.srt"
    vocals_file = "Video-CLI/downloads/浮浮众生_原创/20250924 赵秋明用强硬的态度希望刘浮生随他一起去冬日和但遭拒/vocals.srt"
    
    if not Path(raw_file).exists():
        print(f"Error: {raw_file} not found")
        return
    
    if not Path(vocals_file).exists():
        print(f"Error: {vocals_file} not found")
        return
    
    results = compare_subtitles(raw_file, vocals_file)
    
    print("\nSUMMARY:")
    print(f"Quality: {results['quality']}")
    print(f"Similarity: {results['avg_similarity']:.2%}")
    print(f"Accuracy: {results['accuracy_rate']:.2f}%")
    print(f"Mismatches: {results['mismatches']}/{results['total_entries']}")

if __name__ == "__main__":
    main()
