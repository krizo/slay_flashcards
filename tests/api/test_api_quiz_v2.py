"""
Tests for Quiz API v0.2.0 features (draft status, tags, image)
"""
# pylint: disable=redefined-outer-name,unused-argument
import base64
import pytest


@pytest.fixture
def sample_tags(authenticated_client):
    """Create sample tags for testing."""
    tags_data = [
        {"name": "Science", "color": "#00FF00"},
        {"name": "Mathematics", "color": "#0000FF"},
        {"name": "Beginner", "color": "#FFFF00"}
    ]

    tags = []
    for tag_data in tags_data:
        response = authenticated_client.post("/api/v1/tags/", json=tag_data)
        tags.append(response.json()["data"])

    return tags


def test_create_quiz_with_draft_status(authenticated_client):
    """Test creating a quiz with draft status."""
    quiz_data = {
        "name": "Draft Quiz",
        "subject": "Testing",
        "is_draft": True,
        "status": "draft"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Draft Quiz"
    assert data["is_draft"] is True
    assert data["status"] == "draft"


def test_create_quiz_with_published_status(authenticated_client):
    """Test creating a quiz with published status."""
    quiz_data = {
        "name": "Published Quiz",
        "subject": "Testing",
        "is_draft": False,
        "status": "published"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Published Quiz"
    assert data["is_draft"] is False
    assert data["status"] == "published"


def test_create_quiz_default_draft_status(authenticated_client):
    """Test that quiz defaults to draft status if not specified."""
    quiz_data = {
        "name": "Default Status Quiz",
        "subject": "Testing"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["is_draft"] is True  # Should default to True
    assert data["status"] == "draft"  # Should default to 'draft'


def test_create_quiz_with_tags(authenticated_client, sample_tags):
    """Test creating a quiz with tags."""
    tag_ids = [sample_tags[0]["id"], sample_tags[1]["id"]]

    quiz_data = {
        "name": "Quiz with Tags",
        "subject": "Testing",
        "tag_ids": tag_ids
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Quiz with Tags"
    assert "tag_ids" in data
    assert len(data["tag_ids"]) == 2
    assert set(data["tag_ids"]) == set(tag_ids)


def test_create_quiz_with_small_image(authenticated_client):
    """Test creating a quiz with a small image (< 100KB)."""
    # Create a small image (1KB)
    small_image = b"A" * 1024  # 1KB
    base64_image = base64.b64encode(small_image).decode('utf-8')

    quiz_data = {
        "name": "Quiz with Small Image",
        "subject": "Testing",
        "image": base64_image
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Quiz with Small Image"
    assert data["image"] is not None


def test_create_quiz_with_large_image_fails(authenticated_client):
    """Test that creating a quiz with image > 100KB fails."""
    # Create a large image (150KB)
    large_image = b"A" * (150 * 1024)  # 150KB
    base64_image = base64.b64encode(large_image).decode('utf-8')

    quiz_data = {
        "name": "Quiz with Large Image",
        "subject": "Testing",
        "image": base64_image
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 413  # Request Entity Too Large
    assert "exceeds maximum" in response.json()["detail"].lower()


def test_create_quiz_with_invalid_base64_image(authenticated_client):
    """Test that invalid Base64 image data fails."""
    quiz_data = {
        "name": "Quiz with Invalid Image",
        "subject": "Testing",
        "image": "not-valid-base64!!!"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 400  # Bad Request
    assert "invalid" in response.json()["detail"].lower()


def test_update_quiz_draft_to_published(authenticated_client):
    """Test updating quiz from draft to published status."""
    # Create draft quiz
    quiz_data = {
        "name": "Draft to Published",
        "subject": "Testing",
        "is_draft": True,
        "status": "draft"
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Update to published
    update_data = {
        "is_draft": False,
        "status": "published"
    }
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_draft"] is False
    assert data["status"] == "published"


def test_update_quiz_add_tags(authenticated_client, sample_tags):
    """Test adding tags to an existing quiz."""
    # Create quiz without tags
    quiz_data = {
        "name": "Quiz to Add Tags",
        "subject": "Testing"
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Add tags
    tag_ids = [sample_tags[0]["id"], sample_tags[2]["id"]]
    update_data = {"tag_ids": tag_ids}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["tag_ids"]) == 2
    assert set(data["tag_ids"]) == set(tag_ids)


def test_update_quiz_remove_tags(authenticated_client, sample_tags):
    """Test removing all tags from a quiz."""
    # Create quiz with tags
    tag_ids = [sample_tags[0]["id"], sample_tags[1]["id"]]
    quiz_data = {
        "name": "Quiz to Remove Tags",
        "subject": "Testing",
        "tag_ids": tag_ids
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Remove all tags
    update_data = {"tag_ids": []}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["tag_ids"]) == 0


def test_update_quiz_change_tags(authenticated_client, sample_tags):
    """Test changing quiz tags."""
    # Create quiz with initial tags
    initial_tag_ids = [sample_tags[0]["id"]]
    quiz_data = {
        "name": "Quiz to Change Tags",
        "subject": "Testing",
        "tag_ids": initial_tag_ids
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Change tags
    new_tag_ids = [sample_tags[1]["id"], sample_tags[2]["id"]]
    update_data = {"tag_ids": new_tag_ids}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data["tag_ids"]) == set(new_tag_ids)


def test_update_quiz_add_image(authenticated_client):
    """Test adding an image to an existing quiz."""
    # Create quiz without image
    quiz_data = {
        "name": "Quiz to Add Image",
        "subject": "Testing"
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Add image
    small_image = b"B" * 2048  # 2KB
    base64_image = base64.b64encode(small_image).decode('utf-8')
    update_data = {"image": base64_image}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["image"] is not None


def test_update_quiz_remove_image(authenticated_client):
    """Test removing image from a quiz."""
    # Create quiz with image
    small_image = b"C" * 1024  # 1KB
    base64_image = base64.b64encode(small_image).decode('utf-8')
    quiz_data = {
        "name": "Quiz to Remove Image",
        "subject": "Testing",
        "image": base64_image
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Remove image by passing empty string
    update_data = {"image": ""}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["image"] is None


def test_update_quiz_large_image_fails(authenticated_client):
    """Test that updating with image > 100KB fails."""
    # Create quiz
    quiz_data = {
        "name": "Quiz for Large Image Update",
        "subject": "Testing"
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Try to update with large image
    large_image = b"D" * (150 * 1024)  # 150KB
    base64_image = base64.b64encode(large_image).decode('utf-8')
    update_data = {"image": base64_image}
    response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)

    assert response.status_code == 413  # Request Entity Too Large
    assert "exceeds maximum" in response.json()["detail"].lower()


def test_get_quiz_includes_new_fields(authenticated_client, sample_tags):
    """Test that GET quiz includes is_draft, status, and tag_ids."""
    # Create quiz with all new fields
    tag_ids = [sample_tags[0]["id"]]
    small_image = b"E" * 512  # 512 bytes
    base64_image = base64.b64encode(small_image).decode('utf-8')

    quiz_data = {
        "name": "Complete Quiz",
        "subject": "Testing",
        "is_draft": False,
        "status": "published",
        "tag_ids": tag_ids,
        "image": base64_image
    }
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = create_response.json()["data"]["id"]

    # Get quiz
    response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_draft"] is False
    assert data["status"] == "published"
    assert data["tag_ids"] == tag_ids
    assert data["image"] is not None


def test_list_quizzes_includes_new_fields(authenticated_client, sample_tags):
    """Test that listing quizzes includes new fields."""
    # Create multiple quizzes with different statuses and tags
    quiz1_data = {
        "name": "Draft Quiz 1",
        "subject": "Testing",
        "is_draft": True,
        "status": "draft",
        "tag_ids": [sample_tags[0]["id"]]
    }
    quiz2_data = {
        "name": "Published Quiz 1",
        "subject": "Testing",
        "is_draft": False,
        "status": "published",
        "tag_ids": [sample_tags[1]["id"]]
    }

    authenticated_client.post("/api/v1/quizzes/", json=quiz1_data)
    authenticated_client.post("/api/v1/quizzes/", json=quiz2_data)

    # List quizzes
    response = authenticated_client.get("/api/v1/quizzes/")

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 2

    # Check that all quizzes have new fields
    for quiz in data:
        assert "is_draft" in quiz
        assert "status" in quiz
        assert "tag_ids" in quiz


def test_quiz_with_nonexistent_tag_ids(authenticated_client):
    """Test that creating quiz with nonexistent tag IDs doesn't fail (tags are just not added)."""
    quiz_data = {
        "name": "Quiz with Bad Tags",
        "subject": "Testing",
        "tag_ids": [99999, 88888]  # Nonexistent tag IDs
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

    assert response.status_code == 201
    data = response.json()["data"]
    # Tags that don't exist won't be added
    assert len(data["tag_ids"]) == 0


def test_delete_tag_removes_from_quizzes(authenticated_client):
    """Test that deleting a tag removes it from all associated quizzes."""
    # Create a tag
    tag_data = {"name": "ToDelete", "color": "#000000"}
    tag_response = authenticated_client.post("/api/v1/tags/", json=tag_data)
    tag_id = tag_response.json()["data"]["id"]

    # Create quiz with this tag
    quiz_data = {
        "name": "Quiz with Tag to Delete",
        "subject": "Testing",
        "tag_ids": [tag_id]
    }
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    # Verify quiz has the tag
    get_response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")
    assert tag_id in get_response.json()["data"]["tag_ids"]

    # Delete the tag
    authenticated_client.delete(f"/api/v1/tags/{tag_id}")

    # Verify tag is removed from quiz
    get_response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")
    assert tag_id not in get_response.json()["data"]["tag_ids"]


def test_quiz_status_values(authenticated_client):
    """Test different quiz status values."""
    statuses = ["draft", "published", "archived"]

    for status_value in statuses:
        quiz_data = {
            "name": f"Quiz {status_value}",
            "subject": "Testing",
            "status": status_value
        }

        response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["status"] == status_value
