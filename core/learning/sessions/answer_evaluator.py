# pylint: disable=no-else-return
import difflib
import re
from enum import Enum
from typing import Tuple, Union

from core.db import models


class AnswerType(Enum):
    """Supported answer types."""

    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    RANGE = "range"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_TEXT = "short_text"


class AnswerEvaluation(Enum):
    """Answer evaluation results."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"


class TypedAnswerEvaluator:
    """Enhanced answer evaluator that handles different answer types."""

    def __init__(self, config):
        self.config = config

    def evaluate_answer(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate user answer based on the card's answer type."""
        if not user_answer.strip():
            return AnswerEvaluation.INCORRECT, 0.0

        answer_type = AnswerType(card.answer_type or "text")

        # Route to appropriate evaluation method
        evaluator_methods = {
            AnswerType.TEXT: self._evaluate_text,
            AnswerType.INTEGER: self._evaluate_integer,
            AnswerType.FLOAT: self._evaluate_float,
            AnswerType.RANGE: self._evaluate_range,
            AnswerType.BOOLEAN: self._evaluate_boolean,
            AnswerType.CHOICE: self._evaluate_choice,
            AnswerType.MULTIPLE_CHOICE: self._evaluate_multiple_choice,
            AnswerType.SHORT_TEXT: self._evaluate_short_text,
        }

        evaluator = evaluator_methods.get(answer_type, self._evaluate_text)
        return evaluator(user_answer, card)

    def _evaluate_text(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate free text answers with fuzzy matching."""
        user_norm = self._normalize_text(user_answer)
        correct_norm = self._normalize_text(card.answer_text)

        if user_norm == correct_norm:
            return AnswerEvaluation.CORRECT, 1.0

        if self.config.strict_matching:
            return AnswerEvaluation.INCORRECT, 0.0

        similarity = self._calculate_similarity(user_norm, correct_norm)

        if similarity >= 0.98:
            return AnswerEvaluation.CORRECT, 1.0
        elif similarity >= self.config.similarity_threshold and self.config.allow_partial_credit:
            return AnswerEvaluation.PARTIAL, similarity
        else:
            return AnswerEvaluation.INCORRECT, 0.0

    @staticmethod
    def _evaluate_integer(user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate integer answers."""
        try:
            user_int = int(user_answer.strip())
            correct_int = int(card.answer_text.strip())

            if user_int == correct_int:
                return AnswerEvaluation.CORRECT, 1.0
            else:
                # Check if close (within tolerance if configured)
                tolerance = card.answer_metadata.get("tolerance", 0) if card.answer_metadata else 0
                if tolerance > 0 and abs(user_int - correct_int) <= tolerance:
                    return AnswerEvaluation.PARTIAL, 0.8
                return AnswerEvaluation.INCORRECT, 0.0

        except ValueError:
            return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_float(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate floating point answers."""
        try:
            user_float = float(user_answer.strip())
            correct_float = float(card.answer_text.strip())

            # Default tolerance for float comparison
            tolerance = card.answer_metadata.get("tolerance", 0.01) if card.answer_metadata else 0.01

            if abs(user_float - correct_float) <= tolerance:
                return AnswerEvaluation.CORRECT, 1.0

            # Partial credit for close answers
            if self.config.allow_partial_credit:
                relative_error = (
                    abs(user_float - correct_float) / abs(correct_float) if correct_float != 0 else float("inf")
                )
                if relative_error <= 0.1:  # Within 10%
                    return AnswerEvaluation.PARTIAL, max(0.5, 1.0 - relative_error)

            return AnswerEvaluation.INCORRECT, 0.0

        except ValueError:
            return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_range(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate range answers (e.g., 5-10, 3 to 7)."""
        try:
            # Parse user range
            user_range = self._parse_range(user_answer)
            correct_range = self._parse_range(card.answer_text)

            if user_range == correct_range:
                return AnswerEvaluation.CORRECT, 1.0

            # Check for overlap
            if self.config.allow_partial_credit and user_range and correct_range:
                overlap = self._calculate_range_overlap(user_range, correct_range)
                if overlap > 0:
                    return AnswerEvaluation.PARTIAL, overlap

            return AnswerEvaluation.INCORRECT, 0.0

        except Exception:  # pylint: disable=broad-exception-caught
            return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_boolean(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate boolean (True/False) answers."""
        user_bool = self._parse_boolean(user_answer)
        correct_bool = self._parse_boolean(card.answer_text)

        if user_bool is None:
            return AnswerEvaluation.INCORRECT, 0.0

        if user_bool == correct_bool:
            return AnswerEvaluation.CORRECT, 1.0
        else:
            return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_choice(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate single choice answers."""
        if not card.answer_options:
            return self._evaluate_text(user_answer, card)

        options = card.answer_options
        correct_answer = card.answer_text

        # Normalize user answer
        user_norm = user_answer.strip().lower()

        # Check exact match first
        if user_norm == correct_answer.lower():
            return AnswerEvaluation.CORRECT, 1.0

        # Check if user provided option key/index
        for i, option in enumerate(options):
            option_text = option.get("text", "").lower()
            option_key = option.get("key", str(i + 1)).lower()

            if user_norm == option_text or user_norm == option_key:  # pylint: disable=consider-using-in
                if option_text == correct_answer.lower():
                    return AnswerEvaluation.CORRECT, 1.0
                else:
                    return AnswerEvaluation.INCORRECT, 0.0

        return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_multiple_choice(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate multiple choice answers."""
        if not card.answer_options:
            return self._evaluate_text(user_answer, card)

        # Parse correct answers (could be comma-separated)
        correct_answers = set(ans.strip().lower() for ans in card.answer_text.split(","))

        # Parse user answers
        user_answers = set(ans.strip().lower() for ans in user_answer.split(","))

        if user_answers == correct_answers:
            return AnswerEvaluation.CORRECT, 1.0

        if self.config.allow_partial_credit:
            # Calculate partial credit based on overlap
            intersection = user_answers.intersection(correct_answers)
            union = user_answers.union(correct_answers)

            if intersection:
                # Jaccard similarity
                score = len(intersection) / len(union)
                if score >= 0.5:
                    return AnswerEvaluation.PARTIAL, score

        return AnswerEvaluation.INCORRECT, 0.0

    def _evaluate_short_text(self, user_answer: str, card: models.Flashcard) -> Tuple[AnswerEvaluation, float]:
        """Evaluate short text with stricter matching."""
        user_norm = self._normalize_text(user_answer)
        correct_norm = self._normalize_text(card.answer_text)

        if user_norm == correct_norm:
            return AnswerEvaluation.CORRECT, 1.0

        # More strict similarity threshold for short text
        similarity = self._calculate_similarity(user_norm, correct_norm)

        if similarity >= 0.95:
            return AnswerEvaluation.CORRECT, 1.0
        elif similarity >= 0.85 and self.config.allow_partial_credit:
            return AnswerEvaluation.PARTIAL, similarity
        else:
            return AnswerEvaluation.INCORRECT, 0.0

    # Helper methods
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        normalized = text.strip()

        if not self.config.case_sensitive:
            normalized = normalized.lower()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Remove common punctuation
        normalized = re.sub(r"[.,!?;:]$", "", normalized)

        return normalized

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    @staticmethod
    def _parse_range(range_text: str) -> Union[Tuple[float, float], None]:
        """Parse range text into (min, max) tuple."""
        # Handle different range formats: "5-10", "5 to 10", "5..10", "5 - 10"
        patterns = [
            r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*\.\.\s*(\d+(?:\.\d+)?)",
        ]

        for pattern in patterns:
            match = re.match(pattern, range_text.strip(), re.IGNORECASE)
            if match:
                min_val, max_val = float(match.group(1)), float(match.group(2))
                return (min(min_val, max_val), max(min_val, max_val))

        return None

    @staticmethod
    def _calculate_range_overlap(range1: Tuple[float, float], range2: Tuple[float, float]) -> float:
        """Calculate overlap ratio between two ranges."""
        min1, max1 = range1
        min2, max2 = range2

        overlap_min = max(min1, min2)
        overlap_max = min(max1, max2)

        if overlap_min >= overlap_max:
            return 0.0

        overlap_length = overlap_max - overlap_min
        total_length = max(max1, max2) - min(min1, min2)

        return overlap_length / total_length if total_length > 0 else 0.0

    @staticmethod
    def _parse_boolean(bool_text: str) -> Union[bool, None]:
        """Parse boolean text into True/False."""
        text = bool_text.strip().lower()

        true_values = {"true", "t", "yes", "y", "1", "correct", "right"}
        false_values = {"false", "f", "no", "n", "0", "incorrect", "wrong"}

        if text in true_values:
            return True
        elif text in false_values:
            return False
        else:
            return None
