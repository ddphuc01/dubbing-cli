# Script kiểm tra kết nối Cline và Rules
# Chạy script này để đảm bảo Cline có thể kết nối đến rules

param(
    [string]$LogPath = ".\logs\cline_check_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
)

# Tạo thư mục logs nếu chưa có
$logDir = Split-Path $LogPath -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Hàm ghi log
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogPath -Value $logMessage
}

Write-Log "=== Bat dau kiem tra ket noi Cline va Rules ==="

# Kiểm tra đường dẫn rules
$clineRulesPath = "$env:USERPROFILE\.clinerules\global.md"
$kilocodeRulesPath = "$env:USERPROFILE\.kilocode\rules\hello.md"

Write-Log "Kiem tra duong dan rules cua Cline: $clineRulesPath"
if (Test-Path $clineRulesPath) {
    Write-Log "✓ File rules cua Cline ton tai"
    $fileSize = (Get-Item $clineRulesPath).Length
    Write-Log "  Kich thuoc file: $fileSize bytes"
} else {
    Write-Log "✗ File rules cua Cline khong ton tai"
}

Write-Log "Kiem tra duong dan rules cua KiloCode: $kilocodeRulesPath"
if (Test-Path $kilocodeRulesPath) {
    Write-Log "✓ File rules cua KiloCode ton tai"
    $fileSize = (Get-Item $kilocodeRulesPath).Length
    Write-Log "  Kich thuoc file: $fileSize bytes"
} else {
    Write-Log "✗ File rules cua KiloCode khong ton tai"
}

# Kiểm tra cấu hình workspace
$workspaceSettingsPath = ".\.vscode\settings.json"
Write-Log "Kiem tra cau hinh workspace VSCode: $workspaceSettingsPath"
if (Test-Path $workspaceSettingsPath) {
    Write-Log "✓ File cau hinh workspace ton tai"
} else {
    Write-Log "✗ File cau hinh workspace khong ton tai"
}

# Kiểm tra cấu hình MCP
$clineMcpSettingsPath = "$env:APPDATA\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"
Write-Log "Kiem tra cau hinh MCP: $clineMcpSettingsPath"
if (Test-Path $clineMcpSettingsPath) {
    Write-Log "✓ File cau hinh MCP ton tai"
} else {
    Write-Log "✗ File cau hinh MCP khong ton tai"
}

Write-Log "=== Hoan thanh kiem tra ==="
Write-Log "Log duoc luu tai: $LogPath"
Write-Log ""
Write-Log "Khuyen nghi:"
Write-Log "1. Khoi dong lai VSCode de ap dung cac thay doi cau hinh"
Write-Log "2. Kiem tra Developer Console (Help > Toggle Developer Tools) de xem loi MCP"
Write-Log "3. Dam bao extension Cline duoc bat va cap nhat"
Write-Log "4. Neu van co van de, thu disable va enable lai extension Cline"