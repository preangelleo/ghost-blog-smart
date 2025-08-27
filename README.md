# Ghost Blog Smart

🚀 **A comprehensive solution for Ghost CMS blog management with AI-powered features**

Available as both a **Python Package** and **REST API** with multiple deployment options including Docker, local installation, and PyPI package.

[![PyPI version](https://badge.fury.io/py/ghost-blog-smart.svg)](https://badge.fury.io/py/ghost-blog-smart)
[![Docker Hub](https://img.shields.io/docker/pulls/betashow/ghost-blog-smart-api.svg)](https://hub.docker.com/r/betashow/ghost-blog-smart-api)
[![GitHub Actions](https://github.com/preangelleo/ghost-blog-smart/workflows/Build%20and%20Deploy%20Ghost%20Blog%20Smart%20API/badge.svg)](https://github.com/preangelleo/ghost-blog-smart/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 🎯 **Choose Your Setup Method**

| Method | Best For | Example Files | Documentation Section |
|--------|----------|---------------|----------------------|
| **🐳 Docker API** | Production deployment, quick testing | `example_usage_API.js` | [Docker Deployment](#-docker-deployment) |
| **🐍 Python Package** | Python developers, scripting | `example_usage.py` | [Python Package](#-python-package-usage) |
| **🌐 Local API** | Development, customization | `example_usage_API.js` | [Local API Setup](#-local-api-development) |
| **📦 PyPI Install** | Simple Python integration | `example_usage.py` | [PyPI Installation](#-pypi-installation) |

## 📖 **Table of Contents**

### 🚀 **Getting Started**
- [🎯 Choose Your Setup Method](#-choose-your-setup-method)
- [🐳 Docker Deployment](#-docker-deployment)
- [🐍 Python Package Usage](#-python-package-usage)
- [📦 PyPI Installation](#-pypi-installation)
- [🌐 Local API Development](#-local-api-development)

### 📚 **Usage Examples**
- [💻 Python Examples (example_usage.py)](#-python-examples-example_usagepy)
- [🌐 Node.js API Examples (example_usage_API.js)](#-nodejs-api-examples-example_usage_apijs)

### 📖 **Documentation**
- [✨ Features](#-features)
- [🔧 REST API Reference](#-rest-api-reference)
- [⏱️ Performance & Timeout Guidelines](#️-performance--timeout-guidelines)
- [🧪 Testing](#-testing)

---

## 🐳 **Docker Deployment**

> **Recommended for:** Production environments, quick testing, isolation
> 
> **Example File:** `example_usage_API.js` (Node.js client for REST API)

### Quick Start
```bash
# Pull and run the pre-built Docker image
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

# Test the API
curl http://localhost:5000/health
```

### Docker Compose
```yaml
version: '3.8'
services:
  ghost-blog-smart-api:
    image: betashow/ghost-blog-smart-api:latest
    ports:
      - "5000:5000"
    environment:
      - GHOST_ADMIN_API_KEY=your_key_id:your_secret_key
      - GHOST_API_URL=https://your-ghost-site.com
      - GEMINI_API_KEY=your_gemini_key
      - REPLICATE_API_TOKEN=r8_your_replicate_token
      - FLASK_API_KEY=your_secure_api_key
```

**Next Steps:**
- Use `example_usage_API.js` for Node.js integration
- Follow [Node.js API Examples](#-nodejs-api-examples-example_usage_apijs) section

---

## 🐍 **Python Package Usage**

> **Recommended for:** Python developers, scripting, direct integration
>
> **Example File:** `example_usage.py` (Pure Python usage)

### Installation
```bash
pip install ghost-blog-smart
```

### Basic Usage
```python
from ghost_blog_smart import smart_blog_gateway

# Smart Gateway Method (Recommended)
result = smart_blog_gateway(
    "AI healthcare benefits: faster diagnosis, better accuracy, cost reduction",
    status="published"
)

if result['success']:
    print(f"Post created: {result['url']}")
```

**Next Steps:**
- Follow examples in `example_usage.py`
- See [Python Examples](#-python-examples-example_usagepy) section

---

## 📦 **PyPI Installation**

> **Recommended for:** Simple Python projects, minimal setup

```bash
# Install from PyPI
pip install ghost-blog-smart

# Use directly in your Python code
from ghost_blog_smart import create_ghost_blog_post, smart_blog_gateway
```

Create `.env` file with your credentials:
```env
GHOST_ADMIN_API_KEY=your_admin_api_key_id:your_secret_key_here
GHOST_API_URL=https://your-ghost-site.com
GEMINI_API_KEY=your_gemini_api_key_here
REPLICATE_API_TOKEN=r8_your_replicate_api_token_here
```

---

## 🌐 **Local API Development**

> **Recommended for:** Development, customization, testing
>
> **Example Files:** `example_usage_API.js` (Node.js client) + Local Flask API

### Setup
```bash
# Clone the repository
git clone https://github.com/preangelleo/ghost_blog_smart.git
cd ghost_blog_smart

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the Flask API
python app.py
```

**API runs on:** `http://localhost:5000`

**Next Steps:**
- Use `example_usage_API.js` to test your local API
- Follow [Node.js API Examples](#-nodejs-api-examples-example_usage_apijs) section

---

## 💻 **Python Examples (example_usage.py)**

**For:** Python Package usage, PyPI installation, direct Python integration

### Key Examples from `example_usage.py`:

#### Smart Gateway (AI-Enhanced Creation)
```python
from ghost_blog_smart import smart_blog_gateway

result = smart_blog_gateway(
    "Write about AI benefits in healthcare: faster diagnosis, better accuracy",
    status="published",
    preferred_language="English"
)
```

#### Traditional Method
```python
from ghost_blog_smart import create_ghost_blog_post

result = create_ghost_blog_post(
    title="My Blog Post",
    content="Post content in **Markdown**",
    excerpt="Brief summary",
    tags=["Tutorial", "AI"],
    status="published",
    use_generated_feature_image=True,
    prefer_flux=True
)
```

#### Blog Management
```python
from ghost_blog_smart import get_ghost_posts, update_ghost_post, delete_ghost_post

# Get posts
posts = get_ghost_posts(limit=5, status='published')

# Update post
update_ghost_post(post_id="abc123", featured=True)

# Delete post
delete_ghost_post(post_id="abc123")
```

**📁 Complete examples available in:** [`example_usage.py`](./example_usage.py)

---

## 🌐 **Node.js API Examples (example_usage_API.js)**

**For:** Docker deployment, local API server, REST API integration

### Prerequisites
```bash
npm install axios  # HTTP client for API calls
```

### Key Examples from `example_usage_API.js`:

#### Configuration
```javascript
const CONFIG = {
    baseUrl: 'http://localhost:5000',
    apiKey: 'your_secure_api_key',
    timeout: 300000, // 5 minutes for image generation
    imageTimeout: 300000, // Extended timeout for image endpoints
    standardTimeout: 30000, // Standard timeout for other endpoints
};
```

#### Create Blog Post via API
```javascript
const postData = {
    title: "My API Blog Post",
    content: "Post content in **Markdown**",
    excerpt: "Brief summary",
    tags: ["API", "Node.js"],
    status: "published",
    use_generated_feature_image: true,
    prefer_flux: true,
    image_aspect_ratio: "16:9"
};

const response = await api.post('/api/posts', postData);
```

#### Smart Create via API
```javascript
const smartData = {
    user_input: "Write about JavaScript testing frameworks: Jest vs Mocha vs Cypress",
    status: "draft",
    preferred_language: "English"
};

const response = await api.post('/api/smart-create', smartData);
```

#### Running Tests
```bash
# Run all endpoint tests
node example_usage_API.js

# Run specific test
node example_usage_API.js health

# Run with custom timeout (5 minutes for image generation)
node example_usage_API.js --timeout 300000

# Production mode (creates real posts)
node example_usage_API.js --production
```

**📁 Complete examples available in:** [`example_usage_API.js`](./example_usage_API.js)

---

## ✨ **Features**

### 🤖 **Smart AI Gateway**
- **Intelligent Routing** - Automatically determines if content needs rewriting
- **Structured Output** - Uses Gemini's structured output for consistent formatting
- **Function Calling** - Leverages Gemini function calling for smart decision making
- **Auto Enhancement** - Transforms scattered ideas into complete blog posts
- **Missing Component Detection** - Automatically generates titles, excerpts, and tags

### 🎨 **Dual AI Image Generation**
- **🔥 Replicate Flux-dev**: Ultra-fast generation (3-7 seconds), photorealistic images, WebP format
- **🏔️ Google Imagen-4**: Professional quality, advanced prompt understanding, PNG format
- **Automatic Fallback System**: Intelligent provider switching for maximum reliability
- **Provider Selection**: Choose your preferred provider or let the system decide
- **Multiple Aspect Ratios**: 16:9, 1:1, 9:16, 4:3, 3:2 support

### 📝 **Content Management**
- **Smart Content Formatting** - Auto-format plain text to beautiful Markdown with Gemini AI
- **YouTube-Style Slugs** - Generate 11-character slugs like YouTube video IDs
- **Multi-language Support** - Chinese to Pinyin conversion for slugs
- **Language Translation** - Auto-translate content to any target language
- **Flexible Image Handling** - Support for URLs, local files, base64 data

### 📊 **Blog Management**
- **Advanced Listing** - Get posts with powerful filtering options
- **Search & Query** - Full-text search across all posts
- **Date Range Filtering** - Find posts by publication/creation date
- **Update & Delete** - Modify or remove posts with comprehensive options
- **Batch Operations** - Process multiple posts efficiently
- **Detailed Analytics** - Get complete post details and summaries

---

## 🔧 **REST API Reference**

### **Base URL Structure**
```
http://localhost:5000/          # API information
http://localhost:5000/health    # Health check
http://localhost:5000/api/      # All blog endpoints
```

### **Authentication**
All API endpoints (except `/` and `/health`) require authentication:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:5000/api/posts
```

### **Standard Response Format**
```json
{
  "success": true,
  "timestamp": "2024-01-01T00:00:00.000000Z",
  "data": {
    // Response data here
  }
}
```

### **⚠️ TIMEOUT CONFIGURATION NOTICE**
- **Image Generation Endpoints**: `/api/posts` (with `use_generated_feature_image: true`) and `/api/posts/{id}/image` require extended timeouts
- **Recommended Client Timeout**: **5 minutes (300 seconds)** minimum
- **Typical Response Times**: 60-300 seconds for image generation
- **Without Images**: Standard 30-second timeout is sufficient

### **📝 Core Endpoints**

#### Create Blog Post ⚠️ **Extended Timeout for Images**
```bash
POST /api/posts
Content-Type: application/json
X-API-Key: your_api_key

{
  "title": "My Blog Post",
  "content": "Post content in **Markdown**",
  "excerpt": "Brief summary",
  "tags": ["Tag1", "Tag2"],
  "status": "published",
  "use_generated_feature_image": true,
  "prefer_flux": true,
  "image_aspect_ratio": "16:9"
}
```

**⏱️ Important:** When `use_generated_feature_image: true` is used, generation can take 60-300 seconds. Set client timeout to at least **5 minutes (300 seconds)**.

#### Smart Create (AI-Enhanced)
```bash
POST /api/smart-create
Content-Type: application/json
X-API-Key: your_api_key

{
  "user_input": "Write about AI benefits in healthcare",
  "status": "draft",
  "preferred_language": "English"
}
```

#### Get Posts
```bash
GET /api/posts?limit=5&status=published&featured=true
X-API-Key: your_api_key
```

#### Update Post Image ⚠️ **High Timeout Required**
```bash
PUT /api/posts/{post_id}/image
Content-Type: application/json
X-API-Key: your_api_key

{
  "use_generated_feature_image": true,
  "prefer_imagen": true,
  "image_aspect_ratio": "16:9"
}
```

**⏱️ Important:** Image generation endpoints can take 60-300 seconds to complete. Set client timeout to at least **5 minutes (300 seconds)** for reliable operation.

### **📋 Complete Endpoint List**

| Endpoint | Method | Description | Auth Required | Timeout |
|----------|--------|-------------|---------------|---------|
| `/` | GET | API information | ❌ | Standard |
| `/health` | GET | Health check | ❌ | Standard |
| `/api/posts` | POST | Create blog post | ✅ | **Extended*** |
| `/api/smart-create` | POST | AI-enhanced creation | ✅ | Standard |
| `/api/posts` | GET | List posts | ✅ | Standard |
| `/api/posts/advanced` | GET | Advanced search | ✅ | Standard |
| `/api/posts/{id}` | GET | Get post details | ✅ | Standard |
| `/api/posts/{id}` | PUT/PATCH | Update post | ✅ | Standard |
| `/api/posts/{id}` | DELETE | Delete post | ✅ | Standard |
| `/api/posts/{id}/image` | PUT | Update post image | ✅ | **Extended*** |
| `/api/posts/summary` | GET | Posts summary | ✅ | Standard |
| `/api/posts/batch-details` | POST | Batch get details | ✅ | Standard |
| `/api/posts/search/by-date-pattern` | GET | Date search | ✅ | Standard |

**\*Extended = 5 minutes (300 seconds) for image generation**

---

## ⏱️ **Performance & Timeout Guidelines**

### **Image Generation Performance**
- **Replicate Flux**: 3-7 seconds (ultra-fast)
- **Google Imagen**: 10-15 seconds (professional quality)
- **Upload & Processing**: Additional 45-60 seconds
- **Total Time**: 60-300 seconds for complete image generation

### **Recommended Client Timeouts**
```javascript
// For endpoints WITH image generation
const imageApiTimeout = 300000; // 5 minutes

// For endpoints WITHOUT image generation  
const standardTimeout = 30000; // 30 seconds
```

### **Production Testing Results**
✅ **All endpoints functional**  
⚠️ **Image generation requires extended timeout**  
💡 **Recommendation**: Always set 5-minute timeout for image endpoints

---

## 🧪 **Testing**

### **Python Package Testing**
```bash
# Set test mode to avoid actual posting
python example_usage.py  # Uses is_test=True by default
```

### **API Testing (Docker/Local)**
```bash
# Comprehensive test suite
node example_usage_API.js

# Individual endpoint tests
node example_usage_API.js health
node example_usage_API.js create
node example_usage_API.js smart

# Production mode (creates real posts)
node example_usage_API.js --production

# Extended timeout for image generation
node example_usage_API.js --timeout 300000
```

### **Docker Testing Guide**
See [`TESTING_GUIDE.md`](./TESTING_GUIDE.md) for comprehensive Docker testing instructions.

---

## 📁 **Project Structure**

```
ghost-blog-smart/
├── ghost_blog_smart/             # Main Python package
│   ├── __init__.py              # Package exports
│   ├── main_functions.py        # Core API functions
│   ├── smart_gateway.py         # AI-powered routing
│   ├── post_management.py       # Advanced management
│   └── *.py                    # Other modules
├── example_usage.py             # 🐍 Python package examples
├── example_usage_API.js         # 🌐 Node.js API client examples  
├── app.py                       # 🚀 Flask REST API server
├── Dockerfile                   # 🐳 Docker configuration
├── docker-compose.yml          # 🐳 Docker Compose setup
├── requirements.txt             # Python dependencies
├── setup.py                    # PyPI package setup
├── TESTING_GUIDE.md            # 🧪 Docker testing instructions
└── README.md                   # 📖 This documentation
```

---

## 🎨 **Image Generation Comparison**

| Feature | Replicate Flux-dev | Google Imagen-4 |
|---------|-------------------|-----------------| 
| **Speed** | ⚡ Ultra-fast (3-7s) | 🐢 Moderate (10-15s) |
| **Quality** | 🔥 Photorealistic | 🏔️ Professional |
| **Format** | 📁 WebP (smaller) | 📁 PNG (lossless) |
| **Cost** | 💰 Pay-per-use | 💰 API quota based |
| **Best For** | Realistic scenes, portraits | Abstract concepts, artistic |

**Supported Aspect Ratios:**
- `16:9` - Widescreen (1920x1080) - **Default**
- `1:1` - Square (1024x1024) - Great for social media
- `9:16` - Portrait (1080x1920) - Mobile-optimized
- `4:3` - Traditional (1024x768) - Classic photo ratio
- `3:2` - DSLR (1536x1024) - Professional photography

---

## 📋 **Prerequisites**

- Python 3.8+
- Ghost CMS instance with Admin API access
- **Image Generation** (choose one or both):
  - Google Gemini API key (for Imagen-4 generation)
  - Replicate API token (for Flux-dev generation)

---

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 **License**

MIT License - see LICENSE file for details

---

## 🙏 **Acknowledgments**

- Ghost CMS for the excellent blogging platform
- Google Gemini & Imagen for AI capabilities  
- Replicate for ultra-fast Flux generation
- The open-source community

---

## 📞 **Support**

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ for the Ghost CMS community**

✨ **Available as both Python Package and REST API with comprehensive Docker support!**
<!-- Docker Hub sync: Wed Aug 27 17:55:51 JST 2025 -->
