# Ghost Blog Smart API

🚀 A powerful Python library and REST API for creating and managing Ghost CMS blog posts with AI-powered features including automatic image generation, content formatting, and comprehensive blog management.

[![Docker Hub](https://img.shields.io/docker/pulls/betashow/ghost-blog-smart-api.svg)](https://hub.docker.com/r/betashow/ghost-blog-smart-api)
[![GitHub Actions](https://github.com/preangelleo/ghost-blog-smart/workflows/Build%20and%20Deploy%20Ghost%20Blog%20Smart%20API/badge.svg)](https://github.com/preangelleo/ghost-blog-smart/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📖 Table of Contents

- [🐍 Python Library Usage](#-python-library-usage)
- [🌐 REST API Usage](#-rest-api-usage)
- [🚀 Quick Start (Docker)](#-quick-start-docker)
- [🔧 Installation](#-installation)
- [✨ Features](#-features)
- [🧪 Testing](#-testing)

## 🚀 Quick Start (Docker)

The fastest way to get started is using Docker:

```bash
# Pull and run the pre-built Docker image
docker pull betashow/ghost-blog-smart-api:latest

# Run with your Ghost credentials
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

Or use Docker Compose:

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

## 🔧 Installation

### Python Library

```bash
pip install ghost-blog-smart
```

### REST API (Local Development)

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

## 🌐 REST API Usage

The Ghost Blog Smart API provides a complete REST interface for all library functions.

### Authentication

All API endpoints (except `/` and `/health`) require authentication via API key:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:5000/api/posts
```

### Base URL Structure

```
http://localhost:5000/          # API information
http://localhost:5000/health    # Health check
http://localhost:5000/api/      # All blog endpoints
```

### Standard Response Format

All API responses follow this standard format:

```json
{
  "success": true,
  "timestamp": "2024-01-01T00:00:00.000000Z",
  "data": {
    // Response data here
  }
}
```

For errors:

```json
{
  "success": false,
  "timestamp": "2024-01-01T00:00:00.000000Z",
  "error": "Error type",
  "message": "Detailed error message"
}
```

### 📝 Blog Creation Endpoints

#### Create Blog Post
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

### 📋 Blog Retrieval Endpoints

#### Get Posts
```bash
GET /api/posts?limit=5&status=published&featured=true
X-API-Key: your_api_key
```

#### Advanced Post Search
```bash
GET /api/posts/advanced?search=AI&tag=technology&limit=10&published_after=2024-01-01
X-API-Key: your_api_key
```

#### Get Specific Post
```bash
GET /api/posts/{post_id}
X-API-Key: your_api_key
```

#### Posts Summary
```bash
GET /api/posts/summary?days=30
X-API-Key: your_api_key
```

### ✏️ Blog Update Endpoints

#### Update Post
```bash
PUT /api/posts/{post_id}
Content-Type: application/json
X-API-Key: your_api_key

{
  "title": "Updated Title",
  "featured": true,
  "tags": ["Updated", "Featured"]
}
```

#### Update Post Image
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

### 🗑️ Blog Deletion Endpoints

#### Delete Post
```bash
DELETE /api/posts/{post_id}
X-API-Key: your_api_key
```

### 📊 Batch Operations

#### Batch Get Post Details
```bash
POST /api/posts/batch-details
Content-Type: application/json
X-API-Key: your_api_key

{
  "post_ids": ["post_id_1", "post_id_2", "post_id_3"]
}
```

#### Search by Date Pattern
```bash
GET /api/posts/search/by-date-pattern?pattern=2024-01&limit=10
X-API-Key: your_api_key
```

### 🔍 Complete API Reference

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | API information | ❌ |
| `/health` | GET | Health check | ❌ |
| `/api/posts` | POST | Create blog post | ✅ |
| `/api/smart-create` | POST | AI-enhanced creation | ✅ |
| `/api/posts` | GET | List posts | ✅ |
| `/api/posts/advanced` | GET | Advanced search | ✅ |
| `/api/posts/{id}` | GET | Get post details | ✅ |
| `/api/posts/{id}` | PUT/PATCH | Update post | ✅ |
| `/api/posts/{id}` | DELETE | Delete post | ✅ |
| `/api/posts/{id}/image` | PUT | Update post image | ✅ |
| `/api/posts/summary` | GET | Posts summary | ✅ |
| `/api/posts/batch-details` | POST | Batch get details | ✅ |
| `/api/posts/search/by-date-pattern` | GET | Date search | ✅ |

### 🔧 Configuration Headers

You can provide credentials via headers instead of environment variables:

```bash
curl -H "X-API-Key: your_api_key" \
     -H "X-Ghost-API-Key: your_ghost_key" \
     -H "X-Ghost-API-URL: https://your-site.com" \
     -H "X-Gemini-API-Key: your_gemini_key" \
     -H "X-Replicate-API-Key: your_replicate_token" \
     http://localhost:5000/api/posts
```

## 🐍 Python Library Usage

## ✨ Features

### 🤖 Smart Gateway
- **Intelligent Routing** - Automatically determines if content needs rewriting or can be published directly
- **Structured Output** - Uses Gemini's structured output for consistent blog formatting
- **Function Calling** - Leverages Gemini function calling for smart decision making
- **Auto Enhancement** - Transforms scattered ideas into complete, well-structured blog posts
- **Missing Component Detection** - Automatically generates titles, excerpts, and tags when missing

### 🎨 Dual AI Image Generation
- **🔥 Replicate Flux-dev**: Ultra-fast generation (3-7 seconds), photorealistic images, WebP format
- **🏔️ Google Imagen-4**: Professional quality, advanced prompt understanding, PNG format
- **Automatic Fallback System**: Intelligent provider switching for maximum reliability
- **Provider Selection**: Choose your preferred provider or let the system decide
- **Multiple Aspect Ratios**: 16:9, 1:1, 9:16, 4:3, 3:2 support

### Content Creation & Management
- 📝 **Smart Content Formatting** - Auto-format plain text to beautiful Markdown with Gemini AI
- 🔗 **YouTube-Style Slugs** - Generate 11-character slugs like YouTube video IDs
- 🎬 **YouTube Video Embedding** - Seamlessly embed YouTube videos in posts
- 🌏 **Multi-language Support** - Chinese to Pinyin conversion for slugs
- 🌐 **Language Translation** - Auto-translate content to any target language
- 🖼️ **Flexible Image Handling** - Support for URLs, local files, base64 data

### Blog Management
- 📋 **Advanced Listing** - Get posts with powerful filtering options
- 🔍 **Search & Query** - Full-text search across all posts
- 📅 **Date Range Filtering** - Find posts by publication/creation date
- 📊 **Detailed Post Info** - Get complete post details including content
- ✏️ **Update Posts** - Modify any post property (title, content, dates, etc.)
- ⭐ **Featured Control** - Set posts as featured or unfeatured
- 👁️ **Visibility Management** - Control post visibility (public/members/paid)
- 🔄 **Status Toggle** - Publish/unpublish posts instantly
- 🖼️ **Image Updates** - Replace, generate, or remove feature images
- 📆 **Date Management** - Update published dates for content organization
- 🗑️ **Post Deletion** - Remove posts from Ghost CMS
- ⚡ **Batch Operations** - Process multiple posts efficiently

## 📋 Prerequisites

- Python 3.8+
- Ghost CMS instance with Admin API access
- **Image Generation** (choose one or both):
  - Google Gemini API key (for Imagen-4 generation)
  - Replicate API token (for Flux-dev generation)

## 🚀 Quick Start

### 1. Installation

```bash
pip install ghost-blog-smart
```

### 2. Configuration

Create a `.env` file in your project root:

```env
# Ghost CMS Configuration
GHOST_ADMIN_API_KEY=your_admin_api_key_id:your_secret_key_here
GHOST_API_URL=https://your-ghost-site.com

# Google AI Configuration (for Imagen generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Replicate Configuration (for Flux generation)
REPLICATE_API_TOKEN=r8_your_replicate_api_token_here
```

**Important Notes:**
- `GHOST_ADMIN_API_KEY` format: `key_id:secret_key` (colon-separated)
- `GHOST_API_URL` must include `https://`
- `REPLICATE_API_TOKEN` format: `r8_xxxxxxxxxxxxxx` (get from [Replicate Account](https://replicate.com/account))
- All API keys can be provided either through environment variables OR as function parameters

### 3. Basic Usage

#### Smart Gateway Method (Recommended)
```python
from ghost_blog_smart import smart_blog_gateway

# Transform scattered ideas into a complete blog post
result = smart_blog_gateway(
    "AI healthcare benefits: faster diagnosis, better accuracy, cost reduction. Challenges: privacy, regulation.",
    status="published"
)

# The AI will automatically:
# - Analyze input complexity and completeness
# - Route through optimal processing path
# - Generate missing title, excerpt, tags
# - Structure content professionally
# - Generate feature image with Flux/Imagen
# - Publish to Ghost CMS
```

#### Traditional Method
```python
from ghost_blog_smart import create_ghost_blog_post

# Create a simple blog post
result = create_ghost_blog_post(
    title="My First Post",
    content="This is the content of my blog post.",
    excerpt="A brief summary",
    tags=["Tutorial", "Getting Started"],
    status="published"
)

if result['success']:
    print(f"Post created: {result['url']}")
```

## 🎯 Image Generation Examples

### Replicate Flux (Ultra-Fast)
```python
result = create_ghost_blog_post(
    title="AI Revolution in Photography",
    content="Artificial intelligence is transforming photography...",
    use_generated_feature_image=True,
    prefer_flux=True,  # 3-7 second generation time
    replicate_api_key="r8_your_token_here",
    image_aspect_ratio="16:9"
)
```

### Google Imagen (Professional Quality)
```python
result = create_ghost_blog_post(
    title="Digital Art Mastery Guide", 
    content="Digital art has evolved tremendously...",
    use_generated_feature_image=True,
    prefer_imagen=True,  # Professional quality
    gemini_api_key="your_gemini_key",
    image_aspect_ratio="16:9"
)
```

### Auto-Fallback System
```python
# Set both API keys - system will try Flux first, fallback to Imagen if needed
result = create_ghost_blog_post(
    title="Tech Innovation Landscape",
    content="Today's technology landscape is dynamic...",
    use_generated_feature_image=True,
    replicate_api_key="r8_your_token_here",
    gemini_api_key="your_gemini_key",
    # No preference specified - auto-fallback enabled
    image_aspect_ratio="16:9"
)
```

## 📚 API Reference

### Smart Gateway

#### `smart_blog_gateway(user_input, **kwargs)`

Intelligent gateway that automatically routes blog creation through the optimal path.

**Parameters:**
- `user_input` (str): Your blog content, ideas, or request
- `status` (str): 'published' or 'draft' (default: 'published')
- `preferred_language` (str): Target language for output (optional)
- `replicate_api_key` (str): Replicate API token for Flux generation
- `gemini_api_key` (str): Google Gemini API key for Imagen generation

**Returns:**
```python
{
    'success': bool,
    'response': str,           # Human-readable status message
    'url': str,               # Ghost post URL (if successful)
    'post_id': str,           # Ghost post ID (if successful)
    'generated_title': str,   # AI-generated title
    'generated_excerpt': str, # AI-generated excerpt
    'generated_tags': list,   # AI-generated tags
    'rewritten_data': dict    # Rewritten content details (if applicable)
}
```

### Content Creation

#### `create_ghost_blog_post(**kwargs)`

Main function to create Ghost blog posts.

**Required Parameters:**
- `title` (str): Blog post title
- `content` (str): Blog post content (Markdown or plain text)

**Image Generation Parameters:**
- `use_generated_feature_image` (bool): Generate AI image (default: False)
- `prefer_flux` (bool): Prefer Replicate Flux over Google Imagen
- `prefer_imagen` (bool): Prefer Google Imagen over Replicate Flux
- `replicate_api_key` (str): Replicate API token for Flux generation
- `gemini_api_key` (str): Google Gemini API key for Imagen generation
- `image_generation_prompt` (str): Custom prompt for image generation
- `image_aspect_ratio` (str): '16:9', '1:1', '9:16', '4:3', '3:2' (default: '16:9')

**Other Parameters:**
- `excerpt` (str): Post excerpt/summary
- `tags` (list): List of tags (default: ['Blog'])
- `status` (str): 'published' or 'draft' (default: 'published')
- `visibility` (str): 'public', 'members', 'paid', or 'tiers' (default: 'public')
- `target_language` (str): Target language for content translation
- `auto_format` (bool): Auto-format plain text with AI (default: True)
- `is_test` (bool): Test mode without posting (default: False)

## 🎨 Image Generation Comparison

| Feature | Replicate Flux-dev | Google Imagen-4 |
|---------|-------------------|-----------------| 
| **Speed** | ⚡ Ultra-fast (3-7s) | 🐢 Moderate (10-15s) |
| **Quality** | 🔥 Photorealistic | 🏔️ Professional |
| **Format** | 📁 WebP (smaller) | 📁 PNG (lossless) |
| **Cost** | 💰 Pay-per-use | 💰 API quota based |
| **Best For** | Realistic scenes, portraits | Abstract concepts, artistic |

**Supported Aspect Ratios:**
- `16:9` - Widescreen (1920x1080) - **Default**, ideal for most blogs
- `1:1` - Square (1024x1024) - Great for social media
- `9:16` - Portrait (1080x1920) - Mobile-optimized vertical
- `4:3` - Traditional (1024x768) - Classic photo ratio
- `3:2` - DSLR (1536x1024) - Professional photography ratio

## 🛠️ Advanced Examples

### Language Translation
```python
# Translate Chinese to English
result = create_ghost_blog_post(
    title="科技未来", 
    content="人工智能正在改变世界。医疗诊断更准确。",
    target_language="English",  # Auto-translates content
    status="published"
)
```

### YouTube Video Post
```python
result = create_ghost_blog_post(
    title="Amazing AI Tutorial",
    content="Check out this incredible tutorial...",
    youtube_video_id="dQw4w9WgXcQ",  # Becomes the post slug
    use_generated_feature_image=True,
    tags=["Video", "Tutorial"],
    status="draft"
)
```

### Blog Management
```python
from ghost_blog_smart import (
    get_ghost_posts,
    update_ghost_post,
    update_ghost_post_image,
    delete_ghost_post
)

# Get posts
posts = get_ghost_posts(limit=5, status='published')

# Update post
result = update_ghost_post(
    post_id="your_post_id",
    featured=True,
    tags=["Updated", "Featured"]
)

# Update feature image
result = update_ghost_post_image(
    post_id="your_post_id",
    use_generated_feature_image=True,
    prefer_flux=True
)

# Delete post
result = delete_ghost_post(post_id="your_post_id")
```

## 📁 Project Structure

```
ghost-blog-smart/
├── ghost_blog_smart/             # Main package directory
│   ├── __init__.py              # Package initialization and exports
│   ├── main_functions.py        # Core API functions
│   ├── post_management.py       # Advanced post management
│   ├── smart_gateway.py         # AI-powered intelligent routing
│   ├── clean_imagen_generator.py # Hybrid image generation
│   ├── replicate_flux_generator.py # Replicate Flux integration
│   └── client.py               # Class-based interface
├── example_usage.py             # Complete usage examples
├── requirements.txt             # Python dependencies
├── setup.py                    # Package setup and configuration
└── README.md                   # This documentation
```

## 🧪 Testing

Set `is_test=True` to test without actually posting:

```python
result = create_ghost_blog_post(
    title="Test Post",
    content="Test content",
    is_test=True  # Won't actually post
)
```

## 📊 Token Optimization

The API optimizes token usage by:
- Using only title, excerpt, and first paragraph for image generation
- Caching generated images locally
- Batch processing when possible
- Intelligent content analysis to minimize AI calls

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Ghost CMS for the excellent blogging platform
- Google Gemini & Imagen for AI capabilities  
- Replicate for ultra-fast Flux generation
- The open-source community

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

Made with ❤️ for the Ghost CMS community
✨ **This Flask API is now live on GitHub and ready for Docker publishing!**
