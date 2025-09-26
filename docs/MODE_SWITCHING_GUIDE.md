# Hướng Dẫn Sử Dụng Tự Động Chuyển Đổi Chế Độ

## Tổng Quan
Hệ thống này cho phép tự động chuyển đổi giữa các chế độ làm việc khác nhau (architect, code, test, debug, v.v.) dựa trên nội dung yêu cầu của người dùng.

## Cấu Hình
Hệ thống sử dụng file `MODE_CONFIG.json` để xác định các quy tắc chuyển đổi chế độ:

- `enabled`: Bật/tắt tính năng tự động chuyển đổi
- `rules`: Danh sách các quy tắc với từ khóa và chế độ tương ứng
- `defaultMode`: Chế độ mặc định khi không tìm thấy từ khóa phù hợp

## Các Chế Độ Hỗ Trợ
1. **architect**: Dành cho thiết kế hệ thống, lập kế hoạch, chiến lược
2. **code**: Dành cho viết code, implement chức năng
3. **test-engineer**: Dành cho viết test, kiểm thử
4. **debug**: Dành cho gỡ lỗi, xử lý vấn đề
5. **code-reviewer**: Dành cho review và phân tích code
6. **docs-specialist**: Dành cho viết tài liệu

## Cách Hoạt Động
Script `scripts/mode_switcher.py` sẽ:
1. Phân tích nội dung yêu cầu của người dùng
2. So sánh với các từ khóa trong cấu hình
3. Trả về chế độ phù hợp nhất dựa trên số lượng từ khóa khớp

## Sử Dụng
Bạn có thể chạy script để kiểm tra:
```bash
python scripts/mode_switcher.py "Hãy giúp tôi lập kế hoạch hệ thống dịch thuật"
```

## Tích Hợp
Hệ thống có thể tích hợp với các công cụ khác để tự động chuyển đổi chế độ khi làm việc với dự án.