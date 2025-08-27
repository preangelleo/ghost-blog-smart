#!/usr/bin/env python3
"""
GhostBlogSmart Client Class
Provides a conventional class-based interface for the ghost-blog-smart library.
This allows code assistants to use the library in the expected way.
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Import all the existing functions
from .main_functions import (
    create_ghost_blog_post,
    update_ghost_post,
    update_ghost_post_image,
    get_ghost_posts,
    delete_ghost_post,
    generate_ghost_headers,
)

from .post_management import (
    get_ghost_post_details,
    get_ghost_posts_advanced,
    get_posts_summary,
    batch_get_post_details,
    find_posts_by_date_pattern,
)

from .smart_gateway import smart_blog_gateway

from .clean_imagen_generator import CleanImagenGenerator

# Load environment variables
load_dotenv()


class GhostBlogSmart:
    """
    GhostBlogSmart Client - Main class for interacting with Ghost CMS

    This class provides a conventional interface for all ghost-blog-smart functionality.
    It wraps all the existing functions in a class-based API that code assistants expect.

    Usage:
        # Initialize with default environment variables
        client = GhostBlogSmart()

        # Or initialize with custom credentials
        client = GhostBlogSmart(
            ghost_url="https://your-ghost-site.com",
            ghost_api_key="your-api-key",
            gemini_api_key="your-gemini-key"
        )

        # Create a blog post
        result = client.create_post(
            title="My Blog Post",
            content="This is the content of my blog post..."
        )
    """

    def __init__(
        self,
        ghost_url: Optional[str] = None,
        ghost_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
    ):
        """
        Initialize GhostBlogSmart client

        Args:
            ghost_url: Ghost blog URL (optional, defaults to GHOST_API_URL env var)
            ghost_api_key: Ghost Admin API key (optional, defaults to GHOST_ADMIN_API_KEY env var)
            gemini_api_key: Gemini API key (optional, defaults to GEMINI_API_KEY env var)
        """
        # Set up API credentials with fallback to environment variables
        self.ghost_api_url = (
            ghost_url or os.getenv("GHOST_API_URL") or os.getenv("GHOST_BLOG_URL")
        )
        self.ghost_admin_api_key = (
            ghost_api_key
            or os.getenv("GHOST_ADMIN_API_KEY")
            or os.getenv("GHOST_BLOG_ADMIN_API_KEY")
        )
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        # Validate required credentials
        if not self.ghost_api_url:
            raise ValueError(
                "Ghost API URL is required. Set GHOST_API_URL environment variable or pass ghost_url parameter."
            )
        if not self.ghost_admin_api_key:
            raise ValueError(
                "Ghost Admin API Key is required. Set GHOST_ADMIN_API_KEY environment variable or pass ghost_api_key parameter."
            )

    def _prepare_kwargs(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare kwargs with API credentials for function calls

        Args:
            **kwargs: Additional parameters

        Returns:
            Dictionary with API credentials and other parameters
        """
        result = kwargs.copy()
        result.setdefault("ghost_api_url", self.ghost_api_url)
        result.setdefault("ghost_admin_api_key", self.ghost_admin_api_key)
        if self.gemini_api_key:
            result.setdefault("gemini_api_key", self.gemini_api_key)
        return result

    # ============================================================================
    # BLOG POST CREATION METHODS
    # ============================================================================

    def create_post(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new blog post

        Args:
            title: Blog post title
            content: Blog post content (markdown or plain text)
            **kwargs: Additional parameters (excerpt, tags, status, etc.)

        Returns:
            Dict with success status, URL, and post ID
        """
        params = self._prepare_kwargs(title=title, content=content, **kwargs)
        return create_ghost_blog_post(**params)

    def smart_create_post(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        Create a blog post using AI-powered smart gateway

        Args:
            user_input: Raw content, ideas, or complete blog post
            **kwargs: Additional parameters (status, preferred_language, etc.)

        Returns:
            Dict with success status, URL, and post ID
        """
        params = self._prepare_kwargs(**kwargs)
        return smart_blog_gateway(user_input, **params)

    def create_post_from_readme(self, readme_content: str, **kwargs) -> Dict[str, Any]:
        """
        Create a blog post from README content using smart gateway

        Args:
            readme_content: README file content
            **kwargs: Additional parameters

        Returns:
            Dict with success status, URL, and post ID
        """
        params = self._prepare_kwargs(**kwargs)
        return smart_blog_gateway(readme_content, **params)

    # ============================================================================
    # BLOG POST MANAGEMENT METHODS
    # ============================================================================

    def get_posts(self, **kwargs) -> Dict[str, Any]:
        """
        Get list of blog posts

        Args:
            **kwargs: Query parameters (limit, page, status, etc.)

        Returns:
            Dict with success status and list of posts
        """
        params = self._prepare_kwargs(**kwargs)
        return get_ghost_posts(**params)

    def get_posts_advanced(self, **kwargs) -> Dict[str, Any]:
        """
        Get posts with advanced filtering options

        Args:
            **kwargs: Advanced filter parameters

        Returns:
            Dict with success status and filtered posts
        """
        params = self._prepare_kwargs(**kwargs)
        return get_ghost_posts_advanced(**params)

    def get_post_details(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get detailed information about a specific post

        Args:
            post_id: The Ghost post ID
            **kwargs: Options for included content

        Returns:
            Dict with success status and complete post details
        """
        params = self._prepare_kwargs(**kwargs)
        return get_ghost_post_details(post_id, **params)

    def get_posts_summary(
        self, date_from=None, date_to=None, **kwargs
    ) -> Dict[str, Any]:
        """
        Get a summary of posts with basic info

        Args:
            date_from: Start date for filtering
            date_to: End date for filtering
            **kwargs: Additional filters

        Returns:
            Dict with post summaries
        """
        params = self._prepare_kwargs(**kwargs)
        return get_posts_summary(date_from, date_to, **params)

    # ============================================================================
    # BLOG POST UPDATE METHODS
    # ============================================================================

    def update_post(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update various properties of a blog post

        Args:
            post_id: The ID of the post to update
            **kwargs: Fields to update (title, content, status, featured, etc.)

        Returns:
            Dict with success status and update info
        """
        params = self._prepare_kwargs(**kwargs)
        return update_ghost_post(post_id, **params)

    def update_post_image(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update the feature image of a blog post

        Args:
            post_id: The ID of the post to update
            **kwargs: Image update parameters

        Returns:
            Dict with success status and image info
        """
        params = self._prepare_kwargs(**kwargs)
        return update_ghost_post_image(post_id, **params)

    def delete_post(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Delete a blog post

        Args:
            post_id: The ID of the post to delete
            **kwargs: Additional parameters

        Returns:
            Dict with success status
        """
        params = self._prepare_kwargs(**kwargs)
        return delete_ghost_post(post_id, **params)

    # ============================================================================
    # BATCH OPERATIONS
    # ============================================================================

    def batch_get_post_details(self, post_ids: List[str], **kwargs) -> Dict[str, Any]:
        """
        Get details for multiple posts at once

        Args:
            post_ids: List of post IDs to fetch
            **kwargs: Options for included content

        Returns:
            Dict with details for all requested posts
        """
        params = self._prepare_kwargs(**kwargs)
        return batch_get_post_details(post_ids, **params)

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def find_posts_by_date_pattern(self, **kwargs) -> Dict[str, Any]:
        """
        Find posts that match specific date patterns

        Args:
            **kwargs: Date pattern parameters (year, month, day, etc.)

        Returns:
            Dict with posts matching the date pattern
        """
        params = self._prepare_kwargs(**kwargs)
        return find_posts_by_date_pattern(**params)

    def generate_headers(self) -> Optional[Dict[str, str]]:
        """
        Generate Ghost API headers for manual requests

        Returns:
            Dict with Authorization and Content-Type headers
        """
        return generate_ghost_headers(self.ghost_admin_api_key)

    def create_image_generator(self) -> CleanImagenGenerator:
        """
        Create an image generator instance

        Returns:
            CleanImagenGenerator instance
        """
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required for image generation")
        return CleanImagenGenerator(api_key=self.gemini_api_key)

    # ============================================================================
    # CONVENIENCE PROPERTIES
    # ============================================================================

    @property
    def is_configured(self) -> bool:
        """Check if client is properly configured"""
        return bool(self.ghost_api_url and self.ghost_admin_api_key)

    @property
    def has_ai_features(self) -> bool:
        """Check if AI features are available (requires Gemini API key)"""
        return bool(self.gemini_api_key)

    def __repr__(self) -> str:
        """String representation of the client"""
        status = "configured" if self.is_configured else "not configured"
        ai_status = (
            "with AI features" if self.has_ai_features else "without AI features"
        )
        return f"GhostBlogSmart(status={status}, {ai_status})"

    def __str__(self) -> str:
        """Human-readable string representation"""
        return self.__repr__()


# ============================================================================
# CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================


def create_client(
    ghost_url: Optional[str] = None,
    ghost_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
) -> GhostBlogSmart:
    """
    Convenience function to create a GhostBlogSmart client

    Args:
        ghost_url: Ghost blog URL
        ghost_api_key: Ghost Admin API key
        gemini_api_key: Gemini API key for AI features

    Returns:
        Configured GhostBlogSmart client
    """
    return GhostBlogSmart(
        ghost_url=ghost_url, ghost_api_key=ghost_api_key, gemini_api_key=gemini_api_key
    )


if __name__ == "__main__":
    # Example usage
    print("GhostBlogSmart Client Example")
    print("=" * 50)

    try:
        # Create client with environment variables
        client = GhostBlogSmart()
        print(f"✅ Client created: {client}")

        # Example: Get posts
        print("\n📚 Getting recent posts...")
        result = client.get_posts(limit=3)
        if result["success"]:
            print(f"   Found {len(result['posts'])} posts")
            for post in result["posts"]:
                print(f"   - {post['title']} ({post['status']})")
        else:
            print(f"   ❌ Error: {result['message']}")

    except Exception as e:
        print(f"❌ Error creating client: {e}")
        print("💡 Make sure your environment variables are set:")
        print("   - GHOST_API_URL or GHOST_BLOG_URL")
        print("   - GHOST_ADMIN_API_KEY or GHOST_BLOG_ADMIN_API_KEY")
        print("   - GEMINI_API_KEY (optional, for AI features)")
