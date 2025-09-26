#!/usr/bin/env python3
"""
Script to check violations in detail
"""

import json
from simple_segment_optimization import optimize_funasr_segments_to_spec, verify_segment_specifications, count_words_in_text
from typing import List, Dict, Any

def check_violations_in_detail():
    # Read the real transcript data
    with open('Video-CLI/downloads/在下熊岛主/20250831 第一集穿越成反派圣子成为天命之子打脸专属/vocals_transcript.json', 'r', encoding='utf-8') as f:
        transcript = json.load(f)
    
    print("Checking original transcript for violations:")
    violations_found = []
    for i, seg in enumerate(transcript):
        duration = seg['end'] - seg['start']
        word_count = count_words_in_text(seg['text'])
        if duration > 0.1 or word_count > 12:
            violations_found.append({
                'index': i,
                'start': seg['start'],
                'end': seg['end'],
                'duration': duration,
                'text': seg['text'],
                'word_count': word_count,
                'duration_violation': duration > 0.1,
                'word_violation': word_count > 12
            })
    
    print(f"Total violations in original: {len(violations_found)}")
    for v in violations_found[:5]:  # Show first 5 violations
        print(f"  Index {v['index']}: [{v['start']:.3f}s-{v['end']:.3f}s] {v['text'][:50]}...")
        print(f"    Duration: {v['duration']:.3f}s ({'VIOLATION' if v['duration_violation'] else 'OK'})")
        print(f"    Words: {v['word_count']} ({'VIOLATION' if v['word_violation'] else 'OK'})")
    
    # Apply optimization
    print("\nApplying optimization...")
    optimized = optimize_funasr_segments_to_spec(transcript)
    
    # Check violations in optimized transcript
    print("\nChecking optimized transcript for violations:")
    opt_violations = []
    # Small tolerance for floating point comparisons
    duration_tolerance = 1e-10
    for i, seg in enumerate(optimized):
        duration = seg['end'] - seg['start']
        word_count = count_words_in_text(seg['text'])
        # Allow a small tolerance for duration comparison to handle floating point precision issues
        if duration > 0.1 + duration_tolerance or word_count > 12:
            opt_violations.append({
                'index': i,
                'start': seg['start'],
                'end': seg['end'],
                'duration': duration,
                'text': seg['text'],
                'word_count': word_count,
                'duration_violation': duration > 0.1 + duration_tolerance,
                'word_violation': word_count > 12
            })
    
    print(f"Total violations in optimized: {len(opt_violations)}")
    for v in opt_violations:  # Show all violations
        print(f"  Index {v['index']}: [{v['start']:.3f}s-{v['end']:.3f}s] {v['text'][:50]}...")
        print(f"    Duration: {v['duration']:.3f}s ({'VIOLATION' if v['duration_violation'] else 'OK'})")
        print(f"    Words: {v['word_count']} ({'VIOLATION' if v['word_violation'] else 'OK'})")
    
    # Detailed analysis of word counting for problematic segments
    if opt_violations:
        print("\nDetailed analysis of problematic segments:")
        for v in opt_violations[:3]:  # Analyze first 3 violations
            print(f"\nSegment {v['index']}:")
            print(f"  Text: {v['text']}")
            print(f"  Duration: {v['duration']:.6f}s")
            print(f"  Word count: {v['word_count']}")
            print(f"  Character analysis:")
            for i, char in enumerate(v['text']):
                print(f"    [{i}] '{char}' - Unicode: U+{ord(char):04X}")

if __name__ == "__main__":
    check_violations_in_detail()
