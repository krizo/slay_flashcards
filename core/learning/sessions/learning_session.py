from typing import List
from enum import Enum

from core.db import models
from core.services.audio_service import AudioServiceInterface
from core.learning.presenters.flashcard_presenter import FlashcardPresenterInterface


class LearningResult(Enum):
    """Results of a learning session."""
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    QUIT_EARLY = "quit_early"


class LearningSessionConfig:
    """Configuration for learning sessions."""

    def __init__(
        self,
        audio_enabled: bool = True,
        question_lang: str = "pl",
        answer_lang: str = "fr",
        allow_repeat: bool = True,
        override_card_languages: bool = True  # NEW: Control language priority
    ):
        self.audio_enabled = audio_enabled
        self.question_lang = question_lang
        self.answer_lang = answer_lang
        self.allow_repeat = allow_repeat
        self.override_card_languages = override_card_languages


class LearningSession:
    """Manages a flashcard learning session."""

    def __init__(
        self,
        flashcards: List[models.Flashcard],
        presenter: FlashcardPresenterInterface,
        audio_service: AudioServiceInterface,
        config: LearningSessionConfig
    ):
        self.flashcards = flashcards
        self.presenter = presenter
        self.audio_service = audio_service
        self.config = config
        self.cards_reviewed = 0

    def start(self) -> LearningResult:
        """Start the learning session."""
        try:
            return self._run_session()
        except KeyboardInterrupt:
            return LearningResult.INTERRUPTED

    def _run_session(self) -> LearningResult:
        """Main learning loop."""
        i = 0
        while i < len(self.flashcards):
            card = self.flashcards[i]

            # Show question
            self.presenter.show_question(card, i + 1, len(self.flashcards))

            # Play question audio with fixed language priority
            if self.config.audio_enabled and self.audio_service.is_available():
                question_lang = self._get_question_language(card)
                self.audio_service.play_text(card.question_text, question_lang)

            # Wait for reveal
            self.presenter.wait_for_reveal()

            # Show answer
            self.presenter.show_answer(card)

            # Play answer audio with fixed language priority
            if self.config.audio_enabled and self.audio_service.is_available():
                answer_lang = self._get_answer_language(card)
                self.audio_service.play_text(card.answer_text, answer_lang)

            # Get user choice for next action
            if i < len(self.flashcards) - 1:
                choice = self.presenter.get_continue_choice()

                if choice in ['n', 'no']:
                    self.cards_reviewed = i + 1
                    return LearningResult.QUIT_EARLY
                elif choice in ['r', 'repeat'] and self.config.allow_repeat:
                    continue  # Stay on same card

            i += 1
            self.cards_reviewed = i

        return LearningResult.COMPLETED

    def _get_question_language(self, card: models.Flashcard) -> str:
        """Get the language to use for question audio, respecting configuration."""
        if self.config.override_card_languages:
            # Command-line argument takes precedence
            return self.config.question_lang
        else:
            # Fallback to card language if no override
            return card.question_lang or self.config.question_lang

    def _get_answer_language(self, card: models.Flashcard) -> str:
        """Get the language to use for answer audio, respecting configuration."""
        if self.config.override_card_languages:
            # Command-line argument takes precedence
            return self.config.answer_lang
        else:
            # Fallback to card language if no override
            return card.answer_lang or self.config.answer_lang