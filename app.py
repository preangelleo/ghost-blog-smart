#!/usr/bin/env python3
"""
Ghost Blog Smart Flask API - FIXED VERSION
A REST API server for the ghost-blog-smart library with comprehensive blog management capabilities.
Enhanced with better error handling and validation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
import logging
from datetime import datetime
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, InternalServerError

# Import ghost_blog_smart functions
from ghost_blog_smart import (
    create_ghost_blog_post,
    smart_blog_gateway,
    get_ghost_posts,
    update_ghost_post,
    delete_ghost_post,
    update_ghost_post_image,
    get_ghost_posts_advanced,
    get_ghost_post_details,
    get_posts_summary,
    batch_get_post_details,
    find_posts_by_date_pattern,
    GhostBlogSmart,
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
API_KEY_HEADER = "X-API-Key"
REQUIRED_API_KEY = os.environ.get("FLASK_API_KEY")

# ============================================================================
# AUTHENTICATION & MIDDLEWARE
# ============================================================================


def require_api_key(f):
    """Decorator to require API key authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if REQUIRED_API_KEY:  # Only check if API key is configured
            api_key = request.headers.get(API_KEY_HEADER)
            if not api_key or api_key != REQUIRED_API_KEY:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Invalid or missing API key",
                            "message": f"Include {API_KEY_HEADER} header with valid API key",
                        }
                    ),
                    401,
                )
        return f(*args, **kwargs)

    return decorated_function


def validate_json():
    """Validate that request contains JSON data"""
    if not request.is_json:
        raise BadRequest("Content-Type must be application/json")
    return request.get_json() or {}


def standardize_response(
    success=True, data=None, error=None, message=None, status_code=200
):
    """Standardize API response format"""
    response = {"success": success, "timestamp": datetime.utcnow().isoformat() + "Z"}

    if success:
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
    else:
        response["error"] = error or "Unknown error occurred"
        if message:
            response["message"] = message

    return jsonify(response), status_code


def safe_call_ghost_function(func, **kwargs):
    """
    Safely call a ghost_blog_smart function with enhanced error handling
    """
    try:
        result = func(**kwargs)

        # Handle different response formats
        if isinstance(result, dict):
            if result.get("success"):
                return {"success": True, "data": result}
            else:
                return {
                    "success": False,
                    "message": result.get("message", "Operation failed"),
                    "error": result.get("error"),
                }
        else:
            # Handle non-dict responses
            return {"success": True, "data": {"result": result}}

    except Exception as e:
        logger.error(f"Error calling {func.__name__}: {str(e)}")
        return {
            "success": False,
            "message": f"Internal error in {func.__name__}: {str(e)}",
        }


# ============================================================================
# HEALTH CHECK & INFO ENDPOINTS
# ============================================================================


