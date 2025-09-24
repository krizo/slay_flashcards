"""
SlayFlashcards Web Application
Main entry point for the Streamlit web interface.

Usage: streamlit run web_app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Import core services
from core.db.database import SessionLocal, Base, engine
from core.learning.presenters.quiz_presenter import AnswerTypeUtils
from core.services.quiz_service import QuizService
from core.services.user_service import UserService
from core.services.audio_service import GTTSAudioService
from core.learning.sessions.quiz_session import TypedAnswerEvaluator

# Configure Streamlit page
st.set_page_config(
    page_title="SlayFlashcards",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    margin-bottom: 1rem;
    text-align: center;
}

.quiz-card {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border: 1px solid #e1e5e9;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
}

.stButton > button {
    width: 100%;
}

.success-box {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border: 1px solid #c3e6cb;
}

.error-box {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
    border: 1px solid #f5c6cb;
}
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        "current_user": "Emila",
        "selected_quiz": None,
        "current_page": "library",
        # Learning mode state
        "learning_cards_index": 0,
        "show_answer": False,
        "learning_quiz_id": None,
        # Test mode state
        "test_cards_index": 0,
        "test_answers": [],
        "test_quiz_id": None,
        "test_completed": False,
        # Quiz creator state
        "new_flashcards": [{"question": {}, "answer": {}}],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_database_session():
    """Get database session with error handling."""
    try:
        return SessionLocal()
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.stop()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_quiz_library():
    """Load quiz library with caching."""
    db = get_database_session()
    try:
        quiz_service = QuizService(db)
        return quiz_service.get_all_quizzes()
    finally:
        db.close()


@st.cache_data(ttl=60)  # Cache for 1 minute
def load_user_data(username: str):
    """Load user data with caching."""
    db = get_database_session()
    try:
        user_service = UserService(db)
        user = user_service.ensure_user_exists(username)
        sessions = user_service.get_user_sessions(user.id)
        stats = user_service.get_user_statistics(user.id)
        return user, sessions, stats
    finally:
        db.close()


def main():
    """Main Streamlit application."""
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🎓 SlayFlashcards</h1>', unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.title("🧭 Navigation")

        # User selection
        username = st.text_input("Username", value=st.session_state.current_user)
        if username != st.session_state.current_user:
            st.session_state.current_user = username
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # Page navigation
        pages = {
            "🎯 Learning Mode": "learning",
            "🧪 Quiz Mode": "testing",
            "📚 Quiz Library": "library",
            "📊 Progress Dashboard": "progress",
            "🎨 Quiz Creator": "creator",
            "⚙️ Settings": "settings"
        }

        selected_page = st.selectbox("Choose a page", list(pages.keys()))
        st.session_state.current_page = pages[selected_page]

        st.divider()

        # Quick user stats
        try:
            current_user, user_sessions, user_stats = load_user_data(st.session_state.current_user)

            st.subheader("📊 Your Stats")
            st.metric("Total Sessions", user_stats.get("total_sessions", 0))

            avg_score = user_stats.get("average_score")
            st.metric("Average Score", f"{avg_score:.1f}%" if avg_score else "N/A")

        except Exception as e:
            st.error(f"Error loading user data: {str(e)}")

    # Main content routing
    try:
        if st.session_state.current_page == "library":
            show_quiz_library()
        elif st.session_state.current_page == "learning":
            show_learning_mode()
        elif st.session_state.current_page == "testing":
            show_quiz_mode()
        elif st.session_state.current_page == "progress":
            show_progress_dashboard()
        elif st.session_state.current_page == "creator":
            show_quiz_creator()
        elif st.session_state.current_page == "settings":
            show_settings()
        else:
            st.error("Page not found!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try refreshing the page or contact support if the issue persists.")


def show_quiz_library():
    """Display quiz library page."""
    st.title("📚 Quiz Library")

    quizzes = load_quiz_library()

    if not quizzes:
        st.warning("No quizzes found. Create or import some quizzes to get started!")

        # Quick import section
        with st.expander("📁 Import Quiz", expanded=True):
            uploaded_file = st.file_uploader("Choose a JSON file", type="json")

            if uploaded_file is not None:
                try:
                    quiz_data = json.load(uploaded_file)

                    if st.button("📥 Import Quiz"):
                        db = get_database_session()
                        try:
                            quiz_service = QuizService(db)
                            if quiz_service.validate_quiz_data(quiz_data):
                                quiz = quiz_service.import_quiz_from_dict(quiz_data)
                                st.success(f"✅ Successfully imported quiz: {quiz.name}")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Invalid quiz format!")
                        except Exception as e:
                            st.error(f"Import error: {str(e)}")
                        finally:
                            db.close()

                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file!")
                except Exception as e:
                    st.error(f"❌ File error: {str(e)}")
        return

    # Display available quizzes
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Available Quizzes ({len(quizzes)})")

        for quiz in quizzes:
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

                # Get quiz statistics
                db = get_database_session()
                try:
                    quiz_service = QuizService(db)
                    cards = quiz_service.get_quiz_flashcards(quiz.id)

                    # Quiz metrics
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

                # Action buttons
                button_col1, button_col2 = st.columns(2)

                with button_col1:
                    if st.button(f"🎯 Learn", key=f"learn_btn_{quiz.id}"):
                        st.session_state.selected_quiz = quiz.id
                        st.session_state.current_page = "learning"
                        st.session_state.learning_cards_index = 0
                        st.session_state.show_answer = False
                        st.session_state.learning_quiz_id = quiz.id
                        st.rerun()

                with button_col2:
                    if st.button(f"🧪 Test", key=f"test_btn_{quiz.id}"):
                        st.session_state.selected_quiz = quiz.id
                        st.session_state.current_page = "testing"
                        st.session_state.test_cards_index = 0
                        st.session_state.test_answers = []
                        st.session_state.test_quiz_id = quiz.id
                        st.session_state.test_completed = False
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
                st.write("")  # Add spacing

    with col2:
        st.subheader("📈 Quick Stats")

        # Library statistics
        total_quizzes = len(quizzes)

        db = get_database_session()
        try:
            quiz_service = QuizService(db)
            total_cards = sum(len(quiz_service.get_quiz_flashcards(q.id)) for q in quizzes)
            subjects = set(q.subject for q in quizzes if q.subject)

            st.metric("Total Quizzes", total_quizzes)
            st.metric("Total Cards", total_cards)
            st.metric("Subjects", len(subjects))

            # Recent activity
            current_user, user_sessions, _ = load_user_data(st.session_state.current_user)
            recent_sessions = user_sessions[:5]

            if recent_sessions:
                st.write("**Recent Activity:**")
                for session in recent_sessions:
                    mode_icon = "🎓" if session.mode == "learn" else "🧪"
                    score_text = f" ({session.score}%)" if session.score else ""
                    date_str = session.started_at.strftime('%m/%d')
                    st.write(f"{mode_icon} {session.quiz.name}{score_text}")
                    st.caption(date_str)
            else:
                st.info("No recent activity")

        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
        finally:
            db.close()


def show_learning_mode():
    """Display learning mode page."""
    st.title("🎯 Learning Mode")

    # Get quiz selection
    quizzes = load_quiz_library()
    if not quizzes:
        st.warning("No quizzes available. Please import some quizzes first.")
        return

    # Determine current quiz
    current_quiz = None
    if st.session_state.selected_quiz:
        current_quiz = next((q for q in quizzes if q.id == st.session_state.selected_quiz), None)

    if not current_quiz:
        # Show quiz selector
        quiz_options = {f"{q.name} ({q.subject or 'General'})": q.id for q in quizzes}
        selected_quiz_name = st.selectbox("Choose a quiz to learn:", ["Select a quiz..."] + list(quiz_options.keys()))

        if selected_quiz_name == "Select a quiz...":
            st.info("Please select a quiz to start learning.")
            return

        quiz_id = quiz_options[selected_quiz_name]
        current_quiz = next(q for q in quizzes if q.id == quiz_id)
        st.session_state.selected_quiz = quiz_id
        st.session_state.learning_quiz_id = quiz_id

    # Load flashcards
    db = get_database_session()
    try:
        quiz_service = QuizService(db)
        user_service = UserService(db)
        cards = quiz_service.get_quiz_flashcards(current_quiz.id)

        if not cards:
            st.error("This quiz has no flashcards!")
            return

        # Quiz info banner
        st.info(f"📚 **{current_quiz.name}** - {len(cards)} cards")

        # Initialize/reset learning state if needed
        if st.session_state.learning_quiz_id != current_quiz.id:
            st.session_state.learning_cards_index = 0
            st.session_state.show_answer = False
            st.session_state.learning_quiz_id = current_quiz.id

        # Learning interface
        if st.session_state.learning_cards_index < len(cards):
            current_card = cards[st.session_state.learning_cards_index]
            card_num = st.session_state.learning_cards_index + 1

            # Progress indicator
            progress = card_num / len(cards)
            st.progress(progress, text=f"Card {card_num} of {len(cards)}")

            # Question display
            st.markdown(f"### 📋 {current_card.question_title}")

            if current_card.question_emoji:
                st.markdown(f"## {current_card.question_emoji}")

            if current_card.question_text != current_card.question_title:
                st.markdown(f"*{current_card.question_text}*")

            # Audio button for question
            if st.button("🔊 Play Question", key="play_q"):
                try:
                    audio_service = GTTSAudioService()
                    if audio_service.is_available():
                        q_lang = current_card.question_lang
                        success = audio_service.play_text(current_card.question_text, q_lang)
                        if not success:
                            st.warning("Audio playback failed.")
                except Exception as e:
                    st.warning(f"Audio error: {str(e)}")

            # Answer reveal logic
            if not st.session_state.show_answer:
                if st.button("👁️ Reveal Answer", type="primary", key="reveal_btn"):
                    st.session_state.show_answer = True
                    st.rerun()
            else:
                # Show answer
                st.success(f"✅ **Answer:** {current_card.answer_text}")

                # Audio button for answer
                if st.button("🔊 Play Answer", key="play_a"):
                    try:
                        audio_service = GTTSAudioService()
                        if audio_service.is_available():
                            a_lang = current_card.answer_lang
                            success = audio_service.play_text(current_card.answer_text, a_lang)
                            if not success:
                                st.warning("Audio playback failed.")
                    except Exception as e:
                        st.warning(f"Audio error: {str(e)}")

                # Navigation buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("🔄 Repeat Card", key="repeat_btn"):
                        st.session_state.show_answer = False
                        st.rerun()

                with col2:
                    if card_num < len(cards):
                        if st.button("➡️ Next Card", type="primary", key="next_btn"):
                            st.session_state.learning_cards_index += 1
                            st.session_state.show_answer = False
                            st.rerun()

                with col3:
                    if st.button("🏁 End Session", key="end_btn"):
                        # Save session to database
                        current_user, _, _ = load_user_data(st.session_state.current_user)
                        user_service.create_session(current_user.id, current_quiz.id, "learn")

                        st.success("🎉 Learning session completed!")
                        st.balloons()

                        # Reset state
                        st.session_state.learning_cards_index = 0
                        st.session_state.show_answer = False
                        st.session_state.selected_quiz = None

                        # Clear cache
                        st.cache_data.clear()

                        # Back to library
                        st.session_state.current_page = "library"
                        st.rerun()
        else:
            # All cards completed
            st.success("🎉 All cards completed!")
            st.balloons()

            # Save session to database
            current_user, _, _ = load_user_data(st.session_state.current_user)
            user_service.create_session(current_user.id, current_quiz.id, "learn")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Start Over", key="start_over_btn"):
                    st.session_state.learning_cards_index = 0
                    st.session_state.show_answer = False
                    st.rerun()

            with col2:
                if st.button("📚 Back to Library", key="back_lib_btn"):
                    st.session_state.selected_quiz = None
                    st.session_state.learning_cards_index = 0
                    st.session_state.show_answer = False
                    st.session_state.current_page = "library"
                    st.rerun()

    except Exception as e:
        st.error(f"Error in learning mode: {str(e)}")
    finally:
        db.close()


def show_quiz_mode():
    """Test mode with support for different answer types."""
    st.title("🧪 Quiz Mode")

    # Get quiz selection
    quizzes = load_quiz_library()
    if not quizzes:
        st.warning("No quizzes available. Please import some quizzes first.")
        return

    # Determine current quiz
    current_quiz = None
    if st.session_state.selected_quiz:
        current_quiz = next((q for q in quizzes if q.id == st.session_state.selected_quiz), None)

    if not current_quiz:
        # Show quiz selector
        quiz_options = {f"{q.name} ({q.subject or 'General'})": q.id for q in quizzes}
        selected_quiz_name = st.selectbox("Choose a quiz to test:", ["Select a quiz..."] + list(quiz_options.keys()))

        if selected_quiz_name == "Select a quiz...":
            st.info("Please select a quiz to start testing.")
            return

        quiz_id = quiz_options[selected_quiz_name]
        current_quiz = next(q for q in quizzes if q.id == quiz_id)
        st.session_state.selected_quiz = quiz_id
        st.session_state.test_quiz_id = quiz_id

    # Load flashcards and services
    db = get_database_session()
    try:
        quiz_service = QuizService(db)
        user_service = UserService(db)
        cards = quiz_service.get_quiz_flashcards(current_quiz.id)

        if not cards:
            st.error("This quiz has no flashcards!")
            return

        # Show quiz statistics
        answer_type_stats = {}
        for card in cards:
            answer_type = card.answer_type or "text"
            answer_type_stats[answer_type] = answer_type_stats.get(answer_type, 0) + 1

        # Test configuration
        with st.expander("⚙️ Quiz Settings"):
            col1, col2 = st.columns(2)
            with col1:
                strict_mode = st.checkbox("Strict matching", value=False)
                case_sensitive = st.checkbox("Case sensitive", value=False)
            with col2:
                similarity_threshold = st.slider("Similarity threshold", 0.0, 1.0, 0.8, 0.1)
                allow_partial = st.checkbox("Allow partial credit", value=True)

        # Quiz info banner with answer type breakdown
        st.info(f"🔬 **{current_quiz.name}** - {len(cards)} questions")

        # if len(answer_type_stats) > 1:
        #     st.write("**Answer Types:**")
        #     type_cols = st.columns(len(answer_type_stats))
        #     for i, (answer_type, count) in enumerate(answer_type_stats.items()):
        #         with type_cols[i]:
        #             from learning.presenters.test_presenter import AnswerTypeUtils
        #             display_name = AnswerTypeUtils.get_answer_type_display_name(answer_type)
        #             st.metric(display_name, count)

        # Initialize/reset test state if needed
        if st.session_state.test_quiz_id != current_quiz.id:
            st.session_state.test_cards_index = 0
            st.session_state.test_answers = []
            st.session_state.test_quiz_id = current_quiz.id
            st.session_state.test_completed = False

        # Quit interface
        if not st.session_state.test_completed and st.session_state.test_cards_index < len(cards):
            current_card = cards[st.session_state.test_cards_index]
            question_num = st.session_state.test_cards_index + 1

            # Progress indicator
            progress = question_num / len(cards)
            st.progress(progress, text=f"Question {question_num} of {len(cards)}")

            # Question display
            st.markdown(f"### ❓ {current_card.question_title}")

            if current_card.question_emoji:
                st.markdown(f"## {current_card.question_emoji}")

            if current_card.question_text != current_card.question_title:
                st.markdown(f"*{current_card.question_text}*")

            # Show answer type indicator
            answer_type = current_card.answer_type or "text"
            display_name = AnswerTypeUtils.get_answer_type_display_name(answer_type)
            # st.caption(f"📝 Answer Type: {display_name}")

            # Audio button for question
            if st.button("🔊 Play Question", key=f"test_audio_q_{question_num}"):
                try:
                    audio_service = GTTSAudioService()
                    if audio_service.is_available():
                        q_lang = current_card.question_lang or "en"
                        success = audio_service.play_text(current_card.question_text, q_lang)
                        if not success:
                            st.warning("Audio playback failed.")
                except Exception as e:
                    st.warning(f"Audio error: {str(e)}")

            # Render typed answer input
            from core.learning.presenters.quiz_presenter import StreamlitTypedPresenter
            presenter = StreamlitTypedPresenter()
            user_answer = presenter.render_answer_input(current_card, f"q{question_num}")


            # Validation feedback
            if user_answer:
                validation = AnswerTypeUtils.validate_answer_format(user_answer, answer_type)
                if not validation["is_valid"]:
                    st.error(f"⚠️ {validation['error_message']}")

            # Submit button
            submit_enabled = bool(user_answer and (
                    answer_type not in ["integer", "float", "boolean"] or
                    AnswerTypeUtils.validate_answer_format(user_answer, answer_type)["is_valid"]
            ))

            if st.button("Submit Answer", type="primary", disabled=not submit_enabled,
                         key=f"submit_{question_num}"):
                # Store answer
                st.session_state.test_answers.append({
                    "card": current_card,
                    "user_answer": str(user_answer).strip(),
                    "correct_answer": current_card.answer_text
                })

                # Move to next question
                st.session_state.test_cards_index += 1

                if st.session_state.test_cards_index >= len(cards):
                    st.session_state.test_completed = True

                st.rerun()

            # Show answer format explanation
            presenter.show_answer_explanation(current_card)

        elif st.session_state.test_completed or st.session_state.test_cards_index >= len(cards):
            # Test completed - show results
            st.success("🎯 Test Completed!")

            # Calculate results using typed evaluator
            from core.learning.sessions.quiz_session import TestSessionConfig

            config = TestSessionConfig(
                strict_matching=strict_mode,
                case_sensitive=case_sensitive,
                similarity_threshold=similarity_threshold,
                allow_partial_credit=allow_partial
            )
            evaluator = TypedAnswerEvaluator(config)

            results = []
            total_score = 0

            for answer_data in st.session_state.test_answers:
                card = answer_data["card"]
                evaluation, score = evaluator.evaluate_answer(answer_data["user_answer"], card)

                results.append({
                    "question": card.question_title,
                    "answer_type": card.answer_type or "text",
                    "user_answer": answer_data["user_answer"],
                    "correct_answer": card.answer_text,
                    "evaluation": evaluation.value,
                    "score": score
                })
                total_score += score

            final_score = int((total_score / len(results)) * 100) if results else 0
            correct = len([r for r in results if r["evaluation"] == "correct"])
            partial = len([r for r in results if r["evaluation"] == "partial"])
            incorrect = len([r for r in results if r["evaluation"] == "incorrect"])

            # Display results metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Final Score", f"{final_score}%")
            with col2:
                st.metric("Correct", f"{correct}/{len(results)}")
            with col3:
                st.metric("Partial", partial)
            with col4:
                st.metric("Incorrect", incorrect)

            # Performance by answer type
            if len(answer_type_stats) > 1:
                st.subheader("📊 Performance by Answer Type")

                type_performance = {}
                for result in results:
                    answer_type = result["answer_type"]
                    if answer_type not in type_performance:
                        type_performance[answer_type] = {"correct": 0, "total": 0, "score_sum": 0}

                    type_performance[answer_type]["total"] += 1
                    type_performance[answer_type]["score_sum"] += result["score"]
                    if result["evaluation"] == "correct":
                        type_performance[answer_type]["correct"] += 1

                perf_cols = st.columns(len(type_performance))
                for i, (answer_type, perf) in enumerate(type_performance.items()):
                    with perf_cols[i]:
                        display_name = AnswerTypeUtils.get_answer_type_display_name(answer_type)
                        avg_score = (perf["score_sum"] / perf["total"] * 100) if perf["total"] > 0 else 0
                        st.metric(
                            display_name,
                            f"{avg_score:.0f}%",
                            f"{perf['correct']}/{perf['total']}"
                        )

            # Performance feedback
            if final_score >= 90:
                st.success("🌟 Excellent work!")
                st.balloons()
            elif final_score >= 80:
                st.success("👏 Great job!")
            elif final_score >= 70:
                st.info("👌 Good effort!")
            elif final_score >= 60:
                st.warning("📚 Keep practicing!")
            else:
                st.error("💪 Don't give up! Review and try again!")

            # Detailed results table with answer types
            if st.checkbox("Show detailed results"):
                import pandas as pd
                results_df = pd.DataFrame(results)

                # Format the dataframe for better display
                results_df["Answer Type"] = results_df["answer_type"].apply(
                    lambda x: AnswerTypeUtils.get_answer_type_display_name(x)
                )
                results_df["Score %"] = (results_df["score"] * 100).round(0).astype(int)

                display_df = results_df[
                    ["question", "Answer Type", "user_answer", "correct_answer", "evaluation", "Score %"]]
                display_df.columns = ["Question", "Type", "Your Answer", "Correct Answer", "Result", "Score %"]

                st.dataframe(display_df, use_container_width=True)

            # Save session to database
            current_user, _, _ = load_user_data(st.session_state.current_user)
            user_service.create_session(current_user.id, current_quiz.id, "test", final_score)

            # Clear cache to update stats
            st.cache_data.clear()

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Retake Test", key="retake_btn"):
                    st.session_state.test_cards_index = 0
                    st.session_state.test_answers = []
                    st.session_state.test_completed = False
                    st.rerun()

            with col2:
                if st.button("📚 Back to Library", key="test_back_btn"):
                    st.session_state.selected_quiz = None
                    st.session_state.test_cards_index = 0
                    st.session_state.test_answers = []
                    st.session_state.test_completed = False
                    st.session_state.current_page = "library"
                    st.rerun()

    except Exception as e:
        st.error(f"Error in test mode: {str(e)}")
        st.exception(e)  # Show full traceback for debugging
    finally:
        db.close()


def show_progress_dashboard():
    """Display progress dashboard."""
    st.title("📊 Progress Dashboard")

    try:
        current_user, user_sessions, user_stats = load_user_data(st.session_state.current_user)
        st.subheader(f"User: {current_user.name}")

        if not user_sessions:
            st.info("No learning sessions found. Start learning to see your progress!")
            return

        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Sessions", user_stats["total_sessions"])
        with col2:
            st.metric("Learning Sessions", user_stats["learn_sessions"])
        with col3:
            st.metric("Test Sessions", user_stats["test_sessions"])
        with col4:
            avg_score = user_stats["average_score"]
            st.metric("Average Score", f"{avg_score:.1f}%" if avg_score else "N/A")

        # Charts and analysis
        tab1, tab2, tab3 = st.tabs(["📈 Activity", "🎯 Performance", "📚 Subjects"])

        with tab1:
            # Activity over time
            if user_sessions:
                # Daily activity chart
                session_dates = [s.started_at.date() for s in user_sessions]
                date_counts = pd.Series(session_dates).value_counts().sort_index()

                if len(date_counts) > 0:
                    fig_activity = px.line(
                        x=date_counts.index,
                        y=date_counts.values,
                        title="Daily Learning Activity",
                        labels={"x": "Date", "y": "Sessions"}
                    )
                    fig_activity.update_traces(mode='markers+lines')
                    st.plotly_chart(fig_activity, use_container_width=True)

                # Session type distribution
                session_types = pd.Series([s.mode for s in user_sessions]).value_counts()
                fig_pie = px.pie(
                    values=session_types.values,
                    names=session_types.index.str.title(),
                    title="Session Types Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        with tab2:
            # Performance analysis
            test_sessions = [s for s in user_sessions if s.mode == "test" and s.score is not None]

            if test_sessions:
                # Score progression
                test_data = pd.DataFrame({
                    "Date": [s.started_at.strftime("%m/%d") for s in test_sessions],
                    "Score": [s.score for s in test_sessions],
                    "Quiz": [s.quiz.name for s in test_sessions]
                })

                fig_scores = px.line(
                    test_data,
                    x="Date",
                    y="Score",
                    hover_data=["Quiz"],
                    title="Test Score Progression",
                    markers=True
                )
                fig_scores.update_yaxis(range=[0, 100])
                st.plotly_chart(fig_scores, use_container_width=True)

                # Score distribution histogram
                fig_hist = px.histogram(
                    test_data,
                    x="Score",
                    nbins=10,
                    title="Score Distribution",
                    labels={"Score": "Test Score (%)", "count": "Number of Tests"}
                )
                st.plotly_chart(fig_hist, use_container_width=True)

                # Best and worst performance
                best_session = max(test_sessions, key=lambda x: x.score)
                worst_session = min(test_sessions, key=lambda x: x.score)

                perf_col1, perf_col2 = st.columns(2)

                with perf_col1:
                    st.success("🏆 **Best Performance**")
                    st.write(f"Score: {best_session.score}%")
                    st.write(f"Quiz: {best_session.quiz.name}")
                    st.write(f"Date: {best_session.started_at.strftime('%Y-%m-%d')}")

                with perf_col2:
                    st.info("📈 **Room for Improvement**")
                    st.write(f"Score: {worst_session.score}%")
                    st.write(f"Quiz: {worst_session.quiz.name}")
                    st.write(f"Date: {worst_session.started_at.strftime('%Y-%m-%d')}")

            else:
                st.info("No test sessions found. Take some tests to see performance metrics!")

        with tab3:
            # Subject analysis
            subject_data = {}
            for session in user_sessions:
                subject = session.quiz.subject or "General"
                if subject not in subject_data:
                    subject_data[subject] = {"sessions": 0, "scores": []}
                subject_data[subject]["sessions"] += 1
                if session.score is not None:
                    subject_data[subject]["scores"].append(session.score)

            if subject_data:
                subjects_df = pd.DataFrame([
                    {
                        "Subject": subject,
                        "Total Sessions": data["sessions"],
                        "Test Sessions": len(data["scores"]),
                        "Average Score": sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
                    }
                    for subject, data in subject_data.items()
                ])

                # Subject performance chart
                if len(subjects_df) > 0:
                    fig_subjects = px.bar(
                        subjects_df,
                        x="Subject",
                        y="Average Score",
                        title="Average Performance by Subject",
                        color="Average Score",
                        color_continuous_scale="viridis"
                    )
                    fig_subjects.update_yaxis(range=[0, 100])
                    st.plotly_chart(fig_subjects, use_container_width=True)

                # Subject details table
                st.subheader("📋 Subject Details")
                st.dataframe(subjects_df, use_container_width=True, hide_index=True)

        # Recent activity timeline
        st.subheader("🕒 Recent Activity")

        activity_data = []
        for session in user_sessions[:10]:  # Last 10 sessions
            activity_data.append({
                "Date & Time": session.started_at.strftime("%Y-%m-%d %H:%M"),
                "Quiz": session.quiz.name,
                "Subject": session.quiz.subject or "General",
                "Mode": session.mode.title(),
                "Score": f"{session.score}%" if session.score else "N/A"
            })

        if activity_data:
            activity_df = pd.DataFrame(activity_data)
            st.dataframe(activity_df, use_container_width=True, hide_index=True)

        # Export data option
        if st.button("📥 Export Progress Data"):
            all_sessions_data = []
            for session in user_sessions:
                all_sessions_data.append({
                    "Date": session.started_at.strftime("%Y-%m-%d"),
                    "Time": session.started_at.strftime("%H:%M"),
                    "Quiz": session.quiz.name,
                    "Subject": session.quiz.subject or "General",
                    "Mode": session.mode,
                    "Score": session.score if session.score else ""
                })

            export_df = pd.DataFrame(all_sessions_data)
            csv = export_df.to_csv(index=False)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"slayflashcards_progress_{current_user.name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading progress dashboard: {str(e)}")


def show_quiz_creator():
    """ Quiz creator with support for different answer types."""
    st.title("🎨 Quiz Creator")

    st.markdown("""
    Create custom quizzes with different answer types including multiple choice, 
    number inputs, ranges, and more for engaging learning experiences.
    """)

    with st.form("quiz_creator_form", clear_on_submit=False):
        st.subheader("📝 Quiz Information")

        col1, col2 = st.columns(2)
        with col1:
            quiz_name = st.text_input("Quiz Name *", placeholder="e.g., Advanced Mathematics")
            quiz_subject = st.text_input("Subject", placeholder="e.g., Mathematics")

        with col2:
            quiz_description = st.text_area("Description", placeholder="Brief description of the quiz...")

        st.subheader("🃏 Flashcards")

        # Initialize flashcards if not present
        if "flashcards" not in st.session_state:
            st.session_state.flashcards = [{
                "question": {},
                "answer": {"type": "text", "options": [], "metadata": {}}
            }]

        # Display flashcard builder
        for i, card in enumerate(st.session_state.flashcards):
            with st.expander(f"Card {i + 1}", expanded=True):
                # Question section
                st.markdown("### 📋 Question")
                col_q1, col_q2 = st.columns(2)

                with col_q1:
                    q_title = st.text_input("Title", key=f"q_title_{i}",
                                            value=card["question"].get("title", ""),
                                            placeholder="Short question title")
                    q_text = st.text_area("Text", key=f"q_text_{i}",
                                          value=card["question"].get("text", ""),
                                          placeholder="Full question text")

                with col_q2:
                    col_lang, col_diff = st.columns(2)
                    with col_lang:
                        q_lang = st.selectbox("Language",
                                              ["en", "fr", "es", "de", "it", "pl", "ru"],
                                              key=f"q_lang_{i}", index=0)
                    with col_diff:
                        q_difficulty = st.select_slider("Difficulty", [1, 2, 3, 4, 5],
                                                        value=card["question"].get("difficulty", 1),
                                                        key=f"q_diff_{i}")

                    q_emoji = st.text_input("Emoji (optional)", key=f"q_emoji_{i}",
                                            value=card["question"].get("emoji", ""),
                                            placeholder="🎯")

                # Answer section
                st.markdown("### ✅ Answer")

                # Answer type selection
                answer_types = {
                    "Free Text": "text",
                    "Short Text": "short_text",
                    "Whole Number": "integer",
                    "Decimal Number": "float",
                    "Number Range": "range",
                    "True/False": "boolean",
                    "Single Choice": "choice",
                    "Multiple Choice": "multiple_choice"
                }

                current_type = card["answer"].get("type", "text")
                current_type_display = next((k for k, v in answer_types.items() if v == current_type), "Free Text")

                selected_type_display = st.selectbox(
                    "Answer Type",
                    list(answer_types.keys()),
                    key=f"a_type_{i}",
                    index=list(answer_types.keys()).index(current_type_display)
                )

                selected_type = answer_types[selected_type_display]

                # Answer content based on type
                col_a1, col_a2 = st.columns(2)

                with col_a1:
                    if selected_type in ["text", "short_text"]:
                        a_text = st.text_area("Answer Text", key=f"a_text_{i}",
                                              value=card["answer"].get("text", ""),
                                              placeholder="Correct answer")
                        a_options = []
                        a_metadata = {}

                    elif selected_type in ["integer", "float"]:
                        if selected_type == "integer":
                            a_number = st.number_input("Correct Answer", key=f"a_number_{i}",
                                                       step=1, format="%d",
                                                       value=int(card["answer"].get("text", "0")) if card["answer"].get("text", "").isdigit() else 0)
                            a_text = str(int(a_number))
                        else:  # float
                            a_number = st.number_input("Correct Answer", key=f"a_number_{i}",
                                                       step=0.01, format="%.2f",
                                                       value=float(card["answer"].get("text", "0.0")) if card["answer"].get("text", "").replace(".", "").isdigit() else 0.0)
                            a_text = str(float(a_number))

                        tolerance = st.number_input("Tolerance (±)", key=f"a_tolerance_{i}",
                                                    min_value=0.0, step=0.01 if selected_type == "float" else 1,
                                                    value=card["answer"].get("metadata", {}).get("tolerance", 0.01 if selected_type == "float" else 0))
                        a_options = []
                        a_metadata = {"tolerance": tolerance}

                    elif selected_type == "range":
                        a_text = st.text_input("Range (e.g., 5-10)", key=f"a_range_{i}",
                                               value=card["answer"].get("text", ""),
                                               placeholder="5-10 or 3 to 7")
                        overlap_threshold = st.slider("Overlap Threshold", 0.0, 1.0,
                                                     card["answer"].get("metadata", {}).get("overlap_threshold", 0.5),
                                                     key=f"a_overlap_{i}")
                        a_options = []
                        a_metadata = {"overlap_threshold": overlap_threshold}

                    elif selected_type == "boolean":
                        bool_answer = st.radio("Correct Answer", ["True", "False"],
                                               key=f"a_bool_{i}",
                                               index=0 if card["answer"].get("text", "True") == "True" else 1)
                        a_text = bool_answer
                        a_options = []
                        a_metadata = {}

                    elif selected_type in ["choice", "multiple_choice"]:
                        a_text = st.text_input("Correct Answer(s)", key=f"a_choice_{i}",
                                               value=card["answer"].get("text", ""),
                                               placeholder="Paris" if selected_type == "choice" else "Red, Blue, Yellow")

                        # Options management
                        st.write("**Answer Options:**")
                        current_options = card["answer"].get("options", [{"text": ""}])

                        # Ensure we have at least one option
                        if not current_options:
                            current_options = [{"text": ""}]

                        new_options = []
                        for opt_idx, option in enumerate(current_options):
                            opt_text = st.text_input(f"Option {opt_idx + 1}",
                                                     key=f"a_opt_{i}_{opt_idx}",
                                                     value=option.get("text", ""),
                                                     placeholder=f"Option {opt_idx + 1}")
                            if opt_text.strip():
                                new_options.append({"text": opt_text.strip()})

                        # Add option button
                        if st.form_submit_button(f"➕ Add Option to Card {i + 1}", key=f"add_opt_{i}"):
                            current_options.append({"text": ""})
                            st.session_state.flashcards[i]["answer"]["options"] = current_options
                            st.rerun()

                        a_options = new_options
                        order_matters = st.checkbox("Order matters (multiple choice)",
                                                   key=f"a_order_{i}",
                                                   value=card["answer"].get("metadata", {}).get("order_matters", False))
                        a_metadata = {"order_matters": order_matters}

                with col_a2:
                    a_lang = st.selectbox("Answer Language",
                                          ["en", "fr", "es", "de", "it", "pl", "ru"],
                                          key=f"a_lang_{i}", index=0)

                    # Show type-specific help
                    if selected_type == "integer":
                        st.info("🔢 Enter a whole number. Tolerance allows for nearby answers.")
                    elif selected_type == "float":
                        st.info("🔢 Enter a decimal number with tolerance for precision.")
                    elif selected_type == "range":
                        st.info("📏 Enter ranges like '5-10', '3 to 7', or '1..5'.")
                    elif selected_type == "boolean":
                        st.info("❓ Simple True/False questions.")
                    elif selected_type == "choice":
                        st.info("🎯 Single correct answer from multiple options.")
                    elif selected_type == "multiple_choice":
                        st.info("☑️ Multiple correct answers possible.")
                    elif selected_type == "short_text":
                        st.info("📝 Brief text answers with stricter matching.")
                    else:
                        st.info("📄 Free-form text answers with fuzzy matching.")

                # Update card data in session state
                st.session_state.flashcards[i] = {
                    "question": {
                        "title": q_title,
                        "text": q_text or q_title,
                        "lang": q_lang,
                        "difficulty": q_difficulty,
                        "emoji": q_emoji if q_emoji else None
                    },
                    "answer": {
                        "text": a_text,
                        "type": selected_type,
                        "lang": a_lang,
                        "options": a_options if a_options else None,
                        "metadata": a_metadata if a_metadata else None
                    }
                }

                # Delete card button (only if more than one card)
                if len(st.session_state.flashcards) > 1:
                    if st.form_submit_button(f"🗑️ Delete Card {i + 1}", key=f"del_card_{i}"):
                        st.session_state.flashcards.pop(i)
                        st.rerun()

        # Form buttons
        col_add, col_preview, col_create = st.columns([1, 1, 2])

        with col_add:
            add_card = st.form_submit_button("➕ Add Card")

        with col_preview:
            preview_quiz = st.form_submit_button("👀 Preview")

        with col_create:
            create_quiz = st.form_submit_button("💾 Create Quiz", type="primary")

        # Handle form submissions
        if add_card:
            st.session_state.flashcards.append({
                "question": {},
                "answer": {"type": "text", "options": [], "metadata": {}}
            })
            st.rerun()

        if preview_quiz:
            st.subheader("👀 Quiz Preview")

            # Count answer types
            type_counts = {}
            for card in st.session_state.flashcards:
                answer_type = card["answer"].get("type", "text")
                type_counts[answer_type] = type_counts.get(answer_type, 0) + 1

            st.write(f"**Total Cards:** {len(st.session_state.flashcards)}")
            # st.write("**Answer Types:**")
            # for answer_type, count in type_counts.items():
            #     display_name = AnswerTypeUtils.get_answer_type_display_name(answer_type)
            #     st.write(f"• {display_name}: {count}")

            # Show first few cards as preview
            st.write("**Sample Cards:**")
            for i, card in enumerate(st.session_state.flashcards[:3]):
                q_title = card["question"].get("title", "").strip()
                a_text = card["answer"].get("text", "").strip()
                a_type = card["answer"].get("type", "text")

                if q_title and a_text:
                    type_display = AnswerTypeUtils.get_answer_type_display_name(a_type)
                    st.write(f"{i+1}. **{q_title}** → {a_text} *({type_display})*")

        if create_quiz:
            # Validation
            if not quiz_name.strip():
                st.error("Quiz name is required!")
            else:
                # Filter out incomplete cards
                complete_cards = []
                for card in st.session_state.flashcards:
                    q_title = card["question"].get("title", "").strip()
                    a_text = card["answer"].get("text", "").strip()

                    if q_title and a_text:
                        # Validate choice questions have options
                        answer_type = card["answer"].get("type", "text")
                        if answer_type in ["choice", "multiple_choice"]:
                            options = card["answer"].get("options", [])
                            if not options or not any(opt.get("text", "").strip() for opt in options):
                                st.warning(f"Card '{q_title}' is missing answer options for {answer_type} type.")
                                continue

                        complete_cards.append(card)

                if not complete_cards:
                    st.error("At least one complete flashcard is required!")
                else:
                    # Create quiz data
                    quiz_data = {
                        "quiz": {
                            "name": quiz_name.strip(),
                            "subject": quiz_subject.strip() if quiz_subject.strip() else None,
                            "description": quiz_description.strip() if quiz_description.strip() else None,
                            "created_at": datetime.now().isoformat()
                        },
                        "flashcards": complete_cards
                    }

                    # Save quiz to database
                    db = get_database_session()
                    try:
                        quiz_service = QuizService(db)

                        # Validate quiz data
                        if not quiz_service.validate_quiz_data(quiz_data):
                            st.error("Invalid quiz data structure!")
                            return

                        quiz = quiz_service.import_quiz_from_dict(quiz_data)

                        # Show success message with statistics
                        type_counts = {}
                        for card in complete_cards:
                            answer_type = card["answer"].get("type", "text")
                            type_counts[answer_type] = type_counts.get(answer_type, 0) + 1

                        success_msg = f"✅ Quiz '{quiz.name}' created successfully with {len(complete_cards)} cards!"
                        st.success(success_msg)
                        st.balloons()

                        # Show breakdown
                        st.write("**Answer Type Breakdown:**")
                        for answer_type, count in type_counts.items():
                            display_name = AnswerTypeUtils.get_answer_type_display_name(answer_type)
                            st.write(f"• {display_name}: {count} card{'s' if count != 1 else ''}")

                        # Clear form and cache
                        st.session_state.flashcards = [{
                            "question": {},
                            "answer": {"type": "text", "options": [], "metadata": {}}
                        }]
                        st.cache_data.clear()

                        # Option to download as JSON
                        import json
                        json_str = json.dumps(quiz_data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_str,
                            file_name=f"{quiz.name.lower().replace(' ', '_').replace('/', '_')}_typed.json",
                            mime="application/json"
                        )

                        # Option to test the quiz immediately
                        col_test, col_lib = st.columns(2)
                        with col_test:
                            if st.button("🧪 Test This Quiz"):
                                st.session_state.selected_quiz = quiz.id
                                st.session_state.current_page = "testing"
                                st.session_state.test_cards_index = 0
                                st.session_state.test_answers = []
                                st.session_state.test_quiz_id = quiz.id
                                st.session_state.test_completed = False
                                st.rerun()

                        with col_lib:
                            if st.button("📚 Go to Library"):
                                st.session_state.current_page = "library"
                                st.rerun()

                    except Exception as e:
                        st.error(f"Error creating quiz: {str(e)}")
                        st.exception(e)
                    finally:
                        db.close()

    # Show examples section
    with st.expander("📖 Answer Type Examples", expanded=False):
        st.markdown("""
        ### Answer Type Examples
        
        **Free Text**: "Describe the process of photosynthesis"
        - Best for: Essay questions, explanations, open-ended responses
        
        **Short Text**: "What is the capital of France?" → "Paris"  
        - Best for: Single word or brief phrase answers
        
        **Whole Number**: "How many sides does a triangle have?" → 3
        - Best for: Counting, ages, quantities
        
        **Decimal Number**: "What is the value of π to 2 decimal places?" → 3.14
        - Best for: Measurements, calculations, percentages
        
        **Number Range**: "What is the typical human body temperature range?" → "97-99"
        - Best for: Acceptable ranges, estimates, approximate values
        
        **True/False**: "The Earth is flat." → False
        - Best for: Facts, yes/no questions, binary choices
        
        **Single Choice**: "What is the largest planet?" 
        - Options: Jupiter, Saturn, Earth, Mars → Jupiter
        - Best for: Multiple choice with one correct answer
        
        **Multiple Choice**: "Which are primary colors?"
        - Options: Red, Blue, Yellow, Green, Purple → Red, Blue, Yellow
        - Best for: Questions with multiple correct answers
        """)

    # Import existing quiz section
    st.divider()
    st.subheader("📤 Import Existing Quiz")

    uploaded_file = st.file_uploader(
        "Upload JSON quiz file",
        type="json",
        help="Upload a quiz JSON file to edit or extend"
    )

    if uploaded_file is not None:
        try:
            import json
            quiz_data = json.load(uploaded_file)

            if st.button("📥 Load Quiz for Editing"):
                # Convert quiz data to enhanced format
                cards = []
                for card_data in quiz_data.get("flashcards", []):
                    card = {
                        "question": card_data.get("question", {}),
                        "answer": {
                            "text": card_data.get("answer", {}).get("text", ""),
                            "type": card_data.get("answer", {}).get("type", "text"),
                            "lang": card_data.get("answer", {}).get("lang", "en"),
                            "options": card_data.get("answer", {}).get("options", []),
                            "metadata": card_data.get("answer", {}).get("metadata", {})
                        }
                    }
                    cards.append(card)

                st.session_state.flashcards = cards
                st.success(f"Loaded {len(cards)} cards for editing!")
                st.rerun()

        except Exception as e:
            st.error(f"Error loading quiz file: {str(e)}")


def show_settings():
    """Display settings page."""
    st.title("⚙️ Settings")

    st.markdown("""
    Manage your SlayFlashcards application settings, user data, and system configuration.
    """)

    # Settings tabs
    tab1, tab2, tab3 = st.tabs(["🗄️ Database", "📁 Import/Export", "👤 Users"])

    with tab1:
        st.subheader("🗄️ Database Management")

        # Database statistics
        db = get_database_session()
        try:
            user_service = UserService(db)
            quiz_service = QuizService(db)

            users = user_service.get_all_users()
            quizzes = quiz_service.get_all_quizzes()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Users", len(users))
            with col2:
                st.metric("Quizzes", len(quizzes))
            with col3:
                total_sessions = sum(len(user_service.get_user_sessions(u.id)) for u in users)
                st.metric("Total Sessions", total_sessions)

            st.divider()

            # Database reset (danger zone)
            st.subheader("⚠️ Danger Zone")

            with st.expander("Reset Database"):
                st.warning("⚠️ This will permanently delete ALL data including users, quizzes, and progress!")

                confirm_text = st.text_input("Type 'DELETE ALL DATA' to confirm:")

                if confirm_text == "DELETE ALL DATA":
                    if st.button("🗑️ RESET DATABASE", type="secondary"):
                        try:
                            from core.db.database import reset_database
                            reset_database()
                            st.success("✅ Database reset successfully!")
                            st.cache_data.clear()

                            # Reset session state
                            for key in list(st.session_state.keys()):
                                if key.startswith(('learning_', 'test_', 'new_flashcards')):
                                    del st.session_state[key]

                            st.rerun()
                        except Exception as e:
                            st.error(f"Error resetting database: {str(e)}")
                else:
                    st.info("Enter the confirmation text above to enable the reset button.")

        finally:
            db.close()

    with tab2:
        st.subheader("📁 Import & Export")

        # Import quiz section
        st.subheader("📥 Import Quiz")
        uploaded_file = st.file_uploader("Choose a JSON file", type="json", key="settings_upload")

        if uploaded_file is not None:
            try:
                quiz_data = json.load(uploaded_file)

                # Preview quiz info
                if "quiz" in quiz_data:
                    quiz_info = quiz_data["quiz"]
                    st.info(f"**Preview:** {quiz_info.get('name', 'Unnamed Quiz')} - "
                            f"{len(quiz_data.get('flashcards', []))} cards")

                    # Validate quiz data
                    db = get_database_session()
                    try:
                        quiz_service = QuizService(db)
                        is_valid = quiz_service.validate_quiz_data(quiz_data)

                        if is_valid:
                            st.success("✅ Quiz file is valid!")

                            if st.button("📥 Import Quiz", key="settings_import"):
                                try:
                                    quiz = quiz_service.import_quiz_from_dict(quiz_data)
                                    st.success(f"✅ Successfully imported quiz: {quiz.name}")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Import failed: {str(e)}")
                        else:
                            st.error("❌ Invalid quiz file format!")

                    finally:
                        db.close()
                else:
                    st.error("❌ Invalid quiz file format - missing 'quiz' section!")

            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file!")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")

        st.divider()

        # Export data section
        st.subheader("📤 Export Data")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            if st.button("📊 Export All Progress Data"):
                db = get_database_session()
                try:
                    user_service = UserService(db)
                    users = user_service.get_all_users()

                    all_data = []
                    for user in users:
                        sessions = user_service.get_user_sessions(user.id)
                        for session in sessions:
                            all_data.append({
                                "user": user.name,
                                "quiz": session.quiz.name,
                                "subject": session.quiz.subject or "General",
                                "mode": session.mode,
                                "score": session.score if session.score else "",
                                "date": session.started_at.strftime("%Y-%m-%d"),
                                "time": session.started_at.strftime("%H:%M:%S")
                            })

                    if all_data:
                        export_df = pd.DataFrame(all_data)
                        csv = export_df.to_csv(index=False)

                        st.download_button(
                            label="📥 Download Progress CSV",
                            data=csv,
                            file_name=f"slayflashcards_all_progress_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No progress data to export.")

                finally:
                    db.close()

        with export_col2:
            if st.button("📚 Export Quiz Library"):
                db = get_database_session()
                try:
                    quiz_service = QuizService(db)
                    quizzes = quiz_service.get_all_quizzes()

                    quiz_data = []
                    for quiz in quizzes:
                        cards = quiz_service.get_quiz_flashcards(quiz.id)
                        quiz_data.append({
                            "name": quiz.name,
                            "subject": quiz.subject or "",
                            "description": quiz.description or "",
                            "cards": len(cards),
                            "created": quiz.created_at.strftime("%Y-%m-%d") if quiz.created_at else ""
                        })

                    if quiz_data:
                        quiz_df = pd.DataFrame(quiz_data)
                        csv = quiz_df.to_csv(index=False)

                        st.download_button(
                            label="📥 Download Quiz List CSV",
                            data=csv,
                            file_name=f"slayflashcards_quiz_library_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No quizzes to export.")

                finally:
                    db.close()

    with tab3:
        st.subheader("👤 User Management")

        db = get_database_session()
        try:
            user_service = UserService(db)
            users = user_service.get_all_users()

            if users:
                st.write(f"**Total Users:** {len(users)}")

                # User list with stats
                user_data = []
                for user in users:
                    sessions = user_service.get_user_sessions(user.id)
                    stats = user_service.get_user_statistics(user.id)

                    last_active = max([s.started_at for s in sessions]).strftime("%Y-%m-%d") if sessions else "Never"

                    user_data.append({
                        "User": user.name,
                        "Total Sessions": stats["total_sessions"],
                        "Test Sessions": stats["test_sessions"],
                        "Average Score": f"{stats['average_score']:.1f}%" if stats['average_score'] else "N/A",
                        "Last Active": last_active
                    })

                users_df = pd.DataFrame(user_data)
                st.dataframe(users_df, use_container_width=True, hide_index=True)
            else:
                st.info("No users found.")

        finally:
            db.close()


if __name__ == "__main__":
    main()
