def test_quiz_crud(authenticated_client):
    """Test quiz creation, retrieval, and deletion."""
    quiz_data = {"name": "Physics Quiz", "subject": "Science"}

    # Create a quiz
    create_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert create_response.status_code == 201
    quiz_id = create_response.json()["data"]["id"]

    # Retrieve the created quiz
    get_response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["name"] == "Physics Quiz"

    # Update the quiz
    update_data = {"name": "Advanced Physics Quiz"}
    update_response = authenticated_client.put(f"/api/v1/quizzes/{quiz_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "Advanced Physics Quiz"

    # Delete the quiz
    delete_response = authenticated_client.delete(f"/api/v1/quizzes/{quiz_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    verify_delete_response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}")
    assert verify_delete_response.status_code == 404

def test_quiz_list_and_filters(authenticated_client):
    """Test listing quizzes with various filters."""
    # Create multiple quizzes for testing
    authenticated_client.post("/api/v1/quizzes/", json={"name": "Quiz 1", "subject": "History"})
    authenticated_client.post("/api/v1/quizzes/", json={"name": "Quiz 2", "subject": "Math"})
    authenticated_client.post("/api/v1/quizzes/", json={"name": "Quiz 3", "subject": "History"})

    # Test filtering by subject
    response = authenticated_client.get("/api/v1/quizzes/?subject=History")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

    # Test filtering by name pattern
    response = authenticated_client.get("/api/v1/quizzes/?name_contains=Quiz 2")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1

    # Test pagination (e.g., limit=1)
    response = authenticated_client.get("/api/v1/quizzes/?limit=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
