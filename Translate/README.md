# SRT Translator

Công cụ dịch file phụ đề SRT từ tiếng Trung sang tiếng Việt sử dụng Google Gemini AI hoặc mô hình dịch cục bộ.

## Cài đặt

1. Cài đặt Python dependencies:
```bash
pip install -r requirements.txt
```

2. Đảm bảo có `gemini` CLI tool được cài đặt và cấu hình (credentials ở `C:\Users\phucduong\.gemini\oauth_creds.json`) nếu sử dụng phương pháp dịch qua API

## Sử dụng

### Phương pháp 1: Sử dụng Google Gemini API (cũ)
```bash
python srt_translator.py input.srt
```

File output sẽ được tạo tự động với tên `input_vn.srt`

### Phương pháp 2: Sử dụng mô hình dịch cục bộ (mới - tận dụng GPU)
```bash
python local_translation.py input.srt
```

File output sẽ được tạo tự động với tên `input_vn.srt`

### Phương pháp 3: Sử dụng hệ thống hybrid (kết hợp nhiều phương pháp)
```bash
python hybrid_translator.py input.srt --openrouter-api-key YOUR_API_KEY
```

File output sẽ được tạo tự động với tên `input_vn.srt`

## Tùy chọn nâng cao

### Với phương pháp dịch qua API:
```bash
python srt_translator.py input.srt --batch-size 300 --clear-cache -o output.srt
```

### Với phương pháp dịch cục bộ:
```bash
python local_translation.py input.srt --batch-size 64 -o output.srt
```

### Với phương pháp hybrid:
```bash
python hybrid_translator.py input.srt --openrouter-api-key YOUR_API_KEY --movie-context "Bối cảnh phim" --batch-size 16 --no-gemini
```

Các tùy chọn:
- `--batch-size`: Kích thước batch cho mỗi lần dịch (mặc định: 16 cho phương pháp hybrid)
- `-o, --output`: Chỉ định file đầu ra (mặc định: input_vn.srt)
- `--no-gemini`: Tắt sử dụng Gemini trong phương pháp hybrid
- `--no-openrouter`: Tắt sử dụng OpenRouter trong phương pháp hybrid
- `--no-local`: Tắt sử dụng mô hình cục bộ trong phương pháp hybrid
- `--openrouter-api-key`: API key cho OpenRouter
- `--movie-context`: Cung cấp ngữ cảnh của bộ phim để dịch chính xác hơn

## Tính năng

- Dịch batch với kích thước có thể cấu hình
- Tận dụng bộ nhớ đệm để tránh dịch lại các đoạn giống nhau (chỉ với phương pháp API)
- Prompt cải tiến cho chất lượng dịch tốt hơn
- Hỗ trợ retry khi gặp lỗi (chỉ với phương pháp API)
- Giữ nguyên timestamp của subtitles
- CLI đơn giản, dễ sử dụng
- Hỗ trợ xử lý file lớn
- Hiển thị tiến độ dịch với thời gian ước tính hoàn thành
- Ghi log chi tiết vào file translation.log
- Tận dụng GPU cho quá trình dịch (với phương pháp cục bộ)

## Cải tiến

### Phương pháp dịch qua API:
- **Cơ chế cache**: Các đoạn đã dịch sẽ được lưu vào cache để tránh dịch lại nếu chạy lại
- **Xử lý lỗi cải tiến**: Có cơ chế tạm dừng giữa các lần retry để tránh quá tải API
- **Prompt cải tiến**: Hướng dẫn chi tiết hơn cho AI để có chất lượng dịch tốt hơn
- **Hiển thị tiến trình chi tiết**: Hiển thị tổng số phụ đề, số batch, và tiến độ hiện tại
- **Theo dõi tiến độ**: Hiển thị phần trăm hoàn thành và thời gian ước tính còn lại
- **Logging**: Ghi lại toàn bộ quá trình dịch vào file log để tiện theo dõi và debug

### Phương pháp dịch cục bộ:
- **Tận dụng GPU**: Sử dụng GPU (nếu có) để tăng tốc độ dịch
- **Không giới hạn API**: Không phụ thuộc vào giới hạn rate limit của API
- **Batch processing**: Xử lý nhiều đoạn cùng lúc để tăng hiệu suất
- **Mô hình dịch chuyên biệt**: Sử dụng mô hình Helsinki-NLP/opus-mt-zh-vi được huấn luyện riêng cho dịch từ tiếng Trung sang tiếng Việt
- **Hiển thị tiến độ thực thời**: Sử dụng thanh tiến trình tqdm để hiển thị tiến độ
- **Bảo tồn tên nhân vật**: Tự động nhận diện và giữ nguyên tên nhân vật trong quá trình dịch

## Cấu hình hệ thống

Hệ thống hiện tại:
- Hệ điều hành: Windows 11 Pro
- Bộ nhớ RAM: 32.58 GB
- CPU: Intel Core i5-14400F (6 cores, 12 threads)
- GPU: NVIDIA GeForce RTX 4060 (8GB VRAM)
- CUDA Version: 13.0

Với cấu hình này, phương pháp dịch cục bộ sẽ tận dụng cả CPU đa lõi và GPU để tăng tốc độ dịch. Mô hình dịch có thể xử lý hiệu quả trên cả CPU và GPU, giúp tối ưu hóa hiệu suất dịch thuật.

## Sử dụng kết hợp với OpenRouter.ai

Nếu bạn muốn sử dụng kết hợp với các key OpenRouter.ai, bạn có thể:
1. Thêm mô-đun hỗ trợ OpenRouter API vào file `srt_translator.py`
2. Tạo lớp kết nối với OpenRouter API tương tự như mô hình cục bộ
3. Kết hợp các phương pháp dịch để tối ưu hóa tốc độ và chi phí

Ví dụ về cách thêm hỗ trợ OpenRouter:
```python
import openrouter

class OpenRouterTranslator:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def translate_batch(self, texts):
        # Gửi yêu cầu dịch đến OpenRouter API
        # Trả về kết quả dịch
```

## Lưu ý

- Cần có kết nối internet để gọi Gemini API hoặc tải mô hình cục bộ (lần đầu tiên)
- File SRT đầu vào phải là UTF-8 encoded
- Với phương pháp dịch cục bộ, lần chạy đầu tiên sẽ mất thời gian tải mô hình
- Công cụ này sử dụng API của Gemini, có thể có rate limits (với phương pháp API)
- Với file rất lớn, nên chạy với tùy chọn --clear-cache để đảm bảo bộ nhớ đệm không chiếm nhiều dung lượng (với phương pháp API)
- File log sẽ được tạo tại cùng thư mục với script, tên là translation.log hoặc local_translation.log
- Mô hình dịch cục bộ có thể cần bộ nhớ đáng kể, điều chỉnh batch size nếu gặp vấn đề về bộ nhớ
