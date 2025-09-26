#!/bin/bash

# Script để thiết lập Git và push dự án Video-CLI lên GitHub

echo "Chuẩn bị đẩy dự án Video-CLI lên GitHub..."
echo

# Kiểm tra xem có phải là thư mục dự án Video-CLI không
if [ ! -f "README.md" ] || [ ! -f "requirements.txt" ] || [ ! -f ".gitignore" ]; then
    echo "Lỗi: Không tìm thấy các tệp cần thiết của dự án. Hãy chắc chắn rằng bạn đang ở trong thư mục Video-CLI."
    exit 1
fi

echo "Các tệp cần thiết đã được xác nhận."
echo

# Xóa các thư mục không cần thiết khỏi git tracking
echo "Xóa các thư mục không cần thiết khỏi git tracking..."
git rm -r --cached downloads/ 2>/dev/null || echo "downloads/ không được theo dõi hoặc không tồn tại"
git rm -r --cached test_output/ 2>/dev/null || echo "test_output/ không được theo dõi hoặc không tồn tại"
git rm -r --cached models/ 2>/dev/null || echo "models/ không được theo dõi hoặc không tồn tại"
echo

# Kiểm tra xem đã có repository git chưa
if [ -d ".git" ]; then
    echo "Đã tìm thấy repository Git. Bỏ qua bước khởi tạo."
else
    echo "Khởi tạo repository Git..."
    git init
    if [ $? -ne 0 ]; then
        echo "Lỗi khi khởi tạo repository Git."
        exit 1
    fi
fi
echo

# Hiển thị hướng dẫn để người dùng tạo remote repository trên GitHub
echo "Trước khi tiếp tục, bạn cần tạo một repository trống trên GitHub.com."
echo "Sau đó, sao chép URL của repository đó."
echo
read -p "Vui lòng nhập URL của repository GitHub (ví dụ: https://github.com/username/repository.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "Không có URL được cung cấp. Dừng script."
    exit 1
fi

# Thiết lập remote repository
echo "Thiết lập remote repository..."
git remote remove origin 2>/dev/null
git remote add origin "$repo_url"
if [ $? -ne 0 ]; then
    echo "Lỗi khi thiết lập remote repository."
    exit 1
fi
echo

# Thêm tất cả các tệp vào staging area
echo "Thêm các tệp vào staging area..."
git add .
if [ $? -ne 0 ]; then
    echo "Lỗi khi thêm tệp vào staging area."
    exit 1
fi
echo

# Hiển thị những gì sẽ được commit
echo "Dự án đã sẵn sàng để commit. Dưới đây là danh sách các tệp sẽ được commit:"
echo "(Sử dụng 'git status' để xem chi tiết)"
git status --short
echo

# Yêu cầu người dùng xác nhận commit
read -p "Bạn có muốn tiếp tục commit và push lên GitHub không? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Hủy bỏ quá trình."
    exit 0
fi

# Thực hiện commit
echo "Thực hiện commit..."
git commit -m "Initial commit: Add Video-CLI project"

if [ $? -ne 0 ]; then
    echo "Lỗi khi thực hiện commit."
    exit 1
fi
echo

# Đổi tên nhánh chính sang main (nếu chưa)
git branch -M main

# Push lên GitHub
echo "Đang push lên GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "Dự án đã được đẩy thành công lên GitHub!"
    echo "Bạn có thể kiểm tra tại: $repo_url"
    echo
    echo "Lưu ý: Nếu gặp lỗi lần đầu tiên, có thể do repository không trống."
    echo "Trong trường hợp đó, bạn có thể cần phải pull trước khi push:"
    echo "git pull origin main --allow-unrelated-histories"
    echo "Sau đó chạy lại lệnh push: git push -u origin main"
else
    echo
    echo "Lỗi khi push lên GitHub. Vui lòng kiểm tra lại kết nối mạng và URL repository."
    exit 1
fi
