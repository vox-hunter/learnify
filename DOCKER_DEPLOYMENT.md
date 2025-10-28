# Docker Deployment Guide for Learnify

This guide provides comprehensive instructions for deploying the Learnify backend to Render using Docker. The deployment process is optimized for performance, caching, and minimal image size.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Testing](#local-testing)
3. [Render Deployment](#render-deployment)
4. [Render-Specific Optimizations](#render-specific-optimizations)
5. [Deployment Verification](#deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Continuous Deployment](#continuous-deployment)
8. [Cost Optimization](#cost-optimization)
9. [Security Best Practices](#security-best-practices)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

- Docker installed locally (for testing)
- Render account created at https://render.com
- Environment variables ready:
  - `GEMINI_API_KEY` - Your Google Gemini API key from https://makersuite.google.com/app/apikey
  - `MONGODB_URI` - Your MongoDB connection string (Atlas or other)
  - `RESEND_API_KEY` - Your Resend API key from https://resend.com/api-keys

## Local Testing

### Build the Docker Image

```bash
docker build -t learnify-backend .
```

This command builds the Docker image using the provided Dockerfile. The build process:
1. Installs system dependencies (rarely change - cached)
2. Installs Python dependencies (occasionally change - cached)
3. Copies application code (frequently changes - not cached)

The layer-based approach ensures fast rebuilds when code changes but dependencies don't.

### Test Locally with Environment Variables

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY="your-key" \
  -e MONGODB_URI="your-mongodb-uri" \
  -e RESEND_API_KEY="your-resend-key" \
  -e PORT=8000 \
  learnify-backend
```

Replace the environment variable values with your actual credentials.

### Using docker-compose for Easier Local Development

**Step 1: Prepare environment file**
```bash
cp api/.env.example .env
```

**Step 2: Edit .env with your credentials**

Open `.env` and fill in the required values:
```
GEMINI_API_KEY=your-key-here
MONGODB_URI=your-mongodb-uri-here
RESEND_API_KEY=your-resend-key-here
```

**Step 3: Start services**
```bash
docker-compose up
```

This starts both the backend and a local MongoDB instance. The services are connected via the `learnify-network` bridge network.

**Step 4: Monitor logs**
```bash
docker-compose logs -f backend
```

**Step 5: Stop services**
```bash
docker-compose down
```

### Verify the Backend is Running

Open your browser and test these endpoints:

1. **Root endpoint**: http://localhost:8000/
   - Should return a response from the FastAPI root handler

2. **Health check**: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

3. **API documentation**: http://localhost:8000/docs
   - Interactive Swagger UI with all available endpoints

4. **ReDoc documentation**: http://localhost:8000/redoc
   - Alternative API documentation format

## Render Deployment

### Step 1: Push Code to Git Repository

Ensure all files are committed to your Git repository:

```bash
git add Dockerfile .dockerignore docker-compose.yml DOCKER_DEPLOYMENT.md
git commit -m "Add Docker deployment configuration for Render"
git push origin main
```

Make sure you have:
- `Dockerfile` (for container building)
- `.dockerignore` (to optimize build context)
- Application code in `api/` and `backend/` directories
- `api/requirements.txt` (Python dependencies)
- `packages.txt` (system dependencies)

### Step 2: Create Web Service on Render

1. Go to **Render Dashboard** → **New** → **Web Service**
2. Connect your Git repository (GitHub, GitLab, or Bitbucket)
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `learnify-backend` (or your preferred name) |
| **Region** | Choose closest to your users |
| **Branch** | `main` (or your deployment branch) |
| **Runtime** | Docker |
| **Dockerfile Path** | `./Dockerfile` (default) |
| **Docker Build Context** | `.` (root directory) |

### Step 3: Configure Environment Variables

In the Render dashboard, navigate to **Environment** and add these variables:

| Variable | Value | Notes |
|----------|-------|-------|
| `GEMINI_API_KEY` | Your Google Gemini API key | From https://makersuite.google.com/app/apikey |
| `MONGODB_URI` | Your MongoDB connection string | Atlas or self-hosted MongoDB |
| `RESEND_API_KEY` | Your Resend API key | From https://resend.com/api-keys |
| `DEBUG_MODE` | `False` | Set to False for production |
| `COOKIE_ENCRYPTION_KEY` | Secure random string (32+ chars) | Generate with: `openssl rand -hex 16` |

**Important**: Do NOT set `PORT` - Render automatically injects this environment variable based on available resources.

### Step 4: Configure Service Settings

- **Instance Type**: Choose based on your needs (Free tier available)
- **Auto-Deploy**: Enable for automatic deployments on git push
- **Health Check Path**: `/health` (optional but recommended)
- **Health Check Protocol**: HTTP

### Step 5: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Build the Docker image using your Dockerfile
   - Deploy the container
   - Assign a URL (e.g., `https://learnify-backend.onrender.com`)

Monitor the build logs in the Render dashboard. The deployment typically takes 5-10 minutes.

## Render-Specific Optimizations

### Build Optimization

The Dockerfile is designed to maximize Docker layer caching:

1. **System dependencies** (least frequently changed)
   - Cached unless `packages.txt` changes
   
2. **Python dependencies** (occasionally changed)
   - Cached unless `api/requirements.txt` changes
   
3. **Application code** (frequently changed)
   - Always rebuilt when code changes
   - Minimal rebuild time due to cached layers above

Render caches these layers between builds, so subsequent deployments are significantly faster.

### Port Binding

- Render injects the `PORT` environment variable dynamically
- The Dockerfile CMD uses `${PORT:-8000}` for flexibility
- Always bind to `0.0.0.0`, not `localhost` or `127.0.0.1`
- The container must listen on the PORT provided by Render

### Health Checks

Configure health checks in Render dashboard:
- **Health Check Path**: `/health`
- **Health Check Protocol**: HTTP
- **Health Check Interval**: 30 seconds (default)
- **Health Check Timeout**: 5 seconds (default)

Render will automatically restart unhealthy containers. The FastAPI app in `api/main.py` already has a `/health` endpoint.

### Logging

- The Dockerfile sets `PYTHONUNBUFFERED=1` for real-time logging
- All stdout/stderr output is automatically collected by Render
- View logs in the Render dashboard under **Logs** tab
- Logs persist for 7 days on free tier, longer on paid tiers

## Deployment Verification

### Check Deployment Status

1. Open Render Dashboard
2. Monitor build logs
3. Wait for status indicator to show "Live"

### Test Deployed Backend

```bash
# Replace your-app with your actual Render service subdomain
curl https://your-app.onrender.com/health

# Expected response:
# {"status": "healthy"}
```

### Verify API Endpoints

Test these endpoints to verify deployment:

1. **Root**: `https://your-app.onrender.com/`
2. **Health**: `https://your-app.onrender.com/health`
3. **API Docs**: `https://your-app.onrender.com/docs`
4. **ReDoc**: `https://your-app.onrender.com/redoc`

If all endpoints respond correctly, your deployment is successful.

## Troubleshooting

### Build Failures

**Error: "Dockerfile not found"**
- Ensure `Dockerfile` is in the repository root
- Verify the filename case (Docker is case-sensitive on some systems)

**Error: "requirements.txt not found"**
- Verify `api/requirements.txt` exists
- Check the COPY command in Dockerfile matches actual path

**Error: "packages.txt or other file not found"**
- Verify all referenced files exist in repository
- Check file paths in COPY commands

**Build takes too long or times out**
- First build may take 15-30 minutes on free tier
- Ensure docker layers are being cached (each layer should show "CACHED")
- Consider upgrading to paid tier for faster builds

### Runtime Errors

**Error: "Connection refused" or "Unable to connect to MongoDB"**
- Verify `MONGODB_URI` environment variable is set correctly
- Check MongoDB Atlas connection string format
- Test connection locally first: `mongosh "mongodb://..."`

**Error: "GEMINI_API_KEY invalid" or API calls failing**
- Verify API key is correct and active
- Check if API quota exceeded
- Ensure API is enabled in Google Cloud project

**Error: Port already in use (port 8000)**
- Check if another service is running on port 8000
- Use `docker ps` to see running containers
- Stop conflicting container: `docker stop <container-id>`

**Error: "Application crashed" or "Health check failed"**
- Check application logs: `docker logs <container-id>`
- Verify all environment variables are set
- Test Docker image locally first
- Check for missing dependencies or import errors

### Port Binding Issues

**Error: "Cannot bind to address"**
- Verify CMD uses `0.0.0.0` not `localhost`
- Ensure `${PORT}` variable is being used
- Test locally: `docker run -p 8000:8000 -e PORT=8000 learnify-backend`

**Error: "Port X is not accessible"**
- Verify Render Port is correctly configured
- Check firewall settings
- Ensure application binds to the injected PORT

### Performance Issues

**Slow cold starts (first request after spin-down)**
- Normal on Render free tier (30-60 seconds)
- Can be mitigated with paid tier or uptime monitoring
- Use services like UptimeRobot to keep app warm

**High memory usage or CPU**
- Monitor resource usage in Render dashboard
- Consider upgrading instance type
- Check for memory leaks in application code
- Review database queries and optimize if needed

**Database connection issues**
- Monitor MongoDB Atlas connection pool
- Check network access list in MongoDB Atlas
- Verify MONGODB_URI environment variable
- Test connection with `mongosh` command

## Continuous Deployment

### Automatic Deployments

1. In Render Dashboard, go to **Settings** → **Deploy hooks**
2. Enable **"Auto-Deploy"** for your branch
3. Each `git push` to your deployment branch triggers automatic:
   - Docker image build
   - Deployment to Render
   - Service restart

**Best practice**: Use branch protection rules to prevent unreviewed code deployments.

### Manual Deployments

1. In Render Dashboard, click **Manual Deploy**
2. Select the branch/commit to deploy
3. Useful for:
   - Testing specific commits before merging to main
   - Rolling back to previous versions
   - Deploying hotfixes immediately

### Deployment Best Practices

- Always test changes locally with `docker build` and `docker-compose up`
- Use semantic versioning for releases
- Tag releases in Git: `git tag v1.0.0 && git push --tags`
- Document changes in commit messages
- Keep main branch stable and deployable

## Cost Optimization

### Free Tier Considerations

The Render free tier is suitable for development and testing:

- **Cold starts**: Service spins down after 15 minutes of inactivity
- **Startup time**: First request takes 30-60 seconds after spin-down
- **Instance size**: Shared CPU, limited memory
- **Monthly hours**: Limited free compute hours

**Workarounds for free tier**:
- Use UptimeRobot (free) to ping `/health` every 5 minutes
- Schedule production traffic during free tier active hours
- Consider paid tier for production deployments

### Paid Tier Benefits

- No cold starts
- Dedicated CPU and memory
- Higher availability SLA
- More compute hours per month

### Image Size Optimization

The Dockerfile is already optimized:

- Uses `python:3.11-slim` instead of full Python image (saves ~600MB)
- `.dockerignore` excludes unnecessary files
- Multi-stage build not needed but could be enhanced further
- Removes apt cache after installation

Current optimizations reduce build time and deployment speed significantly.

## Security Best Practices

### Environment Variables

- **Never commit .env files** to Git (already in .gitignore)
- Use Render's built-in environment variable management
- Rotate API keys regularly (monthly recommended)
- Use `.env.example` as a template without secrets
- Audit who has access to environment variables

### Secrets Management

- Store sensitive data in environment variables only
- Consider using Secret Manager for enhanced security
- Restrict access to production environment variables
- Use separate credentials for development vs. production

### CORS Configuration

The app in `api/main.py` uses CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production recommendation**: Replace `["*"]` with specific allowed origins:
```python
allow_origins=[
    "https://your-domain.com",
    "https://www.your-domain.com",
]
```

### HTTPS

- Render provides free SSL certificates automatically
- All traffic is encrypted by default
- HTTPS is required for authentication cookies
- No manual configuration needed

### Container Security

- Keep Python and system dependencies updated
- Review installed packages regularly
- Use specific versions (not latest/wildcard) for dependencies
- Run security scans on Docker images: `docker scan learnify-backend`

## Monitoring and Maintenance

### Health Monitoring

Set up uptime monitoring to keep your service running:

1. **Use UptimeRobot (free)**:
   - Create account at https://uptimerobot.com
   - Add monitor for `https://your-app.onrender.com/health`
   - Set check interval to 5 minutes
   - Get alerts if service goes down

2. **Use Render's built-in health checks**:
   - Configured to `/health` endpoint
   - Automatic restarts on failure
   - View health history in dashboard

### Log Monitoring

**Local logging**:
```bash
docker-compose logs -f backend
```

**Render logging**:
- View in Render Dashboard → **Logs** tab
- Logs persist for 7 days on free tier
- Download logs for long-term storage if needed

**Production logging setup**:
- Consider log aggregation services (Papertrail, Loggly, Datadog)
- Set up alerts for error rates
- Monitor specific endpoints or error patterns

### Performance Monitoring

1. **In Render Dashboard**:
   - Monitor CPU usage
   - Monitor memory usage
   - Check response times
   - Review error rates

2. **Application metrics**:
   - Add APM tool like New Relic (configured in `newrelic.ini`)
   - Monitor database query performance
   - Track API response times

3. **Database monitoring**:
   - Monitor MongoDB Atlas metrics
   - Check connection pool utilization
   - Review slow query logs

### Updates and Maintenance

**Dependency updates**:
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > api/requirements.txt
```

**Testing updates**:
1. Update locally in `api/requirements.txt`
2. Test with `docker build` and `docker-compose up`
3. Verify all tests pass
4. Commit and deploy to Render

**Version management**:
- Use semantic versioning for releases
- Tag releases in Git
- Keep changelog of updates
- Test updates thoroughly before production

**Scheduled maintenance**:
- Plan maintenance windows during off-peak hours
- Communicate downtime to users if needed
- Test rollback procedures
- Keep backups of database

### Monitoring Checklist

Regular maintenance tasks:

- [ ] Review Render logs weekly
- [ ] Check error rates daily
- [ ] Monitor database size monthly
- [ ] Update dependencies monthly
- [ ] Review security updates immediately
- [ ] Test backup/restore procedures quarterly
- [ ] Audit access logs monthly
- [ ] Review cost trends monthly

## Additional Resources

- **Render Docker Documentation**: https://render.com/docs/docker
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Docker Documentation**: https://docs.docker.com/
- **MongoDB Atlas Documentation**: https://docs.atlas.mongodb.com/
- **Google Gemini API**: https://makersuite.google.com/app/apikey
- **Resend Email API**: https://resend.com/docs

## Support

For issues or questions:

1. Check Render's status page: https://status.render.com/
2. Review Render documentation: https://render.com/docs/
3. Check application logs in Render Dashboard
4. Test locally with Docker first before deploying
5. Verify environment variables are correctly configured

---

**Last Updated**: October 27, 2025
**Docker Version**: 3.8
**Python Version**: 3.11-slim
**Render Runtime**: Docker
