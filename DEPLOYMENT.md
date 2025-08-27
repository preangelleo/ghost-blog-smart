# Ghost Blog Smart API - Deployment Guide

This guide covers deploying the Ghost Blog Smart API using Docker and GitHub Actions.

## 🚀 Quick Deployment

### Option 1: Docker Hub (Recommended)

```bash
# Pull the pre-built image
docker pull betashow/ghost-blog-smart-api:latest

# Run with your credentials
docker run -d \
  -p 5000:5000 \
  -e GHOST_ADMIN_API_KEY="your_key_id:your_secret_key" \
  -e GHOST_API_URL="https://your-ghost-site.com" \
  -e GEMINI_API_KEY="your_gemini_key" \
  -e REPLICATE_API_TOKEN="r8_your_replicate_token" \
  -e FLASK_API_KEY="your_secure_api_key" \
  --name ghost-blog-api \
  betashow/ghost-blog-smart-api:latest

# Test the deployment
curl http://localhost:5000/health
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ghost-blog-smart-api:
    image: betashow/ghost-blog-smart-api:latest
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - GHOST_ADMIN_API_KEY=${GHOST_ADMIN_API_KEY}
      - GHOST_API_URL=${GHOST_API_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
      - FLASK_API_KEY=${FLASK_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:

```bash
docker-compose up -d
```

## 🛠️ Local Development & Testing

### 1. Clone and Setup

```bash
git clone https://github.com/preangelleo/ghost_blog_smart.git
cd ghost_blog_smart

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt
pip install -e .
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:

```bash
# Ghost CMS
GHOST_ADMIN_API_KEY=your_key_id:your_secret_key
GHOST_API_URL=https://your-ghost-site.com

# AI Services
GEMINI_API_KEY=your_gemini_key
REPLICATE_API_TOKEN=r8_your_replicate_token

# API Security (optional)
FLASK_API_KEY=your_secure_api_key

# Development
FLASK_ENV=development
FLASK_DEBUG=true
PORT=5000
```

### 3. Test the Setup

```bash
# Test Python library functions
python test_credentials.py

# Run the Flask API
python app.py

# Test API endpoints
curl http://localhost:5000/health
curl -H "X-API-Key: your_api_key" http://localhost:5000/api/posts?limit=2
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=ghost_blog_smart --cov=app --cov-report=html
```

## 🏗️ Building from Source

### Local Docker Build

```bash
# Build the image
docker build -t ghost-blog-smart-api:local .

# Test the local build
docker run -d \
  -p 5000:5000 \
  -e GHOST_ADMIN_API_KEY="your_key" \
  -e GHOST_API_URL="https://your-site.com" \
  -e FLASK_API_KEY="test_key" \
  --name ghost-api-test \
  ghost-blog-smart-api:local

# Test
curl http://localhost:5000/health
docker stop ghost-api-test && docker rm ghost-api-test
```

## 🚢 GitHub Actions Deployment

The project includes automated CI/CD with GitHub Actions that:

1. **Tests** - Runs comprehensive tests on Python 3.9, 3.10, 3.11
2. **Security Scan** - Checks for vulnerabilities with safety and bandit
3. **Docker Build** - Builds multi-platform Docker images (amd64, arm64)
4. **Publish** - Pushes to Docker Hub automatically
5. **Deploy** - Can deploy to staging/production environments

### Required GitHub Secrets

Set these in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

```bash
DOCKER_ACCESS_TOKEN=your_docker_hub_token
```

Optional secrets for enhanced functionality:

```bash
CODECOV_TOKEN=your_codecov_token  # For coverage reporting
```

### Manual Deployment Trigger

You can manually trigger deployments by:

1. **Push to `main`** - Builds and tags as `latest`
2. **Push to `develop`** - Builds and deploys to staging
3. **Create tag `v*`** - Creates production release

```bash
# Create a production release
git tag v1.0.0
git push origin v1.0.0
```

