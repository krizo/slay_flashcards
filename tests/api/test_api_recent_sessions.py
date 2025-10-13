"""
Tests for recent sessions endpoint fixes.

This module tests the fixes made to the /api/v1/sessions/user/{user_id}/recent endpoint:
1. Proper filtering of test/learn sessions (completed tests, all learn sessions)
2. Quiz metadata inclusion (quiz_name, quiz_category, quiz_level)
3. Handling of many incomplete test sessions
"""


def test_recent_sessions_includes_quiz_metadata(authenticated_client):
    """Test that recent sessions include quiz name, category, and level."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create a quiz with metadata
    quiz_data = {
        "name": "Physics Quiz",
        "subject": "Science",
        "category": "Mechanics",
        "level": "Grade 10"
    }
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    quiz_id = quiz_response.json()["data"]["id"]

    # Create a learn session
    session_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "learn"}
    session_response = authenticated_client.post("/api/v1/sessions/", json=session_data)
    assert session_response.status_code == 201

    # Get recent sessions
    response = authenticated_client.get(f"/api/v1/sessions/user/{user_id}/recent?limit=5")
    assert response.status_code == 200

    sessions = response.json()["data"]
    assert len(sessions) > 0

    # Find our session
    our_session = next((s for s in sessions if s["quiz_id"] == quiz_id), None)
    assert our_session is not None, "Session not found in recent sessions"

    # Verify quiz metadata is included
    assert our_session["quiz_name"] == "Physics Quiz"
    assert our_session["quiz_category"] == "Mechanics"
    assert our_session["quiz_level"] == "Grade 10"


def test_recent_sessions_filters_incomplete_test_sessions(authenticated_client):
    """Test that incomplete test sessions are filtered out but learn sessions are included."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create a quiz
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Filter Test Quiz"})
    quiz_id = quiz_response.json()["data"]["id"]

    # Create an incomplete test session (should be filtered out)
    incomplete_test_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "test"}
    incomplete_test_response = authenticated_client.post("/api/v1/sessions/", json=incomplete_test_data)
    incomplete_test_id = incomplete_test_response.json()["data"]["id"]

    # Create a learn session (should be included even if incomplete)
    learn_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "learn"}
    learn_response = authenticated_client.post("/api/v1/sessions/", json=learn_data)
    learn_id = learn_response.json()["data"]["id"]

    # Get recent sessions
    response = authenticated_client.get(f"/api/v1/sessions/user/{user_id}/recent?limit=10")
    assert response.status_code == 200

    sessions = response.json()["data"]
    session_ids = [s["id"] for s in sessions]

    # Incomplete test session should NOT be in the list
    assert incomplete_test_id not in session_ids, "Incomplete test session should be filtered out"

    # Learn session SHOULD be in the list (even if incomplete)
    assert learn_id in session_ids, "Learn session should be included even if incomplete"


def test_recent_sessions_includes_completed_test_sessions(authenticated_client):
    """Test that completed test sessions are included in recent sessions."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create a quiz with a flashcard
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Completed Test Quiz"})
    quiz_id = quiz_response.json()["data"]["id"]

    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Test Question", "text": "What is 2+2?", "difficulty": 1},
        "answer": {"text": "4"}
    }
    flashcard_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    flashcard_id = flashcard_response.json()["data"]["id"]

    # Create a test session
    session_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "test"}
    session_response = authenticated_client.post("/api/v1/sessions/", json=session_data)
    session_id = session_response.json()["data"]["id"]

    # Submit test answers to complete the session
    test_submission = {
        "session_id": session_id,
        "answers": [{"flashcard_id": flashcard_id, "user_answer": "4", "time_taken": 2.0}]
    }
    submit_response = authenticated_client.post("/api/v1/sessions/test/submit", json=test_submission)
    assert submit_response.status_code == 200

    # Get recent sessions
    response = authenticated_client.get(f"/api/v1/sessions/user/{user_id}/recent?limit=10")
    assert response.status_code == 200

    sessions = response.json()["data"]
    session_ids = [s["id"] for s in sessions]

    # Completed test session SHOULD be in the list
    assert session_id in session_ids, "Completed test session should be included"

    # Find the session and verify it has a score
    completed_session = next((s for s in sessions if s["id"] == session_id), None)
    assert completed_session is not None
    assert completed_session["completed"] is True
    assert completed_session["score"] is not None
    assert completed_session["mode"] == "test"


def test_recent_sessions_handles_many_incomplete_tests(authenticated_client):
    """Test that endpoint can find valid sessions even with many incomplete test sessions."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create a quiz
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Many Sessions Quiz"})
    quiz_id = quiz_response.json()["data"]["id"]

    # Create many incomplete test sessions (simulating the real-world scenario)
    for _ in range(20):
        incomplete_test_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "test"}
        authenticated_client.post("/api/v1/sessions/", json=incomplete_test_data)

    # Create a learn session that should still be found
    learn_data = {"user_id": user_id, "quiz_id": quiz_id, "mode": "learn"}
    learn_response = authenticated_client.post("/api/v1/sessions/", json=learn_data)
    learn_id = learn_response.json()["data"]["id"]

    # Get recent sessions with small limit
    response = authenticated_client.get(f"/api/v1/sessions/user/{user_id}/recent?limit=5")
    assert response.status_code == 200

    sessions = response.json()["data"]

    # The learn session should be found despite many incomplete tests before it
    session_ids = [s["id"] for s in sessions]
    assert learn_id in session_ids, "Learn session should be found despite many incomplete test sessions"


