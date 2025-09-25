def test_create_session(authenticated_client):
    """Test creating a new session."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create quiz
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Session Test"})
    quiz_id = quiz_response.json()["data"]["id"]

    session_data = {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "mode": "learn"
    }

    response = authenticated_client.post("/api/v1/sessions/", json=session_data)
    assert response.status_code == 201
    assert response.json()["data"]["user_id"] == user_id
    assert response.json()["data"]["mode"] == "learn"


def test_test_submission_and_results(authenticated_client):
    """Test submitting answers for a test session."""
    # Setup: user, quiz, and flashcard
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Test Submission Quiz"})
    quiz_id = quiz_response.json()["data"]["id"]

    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Capital of France?", "text": "What's the capital of France?", "difficulty": 2},
        "answer": {"text": "Paris"}
    }
    flashcard_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    flashcard_id = flashcard_response.json()["data"]["id"]

    # Start a test session
    session_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "test"}
    session_response = authenticated_client.post("/api/v1/sessions/", json=session_data)
    session_id = session_response.json()["data"]["id"]

    # Submit a correct answer
    test_submission = {
        "session_id": session_id,
        "answers": [{"flashcard_id": flashcard_id, "user_answer": "Paris", "time_taken": 5.0}]
    }

    test_response = authenticated_client.post("/api/v1/sessions/test/submit", json=test_submission)
    assert test_response.status_code == 200
    results = test_response.json()["data"]

    assert results["final_score"] == 100
    assert results["correct"] == 1
    assert results["breakdown"][0]["evaluation"] == "correct"


def test_session_statistics(authenticated_client):
    """Test retrieving session statistics for a user."""
    # Step 1: Get the user ID of the authenticated user
    me_response = authenticated_client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    user_id = me_response.json()["data"]["id"]

    # Step 2: Create a quiz
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Stats Quiz"})
    assert quiz_response.status_code == 201
    quiz_id = quiz_response.json()["data"]["id"]

    # Step 3: Create sessions for the user and quiz
    authenticated_client.post("/api/v1/sessions/", json={"user_id": user_id, "quiz_id": quiz_id, "mode": "learn"})
    authenticated_client.post("/api/v1/sessions/", json={"user_id": user_id, "quiz_id": quiz_id, "mode": "test", "score": 85})

    # Step 4: Call the statistics endpoint with the correct user_id as a query parameter
    response = authenticated_client.get(f"/api/v1/sessions/statistics?user_id={user_id}")
    assert response.status_code == 200
    stats = response.json()["data"]

    # Step 5: Assert the results
    assert stats["total_sessions"] >= 2
    assert stats["test_sessions"] >= 1
    assert stats["average_score"] == 85
    assert stats["learn_sessions"] >= 1