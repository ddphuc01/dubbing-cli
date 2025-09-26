# Hướng Dẫn Thiết Lập Cấu Hình Mặc Định Cho Tất Cả Dự Án

## Mục Tiêu
Hướng dẫn này giúp bạn thiết lập cấu hình mặc định để áp dụng tự động cho tất cả các dự án trong tương lai.

## 1. Cập Nhật File Quy Tắc Toàn Cục

Để áp dụng cấu hình mặc định cho tất cả các dự án, bạn cần cập nhật file:
`C:\Users\ddphu\.kilocode\rules\hello.md`

### Thêm các quy tắc mới vào file hello.md:

```markdown
## Project Initialization
- Khi bắt đầu dự án mới, tự động tạo các file cấu hình mặc định
- Sử dụng script setup_project_defaults.py để khởi tạo nhanh
- Áp dụng hệ thống tự động chuyển đổi chế độ (mode switching)

## Default Project Structure
- Tạo PROJECT_RULES.md với quy tắc phù hợp cho từng loại dự án
- Tạo PROJECT_TODO.md để theo dõi tiến độ
- Tạo global.md cho thông tin tổng quan dự án
- Thiết lập .kilocode/mcp.json với các server cần thiết

## Mode Switching System
- Hệ thống tự động nhận diện loại công việc (lập kế hoạch, code, test, debug)
- Chuyển đổi chế độ làm việc phù hợp tự động
- Sử dụng MODE_CONFIG.json để cấu hình quy tắc chuyển đổi
```

## 2. Cách Cập Nhật File Hello.md

### Bước 1: Sao lưu file gốc
```powershell
Copy-Item "C:\Users\ddphu\.kilocode\rules\hello.md" "C:\Users\ddphu\.kilocode\rules\hello.md.bak"
```

### Bước 2: Thêm nội dung mới vào cuối file hello.md
Bạn có thể thêm các phần trên vào cuối file hello.md hiện tại.

## 3. Sử Dụng Script Thiết Lập Tự Động

Script `scripts/setup_project_defaults.py` sẽ tự động:
- Tạo MODE_CONFIG.json với cấu hình chuyển đổi chế độ
- Cập nhật .kilocode/mcp.json với các MCP server cần thiết
- Tạo PROJECT_RULES.md với quy tắc mặc định
- Tạo PROJECT_TODO.md với danh sách công việc
- Tạo global.md với thông tin tổng quan

## 4. Áp Dụng Cho Dự Án Mới

Khi bắt đầu dự án mới, chỉ cần chạy:
```bash
python scripts/setup_project_defaults.py
```

## 5. Template Cấu Hình

Bạn cũng có thể sử dụng `PROJECT_DEFAULT_TEMPLATE.md` như một hướng dẫn để thiết lập thủ công cho các trường hợp đặc biệt.

## Lợi Ích

- Tiết kiệm thời gian thiết lập dự án mới
- Đảm bảo tính nhất quán giữa các dự án
- Tự động áp dụng best practices
- Tối ưu hóa workflow với chế độ chuyển đổi thông minh