def test_recent_sessions_mixed_modes(authenticated_client):
    """Test recent sessions with a mix of completed/incomplete test and learn sessions."""
    # Get user ID
    me_response = authenticated_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]

    # Create quiz with flashcard
    quiz_response = authenticated_client.post("/api/v1/quizzes/", json={"name": "Mixed Sessions Quiz"})
    quiz_id = quiz_response.json()["data"]["id"]

    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Q", "text": "Test", "difficulty": 1},
        "answer": {"text": "A"}
    }
    flashcard_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    flashcard_id = flashcard_response.json()["data"]["id"]

    # 1. Create incomplete test (should NOT appear unless it's the only test)
    incomplete_test_response = authenticated_client.post("/api/v1/sessions/", json={
        "user_id": user_id, "quiz_id": quiz_id, "mode": "test"
    })
    incomplete_test_id = incomplete_test_response.json()["data"]["id"]

    # 2. Create completed test (should appear)
    completed_test_response = authenticated_client.post("/api/v1/sessions/", json={
        "user_id": user_id, "quiz_id": quiz_id, "mode": "test"
    })
    completed_test_id = completed_test_response.json()["data"]["id"]
    authenticated_client.post("/api/v1/sessions/test/submit", json={
        "session_id": completed_test_id,
        "answers": [{"flashcard_id": flashcard_id, "user_answer": "A"}]
    })

    # 3. Create incomplete learn (should appear)
    incomplete_learn_response = authenticated_client.post("/api/v1/sessions/", json={
        "user_id": user_id, "quiz_id": quiz_id, "mode": "learn"
    })
    incomplete_learn_id = incomplete_learn_response.json()["data"]["id"]

    # 4. Create completed learn (should appear)
    completed_learn_response = authenticated_client.post("/api/v1/sessions/", json={
        "user_id": user_id, "quiz_id": quiz_id, "mode": "learn"
    })
    completed_learn_id = completed_learn_response.json()["data"]["id"]
    authenticated_client.post(f"/api/v1/sessions/{completed_learn_id}/complete")

    # Get recent sessions
    response = authenticated_client.get(f"/api/v1/sessions/user/{user_id}/recent?limit=10")
    assert response.status_code == 200

    recent_sessions = response.json()["data"]
    recent_ids = [s["id"] for s in recent_sessions]

    # Core assertions: verify the filtering logic works correctly
    # All test sessions in results MUST be completed
    test_sessions = [s for s in recent_sessions if s["mode"] == "test"]
    for test_session in test_sessions:
        assert test_session["completed"] is True, \
            f"Test session {test_session['id']} should be completed but isn't"
        assert test_session["score"] is not None, \
            f"Test session {test_session['id']} should have a score"

    # Learn sessions can be incomplete or completed
    learn_sessions = [s for s in recent_sessions if s["mode"] == "learn"]
    assert len(learn_sessions) >= 1, "Should have at least 1 learn session"

    # The completed test should always appear
    assert completed_test_id in recent_ids, "Completed test session should appear in recent sessions"

    # At least one learn session should appear
    learn_session_found = incomplete_learn_id in recent_ids or completed_learn_id in recent_ids
    assert learn_session_found, "At least one learn session should appear in recent sessions"
