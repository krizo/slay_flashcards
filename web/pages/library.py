"""
Quiz Library page - Browse and select quizzes.
"""

import streamlit as st
import json
from web.web_database import load_quiz_library, get_database_session, import_quiz_from_dict, validate_quiz_data
from web.components.quiz_card import render_quiz_card
from web.components.sidebar import render_page_header
from web.state import set_selected_quiz, navigate_to_page


def show_page():
    """Display quiz library page."""
    render_page_header(
        "Quiz Library",
        "Browse and select quizzes for learning and testing",
        "📚"
    )

    quizzes = load_quiz_library()

    if not quizzes:
        _show_empty_state()
        return

    _show_quiz_library(quizzes)


def _show_empty_state():
    """Show empty state when no quizzes are available."""
    st.warning("No quizzes found. Create or import some quizzes to get started!")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Get Started:**\n- Import a quiz from JSON file\n- Create a new quiz\n- Check the example files")

    with col2:
        if st.button("🎨 Create Your First Quiz", type="primary"):
            navigate_to_page("creator")
            st.rerun()

    st.divider()

    # Quick import section
    with st.expander("📁 Import Quiz", expanded=True):
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")

        if uploaded_file is not None:
            _handle_file_upload(uploaded_file)


def _handle_file_upload(uploaded_file):
    """Handle quiz file upload."""
    try:
        quiz_data = json.load(uploaded_file)

        # Validate quiz data
        is_valid = validate_quiz_data(quiz_data)

        if is_valid:
            # Preview quiz info
            quiz_info = quiz_data.get("quiz", {})
            st.success("✅ Quiz file is valid!")

            with st.container():
                st.write("**Preview:**")
                st.write(f"- **Name:** {quiz_info.get('name', 'Unnamed Quiz')}")
                st.write(f"- **Subject:** {quiz_info.get('subject', 'General')}")
                st.write(f"- **Cards:** {len(quiz_data.get('flashcards', []))}")

                if quiz_info.get('description'):
                    st.write(f"- **Description:** {quiz_info['description']}")

            if st.button("📥 Import Quiz", type="primary"):
                _import_quiz(quiz_data)
        else:
            st.error("❌ Invalid quiz file format! Please check the JSON structure.")

    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file! Please check the file format.")
    except Exception as e:
        st.error(f"❌ File error: {str(e)}")


def _import_quiz(quiz_data):
    """Import quiz data to database."""
    try:
        quiz = import_quiz_from_dict(quiz_data)
        st.success(f"✅ Successfully imported quiz: {quiz.name}")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Import error: {str(e)}")


