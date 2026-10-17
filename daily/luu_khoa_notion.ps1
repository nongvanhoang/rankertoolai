# Lưu khoá Notion cho bảng đăng bài (chạy 1 lần). Chuột phải tệp này → Run with PowerShell.
# Khoá được lưu vào biến môi trường của tài khoản Windows (NOTION_TOKEN), không ghi ra file.
$sec = Read-Host -AsSecureString "Dán khoá Notion (bắt đầu bằng ntn_ hoặc secret_) rồi Enter"
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
if (-not $plain -or $plain.Length -lt 20) { Write-Host "Khoá trống hoặc quá ngắn, chưa lưu." -ForegroundColor Red; Read-Host "Enter để đóng"; exit 1 }
[Environment]::SetEnvironmentVariable("NOTION_TOKEN", $plain.Trim(), "User")
Write-Host "Đã lưu khoá Notion. Nhắn Claude: 'đã lưu khoá notion'." -ForegroundColor Green
Read-Host "Enter để đóng"
