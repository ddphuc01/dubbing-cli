# Hướng Dẫn Thiết Lập Và Cập Nhật Lên GitHub

## 1. Thiết Lập Repository Mới Trên GitHub

### Tạo Repository Trên GitHub
1. Đăng nhập vào tài khoản GitHub
2. Nhấn "New repository"
3. Đặt tên repository (ví dụ: `video-translation-system`)
4. Chọn "Public" hoặc "Private" tùy theo nhu cầu
5. Bỏ chọn "Initialize this repository with a README" (vì chúng ta đã có README)
6. Chọn `.gitignore: Python` hoặc tạo thủ công với file `.gitignore` đã tạo
7. Chọn license nếu cần
8. Nhấn "Create repository"

## 2. Cấu Hình Git Cục Bộ

### Thiết Lập Git Config
```bash
# Thiết lập tên người dùng và email
git config --global user.name "Tên Của Bạn"
git config --global user.email "email@domain.com"

# Thiết lập mặc định cho việc tạo nhánh
git config --global init.defaultBranch main
```

## 3. Kết Nối Dự Án Với Repository GitHub

### Nếu Đây Là Dự Án Mới
```bash
# Di chuyển đến thư mục dự án
cd /path/to/your/project

# Khởi tạo repository git
git init

# Thêm remote repository
git remote add origin https://github.com/username/repository-name.git

# Thêm tất cả các file vào staging
git add .

# Commit lần đầu tiên
git commit -m "Initial commit: Project setup with MCP config, mode switching, and gitignore"

# Push lên GitHub
git branch -M main
git push -u origin main
```

### Nếu Dự Án Đã Có Repository Cục Bộ
```bash
# Thêm remote repository mới
git remote add origin https://github.com/username/repository-name.git

# Đặt nhánh chính là main
git branch -M main

# Push lên GitHub
git push -u origin main
```

## 4. Cấu Hình Chi Tiết Cho Dự Án Dịch Thuật Video

### Cập Nhật README.md
Tạo hoặc cập nhật file `README.md` với thông tin dự án:

```markdown
# Video Translation System

## Overview
A comprehensive video translation system that provides automated translation of video content with high quality output. The system handles audio extraction, speech recognition, translation, and subtitle synchronization.

## Features
- Audio extraction from video files
- Speech-to-text conversion
- High-quality translation between multiple languages
- Subtitle synchronization
- Support for multiple video formats
- Automatic mode switching for optimal workflow

## Prerequisites
- Python 3.8+
- FFmpeg
- Git

## Installation
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Configure MCP servers in `.kilocode/mcp.json`
4. Run setup script: `python scripts/setup_project_defaults.py`

## Usage
- Use automatic mode switching for different tasks
- Process video files through the pipeline
- Configure translation settings in config files

## Project Structure
- `core/` - Core processing modules
- `pipelines/` - Processing workflows
- `Translate/` - Translation-specific modules
- `scripts/` - Utility scripts
- `docs/` - Documentation
```

## 5. Quản Lý Nhánh Và Commit

### Quy Tắc Đặt Tên Nhánh
- `feat/` - Tính năng mới: `feat/video-processing`
- `fix/` - Sửa lỗi: `fix/audio-extraction-bug`
- `docs/` - Tài liệu: `docs/readme-update`
- `refactor/` - Tái cấu trúc: `refactor/translation-module`
- `test/` - Kiểm thử: `test/unit-tests`

### Quy Tắc Commit
Sử dụng conventional commits:
- `feat:` - Tính năng mới
- `fix:` - Sửa lỗi
- `docs:` - Tài liệu
- `style:` - Định dạng code
- `refactor:` - Tái cấu trúc
- `test:` - Kiểm thử
- `chore:` - Công việc khác

Ví dụ:
```
feat: Add automatic mode switching functionality

- Implement mode detection based on user input
- Add configuration file for mode rules
- Create mode switching script
- Update project rules to include mode usage
```

## 6. Cấu Hình GitHub Actions (Tùy chọn)

Tạo file `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r config/requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
```

## 7. Bảo Mật Và Quyền Riêng Tư

### Không Upload File Nhạy Cảm
File `.gitignore` đã được cấu hình để tránh các file:
- File môi trường (`.env`)
- File cache và tạm thời
- File mô hình và dữ liệu lớn
- File log
- File cấu hình có chứa API keys

### Quản Lý API Keys
- Sử dụng biến môi trường
- Không hardcode trong code
- Sử dụng file cấu hình riêng biệt không commit

## 8. Đồng Bộ Hóa Và Cập Nhật

### Pull Thay Đổi Mới
```bash
git pull origin main
```

### Push Thay Đổi
```bash
# Thêm các file thay đổi
git add .

# Commit với tin nhắn mô tả
git commit -m "feat: Add new translation feature"

# Push lên GitHub
git push origin main
```

## 9. Quản Lý Release

### Tạo Release Trên GitHub
1. Vào tab "Releases" trong repository
2. Nhấn "Draft a new release"
3. Đặt tag (ví dụ: `v1.0.0`)
4. Đặt tiêu đề và mô tả
5. Upload bất kỳ file thực thi nếu cần
6. Nhấn "Publish release"

## 10. Xác Minh Cấu Hình

Sau khi thiết lập, kiểm tra lại:
- [ ] Repository GitHub đã được tạo
- [ ] File `.gitignore` đã được thêm vào
- [ ] Cấu hình MCP hoạt động
- [ ] Script thiết lập dự án mặc định hoạt động
- [ ] Không có file nhạy cảm trong repository
- [ ] Commit đầu tiên đã được push thành công

## Lợi Ích Của Việc Sử Dụng GitHub

- Quản lý phiên bản code
- Cộng tác dễ dàng
- Tích hợp CI/CD
- Theo dõi issues và pull requests
- Tự động backup code
- Tăng tính chuyên nghiệp của dự án