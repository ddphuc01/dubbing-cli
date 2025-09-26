# Hướng Dẫn Khắc Phục Vấn Đề Cline và Rules

## Vấn đề: Cline không kết nối được đến rules

### Nguyên nhân có thể có:
1. **Extension Cline chưa được bật hoặc phiên bản cũ**
2. **File rules không tồn tại hoặc nội dung không đúng**
3. **Cấu hình MCP server chưa được thiết lập**
4. **VSCode workspace settings chưa được cấu hình**
5. **Xung đột với extension khác**

### Giải pháp từng bước:

#### Bước 1: Kiểm tra trạng thái hệ thống
Chạy script kiểm tra để xác định vấn đề:

```powershell
# Trong thư mục dự án
.\scripts\check_cline_connection.ps1
```

Script sẽ kiểm tra:
- Tồn tại của file rules
- Cấu hình VSCode workspace
- Cấu hình MCP settings
- Phiên bản Node.js và npm
- Trạng thái VSCode

#### Bước 2: Khởi động lại VSCode
Sau khi chạy script và thực hiện các thay đổi:
1. Đóng VSCode hoàn toàn
2. Mở lại VSCode
3. Mở workspace của dự án

#### Bước 3: Kiểm tra Developer Console
1. Trong VSCode: Help > Toggle Developer Tools
2. Kiểm tra tab Console để xem lỗi liên quan đến MCP hoặc Cline
3. Tìm các thông báo lỗi như:
   - "MCP server connection failed"
   - "Rules file not found"
   - "Extension host error"

#### Bước 4: Kiểm tra extension Cline
1. Mở Extensions (Ctrl+Shift+X)
2. Tìm "Cline" hoặc "saoudrizwan.claude-dev"
3. Đảm bảo extension được bật và cập nhật
4. Nếu cần, disable và enable lại extension

#### Bước 5: Kiểm tra cấu hình MCP
Trong VSCode settings (Ctrl+,):
- Tìm "cline" để xem các setting liên quan
- Đảm bảo global rules được bật
- Kiểm tra đường dẫn đến file rules

#### Bước 6: Thử nghiệm kết nối
1. Mở một file trong workspace
2. Gọi Cline chat (Ctrl+L)
3. Thử hỏi một câu đơn giản để kiểm tra rules có hoạt động không

### Cấu trúc file quan trọng:

```
%USERPROFILE%/
├── .clinerules/
│   └── global.md          # Rules cho Cline
└── .kilocode/
    └── rules/
        └── hello.md       # Rules cho KiloCode

workspace/
├── .vscode/
│   └── settings.json      # Cấu hình workspace
└── scripts/
    └── check_cline_connection.ps1  # Script kiểm tra
```

### Lệnh hữu ích:

```powershell
# Kiểm tra phiên bản extension
code --list-extensions --show-versions | findstr claude

# Xem log VSCode
code --log-trace

# Reset settings Cline (cẩn thận!)
# Xóa file: %APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### Nếu vẫn không hoạt động:

1. **Cập nhật extension Cline** lên phiên bản mới nhất
2. **Kiểm tra xung đột extension**: Tắt các extension AI khác
3. **Reset cấu hình**: Xóa file settings và cấu hình lại
4. **Kiểm tra quyền truy cập**: Đảm bảo VSCode có quyền đọc file rules
5. **Thử trên workspace mới**: Tạo workspace mới để kiểm tra

### Log và Debug:

- Log của script kiểm tra được lưu trong `logs/`
- Log VSCode: `%APPDATA%\Code\logs\`
- MCP debug: Kiểm tra Developer Console trong VSCode

### Liên hệ hỗ trợ:

Nếu các bước trên không giải quyết được vấn đề:
1. Thu thập log từ script kiểm tra
2. Sao chép lỗi từ Developer Console
3. Mô tả chi tiết các bước đã thực hiện
4. Đưa ra thông tin phiên bản VSCode và extension