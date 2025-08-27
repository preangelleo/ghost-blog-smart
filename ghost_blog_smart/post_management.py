#!/usr/bin/env python3
"""
Enhanced Ghost Blog Post Management Functions - FIXED VERSION
Provides advanced querying, filtering, and batch operations for Ghost CMS posts
"""

import os
import jwt
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default credentials from environment
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY")
GHOST_API_URL = os.getenv("GHOST_API_URL")


def get_ghost_posts_advanced(**kwargs) -> Dict[str, Any]:
    """
    Advanced post listing with enhanced filtering options

    Parameters:
        # Pagination & Limits
        limit (int): Number of posts per page (default: 15, max: all)
        page (int): Page number for pagination (default: 1)
        get_all (bool): Get all posts ignoring pagination (default: False)

        # Status & Visibility Filters
        status (str): 'published', 'draft', 'scheduled', 'all' (default: 'all')
        visibility (str): 'public', 'members', 'paid', 'all' (default: 'all')
        featured (bool): Filter by featured status (optional)

        # Date Range Filters
        published_after (str/datetime): Posts published after this date
        published_before (str/datetime): Posts published before this date
        created_after (str/datetime): Posts created after this date
        created_before (str/datetime): Posts created before this date
        updated_after (str/datetime): Posts updated after this date
        updated_before (str/datetime): Posts updated before this date

        # Content Filters
        tag (str): Filter by specific tag slug
        author (str): Filter by author slug
        search (str): Search in title and content

        # Sorting
        order (str): Sort order 'published_at DESC', 'created_at ASC', etc.

        # Output Options
        fields (list): Specific fields to include
        include_content (bool): Include full content (default: False)
        include_html (bool): Include HTML content (default: False)

        # API Credentials
        ghost_admin_api_key (str): Override env Ghost API key
        ghost_api_url (str): Override env Ghost API URL

    Returns:
        dict: {
            'success': bool,
            'posts': list of post objects,
            'total': total number of posts,
            'pages': total pages,
            'meta': pagination metadata
        }
    """
    try:
        # Get API credentials
        admin_key = kwargs.get("ghost_admin_api_key") or GHOST_ADMIN_API_KEY
        api_url = kwargs.get("ghost_api_url") or GHOST_API_URL

        if not admin_key or not api_url:
            return {"success": False, "message": "Ghost API credentials not provided"}

        # Parse admin API key
        if ":" not in admin_key:
            return {"success": False, "message": "Invalid admin API key format"}

        id, secret = admin_key.split(":")

        # Generate JWT token
        iat = int(time.time())
        exp = iat + 5 * 60

        header = {"alg": "HS256", "typ": "JWT", "kid": id}
        payload = {"iat": iat, "exp": exp, "aud": "/admin/"}

        ghost_token = jwt.encode(
            payload, bytes.fromhex(secret), algorithm="HS256", headers=header
        )

        # Build query parameters
        params = {}

        # Pagination
        if kwargs.get("get_all"):
            params["limit"] = "all"
        else:
            params["limit"] = kwargs.get("limit", 15)
            params["page"] = kwargs.get("page", 1)

        # Build filters
        filters = []

        # Status filter
        status = kwargs.get("status", "all")
        if status != "all":
            filters.append(f"status:{status}")

        # Visibility filter
        visibility = kwargs.get("visibility", "all")
        if visibility != "all":
            filters.append(f"visibility:{visibility}")

        # Featured filter
        if "featured" in kwargs:
            filters.append(f'featured:{str(kwargs["featured"]).lower()}')

        # Date range filters
        date_filters = {
            "published_after": "published_at:>",
            "published_before": "published_at:<",
            "created_after": "created_at:>",
            "created_before": "created_at:<",
            "updated_after": "updated_at:>",
            "updated_before": "updated_at:<",
        }

        for key, ghost_filter in date_filters.items():
            if key in kwargs and kwargs[key] is not None:
                date_value = kwargs[key]
                # Convert datetime to ISO format
                if hasattr(date_value, "isoformat"):
                    date_value = date_value.isoformat()
                # Ensure proper format
                if "T" not in str(date_value):
                    date_value = str(date_value) + "T00:00:00.000Z"
                elif not str(date_value).endswith('Z'):
                    if not str(date_value).endswith('+00:00'):
                        date_value = str(date_value) + "Z"
                filters.append(f"{ghost_filter}'{date_value}'")

        # Tag filter
        if "tag" in kwargs and kwargs["tag"]:
            filters.append(f'tag:{kwargs["tag"]}')

        # Author filter
        if "author" in kwargs and kwargs["author"]:
            filters.append(f'author:{kwargs["author"]}')

        # Combine filters
        if filters:
            params["filter"] = "+".join(filters)

        # Search
        if "search" in kwargs and kwargs["search"]:
            params["search"] = kwargs["search"]

        # Sorting
        if "order" in kwargs:
            params["order"] = kwargs["order"]
        else:
            params["order"] = "published_at DESC"

        # Include options
        includes = ["tags", "authors"]
        if kwargs.get("include_content"):
            includes.append("mobiledoc")
        params["include"] = ",".join(includes)

        # Formats
        formats = []
        if kwargs.get("include_html"):
            formats.append("html")
        if kwargs.get("include_content"):
            formats.append("mobiledoc")
        if formats:
            params["formats"] = ",".join(formats)

        # Specific fields
        if "fields" in kwargs and kwargs["fields"]:
            params["fields"] = ",".join(kwargs["fields"])

        # Make request
        headers = {
            "Authorization": f"Ghost {ghost_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{api_url}/ghost/api/admin/posts/", headers=headers, params=params
        )

        if response.status_code == 200:
            data = response.json()
            meta = data.get("meta", {})
            posts = data.get("posts", [])

            # Enhanced response
            result = {
                "success": True,
                "posts": posts,
                "total": meta.get("pagination", {}).get("total", len(posts)),
                "pages": meta.get("pagination", {}).get("pages", 1),
                "page": meta.get("pagination", {}).get("page", 1),
                "limit": meta.get("pagination", {}).get("limit", len(posts)),
                "meta": meta,
            }

            # Add summary info
            if posts:
                result["summary"] = {
                    "first_post_date": posts[-1].get("published_at"),
                    "last_post_date": posts[0].get("published_at"),
                    "post_count": len(posts),
                }

            return result
        else:
            return {
                "success": False,
                "message": f"Failed to get posts: {response.status_code}",
                "error": response.text,
            }

    except Exception as e:
        return {"success": False, "message": f"Error getting posts: {str(e)}"}


