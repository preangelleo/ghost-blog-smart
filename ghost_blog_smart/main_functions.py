

from pypinyin import lazy_pinyin, Style
import re, sys, os, unicodedata, mimetypes, requests, jwt, time, json
import random
import base64
import string
from datetime import datetime
from markdownify import markdownify as md
from markdown_it import MarkdownIt
import markdown
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Import image generation modules
from .clean_imagen_generator import CleanImagenGenerator
from .blog_post_refine_prompt import BLOG_POST_REFINE_SYSTEM_PROMPT, get_refine_prompt_with_language
from .blog_to_image_prompt import BLOG_TO_IMAGE_SYSTEM_PROMPT
IMAGE_GENERATION_AVAILABLE = True

# Load environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GHOST_ADMIN_API_KEY = os.getenv('GHOST_ADMIN_API_KEY')
GHOST_API_URL = os.getenv('GHOST_API_URL')

# Model configuration
GEMINI_FLASH_MODEL = 'gemini-2.5-flash' # For text optimization
IMAGE_MODEL = 'imagen-4.0-generate-001'  # For image generation

def gemini_chat_simple(prompt: str, system_prompt: str = '', model: str = None, api_key: str = None) -> str:
    # Use provided API key or fall back to environment variable
    api_key = api_key or GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required - provide as parameter or set in environment")
    
    # Use provided model or fall back to default
    model = model or GEMINI_FLASH_MODEL
    
    genai.configure(api_key=api_key)
    genai_model = genai.GenerativeModel(model)
    if system_prompt: prompt = f"{system_prompt}\n\nUser:\n\n{prompt}"
    response = genai_model.generate_content(prompt)
    return response.text

