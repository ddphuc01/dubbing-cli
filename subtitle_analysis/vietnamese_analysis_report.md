# Báo Cáo Phân Tích Phụ Đề ASR (Tiếng Việt)

## Tổng Quan

Phân tích so sánh giữa 2 file phụ đề:
- **Raw.srt**: File phụ đề gốc (351 entries)
- **vocals.srt**: File phụ đề từ ASR (462 entries) 
- **adjusted_vocals.srt**: File phụ đề đã được điều chỉnh (351 entries)

## Phát Hiện Chính

### 1. Sự khác biệt ban đầu
- **Số lượng entries**: vocals.srt có 462 entries so với 351 của raw.srt (nhiều hơn 111 entries)
- **Tỷ lệ phân đoạn**: vocals.srt bị phân đoạn quá mức (over-segmented)
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

## Phân Tích Chi Tiết

### Mẫu so sánh đầu tiên:
1. **Entry 1**:
   - Raw: '书姐刚才您和前厅长'
   - Vocals: '书记， 刚才您和前厅'
   - Độ tương đồng: 73.68%

2. **Entry 2**:
   - Raw: '关于粤东省公安系统内部表彰大会'
   - Vocals: '长关于粤 东省公安系 统内部表彰 大会在潮'
   - Độ tương đồng: 83.33% (đã được gộp từ nhiều entries nhỏ)

## Mức Độ Khác Nhau Về Nội Dung

### Kết Luận Chính
**Nội dung và ý nghĩa của 2 file không khác nhau quá lớn**

### Phân tích chi tiết
- **Độ tương đồng nội dung tổng thể**: 89.5%
- **Tỷ lệ ký tự**: 117.75% (vocals.srt có 3,900 ký tự so với 3,312 ký tự của raw.srt)
- **Số lượng entries**: raw.srt (351) vs vocals.srt (462)

**Về mặt nội dung cốt lõi**: KHÔNG CÓ SỰ KHÁC NHAU LỚN
- Nội dung chính được giữ nguyên giữa 2 file (89.5% tương đồng)
- ASR đã nhận diện đúng các từ khóa và câu quan trọng
- Ý nghĩa tổng thể của đoạn hội thoại được bảo toàn

**Về mặt cấu trúc phân đoạn**: CÓ SỰ KHÁC NHAU ĐÁNG KỂ
- vocals.srt bị chia thành nhiều đoạn nhỏ hơn (462 vs 351 entries)
- Các câu bị cắt ngang giữa chừng do phân đoạn quá mức
- Thời gian đồng bộ giữa các entry không khớp

### Ví dụ cụ thể:
1. Entry 1: '书姐刚才您和前厅长' → '书记， 刚才您和前厅' (73.68% tương đồng)
   - Nội dung: Giữ nguyên, chỉ khác từ "书姐" vs "书记"
   - Cấu trúc: vocals bị cắt ngắn hơn

2. Entry 2-3: '关于粤东省公安系统内部表彰大会' và '在朝江市召开的相关内容' 
   → bị chia thành nhiều phần nhỏ trong vocals.srt
   - Nội dung: Giữ nguyên thông tin chính
   - Cấu trúc: vocals.srt chia nhỏ quá mức

## Kết Luận

**Nội dung cơ bản không khác nhau lớn**:
- ASR (FunASR) nhận diện nội dung chính xác ~89.55%
- Các từ khóa, tên người, tên địa điểm đều được giữ nguyên
- Ý nghĩa của đoạn hội thoại không bị thay đổi đáng kể

**Sự khác biệt chủ yếu ở phân đoạn**:
- vocals.srt bị over-segmented (phân đoạn quá mức)
- Các câu bị chia nhỏ, làm giảm tính liên tục
- Không ảnh hưởng đến nội dung cốt lõi nhưng ảnh hưởng đến trải nghiệm đọc

**Điều này chứng tỏ**:
- ASR hoạt động tốt về mặt nhận diện nội dung
- Vấn đề chính là ở tham số phân đoạn, không phải ở chất lượng nhận diện
- File đã điều chỉnh `adjusted_vocals.srt` giải quyết vấn đề này hiệu quả

## Đề Xuất Cải Thiện

1. **Tinh chỉnh tham số ASR**: Điều chỉnh ngưỡng phân đoạn để tạo các entry dài hơn, hợp lý hơn
2. **Post-processing**: Sử dụng thuật toán phân đoạn thông minh để gộp các câu liên quan
3. **Kiểm tra chất lượng**: So sánh với phụ đề gốc để đảm bảo độ chính xác và cấu trúc phù hợp
4. **Tự động hóa**: Tích hợp quá trình điều chỉnh vào pipeline ASR để xử lý tự động

## Các Tệp Đã Tạo
- `compare_subtitles.py`: So sánh cơ bản giữa 2 file phụ đề
- `detailed_analysis.py`: Phân tích chi tiết các mẫu lỗi và chất lượng
- `merge_subtitles.py`: Gộp và điều chỉnh phụ đề ASR
- `adjusted_vocals.srt`: File phụ đề đã được điều chỉnh (351 entries)
- `subtitle_analysis_report.md`: Báo cáo gốc
- `content_difference_analysis.md`: Phân tích sự khác biệt nội dung
- `vietnamese_analysis_report.md`: Báo cáo này (tiếng Việt)