def get_ghost_post_details(post_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get complete details of a specific Ghost post by ID

    Parameters:
        post_id (str): The Ghost post ID
        include_html (bool): Include HTML content (default: True)
        include_mobiledoc (bool): Include Mobiledoc/Lexical content (default: True)
        include_tags (bool): Include tags (default: True)
        include_authors (bool): Include authors (default: True)
        include_count (bool): Include view count stats (default: False)
        ghost_admin_api_key (str): Override env Ghost API key
        ghost_api_url (str): Override env Ghost API URL

    Returns:
        dict: {
            'success': bool,
            'post': Complete post object with all details,
            'message': Error message if failed
        }
    """
    try:
        # Validate post_id
        if not post_id or post_id.strip() == "":
            return {"success": False, "message": "Post ID is required"}

        # Get API credentials
        admin_key = kwargs.get("ghost_admin_api_key") or GHOST_ADMIN_API_KEY
        api_url = kwargs.get("ghost_api_url") or GHOST_API_URL

        if not admin_key or not api_url:
            return {"success": False, "message": "Ghost API credentials not provided"}

        # Parse admin API key
        if ":" not in admin_key:
            return {"success": False, "message": "Invalid admin API key format"}

        id, secret = admin_key.split(":")

        # Generate JWT token
        iat = int(time.time())
        exp = iat + 5 * 60

        header = {"alg": "HS256", "typ": "JWT", "kid": id}
        payload = {"iat": iat, "exp": exp, "aud": "/admin/"}

        ghost_token = jwt.encode(
            payload, bytes.fromhex(secret), algorithm="HS256", headers=header
        )

        # Build query parameters
        includes = []
        if kwargs.get("include_tags", True):
            includes.append("tags")
        if kwargs.get("include_authors", True):
            includes.append("authors")
        if kwargs.get("include_count", False):
            includes.append("count.posts")

        params = {}
        if includes:
            params["include"] = ",".join(includes)

        # Formats
        formats = []
        if kwargs.get("include_html", True):
            formats.append("html")
        if kwargs.get("include_mobiledoc", True):
            formats.append("mobiledoc")
        if formats:
            params["formats"] = ",".join(formats)

        # Make request
        headers = {
            "Authorization": f"Ghost {ghost_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(
            f"{api_url}/ghost/api/admin/posts/{post_id}/",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])
            
            if not posts:
                return {"success": False, "message": f"Post not found: {post_id}"}
                
            post = posts[0]

            # Add computed fields for convenience
            if post:
                # Format dates for readability
                for date_field in ["published_at", "created_at", "updated_at"]:
                    if post.get(date_field):
                        # Keep original ISO format
                        post[f"{date_field}_iso"] = post[date_field]
                        # Add human-readable format
                        try:
                            dt = datetime.fromisoformat(
                                post[date_field].replace("Z", "+00:00")
                            )
                            post[f"{date_field}_formatted"] = dt.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        except:
                            pass

                # Add content preview if full content exists
                if post.get("html"):
                    # Strip HTML tags for preview
                    import re

                    text = re.sub("<[^<]+?>", "", post["html"])
                    post["content_preview"] = (
                        text[:500] + "..." if len(text) > 500 else text
                    )

                # Add word count
                if post.get("html"):
                    import re
                    text = re.sub("<[^<]+?>", "", post["html"])
                    post["word_count"] = len(text.split())

            return {"success": True, "post": post}
        elif response.status_code == 404:
            return {"success": False, "message": f"Post not found: {post_id}"}
        else:
            return {
                "success": False,
                "message": f"Failed to get post details: {response.status_code}",
                "error": response.text,
            }

    except Exception as e:
        return {"success": False, "message": f"Error getting post details: {str(e)}"}


def get_posts_summary(days=None, date_from=None, date_to=None, **kwargs) -> Dict[str, Any]:
    """
    Get a summary of posts with basic info for quick overview - FIXED VERSION

    Parameters:
        days (int): Number of days back from today (overrides date_from/date_to)
        date_from (str/datetime): Start date for filtering
        date_to (str/datetime): End date for filtering
        status (str): Post status filter
        ghost_admin_api_key (str): Override env Ghost API key
        ghost_api_url (str): Override env Ghost API URL

    Returns:
        dict: Summary of posts with id, title, status, dates
    """
    try:
        # Handle days parameter properly
        if days is not None:
            try:
                days_int = int(days)
                date_to = datetime.now()
                date_from = date_to - timedelta(days=days_int)
            except (ValueError, TypeError):
                # If days is not a valid integer, ignore it
                pass

        # Use advanced function with minimal fields for performance
        result = get_ghost_posts_advanced(
            published_after=date_from,
            published_before=date_to,
            get_all=True,  # Get all posts in range
            fields=[
                "id",
                "title",
                "slug",
                "status",
                "published_at",
                "updated_at",
                "featured",
            ],
            status=kwargs.get("status", "all"),
            ghost_admin_api_key=kwargs.get("ghost_admin_api_key"),
            ghost_api_url=kwargs.get("ghost_api_url"),
        )

        if result.get("success"):
            posts = result.get("posts", [])
            
            # Handle empty posts list
            if not posts:
                return {
                    "success": True,
                    "total_posts": 0,
                    "posts": [],
                    "date_range": {"from": date_from, "to": date_to},
                    "message": "No posts found in the specified date range"
                }

            # Format for easy viewing
            posts_summary = []
            for post in posts:
                # Safely handle potential None values
                summary_post = {
                    "id": post.get("id", ""),
                    "title": post.get("title", "Untitled"),
                    "slug": post.get("slug", ""),
                    "status": post.get("status", "unknown"),
                    "featured": post.get("featured", False),
                    "published_at": post.get("published_at"),
                    "updated_at": post.get("updated_at"),
                }
                posts_summary.append(summary_post)

            return {
                "success": True,
                "total_posts": len(posts_summary),
                "posts": posts_summary,
                "date_range": {"from": str(date_from) if date_from else None, "to": str(date_to) if date_to else None},
                "filters_applied": {
                    "days": days,
                    "status": kwargs.get("status", "all")
                }
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "Failed to retrieve posts for summary"),
                "error": result.get("error")
            }

    except Exception as e:
        return {"success": False, "message": f"Error getting posts summary: {str(e)}"}


def batch_get_post_details(post_ids: List[str], **kwargs) -> Dict[str, Any]:
    """
    Get details for multiple posts at once - FIXED VERSION

    Parameters:
        post_ids (list): List of post IDs to fetch
        include_content (bool): Include full content (default: False)
        ghost_admin_api_key (str): Override env Ghost API key
        ghost_api_url (str): Override env Ghost API URL

    Returns:
        dict: Details for all requested posts
    """
    try:
        # Validate input
        if not post_ids or not isinstance(post_ids, list):
            return {
                "success": False, 
                "message": "post_ids must be a non-empty list",
                "posts": {},
                "failed": []
            }

        results = {"success": True, "posts": {}, "failed": []}

        # Filter out empty/invalid post IDs
        valid_post_ids = [pid for pid in post_ids if pid and str(pid).strip()]

        if not valid_post_ids:
            return {
                "success": False, 
                "message": "No valid post IDs provided",
                "posts": {},
                "failed": [{"id": "invalid", "error": "All post IDs were empty or invalid"}]
            }

        for post_id in valid_post_ids:
            try:
                result = get_ghost_post_details(
                    post_id,
                    include_html=kwargs.get("include_content", False),
                    include_mobiledoc=kwargs.get("include_content", False),
                    ghost_admin_api_key=kwargs.get("ghost_admin_api_key"),
                    ghost_api_url=kwargs.get("ghost_api_url"),
                )

                if result.get("success"):
                    results["posts"][post_id] = result["post"]
                else:
                    results["failed"].append({"id": post_id, "error": result.get("message", "Unknown error")})
                    
            except Exception as e:
                results["failed"].append({"id": post_id, "error": f"Exception: {str(e)}"})

        results["total_fetched"] = len(results["posts"])
        results["total_failed"] = len(results["failed"])
        results["total_requested"] = len(valid_post_ids)

        return results
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in batch operation: {str(e)}",
            "posts": {},
            "failed": []
        }


def find_posts_by_date_pattern(pattern=None, **kwargs) -> Dict[str, Any]:
    """
    Find posts that match specific date patterns - FIXED VERSION
    Useful for finding posts that need date corrections

    Parameters:
        pattern (str): Date pattern to search for (e.g., "2024", "2024-01", "2024-01-15")
        year (int): Filter by specific year
        month (int): Filter by specific month (1-12)
        day (int): Filter by specific day (1-31)
        hour (int): Filter by specific hour (0-23)
        limit (int): Maximum number of posts to return
        same_date_time (bool): Find posts with identical publish times
        ghost_admin_api_key (str): Override env Ghost API key
        ghost_api_url (str): Override env Ghost API URL

    Returns:
        dict: Posts matching the date pattern
    """
    try:
        # Build date range based on parameters
        filters = {}
        limit = kwargs.get("limit", 100)  # Default limit to prevent overwhelming results

        # Handle pattern parameter (e.g., "2024", "2024-01", "2024-01-15")
        if pattern:
            pattern = str(pattern).strip()
            if len(pattern) == 4:  # Year only
                year = int(pattern)
                filters["published_after"] = f"{year}-01-01T00:00:00.000Z"
                filters["published_before"] = f"{year}-12-31T23:59:59.999Z"
            elif len(pattern) == 7:  # Year-month
                year, month = map(int, pattern.split("-"))
                # Calculate last day of month
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year
                filters["published_after"] = f"{year}-{month:02d}-01T00:00:00.000Z"
                filters["published_before"] = f"{next_year}-{next_month:02d}-01T00:00:00.000Z"
            elif len(pattern) == 10:  # Year-month-day
                filters["published_after"] = f"{pattern}T00:00:00.000Z"
                filters["published_before"] = f"{pattern}T23:59:59.999Z"

        # Handle individual parameters
        if "year" in kwargs:
            year = kwargs["year"]
            filters["published_after"] = f"{year}-01-01T00:00:00.000Z"
            filters["published_before"] = f"{year}-12-31T23:59:59.999Z"

            if "month" in kwargs:
                month = kwargs["month"]
                # Calculate last day of month
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year

                filters["published_after"] = f"{year}-{month:02d}-01T00:00:00.000Z"
                filters["published_before"] = f"{next_year}-{next_month:02d}-01T00:00:00.000Z"

                if "day" in kwargs:
                    day = kwargs["day"]
                    filters["published_after"] = f"{year}-{month:02d}-{day:02d}T00:00:00.000Z"
                    filters["published_before"] = f"{year}-{month:02d}-{day:02d}T23:59:59.999Z"

                    if "hour" in kwargs:
                        hour = kwargs["hour"]
                        filters["published_after"] = f"{year}-{month:02d}-{day:02d}T{hour:02d}:00:00.000Z"
                        filters["published_before"] = f"{year}-{month:02d}-{day:02d}T{hour:02d}:59:59.999Z"

        # Get posts with date filters
        result = get_ghost_posts_advanced(
            **filters,
            limit=limit,
            get_all=False,  # Use limit to prevent huge results
            fields=["id", "title", "slug", "published_at", "created_at", "updated_at"],
            status="all",
            ghost_admin_api_key=kwargs.get("ghost_admin_api_key"),
            ghost_api_url=kwargs.get("ghost_api_url"),
        )

        if not result.get("success"):
            return result

        posts = result.get("posts", [])

        # Find posts with same date/time if requested
        if kwargs.get("same_date_time"):
            from collections import defaultdict

            date_groups = defaultdict(list)

            for post in posts:
                if post.get("published_at"):
                    # Group by exact timestamp
                    date_groups[post["published_at"]].append(post)

            # Filter to only groups with multiple posts
            duplicates = {
                date: posts_list
                for date, posts_list in date_groups.items()
                if len(posts_list) > 1
            }

            if duplicates:
                return {
                    "success": True,
                    "duplicate_dates": duplicates,
                    "total_duplicates": sum(len(posts) for posts in duplicates.values()),
                }

        return {
            "success": True,
            "posts": posts,
            "total": len(posts),
            "date_pattern": pattern or kwargs,
            "limit_applied": limit,
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error in date pattern search: {str(e)}"}


# Convenience functions for common operations


def get_all_post_ids(**kwargs) -> List[str]:
    """
    Quick function to get just the IDs of all posts

    Returns:
        list: List of all post IDs
    """
    try:
        result = get_ghost_posts_advanced(
            get_all=True,
            fields=["id"],
            status=kwargs.get("status", "all"),
            ghost_admin_api_key=kwargs.get("ghost_admin_api_key"),
            ghost_api_url=kwargs.get("ghost_api_url"),
        )

        if result.get("success"):
            posts = result.get("posts", [])
            return [post.get("id") for post in posts if post.get("id")]
        return []
    except Exception as e:
        print(f"Error getting post IDs: {str(e)}")
        return []


def get_posts_for_date_update(**kwargs) -> Dict[str, Any]:
    """
    Get posts formatted specifically for date update operations
    Shows current dates and allows for planning date changes

    Returns:
        dict: Posts with date information formatted for updates
    """
    try:
        result = get_ghost_posts_advanced(
            get_all=True,
            fields=["id", "title", "slug", "status", "published_at", "created_at"],
            order="published_at ASC",  # Oldest first
            status=kwargs.get("status", "published"),
            ghost_admin_api_key=kwargs.get("ghost_admin_api_key"),
            ghost_api_url=kwargs.get("ghost_api_url"),
        )

        if not result.get("success"):
            return result

        posts = result.get("posts", [])
        posts_for_update = []
        
        for post in posts:
            post_info = {
                "id": post.get("id", ""),
                "title": post.get("title", "Untitled"),
                "slug": post.get("slug", ""),
                "status": post.get("status", "unknown"),
                "current_published_at": post.get("published_at"),
                "created_at": post.get("created_at"),
                "new_published_at": None,  # Placeholder for new date
            }

            # Add formatted dates for readability
            if post.get("published_at"):
                try:
                    dt = datetime.fromisoformat(post["published_at"].replace("Z", "+00:00"))
                    post_info["published_date"] = dt.strftime("%Y-%m-%d")
                    post_info["published_time"] = dt.strftime("%H:%M:%S")
                except:
                    pass

            posts_for_update.append(post_info)

        return {
            "success": True,
            "posts": posts_for_update,
            "total": len(posts_for_update),
            "instructions": "Use update_ghost_post() with published_at parameter to update dates",
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error getting posts for date update: {str(e)}"}


if __name__ == "__main__":
    # Example usage
    print("Ghost Blog Post Management Functions - FIXED VERSION")
    print("=" * 60)

    # Example 1: Get all posts from last month
    from datetime import datetime, timedelta

    last_month = datetime.now() - timedelta(days=30)

    print("\n1. Posts from last 30 days:")
    result = get_posts_summary(days=30)
    if result["success"]:
        print(f"   Found {result['total_posts']} posts")
        for post in result["posts"][:3]:  # Show first 3
            print(f"   - {post['title']} ({post['status']})")
    else:
        print(f"   Error: {result['message']}")

    print("\n" + "=" * 60)
    print("✅ Post Management Functions Ready!")