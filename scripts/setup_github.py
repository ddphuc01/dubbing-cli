#!/usr/bin/env python3
"""
Script tự động thiết lập và push dự án lên GitHub
"""
import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Chạy lệnh hệ thống và hiển thị kết quả"""
    print(f"🏃 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success: {result.stdout.strip() if result.stdout.strip() else 'Command completed successfully'}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def setup_github():
    """Thiết lập dự án với GitHub"""
    print("🚀 Bắt đầu thiết lập dự án với GitHub")
    print("=" * 50)
    
    # Kiểm tra git có sẵn không
    if not run_command("git --version", "Kiểm tra Git"):
        print("❌ Git chưa được cài đặt. Vui lòng cài đặt Git trước.")
        return False
    
    # Kiểm tra xem đã có repository chưa
    is_new_repo = not Path(".git").exists()
    
    if is_new_repo:
        print("\n📁 Khởi tạo Git repository mới...")
        if not run_command("git init", "Khởi tạo Git repository"):
            return False
        
        if not run_command("git add .", "Thêm tất cả file vào staging"):
            return False
        
        if not run_command('git commit -m "Initial commit: Project setup with MCP config, mode switching, and gitignore"', "Tạo commit đầu tiên"):
            return False
    else:
        print("\n📁 Đã có repository Git tồn tại")
    
    # Yêu cầu thông tin repository từ người dùng
    print("\n📝 Vui lòng nhập thông tin repository GitHub:")
    repo_url = input("GitHub repository URL (https://github.com/username/repo.git): ").strip()
    
    if not repo_url:
        print("❌ Repository URL không được để trống")
        return False
    
    # Kiểm tra và xử lý remote origin
    print(f"\n📡 Thiết lập remote repository: {repo_url}")
    
    # Kiểm tra xem remote origin đã tồn tại chưa
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        # Remote origin đã tồn tại, cập nhật URL
        print("   Remote origin đã tồn tại, đang cập nhật URL...")
        if not run_command(f'git remote set-url origin "{repo_url}"', "Cập nhật URL remote origin"):
            return False
    else:
        # Remote origin chưa tồn tại, thêm mới
        if not run_command(f'git remote add origin "{repo_url}"', "Thêm remote repository"):
            return False
    
    # Đặt nhánh chính là main
    print("\nSetBranch main là nhánh chính...")
    run_command("git branch -M main", "Đặt nhánh chính là main")
    
    # Push lên GitHub
    print("\n📤 Push lên GitHub...")
    if not run_command("git push -u origin main", "Push lên GitHub"):
        print("\n⚠️ Nếu gặp lỗi do repository không trống, vui lòng:")
        print("   1. Pull trước: git pull origin main --allow-unrelated-histories")
        print("   2. Rồi thử push lại: git push -u origin main")
        return False
    
    print("\n🎉 Thiết lập GitHub hoàn tất!")
    print(f"✅ Repository đã được tạo tại: {repo_url}")
    print("✅ Tất cả file đã được push lên GitHub")
    print("✅ Nhánh chính đã được thiết lập là 'main'")
    
    # Hướng dẫn tiếp theo
    print("\n📋 Hướng dẫn tiếp theo:")
    print("   - Kiểm tra repository trên GitHub để xác nhận")
    print("   - Thiết lập branch protection rules nếu cần")
    print("   - Cấu hình GitHub Actions trong tab Settings")
    print("   - Thêm collaborators nếu cần")
    
    return True

def main():
    """Hàm chính"""
    print("🔧 Script Thiết Lập GitHub cho Dự Án Dịch Thuật Video")
    print("   Hỗ trợ thiết lập Git và push lên GitHub")
    print()
    
    # Xác nhận với người dùng
    response = input("Bạn có muốn tiếp tục thiết lập GitHub không? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 'có', 'c']:
        print("❌ Hủy thiết lập GitHub")
        return
    
    success = setup_github()
    
    if success:
        print("\n✨ Thiết lập GitHub hoàn tất thành công!")
    else:
        print("\n💥 Có lỗi xảy ra trong quá trình thiết lập GitHub")
        print("💡 Vui lòng kiểm tra lại các bước và thử lại")

if __name__ == "__main__":
    main()