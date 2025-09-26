@echo off
REM Script để thiết lập Git và push dự án Video-CLI lên GitHub trên Windows

echo Chu?n b? d?y d? án Video-CLI lên GitHub...
echo.

REM Ki?m tra xem có ph?i là th? m?c d? án Video-CLI không
if not exist "README.md" (
    echo L?i: Không tìm th?y t?p README.md. Hãy ch?c ch?n r?ng b?n d?ng ? trong th? m?c Video-CLI.
    exit /b 1
)
if not exist "requirements.txt" (
    echo L?i: Không tìm th?y t?p requirements.txt. Hãy ch?c ch?n r?ng b?n d?ng ? trong th? m?c Video-CLI.
    exit /b 1
)
if not exist ".gitignore" (
    echo L?i: Không tìm th?y t?p .gitignore. Hãy ch?c ch?n r?ng b?n d?ng ? trong th? m?c Video-CLI.
    exit /b 1
)

echo Các t?p c?n thi?t dã d?c xác nh?n.
echo.

REM Xóa các th? m?c không c?n thi?t kh?i git tracking
echo Xóa các th? m?c không c?n thi?t kh?i git tracking...
git rm -r --cached downloads/ 2>nul
if %errorlevel% neq 0 echo downloads/ không d?c theo dõi ho?c không t?n t?i
git rm -r --cached test_output/ 2>nul
if %errorlevel% neq 0 echo test_output/ không d?c theo dõi ho?c không t?n t?i
git rm -r --cached models/ 2>nul
if %errorlevel% neq 0 echo models/ không d?c theo dõi ho?c không t?n t?i
echo.

REM Ki?m tra xem dã có repository git ch?a
if exist ".git" (
    echo Dã tìm th?y repository Git. B? qua b??c kh?i t?o.
) else (
    echo Kh?i t?o repository Git...
    git init
    if %errorlevel% neq 0 (
        echo L?i khi kh?i t?o repository Git.
        exit /b 1
    )
)
echo.

REM Hi?n th? h??ng d?n d? ng??i dùng t?o remote repository trên GitHub
echo Tr??c khi ti?p t?c, b?n c?n t?o m?t repository tr?ng trên GitHub.com.
echo Sau dó, sao chép URL c?a repository dó.
echo.
set /p repo_url="Vui lòng nh?p URL c?a repository GitHub (ví d?: https://github.com/username/repository.git): "

if "%repo_url%"=="" (
    echo Không có URL d?c cung c?p. D?ng script.
    exit /b 1
)

REM Thi?t l?p remote repository
echo Thi?t l?p remote repository...
git remote remove origin 2>nul
git remote add origin "%repo_url%"
if %errorlevel% neq 0 (
    echo L?i khi thi?t l?p remote repository.
    exit /b 1
)
echo.

REM Thêm t?t c? các t?p vào staging area
echo Thêm các t?p vào staging area...
git add .
if %errorlevel% neq 0 (
    echo L?i khi thêm t?p vào staging area.
    exit /b 1
)
echo.

REM Hi?n th? nh?ng gì s? d?c commit
echo D? án dã s?n sàng d? commit. D??i dây là danh sách các t?p s? d?c commit:
git status --short
echo.

REM Yêu c?u ng??i dùng xác nh?n commit
set /p confirm="B?n có mu?n ti?p t?c commit và push lên GitHub không? (y/n): "

if /i not "%confirm%"=="y" (
    echo H?y b? quá trình.
    exit /b 0
)

REM Th?c hi?n commit
echo Th?c hi?n commit...
git commit -m "Initial commit: Add Video-CLI project"
if %errorlevel% neq 0 (
    echo L?i khi th?c hi?n commit.
    exit /b 1
)
echo.

REM D?i tên nhánh chính sang main (n?u ch?a)
git branch -M main

REM Push lên GitHub
echo Dang push lên GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo D? án dã d?c d?y thành công lên GitHub!
    echo B?n có th? ki?m tra t?i: %repo_url%
    echo.
    echo Luu ý: N?u g?p l?i l?n d?u tiên, có th? do repository không tr?ng.
    echo Trong tr??ng h?p dó, b?n có th? c?n ph?i pull tr??c khi push:
    echo git pull origin main --allow-unrelated-histories
    echo Sau dó ch?y l?i l?nh push: git push -u origin main
) else (
    echo.
    echo L?i khi push lên GitHub. Vui lòng ki?m tra l?i k?t n?i m?ng và URL repository.
    exit /b 1
)
