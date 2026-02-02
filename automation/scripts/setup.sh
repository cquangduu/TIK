#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# TOPIK Daily - DigitalOcean Droplet Setup Script
# For: Premium Intel 1vCPU / 2GB RAM / 50GB SSD
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "🚀 TOPIK Daily - Server Setup Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
apt install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    nginx certbot python3-certbot-nginx \
    supervisor \
    ffmpeg \
    sqlite3 \
    htop iotop \
    fail2ban \
    ufw

# ═══════════════════════════════════════════════════════════════════════════════
# SWAP CONFIGURATION (Critical for 2GB RAM)
# ═══════════════════════════════════════════════════════════════════════════════

echo "💾 Configuring 2GB swap file..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    # Optimize swap settings for low RAM
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
    sysctl -p
fi

echo "✓ Swap configured: $(free -h | grep Swap)"

# ═══════════════════════════════════════════════════════════════════════════════
# CREATE APPLICATION USER
# ═══════════════════════════════════════════════════════════════════════════════

echo "👤 Creating application user..."
if ! id "topik" &>/dev/null; then
    useradd -m -s /bin/bash topik
    usermod -aG sudo topik
fi

# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION DIRECTORY SETUP
# ═══════════════════════════════════════════════════════════════════════════════

echo "📁 Setting up application directories..."
APP_DIR="/opt/topik-daily"
mkdir -p $APP_DIR/{automation,data,logs,config}
mkdir -p $APP_DIR/data/{content,audio,videos,reports}

# Clone repository (or copy files)
if [ -d "/tmp/topik-source" ]; then
    cp -r /tmp/topik-source/* $APP_DIR/
fi

chown -R topik:topik $APP_DIR

# ═══════════════════════════════════════════════════════════════════════════════
# PYTHON ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

echo "🐍 Setting up Python environment..."
cd $APP_DIR

sudo -u topik python3 -m venv venv
sudo -u topik $APP_DIR/venv/bin/pip install --upgrade pip wheel

# Install dependencies
sudo -u topik $APP_DIR/venv/bin/pip install \
    httpx[http2] \
    python-dotenv \
    schedule \
    psutil \
    aiofiles \
    pydantic \
    tenacity

echo "✓ Python environment ready"

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════

echo "🔐 Creating environment file template..."
cat > $APP_DIR/config/.env.template << 'EOF'
# ═══════════════════════════════════════════════════════════════════════════════
# TOPIK Daily - Environment Variables
# Copy to .env and fill in your values
# ═══════════════════════════════════════════════════════════════════════════════

# OpenAI API
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Azure TTS
AZURE_SPEECH_KEY=your-azure-key
AZURE_SPEECH_REGION=koreacentral

# News API
NEWS_API_KEY=your-newsapi-key

# GitHub (for Actions rendering)
GITHUB_TOKEN=ghp_your-token
GITHUB_REPO=username/topik-video
GITHUB_WORKFLOW=render-videos.yml
RENDER_STRATEGY=github

# TikTok
TIKTOK_ACCESS_TOKEN=
TIKTOK_OPEN_ID=

# YouTube
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
YOUTUBE_API_KEY=
YOUTUBE_CHANNEL_ID=

# Facebook
FACEBOOK_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=
INSTAGRAM_ACCOUNT_ID=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=@your_channel

# Cloudflare R2 (optional - for video storage)
R2_ENDPOINT=
R2_ACCESS_KEY=
R2_SECRET_KEY=
R2_BUCKET=topik-videos
EOF

chown topik:topik $APP_DIR/config/.env.template

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEMD SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/topik-scheduler.service << 'EOF'
[Unit]
Description=TOPIK Daily Scheduler
After=network.target

[Service]
Type=simple
User=topik
Group=topik
WorkingDirectory=/opt/topik-daily
Environment="PATH=/opt/topik-daily/venv/bin"
EnvironmentFile=/opt/topik-daily/config/.env
ExecStart=/opt/topik-daily/venv/bin/python automation/scheduler.py --daemon
Restart=always
RestartSec=10
StandardOutput=append:/opt/topik-daily/logs/scheduler.log
StandardError=append:/opt/topik-daily/logs/scheduler-error.log

# Resource limits for 2GB RAM
MemoryMax=512M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable topik-scheduler

# ═══════════════════════════════════════════════════════════════════════════════
# NGINX CONFIGURATION (for API/Webhook)
# ═══════════════════════════════════════════════════════════════════════════════

echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/topik-daily << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }

    location /static/ {
        alias /opt/topik-daily/data/;
        expires 7d;
    }

    location /health {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

ln -sf /etc/nginx/sites-available/topik-daily /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ═══════════════════════════════════════════════════════════════════════════════
# FIREWALL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

echo "🛡️ Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# ═══════════════════════════════════════════════════════════════════════════════
# FAIL2BAN CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

echo "🔒 Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
EOF

systemctl restart fail2ban

# ═══════════════════════════════════════════════════════════════════════════════
# LOG ROTATION
# ═══════════════════════════════════════════════════════════════════════════════

echo "📋 Configuring log rotation..."
cat > /etc/logrotate.d/topik-daily << 'EOF'
/opt/topik-daily/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 topik topik
}
EOF

# ═══════════════════════════════════════════════════════════════════════════════
# CRON JOBS (Backup)
# ═══════════════════════════════════════════════════════════════════════════════

echo "⏰ Setting up cron jobs..."
cat > /etc/cron.d/topik-daily << 'EOF'
# Backup database daily at 2 AM
0 2 * * * topik sqlite3 /opt/topik-daily/data/analytics.db ".backup '/opt/topik-daily/data/analytics-backup.db'"

# Clean old logs weekly
0 3 * * 0 topik find /opt/topik-daily/logs -name "*.log" -mtime +14 -delete

# System health check every 5 minutes
*/5 * * * * topik /opt/topik-daily/venv/bin/python /opt/topik-daily/automation/scheduler.py --run health_check > /dev/null 2>&1
EOF

