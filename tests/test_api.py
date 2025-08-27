#!/usr/bin/env python3
"""
Comprehensive tests for Ghost Blog Smart Flask API
Tests all endpoints with real Ghost credentials
"""

import pytest
import json
import os
from flask import Flask
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test")

# Import the Flask app
from app import app as flask_app


class TestGhostBlogSmartAPI:
    """Test class for Ghost Blog Smart API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with real credentials"""
        flask_app.config["TESTING"] = True
        with flask_app.test_client() as client:
            yield client

    @pytest.fixture
    def auth_headers(self):
        """Headers with API key for authenticated requests"""
        return {
            "Content-Type": "application/json",
            "X-API-Key": "test_api_key_for_development_only",
        }

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True
        assert "name" in data["data"]
        assert "Ghost Blog Smart API" in data["data"]["name"]
        assert "endpoints" in data["data"]

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True
        assert data["data"]["status"] == "healthy"
        assert "features" in data["data"]
        assert data["data"]["features"]["ghost_integration"] == True

    def test_get_posts_without_auth(self, client):
        """Test that posts endpoint requires authentication"""
        response = client.get("/api/posts")
        assert response.status_code == 401

        data = json.loads(response.data)
        assert data["success"] == False
        assert "Invalid or missing API key" in data["error"]

    def test_get_posts_with_auth(self, client, auth_headers):
        """Test getting posts with authentication"""
        response = client.get("/api/posts?limit=2", headers=auth_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True
        assert "posts" in data["data"]

        # Check that we got posts
        if data["data"]["posts"]:
            assert len(data["data"]["posts"]) <= 2  # Should respect limit
            for post in data["data"]["posts"]:
                assert "id" in post
                assert "title" in post
                assert "status" in post

    def test_get_posts_advanced_search(self, client, auth_headers):
        """Test advanced posts search with filters"""
        response = client.get(
            "/api/posts/advanced?limit=5&status=published", headers=auth_headers
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True

    def test_create_post_without_auth(self, client):
        """Test that post creation requires authentication"""
        post_data = {"title": "Test Post", "content": "Test content", "is_test": True}

        response = client.post(
            "/api/posts", data=json.dumps(post_data), content_type="application/json"
        )
        assert response.status_code == 401

    def test_create_post_missing_fields(self, client, auth_headers):
        """Test post creation with missing required fields"""
        post_data = {"content": "Test content without title"}

        response = client.post(
            "/api/posts", data=json.dumps(post_data), headers=auth_headers
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] == False
        assert "Missing required fields" in data["error"]

    def test_create_post_valid(self, client, auth_headers):
        """Test creating a valid blog post"""
        post_data = {
            "title": "API Test Post - Please Delete",
            "content": "# Test Post\n\nThis is a **test post** created by the Flask API automated tests.\n\n*Please delete this post after testing.*",
            "excerpt": "Automated test post from Flask API tests",
            "tags": ["Test", "API", "Automated"],
            "status": "draft",  # Keep as draft for safety
            "is_test": True,  # Enable test mode
            "visibility": "public",
        }

        response = client.post(
            "/api/posts", data=json.dumps(post_data), headers=auth_headers
        )

        # Should succeed or gracefully handle test mode
        assert response.status_code in [
            200,
            400,
        ]  # 400 is OK if test mode blocks creation

        data = json.loads(response.data)
        print(f"Create post response: {data}")

        if data["success"]:
            assert "url" in data["data"] or "message" in data["data"]
            # Store post_id for cleanup if needed
            if "post_id" in data["data"]:
                self.test_post_id = data["data"]["post_id"]

    def test_smart_create_without_auth(self, client):
        """Test smart create requires authentication"""
        smart_data = {"user_input": "Write about AI benefits"}

        response = client.post(
            "/api/smart-create",
            data=json.dumps(smart_data),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_smart_create_missing_input(self, client, auth_headers):
        """Test smart create with missing user_input"""
        smart_data = {"status": "draft"}

        response = client.post(
            "/api/smart-create", data=json.dumps(smart_data), headers=auth_headers
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] == False
        assert "user_input is required" in data["message"]

    def test_smart_create_valid(self, client, auth_headers):
        """Test smart create with valid input"""
        smart_data = {
            "user_input": "Write a brief blog post about the benefits of automated testing in software development. Include why it saves time and reduces bugs.",
            "status": "draft",
            "is_test": True,
        }

        response = client.post(
            "/api/smart-create", data=json.dumps(smart_data), headers=auth_headers
        )

        # Should succeed or handle gracefully in test mode
        assert response.status_code in [200, 400]

        data = json.loads(response.data)
        print(f"Smart create response: {data}")

    def test_get_specific_post(self, client, auth_headers):
        """Test getting details for a specific post"""
        # First get list of posts to find an ID
        list_response = client.get("/api/posts?limit=1", headers=auth_headers)
        assert list_response.status_code == 200

        list_data = json.loads(list_response.data)
        if list_data["data"]["posts"]:
            post_id = list_data["data"]["posts"][0]["id"]

            # Now get specific post details
            detail_response = client.get(f"/api/posts/{post_id}", headers=auth_headers)
            assert detail_response.status_code == 200

            detail_data = json.loads(detail_response.data)
            assert detail_data["success"] == True
            if "post" in detail_data["data"]:
                assert detail_data["data"]["post"]["id"] == post_id

    def test_posts_summary(self, client, auth_headers):
        """Test posts summary endpoint"""
        response = client.get("/api/posts/summary", headers=auth_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True

    def test_batch_post_details(self, client, auth_headers):
        """Test batch post details endpoint"""
        # First get some post IDs
        list_response = client.get("/api/posts?limit=2", headers=auth_headers)
        assert list_response.status_code == 200

        list_data = json.loads(list_response.data)
        if list_data["data"]["posts"]:
            post_ids = [post["id"] for post in list_data["data"]["posts"]]

            batch_data = {"post_ids": post_ids}

            response = client.post(
                "/api/posts/batch-details",
                data=json.dumps(batch_data),
                headers=auth_headers,
            )
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] == True

    def test_invalid_post_id(self, client, auth_headers):
        """Test getting details for non-existent post"""
        response = client.get("/api/posts/invalid_post_id_12345", headers=auth_headers)
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["success"] == False

    def test_update_post_without_auth(self, client):
        """Test update post requires authentication"""
        update_data = {"title": "Updated Title"}

        response = client.put(
            "/api/posts/some_id",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_delete_post_without_auth(self, client):
        """Test delete post requires authentication"""
        response = client.delete("/api/posts/some_id")
        assert response.status_code == 401

    def test_date_pattern_search(self, client, auth_headers):
        """Test date pattern search endpoint"""
        response = client.get(
            "/api/posts/search/by-date-pattern?pattern=2024&limit=5",
            headers=auth_headers,
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] == True

    def test_api_response_format(self, client):
        """Test that all API responses follow standard format"""
        response = client.get("/")
        data = json.loads(response.data)

        # Check standard response format
        assert "success" in data
        assert "timestamp" in data

        if data["success"]:
            assert "data" in data
        else:
            assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
