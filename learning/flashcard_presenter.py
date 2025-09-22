from typing import Protocol
from db import models


class FlashcardPresenterInterface(Protocol):
    """Interface for presenting flashcards to users."""

    def show_question(self, card: models.Flashcard, card_num: int, total_cards: int) -> None:
        """Display the question part of a flashcard."""
        pass

    def show_answer(self, card: models.Flashcard) -> None:
        """Display the answer part of a flashcard."""
        pass

    def wait_for_reveal(self) -> None:
        """Wait for user input to reveal answer."""
        pass

    def get_continue_choice(self) -> str:
        """Get user choice to continue, quit, or repeat."""
        pass


class CLIFlashcardPresenter:
    """CLI implementation of flashcard presenter."""

    @staticmethod
    def show_question(card: models.Flashcard, card_num: int, total_cards: int) -> None:
        """Display question in CLI format."""
        print(f"\n📋 Card {card_num}/{total_cards}")
        print(f"\n❓ {card.question_title}")

        if card.question_emoji:
            print(f"   {card.question_emoji}")

        if card.question_text != card.question_title:
            print(f"   {card.question_text}")

    @staticmethod
    def show_answer(card: models.Flashcard) -> None:
        """Display answer in CLI format."""
        print(f"\n✅ Answer: {card.answer_text}")

    @staticmethod
    def wait_for_reveal() -> None:
        """Wait for Enter key to reveal answer."""
        input("\n⏸️  Press Enter to reveal answer...")

    @staticmethod
    def get_continue_choice() -> str:
        """Get user choice via CLI prompt."""
        try:
            choice = input("\n🔄 Continue? ([y]es/[n]o/[r]epeat): ").lower()
            return choice if choice in ['y', 'n', 'r', 'yes', 'no', 'repeat'] else 'y'
        except (EOFError, KeyboardInterrupt):
            return 'n'
