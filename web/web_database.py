import streamlit as st
from db.database import SessionLocal, Base, engine


def initialize_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


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
    from services.quiz_service import QuizService

    db = get_database_session()
    try:
        quiz_service = QuizService(db)
        return quiz_service.get_all_quizzes()
    finally:
        db.close()


@st.cache_data(ttl=60)  # Cache for 1 minute
def load_user_data(username: str):
    """Load user data with caching."""
    from services.user_service import UserService

    db = get_database_session()
    try:
        user_service = UserService(db)
        user = user_service.ensure_user_exists(username)
        sessions = user_service.get_user_sessions(user.id)
        stats = user_service.get_user_statistics(user.id)
        return user, sessions, stats
    finally:
        db.close()
