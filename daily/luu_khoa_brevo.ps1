# Lưu khoá API Brevo của 2 site (chạy 1 lần). Chuột phải → Run with PowerShell.
# Brevo → góc phải (tên tài khoản) → SMTP & API → API Keys → Generate a new API key.
# RankerNest và RankerToolAI là 2 tài khoản Brevo khác nhau: lấy khoá ở từng tài khoản.
foreach ($pair in @(@("RN_BREVO_API_KEY","RankerNest"), @("RTA_BREVO_API_KEY","RankerToolAI"))) {
  $sec = Read-Host -AsSecureString "Dán khoá Brevo của $($pair[1]) (bỏ trống rồi Enter để bỏ qua)"
  $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
  if ($plain -and $plain.Length -ge 20) { [Environment]::SetEnvironmentVariable($pair[0], $plain.Trim(), "User"); Write-Host "Đã lưu khoá $($pair[1])." -ForegroundColor Green }
  else { Write-Host "Bỏ qua $($pair[1])." -ForegroundColor Yellow }
}
Read-Host "Xong. Enter để đóng"
