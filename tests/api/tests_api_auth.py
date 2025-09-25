from tests.api.conftest import client


def test_login_and_me_endpoints(authenticated_client):
    """Test login with an existing user and retrieve user data."""
    # The authenticated_client fixture already has a user logged in,
    # so we can directly test the /auth/me endpoint.
    response = authenticated_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["success"] is True
    assert user_data["data"]["name"] == "testuser_auth"

def test_unauthenticated_request_is_rejected():
    """Test that protected endpoints reject requests without a token."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 403
    assert "Not authenticated" in response.json().get('detail')

def test_login_with_non_existent_user():
    """Test that a new user is created on first login (as per the code's logic)."""
    login_data = {"username": "new_user_login", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert "access_token" in response.json()["data"]

def test_register_with_existing_username():
    """Test that registration with a duplicate username fails."""
    register_data = {"username": "duplicate_user", "password": "password123"}
    client.post("/api/v1/auth/register", json=register_data)
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"