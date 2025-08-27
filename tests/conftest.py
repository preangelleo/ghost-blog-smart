#!/usr/bin/env python3
"""
Test configuration and fixtures for Ghost Blog Smart API tests
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import json

# Set test environment variables
os.environ["IS_TEST_MODE"] = "true"
os.environ["GHOST_ADMIN_API_KEY"] = "test_key_id:test_secret_key"
os.environ["GHOST_API_URL"] = "https://test-ghost.example.com"
os.environ["GEMINI_API_KEY"] = "test_gemini_key"
os.environ["REPLICATE_API_TOKEN"] = "r8_test_replicate_token"
os.environ["FLASK_API_KEY"] = "test_api_key_for_auth"

# Import app after setting environment variables
from app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    yield flask_app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Headers with API key for authenticated requests"""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "test_api_key_for_auth",
        "X-Ghost-API-Key": "test_key_id:test_secret_key",
        "X-Ghost-API-URL": "https://test-ghost.example.com",
        "X-Gemini-API-Key": "test_gemini_key",
        "X-Replicate-API-Key": "r8_test_replicate_token",
    }


@pytest.fixture
def sample_post_data():
    """Sample blog post data for testing"""
    return {
        "title": "Test Blog Post",
        "content": "This is a test blog post content with **markdown** formatting.",
        "excerpt": "A test blog post for API testing",
        "tags": ["Test", "API", "Blog"],
        "status": "draft",
        "visibility": "public",
        "is_test": True,
    }


@pytest.fixture
def sample_smart_create_data():
    """Sample data for smart create endpoint"""
    return {
        "user_input": "Write about the benefits of AI in healthcare and its challenges",
        "status": "draft",
        "preferred_language": "English",
        "is_test": True,
    }


@pytest.fixture
def mock_ghost_response():
    """Mock successful Ghost API response"""
    return {
        "success": True,
        "message": "Post created successfully",
        "url": "https://test-ghost.example.com/test-post/",
        "post_id": "test_post_id_123",
        "slug": "test-post",
    }


@pytest.fixture
def mock_ghost_posts_response():
    """Mock Ghost posts listing response"""
    return {
        "success": True,
        "posts": [
            {
                "id": "post_1",
                "title": "Test Post 1",
                "status": "published",
                "excerpt": "First test post",
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z",
            },
            {
                "id": "post_2",
                "title": "Test Post 2",
                "status": "draft",
                "excerpt": "Second test post",
                "created_at": "2024-01-02T00:00:00.000Z",
                "updated_at": "2024-01-02T00:00:00.000Z",
            },
        ],
        "total": 2,
        "pages": 1,
    }


@pytest.fixture
def mock_post_details_response():
    """Mock single post details response"""
    return {
        "success": True,
        "post": {
            "id": "test_post_id_123",
            "title": "Test Blog Post",
            "content": "Full content of the test blog post",
            "excerpt": "A test blog post",
            "status": "published",
            "visibility": "public",
            "featured": False,
            "tags": ["Test", "API"],
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z",
            "published_at": "2024-01-01T00:00:00.000Z",
        },
    }


# Mock all ghost_blog_smart functions to prevent actual API calls during testing
@pytest.fixture(autouse=True)
def mock_ghost_functions():
    """Auto-mock all ghost_blog_smart functions"""

    with patch("ghost_blog_smart.create_ghost_blog_post") as mock_create, patch(
        "ghost_blog_smart.smart_blog_gateway"
    ) as mock_smart, patch("ghost_blog_smart.get_ghost_posts") as mock_get_posts, patch(
        "ghost_blog_smart.update_ghost_post"
    ) as mock_update, patch(
        "ghost_blog_smart.delete_ghost_post"
    ) as mock_delete, patch(
        "ghost_blog_smart.update_ghost_post_image"
    ) as mock_update_image, patch(
        "ghost_blog_smart.get_ghost_posts_advanced"
    ) as mock_get_advanced, patch(
        "ghost_blog_smart.get_ghost_post_details"
    ) as mock_get_details, patch(
        "ghost_blog_smart.get_posts_summary"
    ) as mock_summary, patch(
        "ghost_blog_smart.batch_get_post_details"
    ) as mock_batch, patch(
        "ghost_blog_smart.find_posts_by_date_pattern"
    ) as mock_date_search:

        # Configure default mock responses
        mock_create.return_value = {
            "success": True,
            "message": "Post created successfully",
            "url": "https://test-ghost.example.com/test-post/",
            "post_id": "test_post_id_123",
        }

        mock_smart.return_value = {
            "success": True,
            "response": "Smart blog post created successfully",
            "url": "https://test-ghost.example.com/ai-healthcare-benefits/",
            "post_id": "smart_post_123",
            "generated_title": "AI Healthcare Revolution: Benefits and Challenges",
            "generated_excerpt": "Exploring how AI transforms healthcare",
            "generated_tags": ["AI", "Healthcare", "Technology"],
        }

        mock_get_posts.return_value = {
            "success": True,
            "posts": [
                {"id": "post_1", "title": "Test Post 1", "status": "published"},
                {"id": "post_2", "title": "Test Post 2", "status": "draft"},
            ],
            "total": 2,
        }

        mock_update.return_value = {
            "success": True,
            "message": "Post updated successfully",
            "updates": ["title", "content"],
        }

        mock_delete.return_value = {
            "success": True,
            "message": "Post deleted successfully",
        }

        mock_update_image.return_value = {
            "success": True,
            "message": "Feature image updated successfully",
            "image_url": "https://test-ghost.example.com/content/images/test-image.jpg",
        }

        mock_get_advanced.return_value = {
            "success": True,
            "posts": [{"id": "search_post_1", "title": "AI Related Post"}],
            "total": 1,
        }

        mock_get_details.return_value = {
            "success": True,
            "post": {
                "id": "test_post_id_123",
                "title": "Test Blog Post",
                "content": "Full post content",
                "status": "published",
            },
        }

        mock_summary.return_value = {
            "success": True,
            "summary": {"total_posts": 10, "published": 8, "drafts": 2, "featured": 3},
        }

        mock_batch.return_value = {
            "success": True,
            "posts": [
                {"id": "batch_1", "title": "Batch Post 1"},
                {"id": "batch_2", "title": "Batch Post 2"},
            ],
        }

        mock_date_search.return_value = {
            "success": True,
            "posts": [{"id": "date_post_1", "title": "Date Filtered Post"}],
            "pattern": "2024-01",
        }

        yield {
            "create": mock_create,
            "smart": mock_smart,
            "get_posts": mock_get_posts,
            "update": mock_update,
            "delete": mock_delete,
            "update_image": mock_update_image,
            "get_advanced": mock_get_advanced,
            "get_details": mock_get_details,
            "summary": mock_summary,
            "batch": mock_batch,
            "date_search": mock_date_search,
        }
