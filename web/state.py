"""
Session state management for the web application.
"""

import streamlit as st


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        # Global state
        "current_user": "Emila",
        "selected_quiz": None,
        "current_page": "library",
        
        # Learning mode state
        "learning_cards_index": 0,
        "show_answer": False,
        "learning_quiz_id": None,
        "learning_session_started": False,
        
        # Test mode state
        "test_cards_index": 0,
        "test_answers": [],
        "test_quiz_id": None,
        "test_completed": False,
        "test_session_started": False,
        
        # Quiz creator state
        "new_flashcards": [{"question": {}, "answer": {}}],
        "creator_quiz_name": "",
        "creator_quiz_subject": "",
        "creator_quiz_description": "",
        
        # Settings state
        "settings_tab": "database",
        "confirm_reset": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_learning_state():
    """Reset learning mode session state."""
    st.session_state.learning_cards_index = 0
    st.session_state.show_answer = False
    st.session_state.learning_quiz_id = None
    st.session_state.learning_session_started = False


def reset_test_state():
    """Reset test mode session state."""
    st.session_state.test_cards_index = 0
    st.session_state.test_answers = []
    st.session_state.test_quiz_id = None
    st.session_state.test_completed = False
    st.session_state.test_session_started = False


def reset_creator_state():
    """Reset quiz creator state."""
    st.session_state.new_flashcards = [{"question": {}, "answer": {}}]
    st.session_state.creator_quiz_name = ""
    st.session_state.creator_quiz_subject = ""
    st.session_state.creator_quiz_description = ""


def reset_all_states():
    """Reset all session states (useful for logout/reset)."""
    reset_learning_state()
    reset_test_state()
    reset_creator_state()
    st.session_state.selected_quiz = None
    st.session_state.current_page = "library"


def get_learning_progress():
    """Get current learning progress."""
    if not st.session_state.learning_session_started:
        return 0, 0
    
    current = st.session_state.learning_cards_index
    total = getattr(st.session_state, 'learning_total_cards', 0)
    return current, total


def get_test_progress():
    """Get current test progress."""
    if not st.session_state.test_session_started:
        return 0, 0
    
    current = st.session_state.test_cards_index
    total = getattr(st.session_state, 'test_total_cards', 0)
    return current, total


def is_quiz_selected():
    """Check if a quiz is currently selected."""
    return st.session_state.selected_quiz is not None


def get_selected_quiz_id():
    """Get the currently selected quiz ID."""
    return st.session_state.selected_quiz


def set_selected_quiz(quiz_id: int):
    """Set the selected quiz and reset related states."""
    st.session_state.selected_quiz = quiz_id
    
    # Reset states when switching quizzes
    if st.session_state.learning_quiz_id != quiz_id:
        reset_learning_state()
    if st.session_state.test_quiz_id != quiz_id:
        reset_test_state()


def navigate_to_page(page: str):
    """Navigate to a specific page."""
    valid_pages = ["library", "learning", "testing", "progress", "creator", "settings"]
    if page in valid_pages:
        st.session_state.current_page = page
    else:
        raise ValueError(f"Invalid page: {page}")


def start_learning_session(quiz_id: int, total_cards: int):
    """Start a learning session."""
    st.session_state.learning_quiz_id = quiz_id
    st.session_state.learning_session_started = True
    st.session_state.learning_total_cards = total_cards
    st.session_state.learning_cards_index = 0
    st.session_state.show_answer = False


def start_test_session(quiz_id: int, total_cards: int):
    """Start a test session."""
    st.session_state.test_quiz_id = quiz_id
    st.session_state.test_session_started = True
    st.session_state.test_total_cards = total_cards
    st.session_state.test_cards_index = 0
    st.session_state.test_answers = []
    st.session_state.test_completed = False


def add_test_answer(card, user_answer: str, correct_answer: str):
    """Add an answer to the current test session."""
    st.session_state.test_answers.append({
        "card": card,
        "user_answer": user_answer.strip(),
        "correct_answer": correct_answer
    })


def complete_test_session():
    """Mark the current test session as completed."""
    st.session_state.test_completed = True


def get_creator_flashcard_count():
    """Get the number of flashcards in the creator."""
    return len(st.session_state.new_flashcards)


def add_creator_flashcard():
    """Add a new flashcard to the creator."""
    st.session_state.new_flashcards.append({"question": {}, "answer": {}})


def remove_creator_flashcard(index: int):
    """Remove a flashcard from the creator."""
    if 0 <= index < len(st.session_state.new_flashcards) and len(st.session_state.new_flashcards) > 1:
        st.session_state.new_flashcards.pop(index)


def update_creator_flashcard(index: int, question_data: dict, answer_data: dict):
    """Update a flashcard in the creator."""
    if 0 <= index < len(st.session_state.new_flashcards):
        st.session_state.new_flashcards[index] = {
            "question": question_data,
            "answer": answer_data
        }


def get_complete_creator_flashcards():
    """Get only complete flashcards from the creator."""
    complete_cards = []
    for card in st.session_state.new_flashcards:
        q_title = card["question"].get("title", "").strip()
        a_text = card["answer"].get("text", "").strip()
        
        if q_title and a_text:
            complete_cards.append(card)
    
    return complete_cards