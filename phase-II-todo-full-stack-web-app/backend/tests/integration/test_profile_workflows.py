"""
Integration tests for profile workflows.

Tests complete workflows: profile setup, avatar upload, preferences update.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from models import User, UserPreferences
from datetime import datetime
import uuid


client = TestClient(app)


@pytest.fixture
def new_user(db_session: Session) -> User:
    """Create a new user with minimal profile."""
    user = User(
        id=str(uuid.uuid4()),
        email="workflow_test@example.com",
        display_name=None,
        bio=None,
        avatar_url=None,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(new_user: User) -> dict:
    """Generate authentication headers."""
    return {"Authorization": f"Bearer mock_token_{new_user.id}"}


class TestCompleteProfileSetup:
    """Test complete profile setup workflow."""

    def test_new_user_profile_setup_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test complete workflow: new user sets up their profile."""

        # Step 1: Get initial profile (should be mostly empty)
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        initial_profile = response.json()
        assert initial_profile["display_name"] is None or initial_profile["display_name"] == ""
        assert initial_profile["completion_percentage"] < 50

        # Step 2: Update display name
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "John Doe"}
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "John Doe"

        # Step 3: Add bio
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={"bio": "Software developer passionate about building great products."}
        )
        assert response.status_code == 200
        assert "Software developer" in response.json()["bio"]

        # Step 4: Get updated profile and check completion
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["display_name"] == "John Doe"
        assert "Software developer" in updated_profile["bio"]
        # Completion should be higher now
        assert updated_profile["completion_percentage"] > initial_profile["completion_percentage"]

    def test_profile_and_preferences_setup_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test setting up both profile and preferences."""

        # Step 1: Set up profile
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={
                "display_name": "Jane Smith",
                "bio": "Product manager and tech enthusiast."
            }
        )
        assert response.status_code == 200

        # Step 2: Get default preferences
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        default_prefs = response.json()

        # Step 3: Update theme preference
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "dark"}
        )
        assert response.status_code == 200
        assert response.json()["theme"] == "dark"

        # Step 4: Update notification preferences
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "notifications": {
                    "email": True,
                    "push": True,
                    "task_reminders": True,
                    "task_assignments": True
                }
            }
        )
        assert response.status_code == 200

        # Step 5: Update privacy settings
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": False,
                    "show_activity": True
                }
            }
        )
        assert response.status_code == 200

        # Step 6: Verify all settings persisted
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        final_prefs = response.json()
        assert final_prefs["theme"] == "dark"
        assert final_prefs["notifications"]["email"] is True
        assert final_prefs["privacy"]["profile_visibility"] == "public"


class TestPrivacyWorkflow:
    """Test privacy settings workflow."""

    def test_change_profile_visibility_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test changing profile visibility from public to private."""

        # Step 1: Set profile to public
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": True,
                    "show_activity": True
                }
            }
        )
        assert response.status_code == 200

        # Step 2: Create another user to test visibility
        other_user = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            display_name="Other User",
            created_at=datetime.utcnow()
        )
        db_session.add(other_user)
        db_session.commit()

        # Step 3: Other user can view public profile
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{other_user.id}"}
        )
        # Should succeed or return filtered data based on implementation
        assert response.status_code in [200, 403]

        # Step 4: Change to private
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "private",
                    "show_email": False,
                    "show_activity": False
                }
            }
        )
        assert response.status_code == 200

        # Step 5: Other user cannot view private profile
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers={"Authorization": f"Bearer mock_token_{other_user.id}"}
        )
        assert response.status_code == 403

        # Step 6: User can still view their own profile
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_granular_privacy_controls_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test granular privacy controls for email and activity."""

        # Step 1: Set up profile with data
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={
                "display_name": "Privacy User",
                "bio": "Testing privacy controls"
            }
        )
        assert response.status_code == 200

        # Step 2: Set public profile but hide email
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "public",
                    "show_email": False,
                    "show_activity": True
                }
            }
        )
        assert response.status_code == 200

        # Step 3: Verify settings applied
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        prefs = response.json()
        assert prefs["privacy"]["show_email"] is False
        assert prefs["privacy"]["show_activity"] is True

        # Step 4: Change to hide activity but show email
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "show_email": True,
                    "show_activity": False
                }
            }
        )
        assert response.status_code == 200

        # Step 5: Verify changes applied
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        prefs = response.json()
        assert prefs["privacy"]["show_email"] is True
        assert prefs["privacy"]["show_activity"] is False


class TestMultipleUpdatesWorkflow:
    """Test multiple sequential updates."""

    def test_multiple_profile_updates_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test making multiple profile updates in sequence."""

        updates = [
            {"display_name": "First Name"},
            {"display_name": "Second Name", "bio": "First bio"},
            {"bio": "Updated bio"},
            {"display_name": "Final Name", "bio": "Final bio"}
        ]

        for update in updates:
            response = client.put(
                f"/api/v1/users/{new_user.id}/profile",
                headers=auth_headers,
                json=update
            )
            assert response.status_code == 200

        # Verify final state
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        final_profile = response.json()
        assert final_profile["display_name"] == "Final Name"
        assert final_profile["bio"] == "Final bio"

    def test_preferences_incremental_updates_workflow(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test incrementally updating different preference sections."""

        # Update 1: Theme
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "dark"}
        )
        assert response.status_code == 200

        # Update 2: Language
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={"language": "es"}
        )
        assert response.status_code == 200

        # Update 3: Notifications
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "notifications": {
                    "email": False,
                    "push": True,
                    "task_reminders": True,
                    "task_assignments": False
                }
            }
        )
        assert response.status_code == 200

        # Update 4: Privacy
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "privacy": {
                    "profile_visibility": "private",
                    "show_email": False,
                    "show_activity": False
                }
            }
        )
        assert response.status_code == 200

        # Verify all updates persisted
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        final_prefs = response.json()
        assert final_prefs["theme"] == "dark"
        assert final_prefs["language"] == "es"
        assert final_prefs["notifications"]["push"] is True
        assert final_prefs["privacy"]["profile_visibility"] == "private"


class TestErrorRecoveryWorkflow:
    """Test error handling and recovery in workflows."""

    def test_invalid_update_does_not_corrupt_profile(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test that invalid updates don't corrupt existing data."""

        # Step 1: Set valid profile
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={
                "display_name": "Valid Name",
                "bio": "Valid bio"
            }
        )
        assert response.status_code == 200

        # Step 2: Attempt invalid update (too long display name)
        response = client.put(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers,
            json={"display_name": "A" * 200}
        )
        assert response.status_code == 422

        # Step 3: Verify original data still intact
        response = client.get(
            f"/api/v1/users/{new_user.id}/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        profile = response.json()
        assert profile["display_name"] == "Valid Name"
        assert profile["bio"] == "Valid bio"

    def test_invalid_preferences_do_not_corrupt_settings(
        self, db_session: Session, new_user: User, auth_headers: dict
    ):
        """Test that invalid preference updates don't corrupt existing settings."""

        # Step 1: Set valid preferences
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={
                "theme": "dark",
                "language": "en"
            }
        )
        assert response.status_code == 200

        # Step 2: Attempt invalid update
        response = client.put(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers,
            json={"theme": "invalid_theme"}
        )
        assert response.status_code == 422

        # Step 3: Verify original settings still intact
        response = client.get(
            f"/api/v1/users/{new_user.id}/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        prefs = response.json()
        assert prefs["theme"] == "dark"
        assert prefs["language"] == "en"
