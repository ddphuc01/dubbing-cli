# Phân tích Mức Độ Khác Nhau Về Nội Dung Giữa 2 File Phụ Đề

## Kết quả phân tích

### 1. Độ tương đồng nội dung tổng thể
- **Độ tương đồng văn bản kết hợp**: 89.5%
- **Tỷ lệ ký tự**: 117.75% (vocals.srt có 3,900 ký tự so với 3,312 ký tự của raw.srt)
- **Số lượng entries**: raw.srt (351) vs vocals.srt (462)

### 2. Đánh giá mức độ khác nhau về nội dung

**Về mặt nội dung cốt lõi**: KHÔNG CÓ SỰ KHÁC NHAU LỚN
- Nội dung chính được giữ nguyên giữa 2 file (89.55% tương đồng)
- ASR đã nhận diện đúng các từ khóa và câu quan trọng
- Ý nghĩa tổng thể của đoạn hội thoại được bảo toàn

**Về mặt cấu trúc phân đoạn**: CÓ SỰ KHÁC NHAU ĐÁNG KỂ
- vocals.srt bị chia thành nhiều đoạn nhỏ hơn (462 vs 351 entries)
- Các câu bị cắt ngang giữa chừng do phân đoạn quá mức
- Thời gian đồng bộ giữa các entry không khớp

### 3. Phân tích chi tiết sự khác biệt

**Ví dụ cụ thể:**
1. Entry 1: '书姐刚才您和前厅长' → '书记， 刚才您和前厅' (73.68% tương đồng)
   - Nội dung: Giữ nguyên, chỉ khác từ "书姐" vs "书记"
   - Cấu trúc: vocals bị cắt ngắn hơn

2. Entry 2-3: '关于粤东省公安系统内部表彰大会' và '在朝江市召开的相关内容' 
   → bị chia thành nhiều phần nhỏ trong vocals.srt
   - Nội dung: Giữ nguyên thông tin chính
   - Cấu trúc: vocals.srt chia nhỏ quá mức

### 4. Kết luận

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