def create_slug(title=None):
    """
    Create a URL-friendly slug.
    
    Args:
        title (str, optional): The title to convert. If None, generates YouTube-style 11-char ID
        
    Returns:
        str: A URL-friendly slug (YouTube-style 11 chars or converted from title)
        
    Example:
        >>> create_slug()  # No title provided
        'dQw4w9WgXcQ'  # Random YouTube-style ID
        >>> create_slug("Hello World!")
        'hello-world'
        >>> create_slug("创世纪第一章")
        'chuang-shi-ji-di-yi-zhang'
    """
    
    # If no title provided, generate YouTube-style ID
    if not title:
        # YouTube IDs use base64url characters: A-Z, a-z, 0-9, -, _
        # They are typically 11 characters long
        chars = string.ascii_letters + string.digits + '-_'
        return ''.join(random.choice(chars) for _ in range(11))
    
    # Original slug creation logic for titles
    slug = title.lower()
    
    # Check if contains Chinese characters
    if re.search(r'[\u4e00-\u9fff]', slug):
        # Convert Chinese characters to pinyin
        pinyin_list = lazy_pinyin(slug, style=Style.NORMAL)
        slug = '-'.join(pinyin_list)
    
    # Convert unicode characters to ASCII equivalents
    slug = unicodedata.normalize('NFKD', slug)
    slug = slug.encode('ASCII', 'ignore').decode('ASCII')
    
    # Replace any non-alphanumeric characters (except hyphens) with a space
    slug = re.sub(r'[^\w\s-]', ' ', slug)
    
    # Replace all spaces and repeated hyphens with a single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def general_ghost_post(**kwargs):
    """
    Simplified Ghost CMS posting function - all parameters via kwargs
    
    Required Args (in kwargs):
        title (str): Post title
        content (str): Post content (markdown or HTML)
        ghost_admin_api_key (str): Ghost admin API key (required)
        ghost_api_url (str): Ghost API URL (required)
        
    Optional Args (in kwargs):
        content_type (str): 'markdown' or 'html' (default: 'markdown')
        post_type (str): 'post' or 'page' (default: 'post')
        visibility (str): 'public', 'members', 'paid' (default: 'public')
        status (str): 'published', 'draft' (default: 'published')
        tags (list): List of tags (default: [])
        feature_image (str): Feature image path/URL
        custom_excerpt (str): Custom excerpt
        is_test (bool): Test mode (default: False)
        youtube_video_id (str): YouTube video ID for slug
    
    Returns:
        dict: {'success': bool, 'url': str, 'post_id': str, 'message': str}
    """
    # Extract required parameters from kwargs
    title = kwargs.get('title')
    content = kwargs.get('content')

    # Check if API keys are provided as parameters, otherwise use environment variables
    ghost_admin_api_key = kwargs.get('ghost_admin_api_key') or GHOST_ADMIN_API_KEY
    ghost_api_url = kwargs.get('ghost_api_url') or GHOST_API_URL

    # Check test mode - handle feature image even in test mode
    is_test = kwargs.get('is_test', False)
    if is_test:
        slug = kwargs.get('youtube_video_id') or create_slug()
        # Process feature image for test mode too
        feature_image = kwargs.get('feature_image', '')
        ghost_feature_image = None
        if feature_image:
            # For test mode, just use the original feature_image path/URL
            ghost_feature_image = feature_image
        
        return {
            'success': True, 
            'url': f'{ghost_api_url or "https://test.com"}/test-post-{slug}', 
            'post_id': f'test-id-{slug}', 
            'message': 'Test mode - post not actually created',
            'feature_image': ghost_feature_image
        }
    
    # Validate required parameters
    if not all([title, content, ghost_admin_api_key, ghost_api_url]):
        missing = []
        if not title: missing.append('title')
        if not content: missing.append('content')
        if not ghost_admin_api_key: missing.append('ghost_admin_api_key')
        if not ghost_api_url: missing.append('ghost_api_url')
        return {'success': False, 'message': f'Missing required parameters: {", ".join(missing)}'}
    
    # Extract optional parameters with defaults
    content_type = kwargs.get('content_type', 'markdown')
    post_type = kwargs.get('post_type', 'post')
    visibility = kwargs.get('visibility', 'public')
    status = kwargs.get('status', 'published')
    tags = kwargs.get('tags', [])
    feature_image = kwargs.get('feature_image', '')
    custom_excerpt = kwargs.get('custom_excerpt', '')
    youtube_video_id = kwargs.get('youtube_video_id', '')  # is_test already handled above

    custom_excerpt = custom_excerpt[:299]
    
    # Create slug: use youtube_video_id if provided, otherwise generate YouTube-style ID
    if youtube_video_id:
        slug = youtube_video_id
    else:
        # Generate YouTube-style 11-character ID instead of using title
        slug = create_slug()
    
    # Generate Ghost JWT token
    try:
        key_id, secret = ghost_admin_api_key.split(':')
        iat = int(time.time())
        header = {'alg': 'HS256', 'kid': key_id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,  # Token expires in 5 minutes
            'aud': '/admin/'
        }
        ghost_token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
    except Exception as e:
        return {'success': False, 'message': f'Failed to generate JWT token: {str(e)}'}
    
    headers = {
        'Authorization': f'Ghost {ghost_token}',
        'Content-Type': 'application/json'
    }
    
    # Helper function to upload image to Ghost
    def upload_image_to_ghost(image_path_or_url, ghost_api_url, ghost_token):
        try:
            upload_headers = {'Authorization': f'Ghost {ghost_token}'}
            upload_url = f'{ghost_api_url}/ghost/api/admin/images/upload/'
            
            # Handle base64 data
            if image_path_or_url.startswith('data:image/'):
                # Extract base64 data
                
                header, data = image_path_or_url.split(',', 1)
                # Get MIME type from header
                mime_type = header.split(':')[1].split(';')[0]
                # Decode base64
                image_data = base64.b64decode(data)
                # Upload to Ghost
                files = {'file': ('image.jpg', image_data, mime_type)}
                response = requests.post(upload_url, headers=upload_headers, files=files)
            # Handle local file path
            elif os.path.exists(image_path_or_url):
                # Determine MIME type based on file extension
                mime_type, _ = mimetypes.guess_type(image_path_or_url)
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = 'image/jpeg'  # Default fallback
                
                filename = os.path.basename(image_path_or_url)
                with open(image_path_or_url, 'rb') as image_file:
                    files = {'file': (filename, image_file, mime_type)}
                    response = requests.post(upload_url, headers=upload_headers, files=files)
            else:
                # Handle URL - download first then upload
                try:
                    img_response = requests.get(image_path_or_url, timeout=10)
                    if img_response.status_code == 200:
                        files = {'file': ('image.jpg', img_response.content, 'image/jpeg')}
                        response = requests.post(upload_url, headers=upload_headers, files=files)
                    else:
                        print(f"Failed to download image from URL: {image_path_or_url}")
                        return ''
                except Exception as e:
                    print(f"Error downloading image: {str(e)}")
                    return ''
            
            if response.status_code == 201:
                response_data = response.json()
                ghost_image_url = response_data['images'][0]['url']
                print(f"Image uploaded successfully: {ghost_image_url}")
                return ghost_image_url
            else:
                print(f"Image upload failed: {response.status_code} {response.text}")
                return ''
                
        except Exception as e:
            print(f"Error uploading image to Ghost: {str(e)}")
            return ''
    
    # Convert content to HTML if needed
    if content_type.lower() == 'markdown':
        try:
            md_parser = MarkdownIt()
            html_content = md_parser.render(content)
        except ImportError:
            # Fallback to simple markdown conversion
            html_content = content.replace('\n', '<br>')
    else: html_content = content
    
    # Add YouTube video embed if youtube_video_id is provided
    if youtube_video_id:
        youtube_embed = f'''
<div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
    <h3 style="margin-bottom: 20px; color: #333;">🎥 Watch the Animated Story</h3>
    <iframe 
        width="560" 
        height="315" 
        src="https://www.youtube.com/embed/{youtube_video_id}" 
        frameborder="0" 
        allowfullscreen 
        style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    </iframe>
</div>'''
        # Add the YouTube embed at the end of the content
        html_content = f"{html_content}\n\n{youtube_embed}"
    
    # Prepare post data
    date_today = str(datetime.now().date())
    if not custom_excerpt: custom_excerpt = f"Generated on {date_today}"
    
    post_type_key = f"{post_type}s"
    post_content_dict = {
        "title": title,
        "slug": slug,
        "html": html_content,
        "status": status,
        "custom_excerpt": custom_excerpt,
        "visibility": visibility,
        "type": post_type
    }
    
    # Handle feature image upload
    ghost_feature_image = None  # Initialize to track actual uploaded image URL
    if feature_image:
        ghost_feature_image = upload_image_to_ghost(feature_image, ghost_api_url, ghost_token)
        if ghost_feature_image: post_content_dict["feature_image"] = ghost_feature_image
        else: print(f"generic_ghost_post() >> ❌ Feature image processing failed, posting without feature image")
    
    # Add optional fields
    if tags: post_content_dict["tags"] = tags if isinstance(tags, list) else [tags]
    
    post_data = {post_type_key: [post_content_dict]}
    api_url = f'{ghost_api_url}/ghost/api/admin/{post_type_key}/?source=html'
    
    # Handle test mode BEFORE JWT generation to avoid validation issues
    if is_test: 
        return {
            'success': True, 
            'url': f'{ghost_api_url}/test-post-{slug}', 
            'post_id': f'test-id-{slug}', 
            'message': 'Test mode - post not actually created',
            'feature_image': ghost_feature_image  # Include feature image even in test mode
        }
    
    # Make the API request
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(post_data))
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            url = response_data[post_type_key][0]['url']
            post_id = response_data[post_type_key][0]['id']
            
            return {
                'success': True, 
                'url': url, 
                'post_id': post_id, 
                'message': 'Post created successfully',
                'feature_image': ghost_feature_image  # Include actual uploaded image URL
            }
        else:
            error_msg = f"Failed to create post: {response.status_code} {response.text}"
            print(f"❌ Ghost API Error: {error_msg}")
            return {'success': False, 'message': error_msg}
    except Exception as e:
        error_msg = f"Request failed: {str(e)}"
        print(f"generic_ghost_post() >> {error_msg}")
        return {'success': False, 'message': error_msg}


