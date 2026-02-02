#!/usr/bin/env pwsh
# ============================================
# DAILY KOREAN - Deploy to VPS (Clean Copy)
# ============================================
# Loại bỏ file rác trước khi upload lên VPS

param(
    [Parameter(Mandatory=$true)]
    [string]$VpsUser = "dailykorean",
    
    [Parameter(Mandatory=$true)]
    [string]$VpsIP,
    
    [string]$RemotePath = "~/TIK"
)

$SourcePath = "C:\Users\ThinkPad\TIK"
$TempPath = "$env:TEMP\TIK_deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Các thư mục/file cần loại trừ
$ExcludeDirs = @(
    "node_modules",
    "__pycache__",
    ".git",
    "build",
    "venv",
    ".venv",
    "temp_processing",
    "logs",
    ".expo",
    ".next",
    "dist",
    ".cache",
    "coverage"
)

$ExcludeFiles = @(
    "*.pyc",
    "*.pyo",
    "*.log",
    "*.tmp",
    ".DS_Store",
    "Thumbs.db",
    "*.mp4",
    "*.mp3",
    "*.wav"
)

Write-Host "🚀 DAILY KOREAN - Deploy to VPS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Tính dung lượng trước khi clean
$OriginalSize = (Get-ChildItem -Path $SourcePath -Recurse -Force -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "📦 Dung lượng gốc: $([math]::Round($OriginalSize, 2)) MB" -ForegroundColor Yellow

# Tạo thư mục tạm
Write-Host "📂 Tạo thư mục tạm: $TempPath" -ForegroundColor Gray
New-Item -ItemType Directory -Path $TempPath -Force | Out-Null

# Build exclude pattern cho robocopy
$ExcludeDirParams = $ExcludeDirs | ForEach-Object { "/XD", $_ }
$ExcludeFileParams = $ExcludeFiles | ForEach-Object { "/XF", $_ }

# Copy sạch sang thư mục tạm
Write-Host "🔄 Đang copy file sạch..." -ForegroundColor Gray
$robocopyArgs = @(
    $SourcePath,
    $TempPath,
    "/E",           # Copy subdirectories including empty ones
    "/NFL",         # No file list
    "/NDL",         # No directory list
    "/NJH",         # No job header
    "/NJS",         # No job summary
    "/NC",          # No class
    "/NS"           # No size
) + $ExcludeDirParams + $ExcludeFileParams

& robocopy @robocopyArgs | Out-Null

# Tính dung lượng sau khi clean
$CleanSize = (Get-ChildItem -Path $TempPath -Recurse -Force -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "✅ Dung lượng sau khi clean: $([math]::Round($CleanSize, 2)) MB" -ForegroundColor Green
Write-Host "💾 Tiết kiệm: $([math]::Round($OriginalSize - $CleanSize, 2)) MB" -ForegroundColor Green
Write-Host ""

# Upload lên VPS bằng scp
Write-Host "📤 Đang upload lên VPS: $VpsUser@$VpsIP`:$RemotePath" -ForegroundColor Cyan

# Tạo thư mục trên VPS trước
ssh "${VpsUser}@${VpsIP}" "mkdir -p $RemotePath"

# Upload bằng scp
scp -r "$TempPath\*" "${VpsUser}@${VpsIP}:${RemotePath}/"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Upload thành công!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Bước tiếp theo trên VPS:" -ForegroundColor Yellow
    Write-Host "   ssh $VpsUser@$VpsIP" -ForegroundColor Gray
    Write-Host "   cd $RemotePath" -ForegroundColor Gray
    Write-Host "   # Cài đặt Python dependencies" -ForegroundColor Gray
    Write-Host "   python3.11 -m venv venv" -ForegroundColor Gray
    Write-Host "   source venv/bin/activate" -ForegroundColor Gray
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "   # Cài đặt Node.js dependencies" -ForegroundColor Gray
    Write-Host "   cd topik-video && npm install" -ForegroundColor Gray
} else {
    Write-Host "❌ Upload thất bại!" -ForegroundColor Red
}

# Dọn dẹp thư mục tạm
Write-Host ""
Write-Host "🧹 Dọn dẹp thư mục tạm..." -ForegroundColor Gray
Remove-Item -Path $TempPath -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✅ Hoàn tất!" -ForegroundColor Green
