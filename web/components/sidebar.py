import streamlit as st
from web.web_database import load_user_data


def render_sidebar():
    """Render the sidebar and return settings."""
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
            "📚 Quiz Library": "library",
            "🎯 Learning Mode": "learning",
            "🧪 Test Mode": "testing",
            "📊 Progress Dashboard": "progress",
            "🎨 Quiz Creator": "creator",
            "⚙️ Settings": "settings"
        }

        selected_page = st.selectbox("Choose a page", list(pages.keys()))
        st.session_state.current_page = pages[selected_page]

        st.divider()

        # Audio settings
        st.subheader("🔊 Audio Settings")
        audio_enabled = st.checkbox("Enable Text-to-Speech", value=True)

        col1, col2 = st.columns(2)
        with col1:
            question_lang = st.selectbox("Question Lang", ["en", "fr", "es", "de", "it", "pl"])
        with col2:
            answer_lang = st.selectbox("Answer Lang", ["fr", "en", "es", "de", "it", "pl"])

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

        return {
            "audio_enabled": audio_enabled,
            "question_lang": question_lang,
            "answer_lang": answer_lang
        }