def create_ghost_blog_post(**kwargs):
    """
    Create a Ghost blog post - simplified version for general blog posting
    
    Required Args (in kwargs):
        title (str): Blog post title  
        content (str): Blog post content (plain text or markdown)
    
    Optional Args (in kwargs):
        # Basic post settings
        excerpt (str): Post excerpt/summary
        feature_image (str): Path or URL to feature image (or base64 data)
        tags (list): List of tags (default: ['Blog'])
        post_type (str): 'post' or 'page' (default: 'post')
        status (str): 'draft' or 'published' (default: 'published')
        visibility (str): 'public' or 'private' (default: 'public')
        
        # Content formatting  
        content_type (str): 'markdown' or 'html' (default: 'markdown')
        auto_format (bool): Auto-convert plain text to formatted content (default: True)
        target_language (str): Target language for content (e.g., 'English', 'Chinese'). 
                              If not specified, preserves original language
        
        # Image generation settings
        use_generated_feature_image (bool): Generate feature image with AI (default: False)
        image_generation_prompt (str): Custom prompt for image generation
        image_aspect_ratio (str): Aspect ratio for generated image (default: '16:9')
        
        # API settings
        is_test (bool): Test mode (default: False)
        ghost_admin_api_key (str): Override default Ghost API key
        ghost_api_url (str): Override default Ghost API URL
        youtube_video_id (str): YouTube video ID for embedding
        gemini_api_key (str): Gemini API key for AI features
        
    Returns:
        dict: Result from Ghost API with success status, URL, and post ID
    """
    
    def plain_text_to_formatted_content(text, gemini_api_key=None, target_language=None):
        """
        Convert plain text to well-formatted content using Gemini
        
        Args:
            text: The text to format
            gemini_api_key: Optional Gemini API key
            target_language: Optional target language for the content
        """
        
        try:
            prompt = f"Please format this plain text content for better readability:\n\n{text}"
            # Get the system prompt with language directive
            system_prompt = get_refine_prompt_with_language(target_language)
            formatted_result = gemini_chat_simple(prompt, system_prompt, api_key=gemini_api_key)
            return formatted_result.strip()
        except Exception as e:
            print(f"Warning: Failed to format text: {str(e)}")
            # Fallback: simple paragraph formatting
            paragraphs = text.split('\n\n')
            return '\n\n'.join([p.strip() for p in paragraphs if p.strip()])
    
    # Extract required parameters
    title = kwargs.get('title')
    content = kwargs.get('content')
    
    # Validate required parameters
    if not all([title, content]):
        missing = []
        if not title: missing.append('title')
        if not content: missing.append('content')
        return {'success': False, 'message': f'Missing required parameters: {", ".join(missing)}'}

    # Handle feature image generation or validation
    feature_image = kwargs.get('feature_image')
    use_generated_feature_image = kwargs.get('use_generated_feature_image', False)
    
    # Generate feature image if requested and no image provided
    if use_generated_feature_image and not feature_image and IMAGE_GENERATION_AVAILABLE:
        try:
            print("🎨 Generating feature image with AI...")
            
            # Get API keys for image generation
            gemini_api_key = kwargs.get('gemini_api_key') or GEMINI_API_KEY
            replicate_api_key = kwargs.get('replicate_api_key') or os.getenv('REPLICATE_API_TOKEN')
            
            if not gemini_api_key:
                print("⚠️ Cannot generate image: Gemini API key not provided")
            else:
                # Initialize hybrid image generator with both APIs
                generator = CleanImagenGenerator(
                    api_key=gemini_api_key, 
                    model_name=IMAGE_MODEL,
                    replicate_api_key=replicate_api_key
                )
                
                # Create image generation prompt from title and content
                image_prompt = kwargs.get('image_generation_prompt')
                if not image_prompt:
                    # Generate structured prompt from blog content using our system prompt
                    print("🤖 Analyzing blog content to create image description...")
                    
                    # Extract excerpt and first paragraph only (not full content)
                    excerpt = kwargs.get('excerpt', kwargs.get('custom_excerpt', ''))
                    
                    # Get first paragraph from content
                    paragraphs = content.strip().split('\n\n')
                    first_paragraph = paragraphs[0] if paragraphs else content[:500]
                    
                    # Combine title, excerpt, and first paragraph for context
                    blog_context = f"Blog Title: {title}"
                    if excerpt:
                        blog_context += f"\n\nExcerpt: {excerpt}"
                    blog_context += f"\n\nFirst Paragraph:\n{first_paragraph}"
                    
                    # Use Gemini to convert blog to image description
                    full_instruction = BLOG_TO_IMAGE_SYSTEM_PROMPT + "\n\n" + blog_context
                    
                    # Get structured image description
                    image_description = gemini_chat_simple(
                        prompt=full_instruction,
                        model=GEMINI_FLASH_MODEL,
                        api_key=gemini_api_key
                    )
                    
                    # Use the structured description as the image prompt
                    image_prompt = image_description
                    print(f"🔍 Generated image description: {image_prompt[:100]}...")
                
                # Generate image with the prompt (no need to optimize again since we already have structured output)
                # Check if user prefers Flux (Replicate) over Imagen (Google)
                prefer_flux = kwargs.get('prefer_flux', False) or (replicate_api_key and not kwargs.get('prefer_imagen', False))
                
                image_result = generator.generate_image(
                    prompt=image_prompt,
                    aspect_ratio=kwargs.get('image_aspect_ratio', '16:9'),
                    number_of_images=1,
                    optimize_prompt=False,  # Already optimized by our blog-to-image prompt
                    output_directory='./generated_images',
                    image_prefix='blog_feature_',
                    prefer_flux=prefer_flux
                )
                
                if image_result['success']:
                    # Use the generated image path
                    feature_image = image_result['results'][0]['filepath']
                    print(f"✅ Feature image generated: {feature_image}")
                else:
                    print(f"⚠️ Image generation failed: {image_result.get('error')}")
        except Exception as e:
            print(f"⚠️ Error generating feature image: {str(e)}")
    
    # Validate feature_image if provided (only check for local files, not URLs or base64)
    if feature_image:
        # Check if it's base64 data
        if feature_image.startswith('data:image/'):
            print("📸 Using base64 image data")
        # Check if it's a URL
        elif feature_image.startswith(('http://', 'https://')):
            print(f"🌐 Using image URL: {feature_image}")
        # Check if it's a local file
        elif os.path.isfile(feature_image):
            print(f"📁 Using local image: {feature_image}")
        else:
            print(f"⚠️ Warning: Feature image not found: {feature_image}. Proceeding without image.")
            feature_image = None

    try:
        # Get content type and auto-format settings
        content_type = kwargs.get('content_type', 'markdown')
        auto_format = kwargs.get('auto_format', True)
        target_language = kwargs.get('target_language', None)
        
        # Get API key for text formatting
        gemini_api_key = kwargs.get('gemini_api_key') or GEMINI_API_KEY
        
        # Process content based on settings
        processed_content = content
        if auto_format:
            # Auto-format plain text for better readability
            processed_content = plain_text_to_formatted_content(content, gemini_api_key, target_language)
        
        # Convert to HTML if needed
        if content_type == 'markdown':
            try:
                md_parser = MarkdownIt()
                final_content = md_parser.render(processed_content)
                final_content_type = 'html'
            except ImportError:
                print("Warning: markdown_it not available, using plain text")
                final_content = processed_content
                final_content_type = 'markdown'
        else:
            final_content = processed_content
            final_content_type = content_type
        
        # Prepare parameters for general_ghost_post
        post_params = kwargs.copy()  # Start with all original kwargs
        
        # Override with processed values
        post_params.update({
            'title': title,
            'content': final_content,
            'content_type': final_content_type,
            'feature_image': feature_image,
        })
        
        # Set defaults for any missing parameters
        post_params.setdefault('post_type', 'post')
        post_params.setdefault('visibility', 'public')
        post_params.setdefault('status', 'published')
        post_params.setdefault('tags', ['Blog'])
        post_params.setdefault('is_test', False)
        
        # Handle excerpt parameter name mapping
        if 'excerpt' in post_params: post_params['custom_excerpt'] = post_params.pop('excerpt')
        
        # Call the general Ghost post function
        result = general_ghost_post(**post_params)
        
        # The feature_image is now properly returned by general_ghost_post
        # No need to override it here as it contains the actual uploaded URL
        return result
        
    except Exception as e:
        error_msg = f"Failed to create Ghost blog post: {str(e)}"
        print(f"create_ghost_blog_post() >> {error_msg}")
        return {'success': False, 'message': error_msg}


