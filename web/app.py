"""
SlayFlashcards Web Application
Main entry point for the Streamlit web interface.

Usage: streamlit run web/app.py
"""

import streamlit as st
from web.config import configure_page, load_custom_css
from web.state import initialize_session_state
from web.components.sidebar import render_sidebar
from web.pages import library, learning, testing, progress, creator, settings
from web.web_database import initialize_database


def main():
    """Main Streamlit application."""
    # Configure page
    configure_page()
    load_custom_css()

    # Initialize database and session state
    initialize_database()
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">🎓 SlayFlashcards</h1>', unsafe_allow_html=True)

    # Render sidebar and get settings
    sidebar_settings = render_sidebar()

    # Route to appropriate page
    page = st.session_state.current_page

    try:
        if page == "library":
            library.show_page()
        elif page == "learning":
            learning.show_page(**sidebar_settings)
        elif page == "testing":
            testing.show_page(**sidebar_settings)
        elif page == "progress":
            progress.show_page()
        elif page == "creator":
            creator.show_page()
        elif page == "settings":
            settings.show_page()
        else:
            st.error("Page not found!")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try refreshing the page or contact support if the issue persists.")


if __name__ == "__main__":
    main()