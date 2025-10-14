"""
Tests for user language preference functionality.

These tests verify:
- User language field is set during registration
- Language field defaults to 'pl'
- Language field appears in user info responses
- Language field persists across login sessions
"""

import pytest


def test_user_language_defaults_to_pl(test_client):
    """Test that new users have language set to 'pl' by default."""
    register_data = {
        "username": "defaultlanguser",
        "password": "TestPass123!",
        "email": "defaultlang@example.com"
    }
    response = test_client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    # Get token from registration response
    token = response.json()["data"]["access_token"]

    # Get user info from /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    user_response = test_client.get("/api/v1/auth/me", headers=headers)
    assert user_response.status_code == 200

    user_data = user_response.json()["data"]
    assert "language" in user_data
    assert user_data["language"] == "pl"


def test_user_language_can_be_set_during_registration(test_client):
    """Test that language can be specified during registration."""
    register_data = {
        "username": "enlanguser",
        "password": "TestPass123!",
        "email": "enlang@example.com",
        "language": "en"
    }
    response = test_client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    # Get token and check language
    token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_response = test_client.get("/api/v1/auth/me", headers=headers)
    assert user_response.status_code == 200

    user_data = user_response.json()["data"]
    assert user_data["language"] == "en"


def test_user_language_in_user_info(authenticated_client):
    """Test that language field appears in GET /auth/me response."""
    response = authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200

    user_data = response.json()["data"]
    assert "language" in user_data
    assert isinstance(user_data["language"], str)
    assert len(user_data["language"]) <= 10  # Max length constraint


def test_user_language_persists_across_sessions(test_client):
    """Test that user language persists across login sessions."""
    # Register user
    register_data = {
        "username": "persistuser",
        "password": "TestPass123!",
        "email": "persist@example.com"
    }
    response = test_client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201

    # Get token from registration
    token1 = response.json()["data"]["access_token"]

    # Get language with first token
    headers1 = {"Authorization": f"Bearer {token1}"}
    user_response1 = test_client.get("/api/v1/auth/me", headers=headers1)
    assert user_response1.status_code == 200
    language1 = user_response1.json()["data"]["language"]

    # Login second time (new session)
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    login_response2 = test_client.post("/api/v1/auth/login", json=login_data)
    assert login_response2.status_code == 200
    token2 = login_response2.json()["data"]["access_token"]

    # Get language with second token
    headers2 = {"Authorization": f"Bearer {token2}"}
    user_response2 = test_client.get("/api/v1/auth/me", headers=headers2)
    assert user_response2.status_code == 200
    language2 = user_response2.json()["data"]["language"]

    # Language should be the same across sessions
    assert language1 == language2
    assert language1 == "pl"


def test_auth_me_endpoint_requires_authentication(test_client):
    """Test that auth/me endpoint requires authentication."""
    response = test_client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]  # Either Unauthorized or Forbidden is acceptable
