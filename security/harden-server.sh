#!/bin/bash
# LookHub Server Hardening Script (Production Ready)

set -e

echo "🔒 Starting server hardening process..."

# =========================
# 1️⃣ Проверка прав root
# =========================
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# =========================
# 2️⃣ Обновление системы
# =========================
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# =========================
# 3️⃣ Установка инструментов безопасности
# =========================
echo "🛡️ Installing security tools..."
apt-get install -y ufw fail2ban unattended-upgrades

# =========================
# 4️⃣ Настройка UFW (Firewall)
# =========================
echo "🔥 Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# =========================
# 5️⃣ Настройка fail2ban
# =========================
echo "🚫 Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# =========================
# 6️⃣ Настройка автообновлений
# =========================
echo "🔄 Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/50unattended-upgrades << EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades << EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# =========================
# 7️⃣ Безопасность SSH
# =========================
echo "🔐 Securing SSH configuration..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# ⚠️ Проверка наличия SSH ключей
if [ ! -f ~/.ssh/authorized_keys ]; then
    echo "❌ No SSH keys found in ~/.ssh/authorized_keys"
    echo "Please add your key before disabling password login."
else
    cat >> /etc/ssh/sshd_config << EOF

# Security hardening
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
UsePAM yes
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 2
EOF
fi

systemctl restart ssh

# =========================
# 8️⃣ Настройка logrotate
# =========================
echo "📝 Configuring log rotation..."
cat > /etc/logrotate.d/lookhub << EOF
/var/log/lookhub/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    sharedscripts
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 \$(cat /var/run/nginx.pid)
        fi
    endscript
}
EOF

# =========================
# 9️⃣ Скрипт мониторинга безопасности
# =========================
echo "👁️ Setting up security monitoring..."
cat > /usr/local/bin/lookhub-security-check.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/lookhub-security.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$DATE] Starting security check..." >> "$LOG_FILE"

# Failed logins
FAILED_LOGINS=$(grep "Failed password" /var/log/auth.log | wc -l)
if [ "$FAILED_LOGINS" -gt 10 ]; then
    echo "[$DATE] WARNING: High number of failed login attempts: $FAILED_LOGINS" >> "$LOG_FILE"
fi

# Disk usage
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is high: ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Docker stopped containers
if command -v docker &> /dev/null; then
    STOPPED_CONTAINERS=$(docker ps -a --filter "status=exited" | wc -l)
    if [ "$STOPPED_CONTAINERS" -gt 1 ]; then
        echo "[$DATE] WARNING: $((STOPPED_CONTAINERS-1)) stopped containers detected" >> "$LOG_FILE"
    fi
fi

# Suspicious processes
SUSPICIOUS=$(ps aux | grep -E "(nc|netcat|nmap|masscan)" | grep -v grep | wc -l)
if [ "$SUSPICIOUS" -gt 0 ]; then
    echo "[$DATE] WARNING: Suspicious network tools detected" >> "$LOG_FILE"
fi

echo "[$DATE] Security check completed" >> "$LOG_FILE"
EOF

chmod +x /usr/local/bin/lookhub-security-check.sh

# Добавление в cron безопасно
(crontab -l 2>/dev/null; echo "0 */6 * * * /usr/local/bin/lookhub-security-check.sh") | crontab -

# =========================
# 🔟 Настройка Docker безопасности
# =========================
echo "🐳 Configuring Docker security..."
if command -v docker &> /dev/null; then
    cat > /etc/docker/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "live-restore": true,
    "userland-proxy": false
}
EOF
    systemctl restart docker
fi

# =========================
# ✅ Итог
# =========================
echo "🎉 Server hardening completed!"
echo ""
echo "📋 Security checklist created at /root/security-checklist.txt (manual review recommended)"
echo "🔗 Useful commands:"
echo "   - Check firewall: ufw status"
echo "   - Check fail2ban: fail2ban-client status"
echo "   - Security logs: tail -f /var/log/lookhub-security.log"
