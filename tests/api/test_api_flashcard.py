def test_flashcard_crud(authenticated_client):
    """Test flashcard creation, retrieval, update, and deletion."""
    # Setup: create a quiz
    quiz_data = {"name": "Flashcard CRUD Test", "subject": "Test"}
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Test Q", "text": "Test Question", "difficulty": 3},
        "answer": {"text": "Test Answer"}
    }

    # Create flashcard
    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Get flashcard
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["question_text"] == "Test Question"

    # Update flashcard
    update_data = {
        "question": {"title": "Updated Q", "text": "Updated Question"}
    }
    update_response = authenticated_client.put(f"/api/v1/flashcards/{flashcard_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["data"]["question_title"] == "Updated Q"

    # Delete flashcard
    delete_response = authenticated_client.delete(f"/api/v1/flashcards/{flashcard_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    verify_delete_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert verify_delete_response.status_code == 404

def test_bulk_flashcard_creation(authenticated_client):
    """Test creating multiple flashcards at once."""
    # Setup: create a quiz
    quiz_data = {"name": "Bulk Test", "subject": "Test"}
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    bulk_data = {
        "quiz_id": quiz_id,
        "flashcards": [
            {"question": {"title": "Card 1", "text": "Q1"}, "answer": {"text": "A1"}},
            {"question": {"title": "Card 2", "text": "Q2"}, "answer": {"text": "A2"}}
        ]
    }

    response = authenticated_client.post("/api/v1/flashcards/bulk", json=bulk_data)
    assert response.status_code == 201
    result = response.json()["data"]
    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0

def test_get_random_flashcards(authenticated_client):
    """Test retrieving a random set of flashcards."""
    # Setup: create quiz with multiple flashcards
    quiz_data = {"name": "Random Test", "subject": "Test"}
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    for i in range(10):
        flashcard_data = {
            "quiz_id": quiz_id,
            "question": {"title": f"Card {i}", "text": f"Q{i}", "difficulty": 1},
            "answer": {"text": f"A{i}"}
        }
        authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)

    response = authenticated_client.get(f"/api/v1/flashcards/quiz/{quiz_id}/random?count=5")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 5
