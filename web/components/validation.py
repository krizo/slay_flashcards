def validate_quiz_data(data: dict) -> tuple[bool, str]:
    """Validate quiz data and return (is_valid, error_message)."""
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    if "quiz" not in data:
        return False, "Missing 'quiz' section"

    quiz_info = data["quiz"]
    if not quiz_info.get("name", "").strip():
        return False, "Quiz name is required"

    if "flashcards" not in data or not data["flashcards"]:
        return False, "At least one flashcard is required"

    for i, card in enumerate(data["flashcards"]):
        if not isinstance(card, dict):
            return False, f"Flashcard {i+1} must be a dictionary"

        if "question" not in card or "answer" not in card:
            return False, f"Flashcard {i+1} missing question or answer"

        question = card["question"]
        answer = card["answer"]

        if not question.get("title", "").strip():
            return False, f"Flashcard {i+1} question title is required"

        if not answer.get("text", "").strip():
            return False, f"Flashcard {i+1} answer text is required"

    return True, ""


def validate_flashcard_input(question_data: dict, answer_data: dict) -> tuple[bool, str]:
    """Validate flashcard input data."""
    if not question_data.get("title", "").strip():
        return False, "Question title is required"

    if not answer_data.get("text", "").strip():
        return False, "Answer text is required"

    return True, ""