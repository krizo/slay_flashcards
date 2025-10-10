"""
API tests for quiz category and level fields.

Tests the new category and level fields for quizzes through the API.
"""


def test_create_quiz_with_category_and_level(authenticated_client):
    """Test creating a quiz with category and level."""
    quiz_data = {
        "name": "Polish Geography",
        "subject": "Geography",
        "category": "Poland",
        "level": "Class 5"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert response.status_code == 201

    data = response.json()["data"]
    assert data["name"] == "Polish Geography"
    assert data["subject"] == "Geography"
    assert data["category"] == "Poland"
    assert data["level"] == "Class 5"


def test_create_quiz_without_category_and_level(authenticated_client):
    """Test creating a quiz without category and level (should still work)."""
    quiz_data = {
        "name": "Basic Quiz",
        "subject": "Math"
    }

    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert response.status_code == 201

    data = response.json()["data"]
    assert data["name"] == "Basic Quiz"
    assert data["subject"] == "Math"
    assert data["category"] is None
    assert data["level"] is None


def test_filter_quizzes_by_category(authenticated_client):
    """Test filtering quizzes by category."""
    # Create quizzes with different categories
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Poland Geo", "subject": "Geography", "category": "Poland"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "France Geo", "subject": "Geography", "category": "France"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Poland History", "subject": "History", "category": "Poland"
    })

    # Filter by category
    response = authenticated_client.get("/api/v1/quizzes/?category=Poland")
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 2
    assert all(q["category"] == "Poland" for q in data)


def test_filter_quizzes_by_level(authenticated_client):
    """Test filtering quizzes by level."""
    # Create quizzes with different levels
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Beginner Math", "subject": "Mathematics", "level": "Beginner"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Advanced Math", "subject": "Mathematics", "level": "Advanced"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Beginner Science", "subject": "Science", "level": "Beginner"
    })

    # Filter by level
    response = authenticated_client.get("/api/v1/quizzes/?level=Beginner")
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 2
    assert all(q["level"] == "Beginner" for q in data)


def test_filter_quizzes_by_subject_category_and_level(authenticated_client):
    """Test filtering quizzes by multiple criteria."""
    # Create quizzes
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Advanced Poland Geo",
        "subject": "Geography",
        "category": "Poland",
        "level": "Advanced"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Beginner Poland Geo",
        "subject": "Geography",
        "category": "Poland",
        "level": "Beginner"
    })
    authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Advanced France Geo",
        "subject": "Geography",
        "category": "France",
        "level": "Advanced"
    })

    # Filter by subject, category, and level
    response = authenticated_client.get(
        "/api/v1/quizzes/?subject=Geography&category=Poland&level=Advanced"
    )
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Advanced Poland Geo"
    assert data[0]["subject"] == "Geography"
    assert data[0]["category"] == "Poland"
    assert data[0]["level"] == "Advanced"


def test_update_quiz_category_and_level(authenticated_client):
    """Test updating quiz category and level."""
    # Create a quiz
    create_response = authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Test Quiz",
        "subject": "Math"
    })
    quiz_id = create_response.json()["data"]["id"]

    # Update category and level
    update_data = {
        "category": "Algebra",
        "level": "Intermediate"
    }
    update_response = authenticated_client.put(
        f"/api/v1/quizzes/{quiz_id}",
        json=update_data
    )
    assert update_response.status_code == 200

    data = update_response.json()["data"]
    assert data["category"] == "Algebra"
    assert data["level"] == "Intermediate"


def test_quiz_export_includes_category_and_level(authenticated_client):
    """Test that quiz export includes category and level."""
    # Create a quiz with category and level
    create_response = authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Export Test",
        "subject": "Geography",
        "category": "Poland",
        "level": "Class 6"
    })
    quiz_id = create_response.json()["data"]["id"]

    # Export the quiz
    export_response = authenticated_client.get(f"/api/v1/quizzes/{quiz_id}/export")
    assert export_response.status_code == 200

    quiz_data = export_response.json()["quiz"]
    assert quiz_data["category"] == "Poland"
    assert quiz_data["level"] == "Class 6"


def test_quiz_import_with_category_and_level(authenticated_client):
    """Test importing a quiz with category and level."""
    import_data = {
        "quiz": {
            "name": "Imported Quiz",
            "subject": "History",
            "category": "World War II",
            "level": "Advanced",
            "description": "Advanced WWII quiz"
        },
        "flashcards": [
            {
                "question": {
                    "title": "When did WWII start?",
                    "text": "When did World War II start?"
                },
                "answer": {
                    "text": "1939"
                }
            }
        ]
    }

    response = authenticated_client.post("/api/v1/quizzes/import", json=import_data)
    assert response.status_code == 201

    data = response.json()["data"]
    assert data["name"] == "Imported Quiz"
    assert data["subject"] == "History"
    assert data["category"] == "World War II"
    assert data["level"] == "Advanced"


def test_quiz_duplicate_preserves_category_and_level(authenticated_client):
    """Test that duplicating a quiz preserves category and level."""
    # Create original quiz
    create_response = authenticated_client.post("/api/v1/quizzes/", json={
        "name": "Original Quiz",
        "subject": "Science",
        "category": "Physics",
        "level": "Beginner"
    })
    original_id = create_response.json()["data"]["id"]

    # Duplicate the quiz
    duplicate_response = authenticated_client.post(
        f"/api/v1/quizzes/{original_id}/duplicate",
        params={"new_name": "Duplicated Quiz"}
    )
    assert duplicate_response.status_code == 201

    data = duplicate_response.json()["data"]
    assert data["name"] == "Duplicated Quiz"
    assert data["subject"] == "Science"
    assert data["category"] == "Physics"
    assert data["level"] == "Beginner"
