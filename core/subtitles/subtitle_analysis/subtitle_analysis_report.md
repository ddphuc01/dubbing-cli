# Phân tích và Điều chỉnh Phụ đề ASR

## Tổng quan

Phân tích so sánh giữa 2 file phụ đề:
- **Raw.srt**: File phụ đề gốc (351 entries)
- **vocals.srt**: File phụ đề từ ASR (462 entries)
- **adjusted_vocals.srt**: File phụ đề đã được điều chỉnh (351 entries)

## Phát hiện chính

### 1. Sự khác biệt ban đầu
- **Số lượng entries**: vocals.srt có 462 entries so với 351 của raw.srt (nhiều hơn 111 entries)
- **Tỷ lệ phân đoạn**: vocals.srt bị over-segmented (phân đoạn quá mức)
- **Độ tương đồng nội dung**: 89.55% (kết hợp toàn bộ văn bản)
- **Độ tương đồng trung bình mỗi entry**: 4.64% (khi so sánh từng entry riêng lẻ)

### 2. Vấn đề nhận diện
- ASR (FunASR) nhận diện nội dung chính xác nhưng phân đoạn không đúng
- vocals.srt có nhiều entry ngắn (<5 ký tự) do phân đoạn quá mức
- vocals.srt có nhiều dấu câu hơn raw.srt (305 vs 0 entries có dấu câu)

### 3. Kết quả sau điều chỉnh
- Đã giảm số lượng entries từ 462 xuống 351 để phù hợp với raw.srt
- **Độ tương đồng trung bình sau điều chỉnh**: 69.3%
- Giữ được nội dung chính nhưng cải thiện cấu trúc phân đoạn

## Phân tích chi tiết

### Mẫu so sánh đầu tiên:
1. **Entry 1**:
   - Raw: '书姐刚才您和前厅长'
   - Vocals: '书记， 刚才您和前厅'
   - Similarity: 73.68%

2. **Entry 2**:
   - Raw: '关于粤东省公安系统内部表彰大会'
   - Vocals: '长关于粤 东省公安系 统内部表彰 大会在潮'
   - Similarity: 83.33% (đã được gộp từ nhiều entries nhỏ)

## Kết luận

1. **ASR hoạt động tốt về mặt nhận diện nội dung** - độ chính xác văn bản lên đến ~89%
2. **Vấn đề chính là phân đoạn không chính xác** - cần điều chỉnh tham số ASR hoặc post-processing
3. **Giải pháp hiệu quả** - gộp các entry nhỏ thành các entry lớn hơn để phù hợp với cấu trúc gốc
4. **Chất lượng cuối cùng** - đạt 69.33% độ tương đồng trung bình sau khi điều chỉnh

## Đề xuất cải thiện

1. **Tinh chỉnh tham số ASR**: Điều chỉnh ngưỡng phân đoạn để tạo các entry dài hơn, hợp lý hơn
2. **Post-processing**: Sử dụng thuật toán phân đoạn thông minh để gộp các câu liên quan
3. **Kiểm tra chất lượng**: So sánh với phụ đề gốc để đảm bảo độ chính xác và cấu trúc phù hợp
4. **Tự động hóa**: Tích hợp quá trình điều chỉnh vào pipeline ASR để xử lý tự động

## Tệp đã tạo
- `compare_subtitles.py`: So sánh cơ bản giữa 2 file phụ đề
- `detailed_analysis.py`: Phân tích chi tiết các mẫu lỗi và chất lượng
- `merge_subtitles.py`: Gộp và điều chỉnh phụ đề ASR
- `adjusted_vocals.srt`: File phụ đề đã được điều chỉnh (351 entries)
