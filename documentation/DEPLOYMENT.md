# Deployment Guide

## Overview

Science Downloader supports multiple deployment options: development, production web server, and portable applications.

## Deployment Options

### 1. Development Deployment
- **Use Case**: Local development and testing
- **Features**: Auto-reload, debug mode, detailed logging
- **Requirements**: Python 3.8+, pip

### 2. Production Web Deployment
- **Use Case**: Multi-user web application
- **Features**: WSGI server, reverse proxy, SSL, monitoring
- **Requirements**: Linux server, nginx/Apache, SSL certificates

### 3. Portable Application
- **Use Case**: Single-user desktop application
- **Features**: Self-contained, zero dependencies, cross-platform
- **Requirements**: None (pre-built executables)

## Development Deployment

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd science-downloader
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run development server
python app.py
```

### Configuration
```bash
# Environment variables
export FLASK_ENV=development
export FLASK_DEBUG=true
export DATA_DIR=./data
export LOGS_DIR=./data/logs
export FLASK_PORT=5000
```

### Features
- Auto-reload on file changes
- Debug mode with detailed error pages
- Development logging
- Browser auto-launch
- Port auto-detection

## Production Web Deployment

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.8+
- **Memory**: 2GB+ RAM
- **Storage**: 10GB+ disk space
- **Network**: HTTPS access

### Installation

#### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx

# Create application user
sudo useradd -m -s /bin/bash sciencedownloader
sudo usermod -aG www-data sciencedownloader
```

#### 2. Application Setup
```bash
# Switch to application user
sudo su - sciencedownloader

# Clone repository
git clone <repository-url> /home/sciencedownloader/science-downloader
cd /home/sciencedownloader/science-downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create data directories
mkdir -p data/logs
chmod 755 data/
chmod 644 data/*.json
```

#### 3. WSGI Configuration
```python
# wsgi.py
from downloader.web import create_app
from downloader.config import get_config

config = get_config()
app = create_app(config)

if __name__ == "__main__":
    app.run()
```

#### 4. Systemd Service
```ini
# /etc/systemd/system/science-downloader.service
[Unit]
Description=Science Downloader
After=network.target

[Service]
Type=exec
User=sciencedownloader
Group=sciencedownloader
WorkingDirectory=/home/sciencedownloader/science-downloader
Environment=PATH=/home/sciencedownloader/science-downloader/venv/bin
Environment=FLASK_ENV=production
Environment=DATA_DIR=/home/sciencedownloader/science-downloader/data
Environment=LOGS_DIR=/home/sciencedownloader/science-downloader/data/logs
ExecStart=/home/sciencedownloader/science-downloader/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /home/sciencedownloader/science-downloader/data/logs/access.log \
    --error-logfile /home/sciencedownloader/science-downloader/data/logs/error.log \
    wsgi:app

[Install]
WantedBy=multi-user.target
```

#### 5. Nginx Configuration
```nginx
# /etc/nginx/sites-available/science-downloader
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static Files
    location /static/ {
        alias /home/sciencedownloader/science-downloader/downloader/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # File Upload Limits
    client_max_body_size 50M;
}
```

#### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 7. Service Management
```bash
# Enable and start services
sudo systemctl enable science-downloader
sudo systemctl start science-downloader
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status science-downloader
sudo systemctl status nginx

# View logs
sudo journalctl -u science-downloader -f
sudo tail -f /var/log/nginx/access.log
```

### Production Configuration

#### Environment Variables
```bash
# /home/sciencedownloader/science-downloader/.env
FLASK_ENV=production
FLASK_DEBUG=false
DATA_DIR=/home/sciencedownloader/science-downloader/data
LOGS_DIR=/home/sciencedownloader/science-downloader/data/logs
FLASK_HOST=127.0.0.1
FLASK_PORT=8000
```

#### Security Hardening
```bash
# Firewall configuration
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# File permissions
sudo chown -R sciencedownloader:sciencedownloader /home/sciencedownloader/science-downloader
sudo chmod 755 /home/sciencedownloader/science-downloader
sudo chmod 644 /home/sciencedownloader/science-downloader/data/*.json
```

## Portable Application Deployment

### macOS Portable App

#### Building
```bash
cd portable/macos/builder
./build.sh
```

#### Distribution
- **DMG Installer**: `science-downloader.dmg`
- **App Bundle**: `Science Downloader.app`
- **Features**:
  - Native macOS integration
  - Retina display support
  - File associations
  - Auto-updates (optional)

#### Installation
1. Download DMG file
2. Mount DMG and drag app to Applications
3. Launch from Applications folder
4. Grant necessary permissions

### Windows Portable App

#### Building
```bash
cd portable/windows/builder
python build_windows.py
```

#### Distribution
- **Executable**: `science-downloader.exe`
- **Archive**: `science-downloader-portable.rar`
- **Features**:
  - Self-contained executable
  - No installation required
  - Portable across systems

#### Installation
1. Extract executable to desired location
2. Run executable directly
3. No system installation required

## Monitoring and Maintenance

### Health Checks

#### Application Health
```bash
# Check application status
curl -f http://localhost:8000/api/health

# Check database connectivity
curl -f http://localhost:8000/api/stats/overview
```

#### System Health
```bash
# Check system resources
htop
df -h
free -h

# Check service status
sudo systemctl status science-downloader
sudo systemctl status nginx
```

### Logging

#### Application Logs
```bash
# View application logs
tail -f /home/sciencedownloader/science-downloader/data/logs/app.log

# View access logs
tail -f /home/sciencedownloader/science-downloader/data/logs/access.log

# View error logs
tail -f /home/sciencedownloader/science-downloader/data/logs/error.log
```

#### System Logs
```bash
# View systemd logs
sudo journalctl -u science-downloader -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup Strategy

#### Data Backup
```bash
# Create backup script
cat > /home/sciencedownloader/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/sciencedownloader/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf $BACKUP_DIR/science-data-$DATE.tar.gz \
    /home/sciencedownloader/science-downloader/data/

# Backup configuration
tar -czf $BACKUP_DIR/science-config-$DATE.tar.gz \
    /home/sciencedownloader/science-downloader/downloader/config/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/sciencedownloader/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/sciencedownloader/backup.sh
```

### Performance Monitoring

#### Metrics Collection
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor application performance
ps aux | grep science-downloader
netstat -tlnp | grep :8000
```

#### Resource Limits
```bash
# Set resource limits in systemd
# Edit /etc/systemd/system/science-downloader.service
[Service]
# ... existing configuration ...
LimitNOFILE=65536
LimitNPROC=4096
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
sudo journalctl -u science-downloader -n 50

# Check permissions
ls -la /home/sciencedownloader/science-downloader/
sudo chown -R sciencedownloader:sciencedownloader /home/sciencedownloader/science-downloader/
```

#### Port Conflicts
```bash
# Check port usage
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# Kill conflicting process
sudo kill -9 <PID>
```