# Hướng Dẫn Thiết Lập Dự Án Video-CLI Trên GitHub

## Tổng Quan

Dự án đã được chuẩn bị đầy đủ để đẩy lên GitHub với các thành phần sau:

1. **File .gitignore**: Đã được thiết lập để bỏ qua các tệp không cần thiết khi commit
2. **File README.md**: Đã được cập nhật với hướng dẫn đầy đủ về dự án và cách thiết lập Git
3. **File SETUP_GUIDE.md**: Hướng dẫn chi tiết về quá trình thiết lập và push lên GitHub
4. **Script setup_git.sh**: Script tự động hóa quá trình thiết lập Git và push lên GitHub (Linux/Mac)
5. **Script setup_git.bat**: Script tự động hóa quá trình thiết lập Git và push lên GitHub (Windows)

## Các Bước Thực Hiện

### Trên Linux/Mac:

1. Di chuyển vào thư mục dự án:
   ```bash
   cd Video-CLI
   ```

2. Cấp quyền thực thi cho script:
   ```bash
   chmod +x setup_git.sh
   ```

3. Chạy script:
   ```bash
   ./setup_git.sh
   ```

### Trên Windows:

1. Di chuyển vào thư mục dự án:
   ```cmd
   cd Video-CLI
   ```

2. Chạy script:
   ```cmd
   setup_git.bat
   ```

## Những Lưu Ý Quan Trọng

- **Các thư mục sau đã được thêm vào .gitignore và sẽ không bị commit:**
  - `downloads/` - chứa các video đã tải
  - `test_output/` - chứa các kết quả thử nghiệm
 - `models/` - chứa các mô hình AI lớn
  - `.env` - chứa thông tin nhạy cảm

- **Trước khi chạy script, bạn cần tạo một repository trống trên GitHub.com** và sao chép URL của repository đó để cung cấp cho script.

- **File .env.example được giữ lại** như một mẫu hướng dẫn cho người dùng khác về cách cấu hình biến môi trường.

## Các Tệp Được Giữ Lại

- `README.md` - tài liệu hướng dẫn sử dụng đầy đủ
- `requirements.txt` - danh sách các thư viện Python cần thiết
- `.env.example` - mẫu file cấu hình biến môi trường
- Tất cả các file Python và tài liệu khác

Dự án đã sẵn sàng để được đẩy lên GitHub và có thể được sử dụng bởi người khác một cách dễ dàng.
