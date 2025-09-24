"""
Learning Mode page - Interactive flashcard learning.
"""

import streamlit as st
from web.web_database import load_quiz_library, load_quiz_with_cards, get_database_session, save_user_session, load_user_data
from web.components.sidebar import render_page_header, render_quiz_selector, render_progress_indicator, render_quiz_info_banner
from web.components.audio import render_question_audio, render_answer_audio
from web.state import (
    start_learning_session, reset_learning_state, get_learning_progress,
    navigate_to_page, get_selected_quiz_id
)


def show_page(audio_enabled=True, question_lang="en", answer_lang="fr", **kwargs):
    """Display learning mode page."""
    render_page_header(
        "Learning Mode",
        "Review flashcards at your own pace with audio support",
        "🎯"
    )

    quizzes = load_quiz_library()
    if not quizzes:
        st.warning("No quizzes available. Please import some quizzes first.")
        if st.button("📚 Go to Library"):
            navigate_to_page("library")
            st.rerun()
        return

    # Determine current quiz
    current_quiz = _get_current_quiz(quizzes)

    if not current_quiz:
        _show_quiz_selector(quizzes)
        return

    # Load flashcards
    quiz, cards = load_quiz_with_cards(current_quiz.id)
    if not cards:
        st.error("This quiz has no flashcards!")
        return

    # Initialize session if needed
    if not st.session_state.learning_session_started:
        start_learning_session(quiz.id, len(cards))

    # Show learning interface
    _show_learning_interface(quiz, cards, {
        "audio_enabled": audio_enabled,
        "question_lang": question_lang,
        "answer_lang": answer_lang
    })


def _get_current_quiz(quizzes):
    """Get the current quiz for learning."""
    selected_quiz_id = get_selected_quiz_id()

    if selected_quiz_id:
        return next((q for q in quizzes if q.id == selected_quiz_id), None)

    if st.session_state.learning_quiz_id:
        return next((q for q in quizzes if q.id == st.session_state.learning_quiz_id), None)

    return None


def _show_quiz_selector(quizzes):
    """Show quiz selection interface."""
    st.info("Please select a quiz to start learning.")

    selected_quiz = render_quiz_selector(quizzes)

    if selected_quiz:
        if st.button("🎯 Start Learning", type="primary"):
            st.session_state.selected_quiz = selected_quiz.id
            st.session_state.learning_quiz_id = selected_quiz.id
            reset_learning_state()
            st.rerun()


def _show_learning_interface(quiz, cards, settings):
    """Show the main learning interface."""
    # Quiz info banner
    render_quiz_info_banner(quiz, len(cards))

    # Progress indicator
    current_index = st.session_state.learning_cards_index
    render_progress_indicator(current_index + 1, len(cards), "Card")

    if current_index < len(cards):
        _show_flashcard_interface(cards[current_index], current_index + 1, len(cards), settings)
    else:
        _show_completion_interface(quiz)


