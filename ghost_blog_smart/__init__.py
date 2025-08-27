"""
Ghost Blog Smart - A powerful Python API for creating Ghost CMS blog posts with AI-powered features

This library supports two usage patterns:

1. Class-based (Recommended for code assistants):
   ```python
   from ghost_blog_smart import GhostBlogSmart
   
   client = GhostBlogSmart()
   result = client.create_post(title="My Post", content="Content...")
   ```

2. Function-based (Direct):
   ```python
   from ghost_blog_smart import create_ghost_blog_post
   
   result = create_ghost_blog_post(title="My Post", content="Content...")
   ```

Both approaches work with the same underlying functions and provide identical functionality.
"""

__version__ = "1.0.16"
__author__ = "leowang.net"
__email__ = "me@leowang.net"

# Import the main client class
from .client import GhostBlogSmart, create_client

# Import main functions for direct access
from .main_functions import (
    create_ghost_blog_post,
    update_ghost_post,
    update_ghost_post_image,
    get_ghost_posts,
    delete_ghost_post,
    generate_ghost_headers
)

from .post_management import (
    get_ghost_post_details,
    get_ghost_posts_advanced,
    get_posts_summary,
    batch_get_post_details,
    find_posts_by_date_pattern
)

from .smart_gateway import (
    smart_blog_gateway
)

from .clean_imagen_generator import (
    CleanImagenGenerator
)

from .blog_post_refine_prompt import (
    BLOG_POST_REFINE_SYSTEM_PROMPT,
    get_refine_prompt_with_language
)

from .blog_to_image_prompt import (
    BLOG_TO_IMAGE_SYSTEM_PROMPT,
    generate_blog_image_prompt
)


def __getattr__(name):
    """
    Provide helpful error messages for common import mistakes
    """
    if name in ['GhostBlogSmartClient', 'GhostClient', 'Client']:
        raise ImportError(
            f"'{name}' not found. Did you mean 'GhostBlogSmart'?\n"
            "Try: from ghost_blog_smart import GhostBlogSmart\n"
            "Then: client = GhostBlogSmart()"
        )
    
    if name in ['GhostBlog', 'Ghost', 'BlogSmart']:
        raise ImportError(
            f"'{name}' not found. The main class is 'GhostBlogSmart'.\n"
            "Try: from ghost_blog_smart import GhostBlogSmart\n"
            "Then: client = GhostBlogSmart()"
        )
    
    # For other unknown attributes, provide general guidance
    raise AttributeError(
        f"module '{__name__}' has no attribute '{name}'\n\n"
        "💡 Available usage patterns:\n\n"
        "1. Class-based (recommended):\n"
        "   from ghost_blog_smart import GhostBlogSmart\n"
        "   client = GhostBlogSmart()\n"
        "   result = client.create_post(title='...', content='...')\n\n"
        "2. Function-based:\n"
        "   from ghost_blog_smart import create_ghost_blog_post\n"
        "   result = create_ghost_blog_post(title='...', content='...')\n\n"
        "📚 See example_usage.py for more examples."
    )


__all__ = [
    # Main client class (NEW - recommended)
    'GhostBlogSmart',
    'create_client',
    
    # Main functions (existing)
    'create_ghost_blog_post',
    'update_ghost_post',
    'update_ghost_post_image',
    'get_ghost_posts',
    'delete_ghost_post',
    'generate_ghost_headers',
    
    # Post management
    'get_ghost_post_details',
    'get_ghost_posts_advanced',
    'get_posts_summary',
    'batch_get_post_details',
    'find_posts_by_date_pattern',
    
    # Classes
    'CleanImagenGenerator',
    
    # Smart Gateway
    'smart_blog_gateway',
    
    # Prompts
    'BLOG_POST_REFINE_SYSTEM_PROMPT',
    'get_refine_prompt_with_language',
    'BLOG_TO_IMAGE_SYSTEM_PROMPT',
    'generate_blog_image_prompt',
]