#!/usr/bin/env python3
"""
Script to merge and align ASR subtitles with original subtitles
Based on the analysis, this script will merge over-segmented ASR entries
to better match the original subtitle structure.
"""
import re
from pathlib import Path

def parse_srt_content(content):
    """Parse SRT content into list of subtitle entries"""
    entries = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for entry in entries:
        if entry.strip():
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
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
    import difflib
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def merge_vocals_subtitles(vocals_subtitles, target_count):
    """
    Merge over-segmented vocals subtitles to match target count
    This function will combine adjacent entries to reduce the total number
    """
    if len(vocals_subtitles) <= target_count:
        return vocals_subtitles
    
    # Calculate how many entries we need to merge
    merge_factor = len(vocals_subtitles) / target_count
    merged_subtitles = []
    
    i = 0
    while i < len(vocals_subtitles):
        # Determine how many entries to merge
        merge_count = max(1, int(merge_factor))
        
        # Adjust merge count to not exceed remaining entries
        if i + merge_count > len(vocals_subtitles):
            merge_count = len(vocals_subtitles) - i
        
        # Merge entries
        merged_text = ""
        start_time = vocals_subtitles[i]['time'].split(' --> ')[0]
        end_time = vocals_subtitles[i + merge_count - 1]['time'].split(' --> ')[1]
        
        for j in range(merge_count):
            if j == 0:
                merged_text = vocals_subtitles[i + j]['text']
            else:
                merged_text += " " + vocals_subtitles[i + j]['text']
        
        time_range = f"{start_time} --> {end_time}"
        
        merged_subtitles.append({
            'index': len(merged_subtitles) + 1,
            'time': time_range,
            'text': merged_text.strip()
        })
        
        i += merge_count
    
    return merged_subtitles

def align_subtitles_by_content(raw_subtitles, vocals_subtitles):
    """
    Align subtitles by content similarity, allowing for 1:many and many:1 mappings
    """
    alignments = []
    raw_idx = 0
    vocals_idx = 0
    
    while raw_idx < len(raw_subtitles) and vocals_idx < len(vocals_subtitles):
        raw_text = raw_subtitles[raw_idx]['text']
        
        # Try to find best matching vocals entry
        best_match = None
        best_similarity = 0
        best_end_idx = vocals_idx
        
        # Look ahead to find combination of vocals that best matches raw text
        combined_text = ""
        for i in range(vocals_idx, min(len(vocals_subtitles), vocals_idx + 5)):
            if combined_text:
                combined_text += " " + vocals_subtitles[i]['text']
            else:
                combined_text = vocals_subtitles[i]['text']
            
            similarity = calculate_similarity(raw_text, combined_text)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = combined_text
                best_end_idx = i + 1
        
        # If we found a good match, align them
        if best_similarity > 0.6:
            # Get time range for the combined vocals
            start_time = vocals_subtitles[vocals_idx]['time'].split(' --> ')[0]
            end_time = vocals_subtitles[best_end_idx - 1]['time'].split(' --> ')[1]
            time_range = f"{start_time} --> {end_time}"
            
            alignments.append({
                'raw_index': raw_idx,
                'raw_text': raw_text,
                'vocals_text': best_match,
                'vocals_time': time_range,
                'similarity': best_similarity,
                'raw_time': raw_subtitles[raw_idx]['time'],
                'vocals_indices': list(range(vocals_idx, best_end_idx))
            })
            raw_idx += 1
            vocals_idx = best_end_idx
        else:
            # No good match found, move to next raw entry
            alignments.append({
                'raw_index': raw_idx,
                'raw_text': raw_text,
                'vocals_text': vocals_subtitles[vocals_idx]['text'],
                'vocals_time': vocals_subtitles[vocals_idx]['time'],
                'similarity': calculate_similarity(raw_text, vocals_subtitles[vocals_idx]['text']),
                'raw_time': raw_subtitles[raw_idx]['time'],
                'vocals_indices': [vocals_idx]
            })
            raw_idx += 1
            vocals_idx += 1
    
    # Add remaining vocals entries if any
    while vocals_idx < len(vocals_subtitles):
        alignments.append({
            'raw_index': -1,
            'raw_text': '',
            'vocals_text': vocals_subtitles[vocals_idx]['text'],
            'vocals_time': vocals_subtitles[vocals_idx]['time'],
            'similarity': 0,
            'raw_time': '',
            'vocals_indices': [vocals_idx]
        })
        vocals_idx += 1
    
    return alignments

def create_adjusted_subtitles(alignments, output_file):
    """Create adjusted subtitle file based on alignments"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, alignment in enumerate(alignments, 1):
            if alignment['raw_index'] != -1:  # Only include aligned entries
                f.write(f"{i}\n")
                f.write(f"{alignment['vocals_time']}\n")
                f.write(f"{alignment['vocals_text']}\n")
                f.write("\n")

def main():
    """Main function to merge and align subtitles"""
    raw_file = "Video-CLI/downloads/浮浮众生_原创/Raw.srt"
    vocals_file = "Video-CLI/downloads/浮浮众生_原创/20250924 赵秋明用强硬的态度希望刘浮生随他一起去冬日和但遭拒/vocals.srt"
    output_file = "Video-CLI/downloads/浮浮众生_原创/adjusted_vocals.srt"
    
    print("Adjusting ASR Subtitles to Match Original Structure")
    print("=" * 60)
    
    # Load both files
    raw_subtitles = load_srt_file(raw_file)
    vocals_subtitles = load_srt_file(vocals_file)
    
    print(f"Original Raw entries: {len(raw_subtitles)}")
    print(f"Original Vocals entries: {len(vocals_subtitles)}")
    
    # Align subtitles by content
    alignments = align_subtitles_by_content(raw_subtitles, vocals_subtitles)
    
    print(f"Created {len(alignments)} aligned entries")
    
    # Create adjusted subtitle file
    create_adjusted_subtitles(alignments, output_file)
    
    # Load the adjusted file to verify
    adjusted_subtitles = load_srt_file(output_file)
    print(f"Adjusted entries: {len(adjusted_subtitles)}")
    
    # Calculate statistics
    total_similarity = sum(a['similarity'] for a in alignments if a['raw_index'] != -1)
    aligned_count = sum(1 for a in alignments if a['raw_index'] != -1)
    
    if aligned_count > 0:
        avg_similarity = total_similarity / aligned_count
        print(f"Average alignment similarity: {avg_similarity:.2%}")
    
    print(f"Adjusted subtitles saved to: {output_file}")
    
    # Show some examples
    print("\nFirst 5 adjusted entries:")
    print("-" * 40)
    for i in range(min(5, len(alignments))):
        alignment = alignments[i]
        if alignment['raw_index'] != -1:
            print(f"Entry {i+1}:")
            print(f"  Raw:    '{alignment['raw_text'][:50]}{'...' if len(alignment['raw_text']) > 50 else ''}'")
            print(f"  Adjusted: '{alignment['vocals_text'][:50]}{'...' if len(alignment['vocals_text']) > 50 else ''}'")
            print(f"  Similarity: {alignment['similarity']:.2%}")
            print()

if __name__ == "__main__":
    main()
