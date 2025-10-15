"""
Tests for Tag API endpoints (v0.2.0)
"""
# pylint: disable=redefined-outer-name,unused-argument
import pytest


def test_create_tag(authenticated_client):
    """Test creating a new tag."""
    tag_data = {
        "name": "Mathematics",
        "color": "#FF5733"
    }

    response = authenticated_client.post("/api/v1/tags/", json=tag_data)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Tag created successfully"
    assert data["data"]["name"] == "Mathematics"
    assert data["data"]["color"] == "#FF5733"
    assert "id" in data["data"]


def test_create_tag_duplicate_name(authenticated_client):
    """Test that creating a tag with duplicate name fails."""
    tag_data = {
        "name": "Science",
        "color": "#00FF00"
    }

    # Create first tag
    response1 = authenticated_client.post("/api/v1/tags/", json=tag_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = authenticated_client.post("/api/v1/tags/", json=tag_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"].lower()


def test_create_tag_without_color(authenticated_client):
    """Test creating a tag without color (should be optional)."""
    tag_data = {
        "name": "History"
    }

    response = authenticated_client.post("/api/v1/tags/", json=tag_data)

    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "History"
    assert data["data"]["color"] is None


def test_get_all_tags(authenticated_client):
    """Test retrieving all tags."""
    # Create multiple tags
    tags = [
        {"name": "Biology", "color": "#00FF00"},
        {"name": "Chemistry", "color": "#0000FF"},
        {"name": "Physics", "color": "#FF0000"}
    ]

    for tag in tags:
        authenticated_client.post("/api/v1/tags/", json=tag)

    # Get all tags
    response = authenticated_client.get("/api/v1/tags/")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3

    # Verify tags are ordered by name
    tag_names = [tag["name"] for tag in data["data"]]
    assert tag_names == sorted(tag_names)


def test_get_tag_by_id(authenticated_client):
    """Test retrieving a specific tag by ID."""
    # Create a tag
    tag_data = {"name": "Geography", "color": "#FFFF00"}
    create_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["data"]["id"]

    # Get tag by ID
    response = authenticated_client.get(f"/api/v1/tags/{tag_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == tag_id
    assert data["data"]["name"] == "Geography"
    assert data["data"]["color"] == "#FFFF00"


def test_get_nonexistent_tag(authenticated_client):
    """Test retrieving a tag that doesn't exist."""
    response = authenticated_client.get("/api/v1/tags/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_tag(authenticated_client):
    """Test updating a tag."""
    # Create a tag
    tag_data = {"name": "English", "color": "#FF00FF"}
    create_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["data"]["id"]

    # Update the tag
    update_data = {"name": "English Literature", "color": "#FF88FF"}
    response = authenticated_client.put(f"/api/v1/tags/{tag_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "English Literature"
    assert data["data"]["color"] == "#FF88FF"


def test_update_tag_name_only(authenticated_client):
    """Test updating only the tag name."""
    # Create a tag
    tag_data = {"name": "Art", "color": "#AAAAAA"}
    create_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["data"]["id"]

    # Update only name
    update_data = {"name": "Fine Arts"}
    response = authenticated_client.put(f"/api/v1/tags/{tag_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Fine Arts"
    assert data["data"]["color"] == "#AAAAAA"  # Color unchanged


def test_update_tag_color_only(authenticated_client):
    """Test updating only the tag color."""
    # Create a tag
    tag_data = {"name": "Music", "color": "#111111"}
    create_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["data"]["id"]

    # Update only color
    update_data = {"color": "#FFAA00"}
    response = authenticated_client.put(f"/api/v1/tags/{tag_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Music"  # Name unchanged
    assert data["data"]["color"] == "#FFAA00"


def test_update_tag_duplicate_name(authenticated_client):
    """Test that updating a tag with duplicate name fails."""
    # Create two tags
    tag1_data = {"name": "Computer Science"}
    tag2_data = {"name": "Programming"}

    authenticated_client.post("/api/v1/tags/", json=tag1_data)
    create_response2 = authenticated_client.post("/api/v1/tags/", json=tag2_data)
    tag2_id = create_response2.json()["data"]["id"]

    # Try to update tag2 with tag1's name
    update_data = {"name": "Computer Science"}
    response = authenticated_client.put(f"/api/v1/tags/{tag2_id}", json=update_data)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_update_nonexistent_tag(authenticated_client):
    """Test updating a tag that doesn't exist."""
    update_data = {"name": "Nonexistent", "color": "#000000"}
    response = authenticated_client.put("/api/v1/tags/99999", json=update_data)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_tag(authenticated_client):
    """Test deleting a tag."""
    # Create a tag
    tag_data = {"name": "Languages", "color": "#123456"}
    create_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = create_response.json()["data"]["id"]

    # Delete the tag
    response = authenticated_client.delete(f"/api/v1/tags/{tag_id}")

    assert response.status_code == 204

    # Verify tag is deleted
    get_response = authenticated_client.get(f"/api/v1/tags/{tag_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_tag(authenticated_client):
    """Test deleting a tag that doesn't exist."""
    response = authenticated_client.delete("/api/v1/tags/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_tag_requires_authentication(test_client):
    """Test that tag endpoints require authentication."""
    # Try to get tags without authentication
    response = test_client.get("/api/v1/tags/")
    assert response.status_code == 403

    # Try to create tag without authentication
    tag_data = {"name": "Test", "color": "#000000"}
    response = test_client.post("/api/v1/tags/", json=tag_data)
    assert response.status_code == 403


def test_tag_name_validation(authenticated_client):
    """Test tag name validation (max length 50)."""
    # Test with name too long (> 50 chars)
    tag_data = {
        "name": "A" * 51,  # 51 characters
        "color": "#000000"
    }

    response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    assert response.status_code == 422  # Validation error


def test_tag_color_validation(authenticated_client):
    """Test tag color validation (max length 7 for hex codes)."""
    # Test with color too long (> 7 chars)
    tag_data = {
        "name": "ValidName",
        "color": "#FF000000"  # 9 characters (too long)
    }

    response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    assert response.status_code == 422  # Validation error
