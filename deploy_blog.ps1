#!/usr/bin/env pwsh
# ============================================
# DAILY KOREAN - Blog Deploy Script
# ============================================
# Deploy blog lên GitHub Pages

param(
    [string]$CommitMessage = "Update blog: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

$BlogDir = "C:\Users\ThinkPad\TIK\blog_output"

Write-Host "🚀 DAILY KOREAN Blog Deployer" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path "$BlogDir\.git")) {
    Write-Host "⚠️ Git chưa được khởi tạo. Đang khởi tạo..." -ForegroundColor Yellow
    
    Set-Location $BlogDir
    git init
    
    # Prompt for remote URL
    $RemoteUrl = Read-Host "Nhập GitHub repo URL (vd: https://github.com/username/dailykorean-blog.git)"
    git remote add origin $RemoteUrl
    
    # Prompt for user info
    $UserName = Read-Host "Nhập tên Git (vd: Your Name)"
    $UserEmail = Read-Host "Nhập email Git"
    
    git config user.name $UserName
    git config user.email $UserEmail
}

Set-Location $BlogDir

# Count files
$FileCount = (Get-ChildItem -Recurse -File).Count
$PostCount = (Get-ChildItem "posts" -Filter "*.html" -ErrorAction SilentlyContinue).Count

Write-Host "📁 Blog directory: $BlogDir" -ForegroundColor Gray
Write-Host "📄 Total files: $FileCount" -ForegroundColor Gray
Write-Host "📝 Posts: $PostCount" -ForegroundColor Gray
Write-Host ""

# Git status
Write-Host "📊 Checking changes..." -ForegroundColor Gray
$Changes = git status --porcelain

if (-not $Changes) {
    Write-Host "✅ No changes to deploy!" -ForegroundColor Green
    exit 0
}

Write-Host "📝 Changes detected:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Add all changes
Write-Host "➕ Adding changes..." -ForegroundColor Gray
git add .

# Commit
Write-Host "💾 Committing: $CommitMessage" -ForegroundColor Gray
git commit -m $CommitMessage

# Push
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Gray
$PushResult = git push origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Blog deployed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Get remote URL
    $RemoteUrl = git remote get-url origin
    $RepoPath = $RemoteUrl -replace "https://github.com/", "" -replace ".git", ""
    $Username = ($RepoPath -split "/")[0]
    $RepoName = ($RepoPath -split "/")[1]
    
    Write-Host "🌐 Blog URL: https://$Username.github.io/$RepoName/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Note: GitHub Pages có thể mất 1-2 phút để cập nhật." -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host $PushResult
    Write-Host ""
    Write-Host "💡 Thử:" -ForegroundColor Yellow
    Write-Host "   1. Kiểm tra GH_TOKEN trong .env" -ForegroundColor Gray
    Write-Host "   2. git push origin main --force" -ForegroundColor Gray
}
