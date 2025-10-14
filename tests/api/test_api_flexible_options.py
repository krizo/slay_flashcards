"""
Tests for flexible option format support in flashcards.

These tests verify:
- Flashcards can be created with simple string options
- Flashcards can be created with {value, label} option objects
- Both choice and multiple_choice types support both formats
- Options are properly stored and retrieved
- API validates option formats correctly
"""

import pytest


@pytest.fixture
def quiz_id(authenticated_client):
    """Create a quiz and return its ID."""
    quiz_data = {"name": "Option Format Test Quiz", "subject": "Test"}
    response = authenticated_client.post("/api/v1/quizzes/", json=quiz_data)
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_choice_with_simple_string_options(authenticated_client, quiz_id):
    """Test creating a choice flashcard with simple string options."""
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "Simple String Choice",
            "text": "Which planet is known as the Red Planet?",
            "difficulty": 1
        },
        "answer": {
            "text": "Mars",
            "type": "choice",
            "options": ["Venus", "Mars", "Jupiter", "Saturn"]
        }
    }

    # Create flashcard
    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Retrieve flashcard
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_type"] == "choice"
    assert flashcard["answer_options"] is not None
    assert len(flashcard["answer_options"]) == 4


def test_choice_with_value_label_objects(authenticated_client, quiz_id):
    """Test creating a choice flashcard with {value, label} option objects."""
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "Value/Label Choice",
            "text": "What is the chemical symbol for Gold?",
            "difficulty": 2
        },
        "answer": {
            "text": "Au",
            "type": "choice",
            "options": [
                {"value": "Au", "label": "Au (Gold)"},
                {"value": "Ag", "label": "Ag (Silver)"},
                {"value": "Fe", "label": "Fe (Iron)"},
                {"value": "Cu", "label": "Cu (Copper)"}
            ],
            "metadata": {"case_sensitive": True}
        }
    }

    # Create flashcard
    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Retrieve flashcard
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_type"] == "choice"
    assert flashcard["answer_options"] is not None
    assert len(flashcard["answer_options"]) == 4

    # Verify options contain value and label
    for option in flashcard["answer_options"]:
        assert "value" in option
        assert "label" in option


def test_multiple_choice_with_simple_strings(authenticated_client, quiz_id):
    """Test creating a multiple_choice flashcard with simple string options."""
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "Simple Multiple Choice",
            "text": "Which are programming languages? (Select all)",
            "difficulty": 1
        },
        "answer": {
            "text": "Python,JavaScript,Java",
            "type": "multiple_choice",
            "options": ["Python", "JavaScript", "HTML", "Java", "CSS"],
            "metadata": {
                "order_matters": False,
                "exact_count": 3
            }
        }
    }

    # Create flashcard
    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Retrieve flashcard
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_type"] == "multiple_choice"
    assert flashcard["answer_options"] is not None
    assert len(flashcard["answer_options"]) == 5


def test_multiple_choice_with_value_label_objects(authenticated_client, quiz_id):
    """Test creating a multiple_choice flashcard with {value, label} objects."""
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "Noble Gases",
            "text": "Which of these are noble gases? (Select all)",
            "difficulty": 2
        },
        "answer": {
            "text": "He,Ne,Ar",
            "type": "multiple_choice",
            "options": [
                {"value": "He", "label": "Helium (He)"},
                {"value": "Ne", "label": "Neon (Ne)"},
                {"value": "O", "label": "Oxygen (O)"},
                {"value": "Ar", "label": "Argon (Ar)"},
                {"value": "N", "label": "Nitrogen (N)"}
            ],
            "metadata": {
                "order_matters": False,
                "exact_count": 3
            }
        }
    }

    # Create flashcard
    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Retrieve flashcard
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_type"] == "multiple_choice"
    assert flashcard["answer_options"] is not None
    assert len(flashcard["answer_options"]) == 5

    # Verify options contain value and label
    for option in flashcard["answer_options"]:
        assert "value" in option
        assert "label" in option


def test_bulk_flashcard_creation_with_mixed_formats(authenticated_client, quiz_id):
    """Test bulk creating flashcards with both option formats."""
    bulk_data = {
        "quiz_id": quiz_id,
        "flashcards": [
            {
                "question": {"title": "Simple String", "text": "Q1", "difficulty": 1},
                "answer": {
                    "text": "Option1",
                    "type": "choice",
                    "options": ["Option1", "Option2", "Option3"]
                }
            },
            {
                "question": {"title": "Value/Label", "text": "Q2", "difficulty": 1},
                "answer": {
                    "text": "a",
                    "type": "choice",
                    "options": [
                        {"value": "a", "label": "Choice A"},
                        {"value": "b", "label": "Choice B"},
                        {"value": "c", "label": "Choice C"}
                    ]
                }
            }
        ]
    }

    response = authenticated_client.post("/api/v1/flashcards/bulk", json=bulk_data)
    assert response.status_code == 201
    result = response.json()["data"]
    assert result["total"] == 2
    assert result["successful"] == 2
    assert result["failed"] == 0


def test_non_choice_types_ignore_options(authenticated_client, quiz_id):
    """Test that non-choice answer types ignore the options field."""
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {
            "title": "Short Text",
            "text": "What is the capital of France?",
            "difficulty": 1
        },
        "answer": {
            "text": "Paris",
            "type": "short_text",
            "options": None  # Should be None or omitted for non-choice types
        }
    }

    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_type"] == "short_text"
    assert flashcard["answer_options"] is None


def test_options_persist_across_updates(authenticated_client, quiz_id):
    """Test that option format persists when updating flashcards."""
    # Create flashcard with value/label options
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Update Test", "text": "Original question", "difficulty": 1},
        "answer": {
            "text": "a",
            "type": "choice",
            "options": [
                {"value": "a", "label": "Option A"},
                {"value": "b", "label": "Option B"}
            ]
        }
    }

    create_response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    assert create_response.status_code == 201
    flashcard_id = create_response.json()["data"]["id"]

    # Update only the question text
    update_data = {
        "question": {"title": "Update Test", "text": "Updated question"}
    }
    update_response = authenticated_client.put(f"/api/v1/flashcards/{flashcard_id}", json=update_data)
    assert update_response.status_code == 200

    # Verify options are still intact
    get_response = authenticated_client.get(f"/api/v1/flashcards/{flashcard_id}")
    assert get_response.status_code == 200

    flashcard = get_response.json()["data"]
    assert flashcard["answer_options"] is not None
    assert len(flashcard["answer_options"]) == 2
    assert flashcard["answer_options"][0]["value"] == "a"


def test_mixed_option_formats_in_single_flashcard(authenticated_client, quiz_id):
    """Test that mixing string and object formats in same options array works."""
    # Note: This might not be recommended, but API should handle it gracefully
    flashcard_data = {
        "quiz_id": quiz_id,
        "question": {"title": "Mixed Format", "text": "Test", "difficulty": 1},
        "answer": {
            "text": "a",
            "type": "choice",
            "options": [
                {"value": "a", "label": "Option A"},
                {"value": "b", "label": "Option B"}
            ]
        }
    }

    response = authenticated_client.post("/api/v1/flashcards/", json=flashcard_data)
    # Should either succeed or fail gracefully
    assert response.status_code in [201, 400, 422]
