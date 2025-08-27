#!/bin/bash
# Ghost Blog Smart API - Docker Build and Deploy Script
# This script builds and publishes the Docker image to Docker Hub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_USERNAME="betashow"
IMAGE_NAME="ghost-blog-smart-api"
REGISTRY="$DOCKER_USERNAME/$IMAGE_NAME"

echo -e "${BLUE}🚀 Ghost Blog Smart API - Docker Deployment${NC}"
echo "=================================================="

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available and running${NC}"

# Clean up any credential files (SECURITY: Never include credentials in image)
echo -e "${YELLOW}🧹 Cleaning up credential files...${NC}"
rm -f .env .env.test .env.production test_credentials.py comprehensive_test.py

# Get version from setup.py or use 'latest'
VERSION=$(python -c "
try:
    import re
    with open('setup.py', 'r') as f:
        content = f.read()
    match = re.search(r'version=[\'\"](.*?)[\'\"]', content)
    print(match.group(1) if match else 'latest')
except:
    print('latest')
")

echo -e "${BLUE}📦 Building Docker image (version: $VERSION)...${NC}"

# Build the image
docker build \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VCS_REF="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
    -t "$REGISTRY:latest" \
    -t "$REGISTRY:$VERSION" \
    .

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Test the image locally
echo -e "${BLUE}🧪 Testing Docker image locally...${NC}"
CONTAINER_ID=$(docker run -d \
    -p 5001:5000 \
    -e FLASK_ENV=production \
    -e IS_TEST_MODE=true \
    "$REGISTRY:latest")

sleep 5

# Test health endpoint
if curl -f -s http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✅ Docker image test successful${NC}"
else
    echo -e "${RED}❌ Docker image test failed${NC}"
    docker logs "$CONTAINER_ID"
    exit 1
fi

# Stop test container
docker stop "$CONTAINER_ID" > /dev/null
docker rm "$CONTAINER_ID" > /dev/null

# Ask for confirmation to push to Docker Hub
echo ""
read -p "$(echo -e ${YELLOW}🚢 Push to Docker Hub? [y/N]: ${NC})" -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏹️  Build completed, but not pushed to Docker Hub${NC}"
    echo "   Local image available as: $REGISTRY:latest"
    exit 0
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Registry: https://index.docker.io/v1/"; then
    echo -e "${YELLOW}🔑 Please log in to Docker Hub:${NC}"
    docker login
fi

# Push to Docker Hub
echo -e "${BLUE}🚢 Pushing to Docker Hub...${NC}"
docker push "$REGISTRY:latest"

if [ "$VERSION" != "latest" ]; then
    docker push "$REGISTRY:$VERSION"
    echo -e "${GREEN}✅ Pushed both 'latest' and '$VERSION' tags${NC}"
else
    echo -e "${GREEN}✅ Pushed 'latest' tag${NC}"
fi

# Display usage instructions
echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo "=================================================="
echo -e "${BLUE}Docker Hub:${NC} https://hub.docker.com/r/$REGISTRY"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo "docker pull $REGISTRY:latest"
echo ""
echo "docker run -d \\"
echo "  -p 5000:5000 \\"
echo "  -e GHOST_ADMIN_API_KEY=\"your_key_id:your_secret_key\" \\"
echo "  -e GHOST_API_URL=\"https://your-ghost-site.com\" \\"
echo "  -e GEMINI_API_KEY=\"your_gemini_key\" \\"
echo "  -e REPLICATE_API_TOKEN=\"r8_your_replicate_token\" \\"
echo "  -e FLASK_API_KEY=\"your_secure_api_key\" \\"
echo "  --name ghost-blog-api \\"
echo "  $REGISTRY:latest"
echo ""
echo -e "${GREEN}✨ Ready for production use!${NC}"