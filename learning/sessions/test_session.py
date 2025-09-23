from typing import List, Dict, Any
from enum import Enum
import difflib
import re

from db import models
from services.audio_service import AudioServiceInterface


class TestResult(Enum):
    """Results of a test session."""
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    QUIT_EARLY = "quit_early"


class AnswerEvaluation(Enum):
    """Answer evaluation results."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


class CardResult:
    """Result for a single flashcard in test mode."""

    def __init__(self, card: models.Flashcard, user_answer: str, evaluation: AnswerEvaluation, score: float = 0.0):
        self.card = card
        self.user_answer = user_answer.strip()
        self.correct_answer = card.answer_text
        self.evaluation = evaluation
        self.score = score  # 0.0 to 1.0


class TestSessionConfig:
    """Configuration for test sessions."""

    def __init__(
        self,
        audio_enabled: bool = True,
        question_lang: str = "en",
        answer_lang: str = "fr",
        strict_matching: bool = False,
        case_sensitive: bool = False,
        similarity_threshold: float = 0.8,
        allow_partial_credit: bool = True,
        override_card_languages: bool = True
    ):
        self.audio_enabled = audio_enabled
        self.question_lang = question_lang
        self.answer_lang = answer_lang
        self.strict_matching = strict_matching
        self.case_sensitive = case_sensitive
        self.similarity_threshold = similarity_threshold  # For fuzzy matching
        self.allow_partial_credit = allow_partial_credit
        self.override_card_languages = override_card_languages


class AnswerEvaluator:
    """Evaluates user answers against correct answers."""

    def __init__(self, config: TestSessionConfig):
        self.config = config

    def evaluate_answer(self, user_answer: str, correct_answer: str) -> tuple[AnswerEvaluation, float]:
        """
        Evaluate user answer against correct answer.
        Returns (evaluation, score) where score is 0.0-1.0.
        """
        if not user_answer.strip():
            return AnswerEvaluation.INCORRECT, 0.0

        # Normalize answers
        user_norm = self._normalize_answer(user_answer)
        correct_norm = self._normalize_answer(correct_answer)

        # Exact match
        if user_norm == correct_norm:
            return AnswerEvaluation.CORRECT, 1.0

        # Strict matching mode
        if self.config.strict_matching:
            return AnswerEvaluation.INCORRECT, 0.0

        # Fuzzy matching
        similarity = self._calculate_similarity(user_norm, correct_norm)

        if similarity >= 0.95:  # Very close match
            return AnswerEvaluation.CORRECT, 1.0
        elif similarity >= self.config.similarity_threshold and self.config.allow_partial_credit:
            return AnswerEvaluation.PARTIAL, similarity
        else:
            return AnswerEvaluation.INCORRECT, 0.0

    def _normalize_answer(self, answer: str) -> str:
        """Normalize answer for comparison."""
        normalized = answer.strip()

        if not self.config.case_sensitive:
            normalized = normalized.lower()

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        # Remove common punctuation
        normalized = re.sub(r'[.,!?;:]$', '', normalized)

        return normalized

    @staticmethod
    def _calculate_similarity(answer1: str, answer2: str) -> float:
        """Calculate similarity between two answers using difflib."""
        return difflib.SequenceMatcher(None, answer1, answer2).ratio()


class TestSession:
    """Manages a flashcard test session."""

    def __init__(
        self,
        flashcards: List[models.Flashcard],
        presenter: 'TestPresenterInterface',
        audio_service: AudioServiceInterface,
        config: TestSessionConfig
    ):
        self.flashcards = flashcards
        self.presenter = presenter
        self.audio_service = audio_service
        self.config = config
        self.evaluator = AnswerEvaluator(config)

        self.results: List[CardResult] = []
        self.current_card_index = 0

    def start(self) -> TestResult:
        """Start the test session."""
        try:
            self.presenter.show_test_header(len(self.flashcards))
            return self._run_test()
        except KeyboardInterrupt:
            return TestResult.INTERRUPTED

    def _run_test(self) -> TestResult:
        """Main test loop."""
        for i, card in enumerate(self.flashcards):
            self.current_card_index = i

            # Show question
            self.presenter.show_question(card, i + 1, len(self.flashcards))

            # Play question audio
            if self.config.audio_enabled and self.audio_service.is_available():
                question_lang = self._get_question_language(card)
                self.audio_service.play_text(card.question_text, question_lang)

            # Get user answer
            user_answer = self.presenter.get_user_answer()

            # Handle early quit
            if user_answer.lower() in ['quit', 'exit', 'q']:
                return TestResult.QUIT_EARLY

            # Evaluate answer
            evaluation, score = self.evaluator.evaluate_answer(user_answer, card.answer_text)
            result = CardResult(card, user_answer, evaluation, score)
            self.results.append(result)

            # Show result
            self.presenter.show_answer_result(result)

            # Play correct answer audio
            if self.config.audio_enabled and self.audio_service.is_available():
                answer_lang = self._get_answer_language(card)
                self.audio_service.play_text(card.answer_text, answer_lang)

            # Wait before next question (except for last card)
            if i < len(self.flashcards) - 1:
                self.presenter.wait_for_next()

        return TestResult.COMPLETED

    def get_final_score(self) -> int:
        """Calculate final score as percentage."""
        if not self.results:
            return 0

        total_score = sum(result.score for result in self.results)
        return round((total_score / len(self.results)) * 100)

    def get_detailed_results(self) -> Dict[str, Any]:
        """Get detailed test results."""
        if not self.results:
            return {
                "total_questions": 0,
                "correct": 0,
                "partial": 0,
                "incorrect": 0,
                "final_score": 0,
                "breakdown": []
            }

        correct = len([r for r in self.results if r.evaluation == AnswerEvaluation.CORRECT])
        partial = len([r for r in self.results if r.evaluation == AnswerEvaluation.PARTIAL])
        incorrect = len([r for r in self.results if r.evaluation == AnswerEvaluation.INCORRECT])

        breakdown = []
        for result in self.results:
            breakdown.append({
                "question": result.card.question_title,
                "user_answer": result.user_answer,
                "correct_answer": result.correct_answer,
                "evaluation": result.evaluation.value,
                "score": result.score
            })

        return {
            "total_questions": len(self.results),
            "correct": correct,
            "partial": partial,
            "incorrect": incorrect,
            "final_score": self.get_final_score(),
            "breakdown": breakdown
        }

    def _get_question_language(self, card: models.Flashcard) -> str:
        """Get the language to use for question audio."""
        if self.config.override_card_languages:
            return self.config.question_lang
        else:
            return card.question_lang or self.config.question_lang

    def _get_answer_language(self, card: models.Flashcard) -> str:
        """Get the language to use for answer audio."""
        if self.config.override_card_languages:
            return self.config.answer_lang
        else:
            return card.answer_lang or self.config.answer_lang