#!/bin/bash
# ================================================================================
# TOPIK DAILY — DigitalOcean Droplet Setup Script
# ================================================================================
# This script sets up a fresh Ubuntu droplet for running TOPIK Daily automation
# 
# Usage:
#   1. Create a new DigitalOcean droplet (Ubuntu 22.04 LTS, 2GB RAM minimum)
#   2. SSH into the droplet: ssh root@<droplet-ip>
#   3. Run this script: bash setup_digitalocean.sh
# ================================================================================

set -e  # Exit on error

echo "=================================================="
echo "🚀 TOPIK Daily — DigitalOcean Setup"
echo "=================================================="

# ==================== SYSTEM UPDATE ====================
echo ""
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# ==================== INSTALL DEPENDENCIES ====================
echo ""
echo "📦 Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    chromium-browser \
    chromium-chromedriver \
    git \
    curl \
    wget \
    unzip \
    htop \
    screen \
    nginx \
    certbot \
    python3-certbot-nginx

# ==================== INSTALL NODE.JS (for Remotion) ====================
echo ""
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Verify
node --version
npm --version

# ==================== CREATE APP USER ====================
echo ""
echo "👤 Creating app user..."
useradd -m -s /bin/bash topikbot || true
usermod -aG sudo topikbot

# ==================== SETUP APPLICATION ====================
echo ""
echo "📁 Setting up application directory..."
APP_DIR="/home/topikbot/topik-daily"
mkdir -p $APP_DIR
chown -R topikbot:topikbot /home/topikbot

# ==================== CLONE REPOSITORY ====================
echo ""
echo "📥 Cloning repository..."
cd /home/topikbot

# Replace with your actual repo
if [ -d "$APP_DIR/.git" ]; then
    echo "Repository exists, pulling latest..."
    cd $APP_DIR
    git pull
else
    # Clone from GitHub (replace with your repo)
    git clone https://github.com/cquangduu/topik-daily.git $APP_DIR || {
        echo "Creating empty directory..."
        mkdir -p $APP_DIR
    }
fi

cd $APP_DIR

# ==================== PYTHON VIRTUAL ENVIRONMENT ====================
echo ""
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# ==================== INSTALL PYTHON DEPENDENCIES ====================
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip

cat > requirements.txt << 'EOF'
# Core
python-dotenv
requests
beautifulsoup4
google-api-python-client
google-auth-oauthlib
google-auth-httplib2

# Audio/Video
pydub
mutagen
azure-cognitiveservices-speech
edge-tts

# Document
python-docx

# Web scraping
selenium
webdriver-manager

# Utilities
Pillow
aiohttp
EOF

pip install -r requirements.txt

# ==================== INSTALL NPM DEPENDENCIES (Remotion) ====================
echo ""
echo "📦 Installing Node.js dependencies for Remotion..."
cd topik-video 2>/dev/null || mkdir -p topik-video && cd topik-video

if [ -f "package.json" ]; then
    npm install
else
    echo "Initializing Remotion project..."
    npm init -y
    npm install @remotion/cli @remotion/renderer remotion react react-dom
fi

cd $APP_DIR

# ==================== SETUP ENVIRONMENT FILE ====================
echo ""
echo "⚙️ Setting up environment variables..."

if [ ! -f ".env" ]; then
    cat > .env.example << 'EOF'
# ==================== API KEYS ====================
GEMINI_API_KEY=your_gemini_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=koreacentral
PEXELS_API_KEY=your_pexels_api_key

# ==================== GOOGLE DRIVE ====================
DRIVE_FOLDER_ID=your_drive_folder_id
GDRIVE_CREDENTIALS_JSON={"installed":{...}}

# ==================== YOUTUBE ====================
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted
YOUTUBE_PLAYLIST_ID=

# ==================== SOCIAL MEDIA ====================
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
DISCORD_WEBHOOK_URL=your_discord_webhook
TWITTER_BEARER_TOKEN=your_twitter_token

# ==================== GITHUB ====================
GH_TOKEN=your_github_token
GH_BLOG_REPO=username/topik-blog
GH_CUSTOM_DOMAIN=topikdaily.com

