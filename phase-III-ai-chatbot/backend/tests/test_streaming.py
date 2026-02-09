"""Integration tests for streaming endpoint"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestStreamingEndpoint:
    """Integration tests for streaming chat endpoint"""

    def test_streaming_endpoint_without_auth(self):
        """Test streaming endpoint without authentication"""
        response = client.post(
            "/api/chat/stream",
            json={"message": "Add task to buy milk"}
        )
        # Should return 403 (Forbidden) without auth token
        assert response.status_code == 403

    def test_streaming_endpoint_with_auth(self):
        """Test streaming endpoint with authentication"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Add task to buy milk"},
            stream=True
        )
        # Should succeed with auth
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_streaming_endpoint_sse_format(self):
        """Test that streaming endpoint returns SSE format"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Show my tasks"},
            stream=True
        )

        assert response.status_code == 200

        # Check SSE format in response
        content = b""
        for chunk in response.iter_bytes():
            content += chunk
            if b"event:" in content:
                break

        # Should contain SSE event format
        assert b"event:" in content or b"data:" in content

    def test_streaming_endpoint_empty_message(self):
        """Test streaming endpoint with empty message"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": ""},
            stream=True
        )
        # Should return 422 (Validation Error) or stream error event
        assert response.status_code in [200, 422]

    def test_streaming_endpoint_long_message(self):
        """Test streaming endpoint with message exceeding max length"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "x" * 1001},
            stream=True
        )
        # Should return 422 (Validation Error) or stream error event
        assert response.status_code in [200, 422]

    def test_streaming_endpoint_continue_conversation(self):
        """Test streaming endpoint with existing conversation"""
        # First request to create conversation
        response1 = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Add task to buy milk"}
        )
        assert response1.status_code == 200
        conv_id = response1.json()["conversation_id"]

        # Second request with streaming
        response2 = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={
                "conversation_id": conv_id,
                "message": "Show my tasks"
            },
            stream=True
        )
        assert response2.status_code == 200


class TestStreamingEvents:
    """Test streaming event types"""

    def test_text_events(self):
        """Test that text events are streamed"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Hello"},
            stream=True
        )

        assert response.status_code == 200

        # Collect events
        events = []
        for chunk in response.iter_lines():
            if chunk:
                events.append(chunk.decode())

        # Should contain event types
        event_types = [line for line in events if line.startswith("event:")]
        assert len(event_types) > 0

    def test_complete_event(self):
        """Test that complete event is sent at end"""
        response = client.post(
            "/api/chat/stream",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "Add task"},
            stream=True
        )

        assert response.status_code == 200

        # Collect all events
        events = []
        for chunk in response.iter_lines():
            if chunk:
                events.append(chunk.decode())

        # Should contain complete event
        complete_events = [line for line in events if "complete" in line]
        assert len(complete_events) > 0