# ═══════════════════════════════════════════════════════════════════════════════
# MONITORING SCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

echo "📊 Creating monitoring script..."
cat > /usr/local/bin/topik-status << 'EOF'
#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    TOPIK Daily Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📦 Service Status:"
systemctl status topik-scheduler --no-pager | head -5

echo ""
echo "💾 Resource Usage:"
echo "  Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "  Swap:   $(free -h | awk '/^Swap:/ {print $3 "/" $2}')"
echo "  Disk:   $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
echo "  CPU:    $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"

echo ""
echo "📅 Today's Tasks:"
cd /opt/topik-daily
./venv/bin/python automation/scheduler.py --status 2>/dev/null || echo "  No tasks found"

echo ""
echo "📊 Last 5 log entries:"
tail -5 /opt/topik-daily/logs/scheduler.log 2>/dev/null || echo "  No logs found"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
EOF

chmod +x /usr/local/bin/topik-status

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL STEPS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TOPIK Daily Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "  1. Copy .env.template to .env and fill in API keys:"
echo "     cp /opt/topik-daily/config/.env.template /opt/topik-daily/config/.env"
echo "     nano /opt/topik-daily/config/.env"
echo ""
echo "  2. Start the scheduler service:"
echo "     systemctl start topik-scheduler"
echo ""
echo "  3. Check status:"
echo "     topik-status"
echo ""
echo "  4. View logs:"
echo "     tail -f /opt/topik-daily/logs/scheduler.log"
echo ""
echo "  5. (Optional) Setup SSL with Let's Encrypt:"
echo "     certbot --nginx -d yourdomain.com"
echo ""
echo "📊 Resource Configuration:"
echo "  - Max memory for scheduler: 512MB"
echo "  - Swap: 2GB (for peak usage)"
echo "  - Video rendering: Cloud-based (GitHub Actions)"
echo ""
echo "💰 Estimated Monthly Costs:"
echo "  - DigitalOcean: \$6"
echo "  - Azure TTS: \$0-15 (free tier covers most usage)"
echo "  - OpenAI: \$5-20"
echo "  - Total: ~\$12-42/month"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