def _show_flashcard_interface(card, card_num, total_cards, settings):
    """Show interface for a single flashcard."""
    # Question display
    st.markdown('<div class="card-question">', unsafe_allow_html=True)
    st.markdown(f"### 📋 {card.question_title}")

    if card.question_emoji:
        st.markdown(f"## {card.question_emoji}")

    if card.question_text != card.question_title:
        st.markdown(f"*{card.question_text}*")
    st.markdown('</div>', unsafe_allow_html=True)

    # Audio button for question
    if settings["audio_enabled"]:
        render_question_audio(card, settings["question_lang"], card_num)

    # Answer reveal logic
    if not st.session_state.show_answer:
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("👁️ Reveal Answer", type="primary", key="reveal_btn", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
    else:
        _show_answer_interface(card, card_num, total_cards, settings)


def _show_answer_interface(card, card_num, total_cards, settings):
    """Show answer and navigation controls."""
    st.divider()

    # Show answer
    st.markdown('<div class="card-answer">', unsafe_allow_html=True)
    st.markdown(f"### ✅ Answer: {card.answer_text}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Audio button for answer
    if settings["audio_enabled"]:
        render_answer_audio(card, settings["answer_lang"], card_num)

    st.divider()

    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Repeat Card", key="repeat_btn"):
            st.session_state.show_answer = False
            st.rerun()

    with col2:
        if card_num < total_cards:
            if st.button("➡️ Next Card", type="primary", key="next_btn"):
                _go_to_next_card()

    with col3:
        if st.button("⏭️ Skip to End", key="skip_btn"):
            st.session_state.learning_cards_index = total_cards
            st.rerun()

    with col4:
        if st.button("🏁 End Session", key="end_btn"):
            _end_learning_session()


def _go_to_next_card():
    """Move to the next flashcard."""
    st.session_state.learning_cards_index += 1
    st.session_state.show_answer = False
    st.rerun()


def _end_learning_session():
    """End the current learning session."""
    # Save session to database
    current_user, _, _ = load_user_data(st.session_state.current_user)
    save_user_session(
        current_user.id,
        st.session_state.learning_quiz_id,
        "learn"
    )

    # Show completion message
    cards_reviewed = st.session_state.learning_cards_index + (1 if st.session_state.show_answer else 0)

    st.success(f"🎉 Learning session completed! Reviewed {cards_reviewed} cards.")
    st.balloons()

    # Clear cache and reset state
    st.cache_data.clear()
    reset_learning_state()
    st.session_state.selected_quiz = None
    navigate_to_page("library")
    st.rerun()


def _show_completion_interface(quiz):
    """Show completion interface when all cards are done."""
    st.success("🎉 All cards completed!")
    st.balloons()

    # Save session to database
    current_user, _, _ = load_user_data(st.session_state.current_user)
    save_user_session(current_user.id, quiz.id, "learn")

    # Session summary
    st.subheader("📊 Session Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cards Reviewed", st.session_state.learning_cards_index)

    with col2:
        st.metric("Quiz", quiz.name)

    with col3:
        if quiz.subject:
            st.metric("Subject", quiz.subject)

    st.divider()

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Start Over", key="start_over_btn", use_container_width=True):
            reset_learning_state()
            start_learning_session(quiz.id, st.session_state.learning_total_cards)
            st.rerun()

    with col2:
        if st.button("🧪 Take Test", key="take_test_btn", use_container_width=True, type="primary"):
            st.session_state.selected_quiz = quiz.id
            navigate_to_page("testing")
            st.rerun()

    with col3:
        if st.button("📚 Back to Library", key="back_lib_btn", use_container_width=True):
            reset_learning_state()
            st.session_state.selected_quiz = None
            navigate_to_page("library")
            st.rerun()


def _show_learning_stats():
    """Show learning statistics and tips."""
    with st.sidebar:
        st.subheader("📈 Learning Tips")

        current, total = get_learning_progress()
        if total > 0:
            progress_pct = (current / total) * 100
            st.progress(progress_pct / 100)
            st.write(f"Progress: {current}/{total} ({progress_pct:.1f}%)")

        st.write("""
        **Learning Tips:**
        - Take your time with each card
        - Use audio to improve pronunciation
        - Repeat difficult cards
        - Regular practice improves retention
        """)


def render_card_difficulty_indicator(card):
    """Render difficulty indicator for a card."""
    if card.question_difficulty:
        difficulty = card.question_difficulty

        if difficulty <= 2:
            st.success(f"🟢 Easy (Level {difficulty})")
        elif difficulty <= 3:
            st.info(f"🟡 Medium (Level {difficulty})")
        else:
            st.warning(f"🔴 Hard (Level {difficulty})")


def render_card_metadata(card):
    """Render metadata information for a card."""
    metadata = []

    if card.question_lang:
        metadata.append(f"Q: {card.question_lang.upper()}")

    if card.answer_lang:
        metadata.append(f"A: {card.answer_lang.upper()}")

    if card.question_difficulty:
        metadata.append(f"Difficulty: {card.question_difficulty}/5")

    if metadata:
        st.caption(" • ".join(metadata))


def _handle_keyboard_shortcuts():
    """Handle keyboard shortcuts for learning mode."""
    # This would require additional Streamlit functionality
    # Currently Streamlit doesn't have great keyboard shortcut support
    # But we can document the intended shortcuts

    with st.expander("⌨️ Keyboard Shortcuts"):
        st.write("""
        **Intended Shortcuts:**
        - `Space` - Reveal answer
        - `Enter` - Next card
        - `R` - Repeat card
        - `Esc` - End session
        
        *Note: Streamlit doesn't fully support custom keyboard shortcuts yet.*
        """)


def show_learning_preferences():
    """Show learning preferences and settings."""
    with st.expander("⚙️ Learning Preferences"):
        auto_play_audio = st.checkbox("Auto-play audio", value=False)
        show_difficulty = st.checkbox("Show difficulty indicators", value=True)
        show_metadata = st.checkbox("Show card metadata", value=True)

        # Store preferences in session state
        st.session_state.learning_preferences = {
            "auto_play_audio": auto_play_audio,
            "show_difficulty": show_difficulty,
            "show_metadata": show_metadata
        }


def _get_learning_preferences():
    """Get learning preferences from session state."""
    return st.session_state.get("learning_preferences", {
        "auto_play_audio": False,
        "show_difficulty": True,
        "show_metadata": True
    })


def render_enhanced_flashcard(card, card_num, total_cards, settings):
    """Render an enhanced flashcard with preferences."""
    preferences = _get_learning_preferences()

    # Card container
    with st.container():
        # Question section
        st.markdown(f"### 📋 Question {card_num}/{total_cards}")

        if preferences.get("show_difficulty", True):
            render_card_difficulty_indicator(card)

        # Main question display
        if card.question_emoji:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"## {card.question_emoji}")
            with col2:
                st.markdown(f"### {card.question_title}")
                if card.question_text != card.question_title:
                    st.markdown(f"*{card.question_text}*")
        else:
            st.markdown(f"### {card.question_title}")
            if card.question_text != card.question_title:
                st.markdown(f"*{card.question_text}*")

        # Metadata
        if preferences.get("show_metadata", True):
            render_card_metadata(card)

        # Auto-play audio if enabled
        if preferences.get("auto_play_audio", False) and settings["audio_enabled"]:
            render_question_audio(card, settings["question_lang"], card_num)