#!/usr/bin/env python3
"""
Ghost Blog Smart Flask API
A REST API server for the ghost-blog-smart library with comprehensive blog management capabilities.
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


# ============================================================================
# HEALTH CHECK & INFO ENDPOINTS
# ============================================================================


@app.route("/", methods=["GET"])
def root():
    """Root endpoint - API information"""
    return standardize_response(
        data={
            "name": "Ghost Blog Smart API",
            "version": "1.0.0",
            "description": "REST API for Ghost CMS blog management with AI-powered features",
            "features": [
                "Smart blog creation with AI enhancement",
                "Dual image generation (Flux + Imagen)",
                "Comprehensive blog management",
                "Batch operations",
                "Multi-language support",
            ],
            "endpoints": {
                "health": "/health",
                "posts": "/api/posts",
                "smart_create": "/api/smart-create",
                "documentation": "See README.md for full API documentation",
            },
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return standardize_response(
        data={
            "status": "healthy",
            "uptime": "running",
            "features": {
                "ghost_integration": True,
                "ai_enhancement": True,
                "image_generation": True,
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

        # Required fields
        if "title" not in data or "content" not in data:
            return standardize_response(
                success=False,
                error="Missing required fields",
                message="title and content are required",
                status_code=400,
            )

        # Call ghost_blog_smart function
        result = create_ghost_blog_post(**data)

        if result.get("success"):
            return standardize_response(data=result)
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

        # Required field
        if "user_input" not in data:
            return standardize_response(
                success=False,
                error="Missing required field",
                message="user_input is required",
                status_code=400,
            )

        # Call smart gateway
        result = smart_blog_gateway(**data)

        if result.get("success"):
            return standardize_response(data=result)
        else:
            return standardize_response(
                success=False,
                error="Smart blog creation failed",
                message=result.get("response", "Unknown error"),
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
        # Extract query parameters
        params = {}
        if request.args.get("limit"):
            params["limit"] = int(request.args.get("limit"))
        if request.args.get("status"):
            params["status"] = request.args.get("status")
        if request.args.get("featured"):
            params["featured"] = request.args.get("featured").lower() == "true"

        # Add ghost credentials from environment or headers
        params.update(_extract_ghost_credentials())

        # Call function
        result = get_ghost_posts(**params)

        if result.get("success"):
            return standardize_response(data=result)
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

        # Extract query parameters
        for key in ["search", "tag", "author", "limit", "status", "visibility"]:
            if request.args.get(key):
                if key == "limit":
                    params[key] = int(request.args.get(key))
                else:
                    params[key] = request.args.get(key)

        # Date filtering
        if request.args.get("published_after"):
            params["published_after"] = request.args.get("published_after")
        if request.args.get("published_before"):
            params["published_before"] = request.args.get("published_before")

        params.update(_extract_ghost_credentials())

        result = get_ghost_posts_advanced(**params)

        if result.get("success"):
            return standardize_response(data=result)
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
        params = {"post_id": post_id}
        params.update(_extract_ghost_credentials())

        result = get_ghost_post_details(**params)

        if result.get("success"):
            return standardize_response(data=result)
        else:
            return standardize_response(
                success=False,
                error="Failed to retrieve post details",
                message=result.get("message", "Post not found"),
                status_code=404,
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
        data = validate_json()
        data["post_id"] = post_id
        data.update(_extract_ghost_credentials())

        result = update_ghost_post(**data)

        if result.get("success"):
            return standardize_response(data=result)
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
        data = validate_json()
        data["post_id"] = post_id
        data.update(_extract_ghost_credentials())

        result = update_ghost_post_image(**data)

        if result.get("success"):
            return standardize_response(data=result)
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
        params = {"post_id": post_id}
        params.update(_extract_ghost_credentials())

        result = delete_ghost_post(**params)

        if result.get("success"):
            return standardize_response(data=result)
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

        data.update(_extract_ghost_credentials())

        result = batch_get_post_details(**data)

        if result.get("success"):
            return standardize_response(data=result)
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
    """Get posts summary statistics"""
    try:
        params = {}
        if request.args.get("days"):
            params["days"] = int(request.args.get("days"))

        params.update(_extract_ghost_credentials())

        result = get_posts_summary(**params)

        if result.get("success"):
            return standardize_response(data=result)
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
    """Search posts by date pattern"""
    try:
        params = {}
        if request.args.get("pattern"):
            params["pattern"] = request.args.get("pattern")
        if request.args.get("limit"):
            params["limit"] = int(request.args.get("limit"))

        params.update(_extract_ghost_credentials())

        result = find_posts_by_date_pattern(**params)

        if result.get("success"):
            return standardize_response(data=result)
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

    logger.info(f"Starting Ghost Blog Smart API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API Key protection: {'Enabled' if REQUIRED_API_KEY else 'Disabled'}")

    app.run(host="0.0.0.0", port=port, debug=debug)
