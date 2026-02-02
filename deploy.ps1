# ═══════════════════════════════════════════════════════════════════════════════
# DAILY KOREAN — Windows Deploy Script (PowerShell)
# ═══════════════════════════════════════════════════════════════════════════════
# Script này giúp deploy nhanh lên VPS từ Windows
# Usage: .\deploy.ps1 -ServerIP "167.99.123.45"
# ═══════════════════════════════════════════════════════════════════════════════

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [string]$User = "root",
    [string]$RemoteDir = "/home/dailykorean/app"
)

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "🚀 DAILY KOREAN — Deploying to $ServerIP" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green

$Server = "${User}@${ServerIP}"
$LocalDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ─── Step 1: Check required files ───
Write-Host ""
Write-Host "📋 Step 1: Checking required files..." -ForegroundColor Yellow

$RequiredFiles = @(".env", "client_secrets.json", "main.py", "requirements.txt")
$Missing = $false

foreach ($file in $RequiredFiles) {
    $path = Join-Path $LocalDir $file
    if (Test-Path $path) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
        $Missing = $true
    }
}

if ($Missing) {
    Write-Host "❌ Missing required files. Please check and try again." -ForegroundColor Red
    exit 1
}

# ─── Step 2: Test SSH connection ───
Write-Host ""
Write-Host "🔗 Step 2: Testing SSH connection..." -ForegroundColor Yellow

try {
    ssh -o ConnectTimeout=10 -o BatchMode=yes $Server "echo 'SSH OK'" 2>$null
    Write-Host "  ✅ SSH connection OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to $Server" -ForegroundColor Red
    Write-Host "   Make sure:" -ForegroundColor Yellow
    Write-Host "   1. Server IP is correct"
    Write-Host "   2. SSH key is configured"
    Write-Host "   3. Server is running"
    exit 1
}

# ─── Step 3: Create remote directories ───
Write-Host ""
Write-Host "📁 Step 3: Creating remote directories..." -ForegroundColor Yellow

$SetupScript = @"
useradd -m -s /bin/bash dailykorean 2>/dev/null || true
mkdir -p /home/dailykorean/app
mkdir -p /home/dailykorean/logs
chown -R dailykorean:dailykorean /home/dailykorean
"@

ssh $Server $SetupScript
Write-Host "  ✅ Directories created" -ForegroundColor Green

# ─── Step 4: Upload files ───
Write-Host ""
Write-Host "📤 Step 4: Uploading files..." -ForegroundColor Yellow

# Upload Python files
$PythonFiles = Get-ChildItem -Path $LocalDir -Filter "*.py"
foreach ($file in $PythonFiles) {
    Write-Host "  Uploading $($file.Name)..."
    scp $file.FullName "${Server}:${RemoteDir}/"
}

# Upload config files
$ConfigFiles = @(".env", "client_secrets.json", "token.json", "requirements.txt")
foreach ($file in $ConfigFiles) {
    $path = Join-Path $LocalDir $file
    if (Test-Path $path) {
        Write-Host "  Uploading $file..."
        scp $path "${Server}:${RemoteDir}/"
    }
}

# Upload topik-video folder (excluding node_modules)
Write-Host "  Uploading topik-video folder..."
ssh $Server "mkdir -p $RemoteDir/topik-video/src $RemoteDir/topik-video/public"

$TopikVideoPath = Join-Path $LocalDir "topik-video"

# Upload source files
scp -r (Join-Path $TopikVideoPath "src") "${Server}:${RemoteDir}/topik-video/"
scp -r (Join-Path $TopikVideoPath "public") "${Server}:${RemoteDir}/topik-video/"

# Upload config files
$TopikConfigs = @("package.json", "remotion.config.ts", "tsconfig.json", "tailwind.config.js", "postcss.config.mjs")
foreach ($config in $TopikConfigs) {
    $configPath = Join-Path $TopikVideoPath $config
    if (Test-Path $configPath) {
        scp $configPath "${Server}:${RemoteDir}/topik-video/"
    }
}

Write-Host "  ✅ Files uploaded" -ForegroundColor Green

# ─── Step 5: Install dependencies on server ───
Write-Host ""
Write-Host "⚙️ Step 5: Installing dependencies on server..." -ForegroundColor Yellow

$InstallScript = @"
cd /home/dailykorean/app

# Python virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Node.js dependencies
if [ -d "topik-video" ]; then
    cd topik-video
    if [ ! -d "node_modules" ]; then
        echo "  Installing npm packages..."
        npm install --silent
    fi
    cd ..
fi

chown -R dailykorean:dailykorean /home/dailykorean
echo "  Dependencies installed"
"@

ssh $Server $InstallScript
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green

# ─── Step 6: Setup automation ───
Write-Host ""
Write-Host "⏰ Step 6: Setting up automation..." -ForegroundColor Yellow

$AutomationScript = @'
# Create run script
cat > /home/dailykorean/run_daily.sh << 'SCRIPT'
#!/bin/bash
LOG_DIR="/home/dailykorean/logs"
LOG_FILE="$LOG_DIR/daily_$(date +%Y%m%d_%H%M%S).log"
APP_DIR="/home/dailykorean/app"

mkdir -p $LOG_DIR
cd $APP_DIR
source venv/bin/activate

echo "Started at $(date)" >> $LOG_FILE
python main.py >> $LOG_FILE 2>&1

cd topik-video
for comp in TikTok-NewsHealing TikTok-WritingCoach TikTok-VocabQuiz TikTok-GrammarQuiz YouTube-DeepDive; do
    npx remotion render $comp --props="$(cat public/final_data.json)" "out/${comp}.mp4" >> $LOG_FILE 2>&1
done
cd ..

python youtube_uploader.py >> $LOG_FILE 2>&1 || true
echo "Completed at $(date)" >> $LOG_FILE
find $LOG_DIR -name "daily_*.log" -mtime +30 -delete
SCRIPT

chmod +x /home/dailykorean/run_daily.sh
chown dailykorean:dailykorean /home/dailykorean/run_daily.sh

# Create systemd service
cat > /etc/systemd/system/dailykorean.service << 'SERVICE'
[Unit]
Description=Daily Korean Content Generator
After=network.target

[Service]
Type=oneshot
User=dailykorean
WorkingDirectory=/home/dailykorean/app
ExecStart=/home/dailykorean/run_daily.sh
SERVICE

# Create systemd timer (6:00 AM KST = 21:00 UTC)
cat > /etc/systemd/system/dailykorean.timer << 'TIMER'
[Unit]
Description=Run Daily Korean at 6:00 AM KST

[Timer]
OnCalendar=*-*-* 21:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
TIMER

systemctl daemon-reload
systemctl enable dailykorean.timer
systemctl start dailykorean.timer
'@

ssh $Server $AutomationScript
Write-Host "  ✅ Automation configured" -ForegroundColor Green

# ─── Summary ───
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Server: $ServerIP" -ForegroundColor Cyan
Write-Host "📁 App directory: /home/dailykorean/app" -ForegroundColor Cyan
Write-Host "⏰ Schedule: Daily at 6:00 AM KST" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. SSH into server: ssh $Server"
Write-Host "  2. Test run: sudo -u dailykorean /home/dailykorean/run_daily.sh"
Write-Host "  3. Check logs: tail -f /home/dailykorean/logs/daily_*.log"
Write-Host "  4. Check timer: systemctl status dailykorean.timer"
Write-Host ""
