# HTTPS Setup Guide for Cyber Sensei

This guide covers setting up HTTPS for both development and production environments.

## Table of Contents
1. [Development Setup (Self-Signed Certificate)](#development-setup)
2. [Production Setup (Let's Encrypt)](#production-setup)
3. [Production Setup (Nginx Reverse Proxy)](#nginx-reverse-proxy)
4. [Troubleshooting](#troubleshooting)

---

## Development Setup

### Option 1: Generate Self-Signed Certificate

```bash
cd backend
python ssl_config.py
```

This will create:
- `backend/ssl/cert.pem` - SSL certificate
- `backend/ssl/key.pem` - Private key

### Option 2: Use OpenSSL Directly

```bash
# Create ssl directory
mkdir -p backend/ssl

# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out backend/ssl/cert.pem \
  -keyout backend/ssl/key.pem \
  -days 365 \
  -subj "/C=US/ST=California/L=San Francisco/O=Cyber Sensei/CN=localhost"
```

### Start Development Server with HTTPS

```bash
cd backend

# Set environment variables
set SSL_CERT_PATH=ssl/cert.pem
set SSL_KEY_PATH=ssl/key.pem

# Start server
python start_https.py
```

Server will be available at: `https://localhost:8000`

**Note**: Your browser will show a security warning because it's a self-signed certificate. This is normal for development. Click "Advanced" → "Proceed to localhost".

---

## Production Setup

### Option 1: Direct Uvicorn with SSL

#### Step 1: Get SSL Certificate

Use Let's Encrypt (free):

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Certificates will be in:
- Certificate: `/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/yourdomain.com/privkey.pem`

#### Step 2: Configure Environment

```bash
# In backend/.env
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem
ENVIRONMENT=production
```

#### Step 3: Start Server

```bash
cd backend
python start_https.py
```

#### Step 4: Auto-Renewal

```bash
# Add to crontab
sudo crontab -e

# Add this line (renew at 2am daily)
0 2 * * * certbot renew --quiet --post-hook "systemctl restart cyber-sensei"
```

---

## Nginx Reverse Proxy

**Recommended for production** - Nginx handles SSL termination and serves static files efficiently.

### Step 1: Install Nginx

```bash
sudo apt-get update
sudo apt-get install nginx
```

### Step 2: Get SSL Certificate

```bash
# Install certbot with nginx plugin
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (nginx plugin handles configuration)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Step 3: Configure Nginx

```bash
# Copy example configuration
sudo cp backend/nginx.conf.example /etc/nginx/sites-available/cyber-sensei

# Edit configuration
sudo nano /etc/nginx/sites-available/cyber-sensei

# Update these values:
# - server_name: your domain
# - ssl_certificate paths
# - backend upstream (if not localhost:8000)
# - frontend root path

# Enable site
sudo ln -s /etc/nginx/sites-available/cyber-sensei /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 4: Start Backend (HTTP)

Since Nginx handles SSL, backend can run on HTTP:

```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 5: Build and Deploy Frontend

```bash
cd frontend
npm run build

# Copy build to nginx directory
sudo cp -r dist/* /var/www/cyber-sensei/frontend/dist/
```

### Step 6: Auto-Renewal

Certbot with nginx plugin handles renewal automatically:

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal happens automatically via systemd timer
sudo systemctl status certbot.timer
```

---

## Systemd Service (Production)

Create a systemd service for automatic startup:

### Backend Service

```bash
sudo nano /etc/systemd/system/cyber-sensei-backend.service
```

```ini
[Unit]
Description=Cyber Sensei Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/cyber-sensei/backend
Environment="PATH=/var/www/cyber-sensei/backend/venv/bin"
ExecStart=/var/www/cyber-sensei/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable cyber-sensei-backend
sudo systemctl start cyber-sensei-backend

# Check status
sudo systemctl status cyber-sensei-backend
```

---

## Frontend Configuration

Update frontend to use HTTPS API:

```bash
# frontend/.env.production
VITE_API_URL=https://yourdomain.com/api
```

Rebuild frontend:

```bash
cd frontend
npm run build
```

---

## Security Checklist

### SSL/TLS Configuration

- [ ] Use TLS 1.2 or higher
- [ ] Disable weak ciphers
- [ ] Enable HSTS (after testing)
- [ ] Enable OCSP stapling
- [ ] Use strong DH parameters

### Certificate Management

- [ ] Use trusted CA (Let's Encrypt)
- [ ] Set up auto-renewal
- [ ] Monitor expiration dates
- [ ] Keep private keys secure (chmod 600)

### Application Security

- [ ] Update CORS origins to production domain
- [ ] Enable security headers
- [ ] Set secure cookie flags
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting

### Testing

Test your SSL configuration:
- [SSL Labs](https://www.ssllabs.com/ssltest/)
- [Security Headers](https://securityheaders.com/)

---

## Troubleshooting

### Certificate Errors

**Problem**: "Certificate not trusted"
```bash
# Check certificate chain
openssl s_client -connect yourdomain.com:443 -showcerts

# Verify certificate
openssl x509 -in /path/to/cert.pem -text -noout
```

**Problem**: "Certificate expired"
```bash
# Check expiration
openssl x509 -in /path/to/cert.pem -noout -dates

# Renew certificate
sudo certbot renew --force-renewal
```

### Permission Errors

```bash
# Fix certificate permissions
sudo chmod 644 /etc/letsencrypt/live/yourdomain.com/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Add user to ssl-cert group
sudo usermod -a -G ssl-cert www-data
```

### Port Already in Use

```bash
# Find process using port 443
sudo lsof -i :443

# Kill process
sudo kill -9 <PID>
```

### Nginx Errors

```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx
```

### Backend Connection Errors

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check nginx can reach backend
sudo nginx -t

# Check firewall
sudo ufw status
```

---

## Performance Optimization

### Enable HTTP/2

Already enabled in nginx config:
```nginx
listen 443 ssl http2;
```

### Enable Compression

```nginx
# Add to nginx config
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### Cache Static Assets

Already configured in nginx.conf.example:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Monitoring

### Certificate Expiration

```bash
# Check expiration date
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### SSL/TLS Monitoring

Set up monitoring with:
- [Uptime Robot](https://uptimerobot.com/)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

### Logs

```bash
# Nginx access log
sudo tail -f /var/log/nginx/cyber-sensei-access.log

# Nginx error log
sudo tail -f /var/log/nginx/cyber-sensei-error.log

# Backend logs
sudo journalctl -u cyber-sensei-backend -f
```

---

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Certbot Documentation](https://certbot.eff.org/docs/)

---

**Status**: ✅ HTTPS configuration ready for deployment
**Last Updated**: February 2026
