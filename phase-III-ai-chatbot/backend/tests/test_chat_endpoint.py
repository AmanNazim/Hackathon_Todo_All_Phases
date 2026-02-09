"""Integration tests for chat endpoint"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestChatEndpoint:
    """Integration tests for chat API endpoint"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_without_auth(self):
        """Test chat endpoint without authentication"""
        response = client.post(
            "/api/chat",
            json={"message": "Add task to buy milk"}
        )
        # Should return 403 (Forbidden) without auth token
        assert response.status_code == 403

    def test_chat_with_auth(self):
        """Test chat endpoint with authentication"""
        response = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Add task to buy milk"}
        )
        # Should succeed with auth
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "created_at" in data

    def test_chat_continue_conversation(self):
        """Test continuing an existing conversation"""
        # First message
        response1 = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Add task to buy milk"}
        )
        assert response1.status_code == 200
        conv_id = response1.json()["conversation_id"]

        # Second message in same conversation
        response2 = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={
                "conversation_id": conv_id,
                "message": "Show my tasks"
            }
        )
        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conv_id

    def test_chat_invalid_message_length(self):
        """Test chat with message exceeding max length"""
        response = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "x" * 1001}  # Exceeds 1000 char limit
        )
        # Should return 422 (Validation Error)
        assert response.status_code == 422

    def test_chat_empty_message(self):
        """Test chat with empty message"""
        response = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": ""}
        )
        # Should return 422 (Validation Error)
        assert response.status_code == 422

    def test_chat_invalid_conversation_id(self):
        """Test chat with non-existent conversation ID"""
        response = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={
                "conversation_id": "00000000-0000-0000-0000-000000000000",
                "message": "Hello"
            }
        )
        # Should return 404 (Not Found)
        assert response.status_code == 404

    def test_openapi_docs(self):
        """Test that OpenAPI docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
