import streamlit as st
from services.quiz_service import QuizService
from web.web_database import get_database_session


def render_quiz_card(quiz):
    """Render a quiz card with actions."""
    with st.container():
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

        # Quiz header
        header_col1, header_col2 = st.columns([3, 1])

        with header_col1:
            st.subheader(f"🎯 {quiz.name}")
            if quiz.description:
                st.write(quiz.description)
            if quiz.subject:
                st.write(f"**Subject:** {quiz.subject}")

        with header_col2:
            if quiz.created_at:
                st.write(f"**Created:** {quiz.created_at.strftime('%Y-%m-%d')}")

        # Quiz metrics
        _render_quiz_metrics(quiz)

        # Action buttons
        _render_quiz_actions(quiz)

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")  # Add spacing


def _render_quiz_metrics(quiz):
    """Render quiz metrics."""
    db = get_database_session()
    try:
        quiz_service = QuizService(db)
        cards = quiz_service.get_quiz_flashcards(quiz.id)

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("Cards", len(cards))

        with metric_col2:
            difficulties = [c.question_difficulty for c in cards if c.question_difficulty]
            avg_diff = sum(difficulties) / len(difficulties) if difficulties else 0
            st.metric("Avg Difficulty", f"{avg_diff:.1f}" if avg_diff > 0 else "N/A")

        with metric_col3:
            languages = set(c.question_lang for c in cards if c.question_lang)
            st.metric("Languages", len(languages) if languages else 1)

    except Exception as e:
        st.error(f"Error loading quiz data: {str(e)}")
    finally:
        db.close()


def _render_quiz_actions(quiz):
    """Render quiz action buttons."""
    button_col1, button_col2 = st.columns(2)

    with button_col1:
        if st.button(f"🎯 Learn", key=f"learn_btn_{quiz.id}"):
            _start_learning(quiz.id)

    with button_col2:
        if st.button(f"🧪 Test", key=f"test_btn_{quiz.id}"):
            _start_testing(quiz.id)


def _start_learning(quiz_id):
    """Start learning mode for a quiz."""
    from web.state import reset_learning_state

    st.session_state.selected_quiz = quiz_id
    st.session_state.current_page = "learning"
    reset_learning_state()
    st.session_state.learning_quiz_id = quiz_id
    st.rerun()


def _start_testing(quiz_id):
    """Start test mode for a quiz."""
    from web.state import reset_test_state

    st.session_state.selected_quiz = quiz_id
    st.session_state.current_page = "testing"
    reset_test_state()
    st.session_state.test_quiz_id = quiz_id
    st.rerun()