# ============================================================================
# BLOG MANAGEMENT FUNCTIONS
# ============================================================================

def get_ghost_posts(**kwargs):
    """
    Get list of posts from Ghost CMS
    
    Parameters:
    - limit: Number of posts to retrieve (default: 15)
    - page: Page number for pagination (default: 1)
    - status: Filter by status ('published', 'draft', 'all')
    - ghost_admin_api_key: Override env Ghost API key
    - ghost_api_url: Override env Ghost API URL
    
    Returns:
    - dict with 'success', 'posts' list, and 'meta' pagination info
    """
    try:
        # Get API credentials
        admin_key = kwargs.get('ghost_admin_api_key') or GHOST_ADMIN_API_KEY
        api_url = kwargs.get('ghost_api_url') or GHOST_API_URL
        
        if not admin_key or not api_url:
            return {'success': False, 'message': 'Ghost API credentials not provided'}
        
        # Parse the admin API key
        if ':' not in admin_key:
            return {'success': False, 'message': 'Invalid admin API key format'}
        
        id, secret = admin_key.split(':')
        
        # Generate JWT token
        iat = int(time.time())
        exp = iat + 5 * 60  # 5 minute expiry
        
        header = {
            'alg': 'HS256',
            'typ': 'JWT',
            'kid': id
        }
        
        payload = {
            'iat': iat,
            'exp': exp,
            'aud': '/admin/'
        }
        
        ghost_token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
        
        # Build query parameters
        params = {
            'limit': kwargs.get('limit', 15),
            'page': kwargs.get('page', 1),
            'include': 'tags,authors',
            'formats': 'html,mobiledoc'
        }
        
        status = kwargs.get('status', 'all')
        if status != 'all':
            params['filter'] = f'status:{status}'
        
        # Make request
        headers = {
            'Authorization': f'Ghost {ghost_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{api_url}/ghost/api/admin/posts/',
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'posts': data.get('posts', []),
                'meta': data.get('meta', {})
            }
        else:
            return {'success': False, 'message': f'Failed to get posts: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error getting posts: {str(e)}'}


