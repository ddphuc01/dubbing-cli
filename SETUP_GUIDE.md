# Hướng Dẫn Thiết Lập và Đẩy Dự Án Lên GitHub

## 1. Cấu trúc dự án

Dự án Video-CLI là một công cụ dòng lệnh để xử lý video, bao gồm:
- Tải video từ nhiều nền tảng
- Tách âm thanh khỏi video
- Tạo phụ đề bằng nhiều phương pháp (WhisperX, FunASR, NeMo)
- Dịch phụ đề
- Chuyển đổi phụ đề SRT sang âm thanh đồng bộ

## 2. Các tệp quan trọng

- `.gitignore`: Đã được thiết lập để bỏ qua các tệp không cần thiết khi commit
- `README.md`: Tài liệu hướng dẫn sử dụng đầy đủ
- `requirements.txt`: Danh sách các thư viện Python cần thiết
- `.env.example`: Mẫu file cấu hình biến môi trường

## 3. Các bước chuẩn bị trước khi push lên GitHub

### Bước 1: Xóa dữ liệu không cần thiết khỏi thư mục
Trước khi commit, bạn nên xóa các thư mục dữ liệu không cần thiết:

```bash
# Xóa các thư mục tải xuống và đầu ra thử nghiệm
rm -rf downloads/
rm -rf test_output/
rm -rf models/ # Nếu thư mục này quá lớn và không cần thiết để commit
```

### Bước 2: Kiểm tra file .env
Đảm bảo bạn không commit file `.env` thực tế chứa thông tin nhạy cảm. File `.env` đã được liệt kê trong `.gitignore`, nhưng hãy kiểm tra lại:

```bash
# Kiểm tra nếu file .env đang nằm trong staging area
git check-ignore .env
```

## 4. Các bước push dự án lên GitHub

### Bước 1: Khởi tạo repository
```bash
cd Video-CLI
git init
```

### Bước 2: Thêm remote repository
```bash
# Thay thế YOUR_USERNAME và YOUR_REPOSITORY bằng tên người dùng và tên repository của bạn
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

### Bước 3: Thêm tất cả các tệp vào staging area
```bash
git add .
```

### Bước 4: Commit các thay đổi
```bash
git commit -m "Initial commit: Add Video-CLI project"
```

### Bước 5: Push lên GitHub
```bash
git branch -M main
git push -u origin main
```

## 5. Lưu ý quan trọng

### Về thư mục `downloads/` và `test_output/`
- Những thư mục này đã được thêm vào `.gitignore` để không bị commit
- Nếu bạn đã vô tình thêm chúng vào staging area, hãy bỏ chúng ra bằng lệnh:
```bash
git rm -r --cached downloads/
git rm -r --cached test_output/
git commit -m "Remove downloads and test_output from tracking"
```

### Về thư mục `models/`
- Thư mục này có thể chứa các mô hình lớn không nên commit lên GitHub
- Nếu cần, bạn có thể giữ nguyên trong `.gitignore` hoặc tạo một hướng dẫn riêng để người dùng tải mô hình

### Về file `.env`
- File `.env` chứa thông tin nhạy cảm như API keys nên không được commit
- Chỉ commit file `.env.example` như một mẫu hướng dẫn

## 6. Cập nhật README.md (nếu cần)

Bạn có thể cập nhật README.md để thêm phần "Getting Started" hoặc "Installation" nếu chưa có:

```markdown
## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
   cd Video-CLI
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

4. Follow the instructions in the README.md for usage details.
```

## 7. Sau khi push lên GitHub

Sau khi đã push thành công lên GitHub, bạn nên:

1. Tạo một release đầu tiên nếu dự án đã hoàn thiện
2. Cập nhật mô tả repository trên GitHub
3. Thêm các topic liên quan để người khác dễ tìm thấy dự án của bạn
4. Viết thêm tài liệu nếu cần thiết
