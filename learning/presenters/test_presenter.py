from typing import Protocol
from db import models
from learning.sessions.test_session import CardResult, AnswerEvaluation


class TestPresenterInterface(Protocol):
    """Interface for presenting test questions and results to users."""

    def show_test_header(self, total_cards: int) -> None:
        """Display test session header."""
        pass

    def show_question(self, card: models.Flashcard, card_num: int, total_cards: int) -> None:
        """Display the question part of a flashcard for testing."""
        pass

    def get_user_answer(self) -> str:
        """Get user's answer input."""
        pass

    def show_answer_result(self, result: CardResult) -> None:
        """Show the result of the user's answer."""
        pass

    def wait_for_next(self) -> None:
        """Wait before proceeding to next question."""
        pass

    def show_final_results(self, results: dict) -> None:
        """Display final test results."""
        pass


class CLITestPresenter:
    """CLI implementation of test presenter."""

    @staticmethod
    def show_test_header(total_cards: int) -> None:
        """Display test session header in CLI format."""
        print(f"\n🧪 Test Mode Started")
        print(f"📝 {total_cards} questions to answer")
        print("💡 Type 'quit' to exit early")
        print("-" * 50)

    @staticmethod
    def show_question(card: models.Flashcard, card_num: int, total_cards: int) -> None:
        """Display question in CLI format for testing."""
        print(f"\n📋 Question {card_num}/{total_cards}")
        print(f"\n❓ {card.question_title}")

        if card.question_emoji:
            print(f"   {card.question_emoji}")

        if card.question_text != card.question_title:
            print(f"   {card.question_text}")

    @staticmethod
    def get_user_answer() -> str:
        """Get user's answer via CLI input."""
        try:
            return input("\n💭 Your answer: ").strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"

    @staticmethod
    def show_answer_result(result: CardResult) -> None:
        """Show the result of the user's answer in CLI format."""
        if result.evaluation == AnswerEvaluation.CORRECT:
            print(f"✅ Correct! ({result.score * 100:.0f}%)")
        elif result.evaluation == AnswerEvaluation.PARTIAL:
            print(f"⚠️  Partially correct ({result.score * 100:.0f}%)")
            print(f"   Your answer: {result.user_answer}")
            print(f"   Correct answer: {result.correct_answer}")
        else:
            print(f"❌ Incorrect (0%)")
            print(f"   Your answer: {result.user_answer}")
            print(f"   Correct answer: {result.correct_answer}")

    @staticmethod
    def wait_for_next() -> None:
        """Wait for user input before next question."""
        try:
            input("\n⏸️  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            pass

    @staticmethod
    def show_final_results(results: dict) -> None:
        """Display final test results in CLI format."""
        print(f"\n" + "=" * 50)
        print(f"🎯 TEST COMPLETED!")
        print(f"=" * 50)

        total = results["total_questions"]
        correct = results["correct"]
        partial = results["partial"]
        incorrect = results["incorrect"]
        final_score = results["final_score"]

        print(f"📊 Final Score: {final_score}%")
        print(f"📝 Total Questions: {total}")
        print(f"✅ Correct: {correct}")

        if partial > 0:
            print(f"⚠️  Partially Correct: {partial}")

        print(f"❌ Incorrect: {incorrect}")

        # Performance feedback
        if final_score >= 90:
            print(f"\n🌟 Excellent work!")
        elif final_score >= 80:
            print(f"\n👍 Great job!")
        elif final_score >= 70:
            print(f"\n👌 Good effort!")
        elif final_score >= 60:
            print(f"\n📚 Keep practicing!")
        else:
            print(f"\n💪 Don't give up! Review and try again!")

        # Show breakdown if requested
        if total <= 10:  # Only for shorter tests
            print(f"\n📋 Detailed Results:")
            print("-" * 30)
            for i, item in enumerate(results["breakdown"], 1):
                status = "✅" if item["evaluation"] == "correct" else "⚠️" if item["evaluation"] == "partial" else "❌"
                score_text = f"({item['score'] * 100:.0f}%)" if item["score"] > 0 else "(0%)"
                print(f"{i:2d}. {status} {item['question']} {score_text}")

        print()


class WebTestPresenter:
    """Web implementation of test presenter (for future Streamlit interface)."""

    def __init__(self, streamlit_container):
        self.st = streamlit_container
        self.current_question = None
        self.user_answer = ""

    def show_test_header(self, total_cards: int) -> None:
        """Display test session header in web format."""
        self.st.title("🧪 Test Mode")
        self.st.info(f"📝 {total_cards} questions • Type your answers below")

    def show_question(self, card: models.Flashcard, card_num: int, total_cards: int) -> None:
        """Display question in web format."""
        progress = card_num / total_cards
        self.st.progress(progress, text=f"Question {card_num} of {total_cards}")

        self.st.subheader(f"❓ {card.question_title}")

        if card.question_emoji:
            self.st.markdown(f"### {card.question_emoji}")

        if card.question_text != card.question_title:
            self.st.write(card.question_text)

    def get_user_answer(self) -> str:
        """Get user's answer via web input."""
        # This would be implemented with Streamlit session state
        # and form submission in the actual web interface
        return self.st.text_input("Your answer:", key=f"answer_{self.current_question}")

    def show_answer_result(self, result: CardResult) -> None:
        """Show result in web format."""
        if result.evaluation == AnswerEvaluation.CORRECT:
            self.st.success(f"✅ Correct! ({result.score * 100:.0f}%)")
        elif result.evaluation == AnswerEvaluation.PARTIAL:
            self.st.warning(f"⚠️ Partially correct ({result.score * 100:.0f}%)")
            self.st.write(f"**Your answer:** {result.user_answer}")
            self.st.write(f"**Correct answer:** {result.correct_answer}")
        else:
            self.st.error(f"❌ Incorrect")
            self.st.write(f"**Your answer:** {result.user_answer}")
            self.st.write(f"**Correct answer:** {result.correct_answer}")

    def wait_for_next(self) -> None:
        """Wait handled by web interface flow."""
        pass

    def show_final_results(self, results: dict) -> None:
        """Display final results in web format."""
        self.st.balloons()  # Celebration animation

        col1, col2, col3 = self.st.columns(3)

        with col1:
            self.st.metric("Final Score", f"{results['final_score']}%")

        with col2:
            self.st.metric("Correct", f"{results['correct']}/{results['total_questions']}")

        with col3:
            accuracy = (results['correct'] / results['total_questions']) * 100
            self.st.metric("Accuracy", f"{accuracy:.1f}%")

        # Performance chart
        chart_data = {
            'Result': ['Correct', 'Partial', 'Incorrect'],
            'Count': [results['correct'], results['partial'], results['incorrect']]
        }
        self.st.bar_chart(chart_data)