def _show_quiz_library(quizzes):
    """Show the main quiz library interface."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Available Quizzes ({len(quizzes)})")

        # Search/filter options
        search_term = st.text_input("🔍 Search quizzes...", placeholder="Search by name or subject")

        # Filter quizzes based on search
        filtered_quizzes = _filter_quizzes(quizzes, search_term)

        if not filtered_quizzes:
            st.info("No quizzes match your search criteria.")
            return

        # Display filtered quizzes
        for quiz in filtered_quizzes:
            render_quiz_card(quiz)

    with col2:
        _show_library_stats(quizzes)


def _filter_quizzes(quizzes, search_term):
    """Filter quizzes based on search term."""
    if not search_term:
        return quizzes

    search_lower = search_term.lower()
    filtered = []

    for quiz in quizzes:
        if (search_lower in quiz.name.lower() or
            (quiz.subject and search_lower in quiz.subject.lower()) or
            (quiz.description and search_lower in quiz.description.lower())):
            filtered.append(quiz)

    return filtered


def _show_library_stats(quizzes):
    """Show library statistics in sidebar."""
    st.subheader("📈 Quick Stats")

    # Calculate statistics
    stats = _calculate_library_stats(quizzes)

    # Display metrics
    st.metric("Total Quizzes", stats["total_quizzes"])
    st.metric("Total Cards", stats["total_cards"])
    st.metric("Subjects", stats["subjects"])

    # Subject breakdown
    if stats["subject_breakdown"]:
        st.write("**By Subject:**")
        for subject, count in stats["subject_breakdown"].items():
            st.write(f"- {subject}: {count}")

    st.divider()

    # Quick actions
    st.subheader("⚡ Quick Actions")

    if st.button("🎨 Create Quiz", type="secondary", use_container_width=True):
        navigate_to_page("creator")
        st.rerun()

    if st.button("📊 View Progress", type="secondary", use_container_width=True):
        navigate_to_page("progress")
        st.rerun()

    if st.button("⚙️ Settings", type="secondary", use_container_width=True):
        navigate_to_page("settings")
        st.rerun()

    st.divider()

    # Show recent activity
    _show_recent_activity()


def _calculate_library_stats(quizzes):
    """Calculate library statistics."""
    from web.database import get_database_session
    from services.quiz_service import QuizService

    total_quizzes = len(quizzes)
    total_cards = 0
    subject_counts = {}

    db = get_database_session()
    try:
        quiz_service = QuizService(db)

        for quiz in quizzes:
            cards = quiz_service.get_quiz_flashcards(quiz.id)
            total_cards += len(cards)

            subject = quiz.subject or "General"
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

    finally:
        db.close()

    return {
        "total_quizzes": total_quizzes,
        "total_cards": total_cards,
        "subjects": len(subject_counts),
        "subject_breakdown": dict(sorted(subject_counts.items(), key=lambda x: x[1], reverse=True))
    }


def _show_recent_activity():
    """Show recent user activity."""
    from web.database import load_user_data

    try:
        current_user, user_sessions, _ = load_user_data(st.session_state.current_user)
        recent_sessions = user_sessions[:5]

        if recent_sessions:
            st.write("**Recent Activity:**")
            for session in recent_sessions:
                mode_icon = "🎓" if session.mode == "learn" else "🧪"
                score_text = f" ({session.score}%)" if session.score else ""
                date_str = session.started_at.strftime('%m/%d')

                # Make it clickable to go to that quiz
                if st.button(
                    f"{mode_icon} {session.quiz.name}{score_text}",
                    key=f"recent_{session.id}",
                    help=f"Studied on {date_str}"
                ):
                    set_selected_quiz(session.quiz.id)
                    if session.mode == "learn":
                        navigate_to_page("learning")
                    else:
                        navigate_to_page("testing")
                    st.rerun()
        else:
            st.info("No recent activity")

    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")


def render_quiz_preview(quiz_data):
    """Render a preview of quiz data before import."""
    quiz_info = quiz_data.get("quiz", {})
    flashcards = quiz_data.get("flashcards", [])

    st.markdown("### 👀 Quiz Preview")

    # Basic info
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {quiz_info.get('name', 'Unnamed')}")
        st.write(f"**Subject:** {quiz_info.get('subject', 'General')}")

    with col2:
        st.write(f"**Cards:** {len(flashcards)}")
        if quiz_info.get('created_at'):
            st.write(f"**Created:** {quiz_info['created_at']}")

    if quiz_info.get('description'):
        st.write(f"**Description:** {quiz_info['description']}")

    # Sample flashcards
    if flashcards:
        st.write("**Sample Cards:**")
        sample_count = min(3, len(flashcards))

        for i, card in enumerate(flashcards[:sample_count]):
            question = card.get("question", {})
            answer = card.get("answer", {})

            with st.expander(f"Card {i+1}: {question.get('title', 'No title')}"):
                st.write(f"**Q:** {question.get('text', question.get('title', ''))}")
                st.write(f"**A:** {answer.get('text', '')}")

                if question.get('emoji'):
                    st.write(f"**Emoji:** {question['emoji']}")

        if len(flashcards) > sample_count:
            st.write(f"... and {len(flashcards) - sample_count} more cards")


def render_import_help():
    """Render help information for importing quizzes."""
    with st.expander("❓ Import Help"):
        st.markdown("""
        **Supported Format:** JSON files with the following structure:
        
        ```json
        {
          "quiz": {
            "name": "Quiz Name",
            "subject": "Subject (optional)",
            "description": "Description (optional)"
          },
          "flashcards": [
            {
              "question": {
                "title": "Question title",
                "text": "Full question text",
                "lang": "en",
                "difficulty": 1,
                "emoji": "🎯"
              },
              "answer": {
                "text": "Answer text",
                "lang": "fr"
              }
            }
          ]
        }
        ```
        
        **Required Fields:**
        - `quiz.name`
        - `question.title`
        - `answer.text`
        
        **Optional Fields:**
        - All other fields are optional and will enhance the learning experience
        """)


def show_quiz_details(quiz):
    """Show detailed information about a quiz."""
    from web.database import load_quiz_with_cards, load_quiz_statistics

    quiz, cards = load_quiz_with_cards(quiz.id)
    stats = load_quiz_statistics(quiz.id)

    st.subheader(f"📋 Quiz Details: {quiz.name}")

    # Basic information
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Cards", len(cards))

    with col2:
        avg_difficulty = stats.get("difficulty_distribution", {})
        if avg_difficulty:
            total_difficulty = sum(d * count for d, count in avg_difficulty.items())
            avg = total_difficulty / sum(avg_difficulty.values())
            st.metric("Avg Difficulty", f"{avg:.1f}")
        else:
            st.metric("Avg Difficulty", "N/A")

    with col3:
        languages = len(stats.get("question_languages", {}))
        st.metric("Languages", languages if languages > 0 else 1)

    # Additional details
    if quiz.description:
        st.write(f"**Description:** {quiz.description}")

    if quiz.created_at:
        st.write(f"**Created:** {quiz.created_at.strftime('%Y-%m-%d %H:%M')}")

    # Language breakdown
    if stats.get("question_languages") or stats.get("answer_languages"):
        st.write("**Languages:**")
        col1, col2 = st.columns(2)

        with col1:
            st.write("*Questions:*")
            for lang, count in stats.get("question_languages", {}).items():
                st.write(f"- {lang.upper()}: {count}")

        with col2:
            st.write("*Answers:*")
            for lang, count in stats.get("answer_languages", {}).items():
                st.write(f"- {lang.upper()}: {count}")

    # Sample cards
    if cards:
        st.write("**Sample Cards:**")
        sample_cards = cards[:3]

        for i, card in enumerate(sample_cards):
            with st.expander(f"Card {i+1}: {card.question_title}"):
                if card.question_emoji:
                    st.write(f"{card.question_emoji} **{card.question_title}**")
                else:
                    st.write(f"**Q:** {card.question_title}")

                if card.question_text != card.question_title:
                    st.write(f"*{card.question_text}*")

                st.write(f"**A:** {card.answer_text}")

                # Metadata
                metadata = []
                if card.question_lang:
                    metadata.append(f"Q: {card.question_lang}")
                if card.answer_lang:
                    metadata.append(f"A: {card.answer_lang}")
                if card.question_difficulty:
                    metadata.append(f"Difficulty: {card.question_difficulty}")

                if metadata:
                    st.caption(" • ".join(metadata))