# ==================== EMAIL ====================
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_SUBSCRIBER_LIST=subscriber1@email.com,subscriber2@email.com
EOF
    
    echo "⚠️ Please edit .env file with your credentials:"
    echo "   nano /home/topikbot/topik-daily/.env"
fi

# ==================== SETUP CRON JOB ====================
echo ""
echo "⏰ Setting up cron job..."

# Create the run script
cat > /home/topikbot/run_topik_daily.sh << 'EOF'
#!/bin/bash
# TOPIK Daily - Daily Run Script

LOG_FILE="/home/topikbot/logs/topik_$(date +%Y%m%d_%H%M%S).log"
mkdir -p /home/topikbot/logs

cd /home/topikbot/topik-daily
source venv/bin/activate

echo "========================================" >> $LOG_FILE
echo "Starting TOPIK Daily at $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Run main pipeline
python main.py >> $LOG_FILE 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Pipeline completed successfully" >> $LOG_FILE
else
    echo "❌ Pipeline failed" >> $LOG_FILE
fi

# Cleanup old logs (keep last 30 days)
find /home/topikbot/logs -name "topik_*.log" -mtime +30 -delete

echo "Finished at $(date)" >> $LOG_FILE
EOF

chmod +x /home/topikbot/run_topik_daily.sh

# Add cron job (run daily at 6:00 AM KST = 21:00 UTC previous day)
CRON_LINE="0 21 * * * /home/topikbot/run_topik_daily.sh"

(crontab -u topikbot -l 2>/dev/null | grep -v "run_topik_daily"; echo "$CRON_LINE") | crontab -u topikbot -

echo "✅ Cron job added: Daily at 6:00 AM KST"

# ==================== SETUP SYSTEMD SERVICE (Optional) ====================
echo ""
echo "🔧 Setting up systemd service..."

cat > /etc/systemd/system/topik-daily.service << 'EOF'
[Unit]
Description=TOPIK Daily Automation Service
After=network.target

[Service]
Type=oneshot
User=topikbot
WorkingDirectory=/home/topikbot/topik-daily
ExecStart=/home/topikbot/run_topik_daily.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/topik-daily.timer << 'EOF'
[Unit]
Description=Run TOPIK Daily at 6:00 AM KST

[Timer]
OnCalendar=*-*-* 21:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable topik-daily.timer
systemctl start topik-daily.timer

# ==================== SETUP NGINX (for serving blog/podcast) ====================
echo ""
echo "🌐 Setting up Nginx..."

cat > /etc/nginx/sites-available/topik-daily << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /home/topikbot/topik-daily/blog_output;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /podcast {
        alias /home/topikbot/topik-daily/podcast_output;
        autoindex on;
    }
    
    # Podcast RSS feed
    location /feed.xml {
        alias /home/topikbot/topik-daily/podcast_output/feed.xml;
        default_type application/rss+xml;
    }
}
EOF

ln -sf /etc/nginx/sites-available/topik-daily /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ==================== FIREWALL ====================
echo ""
echo "🔥 Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# ==================== SET PERMISSIONS ====================
chown -R topikbot:topikbot /home/topikbot

# ==================== SUMMARY ====================
echo ""
echo "=================================================="
echo "✅ TOPIK Daily Setup Complete!"
echo "=================================================="
echo ""
echo "📁 Application directory: $APP_DIR"
echo "📝 Edit environment variables: nano $APP_DIR/.env"
echo "🔄 Manual run: sudo -u topikbot /home/topikbot/run_topik_daily.sh"
echo "📊 View logs: tail -f /home/topikbot/logs/topik_*.log"
echo "⏰ Cron schedule: Daily at 6:00 AM KST (21:00 UTC)"
echo ""
echo "🌐 Nginx serving:"
echo "   - Blog: http://<server-ip>/"
echo "   - Podcast RSS: http://<server-ip>/feed.xml"
echo ""
echo "🔒 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Upload credentials (token.json, youtube_token.json)"
echo "   3. Test run: sudo -u topikbot /home/topikbot/run_topik_daily.sh"
echo "   4. Set up SSL: certbot --nginx -d yourdomain.com"
echo ""
echo "=================================================="
