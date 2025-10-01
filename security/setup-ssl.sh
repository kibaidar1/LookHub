#!/bin/bash
set -e

# Загружаем переменные из .env.prod
if [ -f .env.prod ]; then
    export $(grep -v '^#' .env.prod | xargs)
fi

echo "🔒 Setting up SSL for domain: $DOMAIN"

if [ "$1" = "dev" ]; then
    echo "🔧 Generating self-signed certificate for development..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "/etc/nginx/ssl/key.pem" \
        -out "/etc/nginx/ssl/cert.pem" \
        -subj "/C=RU/ST=Moscow/L=Moscow/O=LookHub/OU=IT/CN=$DOMAIN"
    echo "✅ Self-signed certificate generated"
else
    echo "🌐 Generating Let's Encrypt certificate..."
    certbot certonly --standalone \
        --email "$SSL_EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN"

    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "/etc/nginx/ssl/cert.pem"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "/etc/nginx/ssl/key.pem"
    echo "✅ Let's Encrypt certificate generated"
fi

chmod 600 "/etc/nginx/ssl/key.pem"
chmod 644 "/etc/nginx/ssl/cert.pem"
echo "🎉 SSL setup completed"