@app.route("/", methods=["GET"])
def root():
    """Root endpoint - API information"""
    return standardize_response(
        data={
            "name": "Ghost Blog Smart API",
            "version": "1.1.0",  # Updated version
            "description": "REST API for Ghost CMS blog management with AI-powered features",
            "features": [
                "Smart blog creation with AI enhancement",
                "Dual image generation (Flux + Imagen)",
                "Comprehensive blog management",
                "Batch operations",
                "Multi-language support",
                "Enhanced error handling",
                "Better input validation",
            ],
            "endpoints": {
                "health": "/health",
                "posts": "/api/posts",
                "smart_create": "/api/smart-create",
                "documentation": "See README.md for full API documentation",
            },
            "improvements": [
                "Fixed Posts Summary NoneType errors",
                "Enhanced post ID validation",
                "Better error handling across all endpoints",
                "Improved input sanitization",
            ],
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return standardize_response(
        data={
            "status": "healthy",
            "uptime": "running",
            "version": "1.1.0",
            "features": {
                "ghost_integration": True,
                "ai_enhancement": True,
                "image_generation": True,
                "enhanced_error_handling": True,
            },
        }
    )


# ============================================================================
# BLOG CREATION ENDPOINTS
# ============================================================================


@app.route("/api/posts", methods=["POST"])
@require_api_key
def create_post():
    """Create a new blog post"""
    try:
        data = validate_json()

        # Required fields validation
        if "title" not in data or "content" not in data:
            return standardize_response(
                success=False,
                error="Missing required fields",
                message="title and content are required",
                status_code=400,
            )

        # Sanitize inputs
        data["title"] = str(data["title"]).strip()
        data["content"] = str(data["content"]).strip()

        if not data["title"] or not data["content"]:
            return standardize_response(
                success=False,
                error="Empty required fields",
                message="title and content cannot be empty",
                status_code=400,
            )

        # Add credentials
        data.update(_extract_ghost_credentials())

        # Call ghost_blog_smart function
        result = safe_call_ghost_function(create_ghost_blog_post, **data)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Blog post creation failed",
                message=result.get("message", "Unknown error"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


@app.route("/api/smart-create", methods=["POST"])
@require_api_key
def smart_create_post():
    """Create blog post using AI-powered smart gateway"""
    try:
        data = validate_json()

        # Required field validation
        if "user_input" not in data:
            return standardize_response(
                success=False,
                error="Missing required field",
                message="user_input is required",
                status_code=400,
            )

        # Sanitize input
        data["user_input"] = str(data["user_input"]).strip()

        if not data["user_input"]:
            return standardize_response(
                success=False,
                error="Empty user input",
                message="user_input cannot be empty",
                status_code=400,
            )

        # Add credentials
        data.update(_extract_ghost_credentials())

        # Call smart gateway
        result = safe_call_ghost_function(smart_blog_gateway, **data)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Smart blog creation failed",
                message=result.get("message", "Unknown error"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error in smart create: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# BLOG RETRIEVAL ENDPOINTS
# ============================================================================


@app.route("/api/posts", methods=["GET"])
@require_api_key
def get_posts():
    """Get blog posts with optional filtering"""
    try:
        # Extract query parameters with validation
        params = {}

        # Validate and convert limit
        if request.args.get("limit"):
            try:
                limit = int(request.args.get("limit"))
                params["limit"] = max(1, min(limit, 100))  # Clamp between 1-100
            except ValueError:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="limit must be a valid integer between 1 and 100",
                    status_code=400,
                )

        # Validate status
        if request.args.get("status"):
            status = request.args.get("status").lower()
            if status not in ["published", "draft", "scheduled", "all"]:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="status must be one of: published, draft, scheduled, all",
                    status_code=400,
                )
            params["status"] = status

        # Validate featured
        if request.args.get("featured"):
            featured_str = request.args.get("featured").lower()
            if featured_str in ["true", "1", "yes"]:
                params["featured"] = True
            elif featured_str in ["false", "0", "no"]:
                params["featured"] = False
            else:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="featured must be true or false",
                    status_code=400,
                )

        # Add ghost credentials
        params.update(_extract_ghost_credentials())

        # Call function
        result = safe_call_ghost_function(get_ghost_posts, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to retrieve posts",
                message=result.get("message", "Unknown error"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error retrieving posts: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


@app.route("/api/posts/advanced", methods=["GET"])
@require_api_key
def get_posts_advanced():
    """Get posts with advanced filtering options"""
    try:
        params = {}

        # Extract and validate query parameters
        for key in ["search", "tag", "author", "status", "visibility"]:
            if request.args.get(key):
                value = str(request.args.get(key)).strip()
                if value:  # Only add non-empty values
                    params[key] = value

        # Validate and convert limit
        if request.args.get("limit"):
            try:
                limit = int(request.args.get("limit"))
                params["limit"] = max(1, min(limit, 100))  # Clamp between 1-100
            except ValueError:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="limit must be a valid integer",
                    status_code=400,
                )

        # Date filtering with validation
        for date_param in ["published_after", "published_before"]:
            if request.args.get(date_param):
                date_str = request.args.get(date_param)
                try:
                    # Validate date format
                    datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    params[date_param] = date_str
                except ValueError:
                    return standardize_response(
                        success=False,
                        error="Invalid parameter",
                        message=f"{date_param} must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                        status_code=400,
                    )

        params.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(get_ghost_posts_advanced, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to retrieve posts",
                message=result.get("message", "Unknown error"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error in advanced posts retrieval: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


@app.route("/api/posts/<post_id>", methods=["GET"])
@require_api_key
def get_post_details(post_id):
    """Get detailed information about a specific post"""
    try:
        # Validate post_id
        if not post_id or not str(post_id).strip():
            return standardize_response(
                success=False,
                error="Invalid post ID",
                message="Post ID cannot be empty",
                status_code=400,
            )

        params = {"post_id": str(post_id).strip()}
        params.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(get_ghost_post_details, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            # Return 404 for post not found, 400 for other errors
            status_code = (
                404 if "not found" in result.get("message", "").lower() else 400
            )
            return standardize_response(
                success=False,
                error="Failed to retrieve post details",
                message=result.get("message", "Post not found"),
                status_code=status_code,
            )

    except Exception as e:
        logger.error(f"Error retrieving post details: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# BLOG UPDATE ENDPOINTS
# ============================================================================


@app.route("/api/posts/<post_id>", methods=["PUT", "PATCH"])
@require_api_key
def update_post(post_id):
    """Update an existing blog post"""
    try:
        # Validate post_id
        if not post_id or not str(post_id).strip():
            return standardize_response(
                success=False,
                error="Invalid post ID",
                message="Post ID cannot be empty",
                status_code=400,
            )

        data = validate_json()

        # Ensure we have some data to update
        if not data:
            return standardize_response(
                success=False,
                error="No data provided",
                message="Request body must contain fields to update",
                status_code=400,
            )

        data["post_id"] = str(post_id).strip()
        data.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(update_ghost_post, **data)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to update post",
                message=result.get("message", "Update failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


@app.route("/api/posts/<post_id>/image", methods=["PUT"])
@require_api_key
def update_post_image(post_id):
    """Update the feature image of a blog post"""
    try:
        # Validate post_id
        if not post_id or not str(post_id).strip():
            return standardize_response(
                success=False,
                error="Invalid post ID",
                message="Post ID cannot be empty",
                status_code=400,
            )

        data = validate_json()
        data["post_id"] = str(post_id).strip()
        data.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(update_ghost_post_image, **data)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to update post image",
                message=result.get("message", "Image update failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error updating post image: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# BLOG DELETION ENDPOINTS
# ============================================================================


@app.route("/api/posts/<post_id>", methods=["DELETE"])
@require_api_key
def delete_post(post_id):
    """Delete a blog post"""
    try:
        # Validate post_id
        if not post_id or not str(post_id).strip():
            return standardize_response(
                success=False,
                error="Invalid post ID",
                message="Post ID cannot be empty",
                status_code=400,
            )

        params = {"post_id": str(post_id).strip()}
        params.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(delete_ghost_post, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to delete post",
                message=result.get("message", "Deletion failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error deleting post: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# BATCH OPERATIONS ENDPOINTS
# ============================================================================


@app.route("/api/posts/batch-details", methods=["POST"])
@require_api_key
def batch_post_details():
    """Get details for multiple posts"""
    try:
        data = validate_json()

        if "post_ids" not in data:
            return standardize_response(
                success=False,
                error="Missing required field",
                message="post_ids array is required",
                status_code=400,
            )

        post_ids = data["post_ids"]

        # Validate post_ids is a list
        if not isinstance(post_ids, list):
            return standardize_response(
                success=False,
                error="Invalid data type",
                message="post_ids must be an array",
                status_code=400,
            )

        # Validate and clean post IDs
        valid_post_ids = [
            str(pid).strip() for pid in post_ids if pid and str(pid).strip()
        ]

        if not valid_post_ids:
            return standardize_response(
                success=False,
                error="No valid post IDs",
                message="post_ids array must contain at least one valid ID",
                status_code=400,
            )

        data["post_ids"] = valid_post_ids
        data.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(batch_get_post_details, **data)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Batch operation failed",
                message=result.get("message", "Batch retrieval failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error in batch operation: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


@app.route("/api/posts/summary", methods=["GET"])
@require_api_key
def posts_summary():
    """Get posts summary statistics - FIXED VERSION"""
    try:
        params = {}

        # Handle days parameter properly
        if request.args.get("days"):
            try:
                days = int(request.args.get("days"))
                if days < 0:
                    return standardize_response(
                        success=False,
                        error="Invalid parameter",
                        message="days must be a positive integer",
                        status_code=400,
                    )
                params["days"] = days
            except ValueError:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="days must be a valid integer",
                    status_code=400,
                )

        # Add status filter if provided
        if request.args.get("status"):
            status = request.args.get("status").lower()
            if status not in ["published", "draft", "scheduled", "all"]:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="status must be one of: published, draft, scheduled, all",
                    status_code=400,
                )
            params["status"] = status

        params.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(get_posts_summary, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Failed to get summary",
                message=result.get("message", "Summary retrieval failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================


@app.route("/api/posts/search/by-date-pattern", methods=["GET"])
@require_api_key
def search_by_date_pattern():
    """Search posts by date pattern - FIXED VERSION"""
    try:
        params = {}

        # Get pattern parameter
        if request.args.get("pattern"):
            pattern = str(request.args.get("pattern")).strip()
            if pattern:
                params["pattern"] = pattern

        # Validate and convert limit
        if request.args.get("limit"):
            try:
                limit = int(request.args.get("limit"))
                params["limit"] = max(1, min(limit, 100))  # Clamp between 1-100
            except ValueError:
                return standardize_response(
                    success=False,
                    error="Invalid parameter",
                    message="limit must be a valid integer",
                    status_code=400,
                )

        params.update(_extract_ghost_credentials())

        result = safe_call_ghost_function(find_posts_by_date_pattern, **params)

        if result.get("success"):
            return standardize_response(data=result.get("data"))
        else:
            return standardize_response(
                success=False,
                error="Date pattern search failed",
                message=result.get("message", "Search failed"),
                status_code=400,
            )

    except Exception as e:
        logger.error(f"Error in date pattern search: {str(e)}")
        return standardize_response(
            success=False,
            error="Internal server error",
            message=str(e),
            status_code=500,
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _extract_ghost_credentials():
    """Extract Ghost credentials from headers or environment"""
    credentials = {}

    # Try headers first, then environment
    ghost_api_key = request.headers.get("X-Ghost-API-Key") or os.environ.get(
        "GHOST_ADMIN_API_KEY"
    )
    ghost_api_url = request.headers.get("X-Ghost-API-URL") or os.environ.get(
        "GHOST_API_URL"
    )
    gemini_api_key = request.headers.get("X-Gemini-API-Key") or os.environ.get(
        "GEMINI_API_KEY"
    )
    replicate_api_key = request.headers.get("X-Replicate-API-Key") or os.environ.get(
        "REPLICATE_API_TOKEN"
    )

    if ghost_api_key:
        credentials["ghost_admin_api_key"] = ghost_api_key
    if ghost_api_url:
        credentials["ghost_api_url"] = ghost_api_url
    if gemini_api_key:
        credentials["gemini_api_key"] = gemini_api_key
    if replicate_api_key:
        credentials["replicate_api_key"] = replicate_api_key

    return credentials


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.errorhandler(400)
def bad_request(e):
    return standardize_response(
        success=False, error="Bad Request", message=str(e.description), status_code=400
    )


@app.errorhandler(401)
def unauthorized(e):
    return standardize_response(
        success=False,
        error="Unauthorized",
        message="Authentication required",
        status_code=401,
    )


@app.errorhandler(404)
def not_found(e):
    return standardize_response(
        success=False,
        error="Not Found",
        message="The requested resource was not found",
        status_code=404,
    )


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return standardize_response(
        success=False,
        error="Internal Server Error",
        message="An unexpected error occurred",
        status_code=500,
    )


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    logger.info(f"Starting Ghost Blog Smart API v1.1.0 on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API Key protection: {'Enabled' if REQUIRED_API_KEY else 'Disabled'}")

    app.run(host="0.0.0.0", port=port, debug=debug)
