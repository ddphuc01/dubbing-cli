import srt
from typing import List, Dict

def parse_srt_file(file_path: str) -> List[Dict]:
    """Parse SRT file and return list of subtitle entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    subtitles = srt.parse(content)
    result = []

    for subtitle in subtitles:
        result.append({
            'index': subtitle.index,
            'start': subtitle.start,
            'end': subtitle.end,
            'text': subtitle.content
        })

    return result

def compare_translations(deepseek_file: str, local_file: str):
    """Compare two translated SRT files."""
    print("So sánh hai file dịch SRT:")
    print(f"1. DeepSeekChat translation: {deepseek_file}")
    print(f"2. Local translation: {local_file}")
    print("=" * 80)
    
    # Parse both files
    deepseek_subs = parse_srt_file(deepseek_file)
    local_subs = parse_srt_file(local_file)
    
    # Compare statistics
    print(f"Tổng số phụ đề DeepSeek: {len(deepseek_subs)}")
    print(f"Tổng số phụ đề Local: {len(local_subs)}")
    
    if len(deepseek_subs) != len(local_subs):
        print("CẢNH BÁO: Số lượng phụ đề không khớp!")
    
    # Compare content
    matching = 0
    differing = 0
    
    min_length = min(len(deepseek_subs), len(local_subs))
    
    print("\nSo sánh chi tiết nội dung:")
    print("-" * 80)
    
    for i in range(min_length):
        deepseek_text = deepseek_subs[i]['text'].strip()
        local_text = local_subs[i]['text'].strip()
        
        if deepseek_text == local_text:
            matching += 1
        else:
            differing += 1
            print(f"\nĐoạn {i+1}:")
            print(f"  DeepSeek: {deepseek_text}")
            print(f"  Local:    {local_text}")
    
    print("-" * 80)
    print("KẾT QUẢ SO SÁNH:")
    print(f"Số đoạn trùng khớp: {matching}")
    print(f"Số đoạn khác nhau: {differing}")
    print(f"Tỷ lệ trùng khớp: {(matching/min_length)*100:.2f}%")
    
    # Additional analysis
    print("\nPHÂN TÍCH CHI TIẾT:")
    
    # Check for common issues in local translation
    local_issues = 0
    for i in range(min_length):
        local_text = local_subs[i]['text'].strip()
        # Check for common translation issues
        if "..." in local_text or "â" in local_text or "áº" in local_text:
            local_issues += 1
    
    print(f"Số đoạn có dấu hiệu lỗi mã hóa trong bản Local: {local_issues}")
    
    # Check for completeness
    if len(deepseek_subs) > len(local_subs):
        print(f"Bản Local thiếu {len(deepseek_subs) - len(local_subs)} đoạn")
    elif len(local_subs) > len(deepseek_subs):
        print(f"Bản DeepSeek thiếu {len(local_subs) - len(deepseek_subs)} đoạn")
    
    # Quality assessment
    print("\nĐÁNH GIÁ CHẤT LƯỢNG:")
    if matching/min_length > 0.8:
        print("✓ Hai bản dịch có độ tương đồng cao")
    else:
        print("⚠ Hai bản dịch có độ tương đồng thấp")
        
    if local_issues > 0:
        print("⚠ Bản Local có vấn đề về mã hóa ký tự")
    else:
        print("✓ Bản Local không có vấn đề về mã hóa ký tự")
        
    if abs(len(deepseek_subs) - len(local_subs)) == 0:
        print("✓ Cả hai bản dịch đều đầy đủ số đoạn")
    else:
        print("⚠ Một trong hai bản dịch bị thiếu đoạn")

if __name__ == "__main__":
    # So sánh hai file dịch
    deepseek_file = "545_deepseek.srt"  # File dịch bằng DeepSeekChat
    local_file = "545_vn.srt"  # File dịch bằng phương pháp local
    
    compare_translations(deepseek_file, local_file)
