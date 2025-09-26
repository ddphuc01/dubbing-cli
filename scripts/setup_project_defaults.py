#!/usr/bin/env python3
"""
Script tự động thiết lập cấu hình mặc định cho dự án mới
"""
import json
import os
from pathlib import Path

def setup_project_defaults():
    """Thiết lập cấu hình mặc định cho dự án mới"""
    
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs("scripts", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    
    # 1. Tạo MODE_CONFIG.json nếu chưa tồn tại
    mode_config_path = Path("MODE_CONFIG.json")
    if not mode_config_path.exists():
        mode_config = {
            "modeAutoSwitch": {
                "enabled": True,
                "rules": [
                    {
                        "keywords": ["plan", "design", "architecture", "structure", "overview", "strategy", "planning", "designing"],
                        "mode": "architect",
                        "description": "Chuyển sang chế độ kiến trúc khi làm việc liên quan đến lập kế hoạch, thiết kế hệ thống"
                    },
                    {
                        "keywords": ["code", "implement", "function", "class", "module", "script", "development", "create", "write code", "programming"],
                        "mode": "code",
                        "description": "Chuyển sang chế độ code khi làm việc liên quan đến viết code, implement chức năng"
                    },
                    {
                        "keywords": ["test", "testing", "unit test", "integration test", "pytest", "unittest", "verify", "validation"],
                        "mode": "test-engineer",
                        "description": "Chuyển sang chế độ test khi làm việc liên quan đến viết test, kiểm thử"
                    },
                    {
                        "keywords": ["debug", "fix", "bug", "error", "issue", "troubleshoot", "problem", "error handling"],
                        "mode": "debug",
                        "description": "Chuyển sang chế độ debug khi làm việc liên quan đến sửa lỗi, gỡ rối"
                    },
                    {
                        "keywords": ["review", "analyze", "analysis", "check", "examine", "inspect", "code review"],
                        "mode": "code-reviewer",
                        "description": "Chuyển sang chế độ review khi cần phân tích, kiểm tra code"
                    },
                    {
                        "keywords": ["document", "documentation", "readme", "guide", "manual", "write documentation"],
                        "mode": "docs-specialist",
                        "description": "Chuyển sang chế độ tài liệu khi làm việc liên quan đến viết tài liệu"
                    }
                ]
            },
            "defaultMode": "code",
            "contextAwareSwitching": True
        }
        
        with open(mode_config_path, 'w', encoding='utf-8') as f:
            json.dump(mode_config, f, indent=2, ensure_ascii=False)
        print("✓ Tạo MODE_CONFIG.json thành công")
    else:
        print("- Bỏ qua MODE_CONFIG.json (đã tồn tại)")
    
    # 2. Cập nhật .kilocode/mcp.json nếu chưa có cấu hình mở rộng
    mcp_config_path = Path(".kilocode/mcp.json")
    if mcp_config_path.exists():
        with open(mcp_config_path, 'r', encoding='utf-8') as f:
            mcp_config = json.load(f)
        
        # Thêm các server nếu chưa có
        servers_to_add = ["python-docs", "openai-api", "whisper-api", "ffmpeg-python"]
        updated = False
        
        for server in servers_to_add:
            if server not in mcp_config.get("mcpServers", {}):
                mcp_config["mcpServers"][server] = {
                    "command": "npx",
                    "args": ["-y", "@upstash/context7-mcp"],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": ["resolve-library-id", "get-library-docs"]
                }
                updated = True
        
        if updated:
            with open(mcp_config_path, 'w', encoding='utf-8') as f:
                json.dump(mcp_config, f, indent=2, ensure_ascii=False)
            print("✓ Cập nhật .kilocode/mcp.json thành công")
        else:
            print("- Bỏ qua .kilocode/mcp.json (đã có cấu hình đầy đủ)")
    else:
        # Tạo file mcp.json mới nếu chưa tồn tại
        os.makedirs(".kilocode", exist_ok=True)
        default_mcp_config = {
            "mcpServers": {
                "context7": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@upstash/context7-mcp"
                    ],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": [
                        "resolve-library-id",
                        "get-library-docs"
                    ]
                },
                "python-docs": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@upstash/context7-mcp"
                    ],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": [
                        "resolve-library-id",
                        "get-library-docs"
                    ]
                },
                "openai-api": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@upstash/context7-mcp"
                    ],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": [
                        "resolve-library-id",
                        "get-library-docs"
                    ]
                },
                "whisper-api": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@upstash/context7-mcp"
                    ],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": [
                        "resolve-library-id",
                        "get-library-docs"
                    ]
                },
                "ffmpeg-python": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@upstash/context7-mcp"
                    ],
                    "env": {
                        "DEFAULT_MINIMUM_TOKENS": "ctx7sk-c68c404e-0056-4a6d-9cc9-689d905cacdb"
                    },
                    "alwaysAllow": [
                        "resolve-library-id",
                        "get-library-docs"
                    ]
                }
            }
        }
        
        with open(mcp_config_path, 'w', encoding='utf-8') as f:
            json.dump(default_mcp_config, f, indent=2, ensure_ascii=False)
        print("✓ Tạo .kilocode/mcp.json thành công")
    
    # 3. Tạo PROJECT_RULES.md nếu chưa tồn tại
    project_rules_path = Path("PROJECT_RULES.md")
    if not project_rules_path.exists():
        project_rules_content = """# Project Rules for New Project

## Project Management
- Khi thực hiện một công việc gì đó hãy đặt plan và chia nhỏ công việc ra
- Tạo checklist cho kế hoạch công việc và cập nhật vào khi hoàn thành theo từng bước
- Luôn kiểm tra công cụ có sẵn trước khi thực hiện lệnh (git, docker, npm, node, python, v.v.)
- Sử dụng hệ thống tự động chuyển đổi chế độ (mode switching) để tối ưu workflow

## File Operations
- Luôn tạo backup trước khi thay đổi file quan trọng
- Ghi log các hành động quan trọng vào thư mục logs/
- Tuân thủ tiêu chuẩn UTF-8, CRLF cho các file text
- Kiểm tra quyền truy cập trước khi thực hiện thao tác ghi/xóa

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
- Backup trạng thái xử lý để có thể resume khi lỗi"""
        
        with open(project_rules_path, 'w', encoding='utf-8') as f:
            f.write(project_rules_content)
        print("✓ Tạo PROJECT_RULES.md thành công")
    else:
        print("- Bỏ qua PROJECT_RULES.md (đã tồn tại)")
    
    # 4. Tạo PROJECT_TODO.md nếu chưa tồn tại
    project_todo_path = Path("PROJECT_TODO.md")
    if not project_todo_path.exists():
        project_todo_content = """# Project Todo List

## Current Status
- [x] Thiết lập cấu hình mặc định cho dự án
- [x] Cấu hình MCP server cơ bản
- [x] Thiết lập hệ thống tự động chuyển đổi chế độ

## Project Planning
- [ ] Xác định yêu cầu và mục tiêu dự án
- [ ] Thiết kế kiến trúc hệ thống
- [ ] Lên kế hoạch phát triển

## Implementation
- [ ] Phát triển các module chính
- [ ] Viết unit test
- [ ] Kiểm thử tích hợp

## Documentation & Deployment
- [ ] Viết tài liệu hướng dẫn sử dụng
- [ ] Tạo script triển khai
- [ ] Tài liệu API (nếu có)"""
        
        with open(project_todo_path, 'w', encoding='utf-8') as f:
            f.write(project_todo_content)
        print("✓ Tạo PROJECT_TODO.md thành công")
    else:
        print("- Bỏ qua PROJECT_TODO.md (đã tồn tại)")
    
    # 5. Tạo global.md nếu chưa tồn tại
    global_path = Path("global.md")
    if not global_path.exists():
        global_content = """# Global Project Information

## Project Overview
This is a new project with default configurations for optimal workflow.

## Project Structure
- `core/` - Core processing modules
- `pipelines/` - Processing pipelines and workflows
- `docs/` - Documentation files
- `examples/` - Example scripts and usage
- `scripts/` - Utility scripts
- `config/` - Configuration files

## Project Rules
See [PROJECT_RULES.md](PROJECT_RULES.md) for detailed project-specific rules and standards.

## Current Tasks
See [PROJECT_TODO.md](PROJECT_TODO.md) for current project tasks and progress tracking.

## MCP Configuration
The project uses MCP servers for documentation and tools. See [.kilocode/mcp.json](.kilocode/mcp.json) for configuration.

## Development Guidelines
- Follow the project rules in PROJECT_RULES.md
- Use checklist approach for complex tasks
- Check available tools before implementing new functionality
- Create backups before modifying important files
- Log important actions to logs/ directory
- Use automatic mode switching to optimize workflow"""
        
        with open(global_path, 'w', encoding='utf-8') as f:
            f.write(global_content)
        print("✓ Tạo global.md thành công")
    else:
        print("- Bỏ qua global.md (đã tồn tại)")
    
    print("\\n🎉 Thiết lập cấu hình mặc định cho dự án hoàn tất!")
    print("Các thành phần đã được tạo/cập nhật:")
    print("- MODE_CONFIG.json: Cấu hình tự động chuyển đổi chế độ")
    print("- .kilocode/mcp.json: Cấu hình MCP server")
    print("- PROJECT_RULES.md: Quy tắc dự án")
    print("- PROJECT_TODO.md: Danh sách công việc")
    print("- global.md: Thông tin tổng quan dự án")

if __name__ == "__main__":
    setup_project_defaults()