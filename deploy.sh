#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# DAILY KOREAN — Quick Deploy Script
# ═══════════════════════════════════════════════════════════════════════════════
# Script này giúp deploy nhanh lên VPS
# Usage: bash deploy.sh <server-ip>
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}❌ Usage: bash deploy.sh <server-ip>${NC}"
    echo "   Example: bash deploy.sh 167.99.123.45"
    exit 1
fi

SERVER_IP=$1
SERVER="root@$SERVER_IP"
REMOTE_DIR="/home/dailykorean/app"

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 DAILY KOREAN — Deploying to $SERVER_IP${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"

# ─── Step 1: Check required files ───
echo ""
echo -e "${YELLOW}📋 Step 1: Checking required files...${NC}"

REQUIRED_FILES=(".env" "client_secrets.json" "main.py" "requirements.txt")
MISSING=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ✅ $file"
    else
        echo -e "  ${RED}❌ $file - MISSING${NC}"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo -e "${RED}❌ Missing required files. Please check and try again.${NC}"
    exit 1
fi

# ─── Step 2: Test SSH connection ───
echo ""
echo -e "${YELLOW}🔗 Step 2: Testing SSH connection...${NC}"

ssh -o ConnectTimeout=10 -o BatchMode=yes $SERVER "echo 'SSH OK'" 2>/dev/null || {
    echo -e "${RED}❌ Cannot connect to $SERVER${NC}"
    echo "   Make sure:"
    echo "   1. Server IP is correct"
    echo "   2. SSH key is configured"
    echo "   3. Server is running"
    exit 1
}
echo -e "  ✅ SSH connection OK"

# ─── Step 3: Create remote directories ───
echo ""
echo -e "${YELLOW}📁 Step 3: Creating remote directories...${NC}"

ssh $SERVER << 'ENDSSH'
useradd -m -s /bin/bash dailykorean 2>/dev/null || true
mkdir -p /home/dailykorean/app
mkdir -p /home/dailykorean/logs
chown -R dailykorean:dailykorean /home/dailykorean
ENDSSH

echo -e "  ✅ Directories created"

# ─── Step 4: Upload files ───
echo ""
echo -e "${YELLOW}📤 Step 4: Uploading files...${NC}"

# Create exclude file
cat > /tmp/rsync_exclude << 'EOF'
node_modules
__pycache__
.git
*.pyc
*.log
out/*.mp4
build/
.env.local
EOF

# Upload using rsync (faster for large directories)
if command -v rsync &> /dev/null; then
    echo "  Using rsync..."
    rsync -avz --exclude-from=/tmp/rsync_exclude \
        --progress \
        ./ $SERVER:$REMOTE_DIR/
else
    # Fallback to scp
    echo "  Using scp (rsync not available)..."
    
    # Upload Python files
    scp *.py $SERVER:$REMOTE_DIR/
    scp requirements.txt $SERVER:$REMOTE_DIR/
    scp .env $SERVER:$REMOTE_DIR/
    scp client_secrets.json $SERVER:$REMOTE_DIR/ 2>/dev/null || true
    scp token.json $SERVER:$REMOTE_DIR/ 2>/dev/null || true
    
    # Upload topik-video (excluding node_modules)
    ssh $SERVER "mkdir -p $REMOTE_DIR/topik-video"
    scp -r topik-video/src $SERVER:$REMOTE_DIR/topik-video/
    scp -r topik-video/public $SERVER:$REMOTE_DIR/topik-video/
    scp topik-video/package.json $SERVER:$REMOTE_DIR/topik-video/
    scp topik-video/remotion.config.ts $SERVER:$REMOTE_DIR/topik-video/
    scp topik-video/tsconfig.json $SERVER:$REMOTE_DIR/topik-video/
fi

echo -e "  ✅ Files uploaded"

# ─── Step 5: Install dependencies on server ───
echo ""
echo -e "${YELLOW}⚙️ Step 5: Installing dependencies on server...${NC}"

ssh $SERVER << 'ENDSSH'
cd /home/dailykorean/app

# Check if first time setup needed
if [ ! -f "venv/bin/activate" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Install Node.js dependencies
if [ -d "topik-video" ]; then
    cd topik-video
    if [ ! -d "node_modules" ]; then
        echo "  Installing npm packages..."
        npm install --silent
    fi
    cd ..
fi

chown -R dailykorean:dailykorean /home/dailykorean
echo "  ✅ Dependencies installed"
ENDSSH

# ─── Step 6: Setup systemd timer ───
echo ""
echo -e "${YELLOW}⏰ Step 6: Setting up automation...${NC}"

ssh $SERVER << 'ENDSSH'
# Create run script
cat > /home/dailykorean/run_daily.sh << 'SCRIPT'
#!/bin/bash
LOG_DIR="/home/dailykorean/logs"
LOG_FILE="$LOG_DIR/daily_$(date +%Y%m%d_%H%M%S).log"
APP_DIR="/home/dailykorean/app"

mkdir -p $LOG_DIR

echo "════════════════════════════════════════" >> $LOG_FILE
echo "🚀 Started at $(date)" >> $LOG_FILE
echo "════════════════════════════════════════" >> $LOG_FILE

cd $APP_DIR
source venv/bin/activate

# Generate content
echo "[$(date +%H:%M:%S)] Generating content..." >> $LOG_FILE
python main.py >> $LOG_FILE 2>&1

# Render videos
echo "[$(date +%H:%M:%S)] Rendering videos..." >> $LOG_FILE
cd topik-video
for comp in TikTok-NewsHealing TikTok-WritingCoach TikTok-VocabQuiz TikTok-GrammarQuiz YouTube-DeepDive; do
    npx remotion render $comp --props="$(cat public/final_data.json)" "out/${comp}.mp4" >> $LOG_FILE 2>&1
done
cd ..

# Upload
echo "[$(date +%H:%M:%S)] Uploading..." >> $LOG_FILE
python youtube_uploader.py >> $LOG_FILE 2>&1 || true

echo "✅ Completed at $(date)" >> $LOG_FILE

# Cleanup old logs
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
StandardOutput=journal
StandardError=journal
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

echo "  ✅ Automation configured (runs daily at 6:00 AM KST)"
ENDSSH

# ─── Step 7: Summary ───
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📍 Server: ${YELLOW}$SERVER_IP${NC}"
echo -e "📁 App directory: ${YELLOW}/home/dailykorean/app${NC}"
echo -e "⏰ Schedule: ${YELLOW}Daily at 6:00 AM KST${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. SSH into server: ssh $SERVER"
echo "  2. Test run: sudo -u dailykorean /home/dailykorean/run_daily.sh"
echo "  3. Check logs: tail -f /home/dailykorean/logs/daily_*.log"
echo "  4. Check timer: systemctl status dailykorean.timer"
echo ""
