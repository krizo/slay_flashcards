from tests.api.conftest import client


def test_successful_registration():
    """Test successful user registration with all required fields."""
    register_data = {
        "username": "newuser",
        "password": "SecurePass123!",
        "email": "newuser@example.com"
    }

    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]


def test_registration_validation_errors():
    """Test registration with invalid data."""

    # Test weak password
    weak_password_data = {
        "username": "testuser",
        "password": "123",  # Too short
        "email": "test@example.com"
    }
    response = client.post("/api/v1/auth/register", json=weak_password_data)
    assert response.status_code == 422

    # Test invalid email
    invalid_email_data = {
        "username": "testuser2",
        "password": "SecurePass123!",
        "email": "not-an-email"
    }
    response = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response.status_code == 422

    # Test invalid username
    invalid_username_data = {
        "username": "ab",  # Too short
        "password": "SecurePass123!",
        "email": "test2@example.com"
    }
    response = client.post("/api/v1/auth/register", json=invalid_username_data)
    assert response.status_code == 422


def test_duplicate_registration():
    """Test registration with duplicate username/email."""
    register_data = {
        "username": "duplicateuser",
        "password": "SecurePass123!",
        "email": "duplicate@example.com"
    }

    # First registration should succeed
    response1 = client.post("/api/v1/auth/register", json=register_data)
    assert response1.status_code == 201

    # Second registration with same username should fail
    response2 = client.post("/api/v1/auth/register", json=register_data)
    assert response2.status_code == 409
    assert "Username already exists" in response2.json()["detail"]

    # Registration with same email but different username should also fail
    register_data_same_email = {
        "username": "differentuser",
        "password": "SecurePass123!",
        "email": "duplicate@example.com"  # Same email
    }
    response3 = client.post("/api/v1/auth/register", json=register_data_same_email)
    assert response3.status_code == 409
    assert "Email address already exists" in response3.json()["detail"]


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