def update_ghost_post(post_id, **kwargs):
    """
    Update various properties of a Ghost blog post
    
    Parameters:
    - post_id: The ID of the post to update
    - status: Update status to 'published' or 'draft'
    - featured: Set featured status (True/False)
    - title: Update post title
    - content: Update post content
    - excerpt: Update post excerpt
    - tags: Update tags (list)
    - visibility: Update visibility ('public', 'members', 'paid', 'tiers')
    - published_at: Update published date (str in ISO format or datetime object)
    - ghost_admin_api_key: Override env Ghost API key
    - ghost_api_url: Override env Ghost API URL
    
    Returns:
    - dict with 'success' and updated post info
    """
    try:
        # Get API credentials
        admin_key = kwargs.get('ghost_admin_api_key') or GHOST_ADMIN_API_KEY
        api_url = kwargs.get('ghost_api_url') or GHOST_API_URL
        
        if not admin_key or not api_url:
            return {'success': False, 'message': 'Ghost API credentials not provided'}
        
        # Generate headers
        headers = generate_ghost_headers(admin_key)
        if not headers:
            return {'success': False, 'message': 'Failed to generate authentication headers'}
        
        # Get current post
        get_response = requests.get(
            f'{api_url}/ghost/api/admin/posts/{post_id}/',
            headers=headers
        )
        
        if get_response.status_code != 200:
            return {'success': False, 'message': f'Post not found: {post_id}'}
        
        current_post = get_response.json()['posts'][0]
        
        # Build update data with only provided fields
        update_fields = {}
        
        # Status update
        if 'status' in kwargs:
            update_fields['status'] = kwargs['status']
        
        # Featured update
        if 'featured' in kwargs:
            update_fields['featured'] = bool(kwargs['featured'])
        
        # Title update
        if 'title' in kwargs:
            update_fields['title'] = kwargs['title']
        
        # Content update
        if 'content' in kwargs:
            content = kwargs['content']
            content_type = kwargs.get('content_type', 'markdown')
            if content_type.lower() == 'markdown':
                content = markdown.markdown(content)
            update_fields['html'] = content
        
        # Excerpt update
        if 'excerpt' in kwargs:
            excerpt = kwargs['excerpt'][:299] if len(kwargs['excerpt']) > 299 else kwargs['excerpt']
            update_fields['custom_excerpt'] = excerpt
        
        # Tags update
        if 'tags' in kwargs:
            tags_list = kwargs['tags'] if isinstance(kwargs['tags'], list) else [kwargs['tags']]
            update_fields['tags'] = [{'name': tag} for tag in tags_list]
        
        # Visibility update
        if 'visibility' in kwargs:
            update_fields['visibility'] = kwargs['visibility']
        
        # Published date update
        if 'published_at' in kwargs:
            published_at = kwargs['published_at']
            # Handle datetime object
            if hasattr(published_at, 'isoformat'):
                # Convert to ISO format and ensure milliseconds
                published_at = published_at.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            elif isinstance(published_at, str):
                # Ensure proper format for string dates
                if not published_at.endswith('Z') and not published_at.endswith('+00:00'):
                    if 'T' in published_at and not any(tz in published_at for tz in ['+', '-', 'Z']):
                        # Add milliseconds if missing
                        if '.' not in published_at:
                            published_at = published_at.replace('T', 'T').split('T')
                            published_at = published_at[0] + 'T' + published_at[1].split('.')[0] + '.000Z'
                        else:
                            published_at = published_at + 'Z'
            update_fields['published_at'] = published_at
        
        # Always include updated_at for version control
        update_fields['updated_at'] = current_post['updated_at']
        
        if not update_fields:
            return {'success': False, 'message': 'No fields to update'}
        
        # Update the post
        update_data = {'posts': [update_fields]}
        
        response = requests.put(
            f'{api_url}/ghost/api/admin/posts/{post_id}/',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            updated_post = response.json()['posts'][0]
            
            # Build update summary
            updates = []
            if 'status' in kwargs:
                updates.append(f"status→{kwargs['status']}")
            if 'featured' in kwargs:
                updates.append(f"featured→{kwargs['featured']}")
            if 'title' in kwargs:
                updates.append("title updated")
            if 'content' in kwargs:
                updates.append("content updated")
            if 'excerpt' in kwargs:
                updates.append("excerpt updated")
            if 'tags' in kwargs:
                updates.append("tags updated")
            if 'visibility' in kwargs:
                updates.append(f"visibility→{kwargs['visibility']}")
            if 'published_at' in kwargs:
                updates.append("published date updated")
            
            update_summary = ", ".join(updates)
            print(f"✅ Post updated successfully ({update_summary}): {api_url}/{updated_post['slug']}")
            
            return {
                'success': True,
                'message': f'Post updated successfully ({update_summary})',
                'post_id': updated_post['id'],
                'status': updated_post['status'],
                'featured': updated_post.get('featured', False),
                'url': f"{api_url}/{updated_post['slug']}",
                'updates': updates
            }
        else:
            return {'success': False, 'message': f'Failed to update post: {response.status_code} - {response.text}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error updating post: {str(e)}'}


def update_ghost_post_image(post_id, **kwargs):
    """
    Update the feature image of a Ghost blog post
    
    Parameters:
    - post_id: The ID of the post to update
    - feature_image: Path/URL/base64 to new image, or None to remove
    - use_generated_feature_image: Generate new AI image (default: False)
    - image_prompt: Custom prompt for AI image generation (required if use_generated_image=True and no auto-generate)
    - auto_generate_prompt: Auto-generate prompt from post content (default: True if no image_prompt)
    - image_aspect_ratio: Aspect ratio for generated image (default: '16:9')
    - ghost_admin_api_key: Override env Ghost API key
    - ghost_api_url: Override env Ghost API URL
    - gemini_api_key: Override env Gemini API key (for AI generation)
    - is_test: Test mode - skip actual API calls (default: False)
    
    Returns:
    - dict with 'success' and updated post info
    """
    try:
        # Get API credentials
        admin_key = kwargs.get('ghost_admin_api_key') or GHOST_ADMIN_API_KEY
        api_url = kwargs.get('ghost_api_url') or GHOST_API_URL
        is_test = kwargs.get('is_test', False)
        
        # Handle test mode
        if is_test:
            return {
                'success': True,
                'message': 'Test mode - image update simulated successfully',
                'post_id': post_id,
                'feature_image': 'test-generated-image.jpg' if kwargs.get('use_generated_feature_image') else kwargs.get('feature_image'),
                'url': f'{api_url or "https://test.com"}/test-post'
            }
        
        if not admin_key or not api_url:
            return {'success': False, 'message': 'Ghost API credentials not provided'}
        
        # Generate headers
        headers = generate_ghost_headers(admin_key)
        if not headers:
            return {'success': False, 'message': 'Failed to generate authentication headers'}
        
        # Get current post
        get_response = requests.get(
            f'{api_url}/ghost/api/admin/posts/{post_id}/',
            headers=headers
        )
        
        if get_response.status_code != 200:
            return {'success': False, 'message': f'Post not found: {post_id}'}
        
        current_post = get_response.json()['posts'][0]
        
        # Handle image generation or upload
        feature_image_url = None
        new_image_path = kwargs.get('feature_image')
        
        # CRITICAL FIX: Check for correct parameter name and handle logic properly
        use_generated = kwargs.get('use_generated_feature_image', kwargs.get('use_generated_image', False))
        if use_generated and IMAGE_GENERATION_AVAILABLE:
            # Generate AI image
            gemini_api_key = kwargs.get('gemini_api_key') or GEMINI_API_KEY
            replicate_api_key = kwargs.get('replicate_api_key') or os.getenv('REPLICATE_API_TOKEN')
            
            if not gemini_api_key:
                return {'success': False, 'message': 'Gemini API key required for image generation'}
            
            print("🎨 Generating new feature image with AI...")
            generator = CleanImagenGenerator(
                api_key=gemini_api_key, 
                model_name=IMAGE_MODEL,
                replicate_api_key=replicate_api_key
            )
            
            # Check for custom prompt
            image_prompt = kwargs.get('image_prompt')
            
            # Auto-generate prompt if not provided and auto_generate_prompt is True
            if not image_prompt and kwargs.get('auto_generate_prompt', True):
                print("🤖 Auto-generating image prompt from post content...")
                title = current_post.get('title', '')
                excerpt = current_post.get('custom_excerpt', '')
                
                # Get first paragraph from content
                html_content = current_post.get('html', '')
                # Simple extraction of first paragraph text
                import re
                text_content = re.sub('<[^<]+?>', '', html_content)  # Strip HTML tags
                paragraphs = text_content.strip().split('\n\n')
                first_paragraph = paragraphs[0][:500] if paragraphs else text_content[:500]
                
                blog_context = f"Blog Title: {title}"
                if excerpt:
                    blog_context += f"\n\nExcerpt: {excerpt}"
                blog_context += f"\n\nFirst Paragraph:\n{first_paragraph}"
                
                full_instruction = BLOG_TO_IMAGE_SYSTEM_PROMPT + "\n\n" + blog_context
                image_prompt = gemini_chat_simple(
                    prompt=full_instruction,
                    model=GEMINI_FLASH_MODEL,
                    api_key=gemini_api_key
                )
                print(f"🔍 Generated prompt: {image_prompt[:100]}...")
            elif not image_prompt:
                return {'success': False, 'message': 'Image prompt required when use_generated_image=True and auto_generate_prompt=False'}
            
            # Generate the image
            # Check if user prefers Flux (Replicate) over Imagen (Google)
            prefer_flux = kwargs.get('prefer_flux', False) or (replicate_api_key and not kwargs.get('prefer_imagen', False))
            
            image_result = generator.generate_image(
                prompt=image_prompt,
                aspect_ratio=kwargs.get('image_aspect_ratio', '16:9'),
                number_of_images=1,
                optimize_prompt=False,  # Already optimized by our blog-to-image prompt
                output_directory='./generated_images',
                prefer_flux=prefer_flux,
                image_prefix='blog_feature_'
            )
            
            if image_result['success']:
                # Get the first image path from results array
                new_image_path = image_result['results'][0]['filepath']
                print(f"✅ Image generated: {new_image_path}")
            else:
                return {'success': False, 'message': f"Image generation failed: {image_result.get('error')}"}
        
        # Upload new image if provided
        if new_image_path:
            # Helper function to upload image
            def upload_image_to_ghost(image_path_or_url, api_url, headers):
                try:
                    upload_url = f'{api_url}/ghost/api/admin/images/upload/'
                    
                    # Handle base64 data
                    if image_path_or_url.startswith('data:image/'):
                        header, data = image_path_or_url.split(',', 1)
                        mime_type = header.split(':')[1].split(';')[0]
                        image_data = base64.b64decode(data)
                        files = {'file': ('image.jpg', image_data, mime_type)}
                        response = requests.post(upload_url, headers={'Authorization': headers['Authorization']}, files=files)
                    # Handle local file path
                    elif os.path.exists(image_path_or_url):
                        mime_type, _ = mimetypes.guess_type(image_path_or_url)
                        if not mime_type or not mime_type.startswith('image/'):
                            mime_type = 'image/jpeg'
                        filename = os.path.basename(image_path_or_url)
                        with open(image_path_or_url, 'rb') as image_file:
                            files = {'file': (filename, image_file, mime_type)}
                            response = requests.post(upload_url, headers={'Authorization': headers['Authorization']}, files=files)
                    else:
                        # Handle URL
                        img_response = requests.get(image_path_or_url, timeout=10)
                        if img_response.status_code == 200:
                            files = {'file': ('image.jpg', img_response.content, 'image/jpeg')}
                            response = requests.post(upload_url, headers={'Authorization': headers['Authorization']}, files=files)
                        else:
                            return ''
                    
                    if response.status_code == 201:
                        response_data = response.json()
                        return response_data['images'][0]['url']
                    else:
                        return ''
                except Exception as e:
                    print(f"Error uploading image: {str(e)}")
                    return ''
            
            feature_image_url = upload_image_to_ghost(new_image_path, api_url, headers)
            if not feature_image_url:
                print("⚠️ Failed to upload image, updating without image")
        
        # Update the post
        update_data = {
            'posts': [{
                'feature_image': feature_image_url,
                'updated_at': current_post['updated_at']
            }]
        }
        
        response = requests.put(
            f'{api_url}/ghost/api/admin/posts/{post_id}/',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            updated_post = response.json()['posts'][0]
            action = 'updated' if feature_image_url else 'removed'
            print(f"✅ Feature image {action} successfully")
            return {
                'success': True,
                'message': f'Feature image {action} successfully',
                'post_id': updated_post['id'],
                'feature_image': updated_post.get('feature_image'),
                'url': f"{api_url}/{updated_post['slug']}"
            }
        else:
            return {'success': False, 'message': f'Failed to update image: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error updating post image: {str(e)}'}


def delete_ghost_post(post_id, **kwargs):
    """
    Delete a Ghost blog post
    
    Parameters:
    - post_id: The ID of the post to delete
    - ghost_admin_api_key: Override env Ghost API key
    - ghost_api_url: Override env Ghost API URL
    
    Returns:
    - dict with 'success' and message
    """
    try:
        # Get API credentials
        admin_key = kwargs.get('ghost_admin_api_key') or GHOST_ADMIN_API_KEY
        api_url = kwargs.get('ghost_api_url') or GHOST_API_URL
        
        if not admin_key or not api_url:
            return {'success': False, 'message': 'Ghost API credentials not provided'}
        
        # Generate headers
        headers = generate_ghost_headers(admin_key)
        if not headers:
            return {'success': False, 'message': 'Failed to generate authentication headers'}
        
        # Delete the post
        response = requests.delete(
            f'{api_url}/ghost/api/admin/posts/{post_id}/',
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"✅ Post deleted successfully: {post_id}")
            return {
                'success': True,
                'message': 'Post deleted successfully',
                'post_id': post_id
            }
        elif response.status_code == 404:
            return {'success': False, 'message': f'Post not found: {post_id}'}
        else:
            return {'success': False, 'message': f'Failed to delete post: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error deleting post: {str(e)}'}


def generate_ghost_headers(admin_key):
    """
    Helper function to generate Ghost API headers with JWT token
    
    Parameters:
    - admin_key: Ghost admin API key
    
    Returns:
    - dict with Authorization and Content-Type headers, or None on error
    """
    try:
        if ':' not in admin_key:
            return None
        
        id, secret = admin_key.split(':')
        
        # Generate JWT token
        iat = int(time.time())
        exp = iat + 5 * 60  # 5 minute expiry
        
        header = {
            'alg': 'HS256',
            'typ': 'JWT',
            'kid': id
        }
        
        payload = {
            'iat': iat,
            'exp': exp,
            'aud': '/admin/'
        }
        
        ghost_token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
        
        return {
            'Authorization': f'Ghost {ghost_token}',
            'Content-Type': 'application/json'
        }
    except Exception as e:
        print(f"Error generating headers: {str(e)}")
        return None


if __name__ == '__main__':
    # Test the create_ghost_blog_post function
    post_params = {
        'title': 'Test Blog Post - ' + datetime.now().strftime('%Y-%m-%d %H:%M'),
        'content': '''
This is a test blog post created programmatically.

It includes multiple paragraphs to test the formatting.

And this is the third paragraph with some **bold** text.
        ''',
        'excerpt': 'This is a test excerpt for the blog post.',
        'tags': ['Test', 'API', 'Python'],
        'status': 'draft',  # Use 'draft' for testing, change to 'published' when ready
        'auto_format': True,
        'is_test': False  # Set to True to skip actual posting
    }
    
    print("Testing Ghost Blog API...")
    result_dict = create_ghost_blog_post(**post_params)
    
    if result_dict['success']:
        print(f"✅ Success! Post created at: {result_dict['url']}")
        print(f"   Post ID: {result_dict['post_id']}")
    else:
        print(f"❌ Failed: {result_dict['message']}")
    
    print("\nResult:", json.dumps(result_dict, indent=2))