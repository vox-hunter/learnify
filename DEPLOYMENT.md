# Deployment Guide - Vue.js + FastAPI Learnify

This guide covers deploying the Vue.js + FastAPI version of Learnify to production.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Platform-Specific Guides](#platform-specific-guides)
8. [Security Considerations](#security-considerations)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Architecture Overview

The production architecture consists of three main components:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend   │─────▶│   MongoDB   │
│  (Vue.js)   │      │  (FastAPI)  │      │  Database   │
│  Static     │      │   API       │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
   Nginx/CDN          Gunicorn/Uvicorn      Atlas/Self-hosted
```

## Prerequisites

- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt or other)
- Server with:
  - Ubuntu 20.04+ / Debian 11+ (or equivalent)
  - 2GB+ RAM
  - 20GB+ storage
  - Python 3.9+
  - Node.js 18+

## Backend Deployment

### Option 1: Deploy with Gunicorn (Recommended)

#### 1. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv nginx -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/learnify.git
cd learnify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r api/requirements.txt

# Install Gunicorn
pip install gunicorn
```

#### 3. Configure Environment

```bash
# Create production .env file
nano api/.env
```

Add:
```env
GEMINI_API_KEY=your_production_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/learnify
DEBUG_MODE=False
```

#### 4. Test Backend

```bash
cd api
python main.py
# Test at http://your-server-ip:8000
# Press Ctrl+C to stop
```

#### 5. Create Systemd Service

```bash
sudo nano /etc/systemd/system/learnify-api.service
```

Add:
```ini
[Unit]
Description=Learnify FastAPI Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/learnify/api
Environment="PATH=/path/to/learnify/venv/bin"
ExecStart=/path/to/learnify/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```

#### 6. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable learnify-api

# Start service
sudo systemctl start learnify-api

# Check status
sudo systemctl status learnify-api
```

### Option 2: Deploy with Docker

#### 1. Create Dockerfile for Backend

```dockerfile
# api/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Add parent backend directory to Python path
ENV PYTHONPATH=/app:/app/..

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
```

#### 2. Build and Run

```bash
# Build image
docker build -t learnify-api ./api

# Run container
docker run -d \
  --name learnify-api \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e MONGODB_URI=your_mongodb_uri \
  learnify-api
```

## Frontend Deployment

### Option 1: Static Hosting (Netlify, Vercel, AWS S3)

#### 1. Build Frontend

```bash
cd vue-frontend

# Install dependencies
npm install

# Build for production
npm run build
```

The built files will be in `vue-frontend/dist/`.

#### 2. Configure API Endpoint

Before building, update the API base URL in `vue-frontend/src/services/api.js`:

```javascript
const api = axios.create({
  baseURL: 'https://api.yourdomain.com/api',  // Your production API URL
  // ...
})
```

#### 3. Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd vue-frontend
netlify deploy --prod --dir=dist
```

#### 4. Configure Redirects

Create `vue-frontend/dist/_redirects`:
```
/api/* https://api.yourdomain.com/api/:splat 200
/* /index.html 200
```

### Option 2: Nginx Static Hosting

#### 1. Build and Copy Files

```bash
# Build
cd vue-frontend
npm run build

# Copy to web directory
sudo mkdir -p /var/www/learnify
sudo cp -r dist/* /var/www/learnify/
```

#### 2. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/learnify
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/learnify;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. Enable Site

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/learnify /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### 4. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
```

## Database Setup

### Option 1: MongoDB Atlas (Cloud - Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist your server IP (or 0.0.0.0/0 for all)
5. Get connection string
6. Update `MONGODB_URI` in your `.env`

### Option 2: Self-Hosted MongoDB

```bash
# Install MongoDB
sudo apt install -y mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Create database and user
mongo
> use learnify_auth
> db.createUser({
  user: "learnify",
  pwd: "strong_password",
  roles: [{role: "readWrite", db: "learnify_auth"}]
})
> use learnify_courses
> db.createUser({
  user: "learnify",
  pwd: "strong_password",
  roles: [{role: "readWrite", db: "learnify_courses"}]
})
```

Update `.env`:
```env
MONGODB_URI=mongodb://learnify:strong_password@localhost:27017/
```

## Environment Configuration

### Production Environment Variables

**Backend (.env):**
```env
# Required
GEMINI_API_KEY=your_production_api_key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/

# Optional
DEBUG_MODE=False
COOKIE_ENCRYPTION_KEY=generate_a_strong_random_key_here
```

### Generating Secure Keys

```bash
# Generate random encryption key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Platform-Specific Guides

### Heroku

#### Backend

1. Create `Procfile` in `api/`:
   ```
   web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

2. Create `runtime.txt`:
   ```
   python-3.9.16
   ```

3. Deploy:
   ```bash
   cd api
   heroku create learnify-api
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set MONGODB_URI=your_mongodb_uri
   git push heroku main
   ```

#### Frontend

Deploy to Netlify or Vercel (see above).

### AWS

#### Backend (Elastic Beanstalk)

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize:
   ```bash
   cd api
   eb init -p python-3.9 learnify-api
   ```

3. Create environment:
   ```bash
   eb create learnify-api-prod
   ```

4. Set environment variables:
   ```bash
   eb setenv GEMINI_API_KEY=your_key MONGODB_URI=your_uri
   ```

#### Frontend (S3 + CloudFront)

1. Build frontend
2. Upload to S3 bucket
3. Configure CloudFront distribution
4. Update DNS

### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build settings:
   - Backend: Docker, use `api/Dockerfile`
   - Frontend: Node.js, build command `npm run build`, output `dist/`
3. Add environment variables in dashboard
4. Deploy

## Security Considerations

### 1. API Security

- ✅ Use HTTPS everywhere
- ✅ Implement rate limiting
- ✅ Validate all inputs
- ✅ Use environment variables for secrets
- ✅ Keep dependencies updated

### 2. MongoDB Security

- ✅ Use strong passwords
- ✅ Enable authentication
- ✅ Whitelist IP addresses
- ✅ Use connection string encryption
- ✅ Regular backups

### 3. CORS Configuration

Update `api/main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. File Upload Security

- Max file size: 20MB (already configured)
- Allowed file types: PDF, DOCX, etc. (already validated)
- Virus scanning (recommended for production)

## Monitoring and Maintenance

### Logging

#### Backend Logs

```bash
# View systemd service logs
sudo journalctl -u learnify-api -f

# Or if using Docker
docker logs -f learnify-api
```

#### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Health Checks

Create a monitoring script:

```bash
#!/bin/bash
# health-check.sh

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API is healthy"
else
    echo "API is down! Restarting..."
    sudo systemctl restart learnify-api
fi
```

Schedule with cron:
```bash
crontab -e
# Add: */5 * * * * /path/to/health-check.sh
```

### Backup Strategy

#### MongoDB Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="your_mongodb_uri" --out=/backups/mongo_$DATE

# Keep only last 7 days
find /backups -name "mongo_*" -mtime +7 -exec rm -rf {} \;
```

Schedule daily backups with cron.

### Updates

```bash
# Backend updates
cd /path/to/learnify
git pull
source venv/bin/activate
pip install -r api/requirements.txt
sudo systemctl restart learnify-api

# Frontend updates
cd vue-frontend
git pull
npm install
npm run build
sudo cp -r dist/* /var/www/learnify/
```

## Troubleshooting

### Backend Issues

**Problem:** API returns 502 Bad Gateway

**Solution:**
```bash
# Check if service is running
sudo systemctl status learnify-api

# View logs
sudo journalctl -u learnify-api -n 50

# Restart service
sudo systemctl restart learnify-api
```

### Frontend Issues

**Problem:** API requests fail with CORS error

**Solution:**
- Verify CORS configuration in `api/main.py`
- Check that frontend URL is in `allow_origins`
- Ensure backend is running and accessible

### Database Issues

**Problem:** MongoDB connection timeout

**Solution:**
- Check MongoDB is running
- Verify connection string
- Check IP whitelist in MongoDB Atlas
- Test connection: `mongosh "your_connection_string"`

## Performance Optimization

### Backend

1. **Enable caching:**
   ```python
   # Add Redis caching for frequently accessed data
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.redis import RedisBackend
   ```

2. **Optimize queries:**
   - Add MongoDB indexes
   - Use pagination for large result sets

3. **Scale horizontally:**
   - Add more Gunicorn workers
   - Use load balancer for multiple servers

### Frontend

1. **Enable compression:**
   ```nginx
   # In Nginx config
   gzip on;
   gzip_types text/plain text/css application/json application/javascript;
   ```

2. **CDN:**
   - Use CloudFlare or AWS CloudFront
   - Cache static assets

3. **Code splitting:**
   - Vite already does this by default
   - Monitor bundle size

## Conclusion

Your Learnify application is now deployed to production! Remember to:

- Monitor logs regularly
- Keep dependencies updated
- Backup database regularly
- Monitor resource usage
- Set up alerts for downtime

For issues or questions, refer to the [VUE_FASTAPI_README.md](./VUE_FASTAPI_README.md) or [QUICKSTART.md](./QUICKSTART.md).
