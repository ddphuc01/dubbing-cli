# Project Rules for Video Translation System

## Project Overview
- Mục tiêu: Hệ thống dịch thuật video tự động với chất lượng cao
- Công nghệ chính: Python, AI/ML, audio/video processing
- Ngôn ngữ: Hỗ trợ đa ngôn ngữ, ưu tiên Việt Nam ↔ English

## AI/ML & Translation Standards
- Luôn kiểm tra chất lượng dịch thuật trước khi triển khai
- Sử dụng mô hình dịch thuật phù hợp với từng ngôn ngữ mục tiêu
- Áp dụng kiểm thử A/B cho các mô hình dịch thuật mới
- Tối ưu hóa thời gian xử lý và chất lượng đầu ra
- Lưu trữ kết quả kiểm thử để phân tích hiệu suất

## Audio/Video Processing
- Kiểm tra định dạng file đầu vào và chuyển đổi nếu cần
- Xử lý file lớn theo batch để tránh tràn bộ nhớ
- Tối ưu hóa tốc độ xử lý âm thanh/video
- Đảm bảo đồng bộ giữa phụ đề và âm thanh
- Hỗ trợ nhiều định dạng video/phụ đề phổ biến (MP4, MKV, SRT, VTT)

## File Operations & Data Management
- Luôn tạo backup trước khi xử lý file gốc
- Sử dụng thư mục cache để lưu trữ tạm thời kết quả xử lý
- Quản lý bộ nhớ hiệu quả khi làm việc với file lớn
- Tuân thủ tiêu chuẩn UTF-8 cho các file văn bản
- Xóa file tạm sau khi hoàn thành xử lý

## API & External Services
- Quản lý API keys an toàn, không hardcode trong code
- Xử lý lỗi kết nối và rate limiting từ dịch vụ bên ngoài
- Implement retry logic cho các yêu cầu API quan trọng
- Cache kết quả API khi có thể để tăng hiệu suất
- Theo dõi và log lỗi API cho việc debug

## Testing & Quality Assurance
- Viết unit test cho các hàm xử lý chính
- Kiểm thử tích hợp cho toàn bộ pipeline
- Test với các loại video có chất lượng âm thanh khác nhau
- Đảm bảo phụ đề dịch có độ chính xác cao và ngữ pháp tự nhiên
- Kiểm thử hiệu năng với file lớn (1GB+)

## Performance & Optimization
- Đo lường thời gian xử lý từng bước trong pipeline
- Tối ưu hóa bộ nhớ khi xử lý video dài
- Sử dụng đa luồng phù hợp cho các tác vụ không liên quan
- Cache kết quả xử lý khi có thể để tránh tính toán lại
- Theo dõi sử dụng CPU/GPU trong quá trình xử lý

## Code Quality & Documentation
- Viết code rõ ràng, dễ đọc và dễ bảo trì
- Document các hàm xử lý chính với ví dụ sử dụng
- Tuân thủ PEP 8 cho định dạng code Python
- Comment các thuật toán phức tạp để dễ hiểu
- Cập nhật tài liệu khi thay đổi chức năng quan trọng
- Sử dụng chế độ phù hợp (architect, code, test, debug) tùy theo nhiệm vụ

## Error Handling & Logging
- Log đầy đủ thông tin cho việc debug
- Xử lý các trường hợp ngoại lệ khi xử lý file
- Thông báo lỗi rõ ràng cho người dùng
- Ghi log thời gian thực cho quá trình xử lý dài
- Backup trạng thái xử lý để có thể resume khi lỗi

## Security & Privacy
- Không lưu trữ dữ liệu người dùng nhạy cảm
- Xử lý file đầu vào an toàn, tránh các lỗ hổng bảo mật
- Kiểm tra định dạng file để tránh injection
- Mã hóa dữ liệu tạm thời nếu cần thiết
- Tuân thủ các quy định về bảo vệ dữ liệu cá nhân

## Deployment & Environment
- Sử dụng virtual environment cho Python
- Quản lý dependencies qua requirements.txt
- Hỗ trợ cả Windows và Linux (nếu cần)
- Cấu hình dễ dàng qua file config
- Kiểm tra tương thích phiên bản thư viện

## Project Management
- Chia nhỏ công việc thành các milestone rõ ràng
- Theo dõi tiến độ qua checklist
- Kiểm tra các công cụ có sẵn trước khi phát triển mới
- Đảm bảo tính nhất quán trong toàn hệ thống
- Tối ưu hóa quy trình làm việc để tăng hiệu quả