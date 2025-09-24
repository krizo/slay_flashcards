import streamlit as st
from services.audio_service import GTTSAudioService


def render_audio_button(text: str, lang: str, label: str, key: str):
    """Render an audio playback button."""
    if st.button(f"🔊 {label}", key=key):
        try:
            audio_service = GTTSAudioService()
            if audio_service.is_available():
                success = audio_service.play_text(text, lang)
                if not success:
                    st.warning("Audio playback failed.")
            else:
                st.warning("Audio service not available.")
        except Exception as e:
            st.warning(f"Audio error: {str(e)}")


def render_question_audio(card, question_lang: str, card_num: int):
    """Render audio button for question."""
    q_lang = card.question_lang or question_lang
    render_audio_button(
        card.question_text,
        q_lang,
        "Play Question",
        f"play_q_{card_num}"
    )


def render_answer_audio(card, answer_lang: str, card_num: int):
    """Render audio button for answer."""
    a_lang = card.answer_lang or answer_lang
    render_audio_button(
        card.answer_text,
        a_lang,
        "Play Answer",
        f"play_a_{card_num}"
    )