## 🌐 Production Deployment

### AWS ECS/Fargate

```yaml
# task-definition.json
{
  "family": "ghost-blog-smart-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "ghost-blog-smart-api",
      "image": "betashow/ghost-blog-smart-api:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "GHOST_ADMIN_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:ghost-api-key"
        },
        {
          "name": "FLASK_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:flask-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ghost-blog-smart-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy ghost-blog-smart-api \
  --image=betashow/ghost-blog-smart-api:latest \
  --platform=managed \
  --region=us-central1 \
  --set-env-vars="FLASK_ENV=production" \
  --set-secrets="GHOST_ADMIN_API_KEY=ghost-api-key:latest,FLASK_API_KEY=flask-api-key:latest" \
  --port=5000 \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --allow-unauthenticated
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ghost-blog-smart-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ghost-blog-smart-api
  template:
    metadata:
      labels:
        app: ghost-blog-smart-api
    spec:
      containers:
      - name: ghost-blog-smart-api
        image: betashow/ghost-blog-smart-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: PORT
          value: "5000"
        envFrom:
        - secretRef:
            name: ghost-blog-smart-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ghost-blog-smart-api-service
spec:
  selector:
    app: ghost-blog-smart-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GHOST_ADMIN_API_KEY` | ✅ | Ghost Admin API key | `key_id:secret_key` |
| `GHOST_API_URL` | ✅ | Ghost site URL | `https://your-site.com` |
| `GEMINI_API_KEY` | ⚠️ | Google Gemini API key | `AIza...` |
| `REPLICATE_API_TOKEN` | ⚠️ | Replicate API token | `r8_...` |
| `FLASK_API_KEY` | ❌ | API authentication key | `secure_random_key` |
| `FLASK_ENV` | ❌ | Environment mode | `production` |
| `PORT` | ❌ | Server port | `5000` |

⚠️ = Required for AI features
❌ = Optional

### Health Checks

The API provides comprehensive health checking:

```bash
# Basic health check
curl http://localhost:5000/health

# Expected response
{
  "success": true,
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "status": "healthy",
    "uptime": "running",
    "features": {
      "ghost_integration": true,
      "ai_enhancement": true,
      "image_generation": true
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use**
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   
   # Use different port
   PORT=8080 python app.py
   ```

2. **Ghost API connection failed**
   ```bash
   # Test Ghost API key manually
   curl -H "Authorization: Ghost your_admin_api_key" \
        https://your-site.com/ghost/api/admin/posts/
   ```

3. **Docker build fails**
   ```bash
   # Check Docker daemon
   docker info
   
   # Build with verbose output
   docker build --progress=plain -t ghost-blog-smart-api:debug .
   ```

4. **API authentication issues**
   ```bash
   # Test without authentication
   curl http://localhost:5000/health
   
   # Test with authentication
   curl -H "X-API-Key: your_key" http://localhost:5000/api/posts
   ```

### Logs and Debugging

```bash
# View container logs
docker logs ghost-blog-api

# Follow logs in real-time
docker logs -f ghost-blog-api

# Debug mode
FLASK_DEBUG=true python app.py
```

## 📊 Monitoring

### Prometheus Metrics (Optional)

Add metrics collection by installing prometheus client:

```bash
pip install prometheus-client
```

### Performance Monitoring

The API includes built-in request timing and error tracking. For production, consider:

- Application Performance Monitoring (APM)
- Log aggregation (ELK stack, Fluentd)
- Health check monitoring
- Resource usage alerts

## 🔐 Security Considerations

1. **API Keys**: Use strong, unique API keys
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Consider adding rate limiting for production use
4. **Secrets Management**: Use proper secret management (AWS Secrets Manager, etc.)
5. **Network Security**: Restrict network access as needed
6. **Regular Updates**: Keep dependencies updated

---

## 📞 Support

For issues or questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review GitHub Issues
3. Check API logs for detailed error messages
4. Test with minimal configuration first