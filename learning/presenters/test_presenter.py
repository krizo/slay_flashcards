from typing import Protocol, Dict, Any
import streamlit as st
from db import models


class TypedPresenterInterface(Protocol):
    """Interface for presenting different answer types."""

    def render_answer_input(self, card: models.Flashcard, key_suffix: str = "") -> str:
        """Render appropriate input widget based on answer type."""
        pass

    def show_answer_hint(self, card: models.Flashcard) -> None:
        """Show hint about expected answer format."""
        pass


class CLITestPresenter:
    """CLI presenter for different answer types."""

    @staticmethod
    def get_user_answer(card: models.Flashcard) -> str:
        """Get user answer with type-specific prompting."""
        answer_type = card.answer_type or "text"

        prompts = {
            "text": "💭 Your answer: ",
            "integer": "🔢 Enter a whole number: ",
            "float": "🔢 Enter a decimal number: ",
            "range": "📏 Enter a range (e.g., 5-10): ",
            "boolean": "❓ True or False: ",
            "choice": "🎯 Select your answer: ",
            "multiple_choice": "☑️  Select multiple answers (comma-separated): ",
            "short_text": "📝 Enter short answer: ",
        }

        prompt = prompts.get(answer_type, "💭 Your answer: ")

        # Show options for choice questions
        if answer_type in ["choice", "multiple_choice"] and card.answer_options:
            print("\nOptions:")
            for i, option in enumerate(card.answer_options, 1):
                print(f"  {i}. {option.get('text', option)}")

        # Show format hint
        CLITestPresenter.show_answer_hint(card)

        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"

    @staticmethod
    def show_answer_hint(card: models.Flashcard) -> None:
        """Show hint about expected answer format."""
        answer_type = card.answer_type or "text"
        metadata = card.answer_metadata or {}

        hints = {
            "integer": "💡 Hint: Enter a whole number (e.g., 42)",
            "float": "💡 Hint: Enter a decimal number (e.g., 3.14)",
            "range": "💡 Hint: Enter a range like '5-10' or '3 to 7'",
            "boolean": "💡 Hint: Enter True/False, Yes/No, or 1/0",
            "multiple_choice": "💡 Hint: Separate multiple answers with commas",
        }

        hint = hints.get(answer_type)
        if hint:
            print(hint)

        # Show tolerance info if available
        if "tolerance" in metadata:
            tolerance = metadata["tolerance"]
            print(f"📏 Tolerance: ±{tolerance}")


class StreamlitTypedPresenter:
    """Streamlit presenter for different answer types."""

    @staticmethod
    def render_answer_input(card: models.Flashcard, key_suffix: str = "") -> str:
        """Render appropriate Streamlit input widget based on answer type."""
        answer_type = card.answer_type or "text"
        key = f"answer_input_{answer_type}_{key_suffix}"

        # Show combined answer info line (UPDATED)
        StreamlitTypedPresenter.show_answer_info_line(card)

        if answer_type == "text":
            return st.text_area(
                "Your answer:",
                key=key,
                placeholder="Enter your answer here...",
                help="Free text answer"
            )

        elif answer_type == "integer":
            # Use number_input with step=1 for integers
            num_val = st.number_input(
                "Your answer:",
                key=key,
                step=1,
                format="%d",
                help="Enter a whole number"
            )
            return str(int(num_val)) if num_val is not None else ""

        elif answer_type == "float":
            # Use number_input for floats
            num_val = st.number_input(
                "Your answer:",
                key=key,
                step=0.01,
                format="%.2f",
                help="Enter a decimal number"
            )
            return str(float(num_val)) if num_val is not None else ""

        elif answer_type == "range":
            return st.text_input(
                "Your answer:",
                key=key,
                placeholder="e.g., 5-10 or 3 to 7",
                help="Enter a range using formats like '5-10' or '3 to 7'"
            )

        elif answer_type == "boolean":
            # Use radio buttons for boolean
            bool_val = st.radio(
                "Your answer:",
                options=["True", "False"],
                key=key,
                horizontal=True,
                help="Select True or False"
            )
            return bool_val

        elif answer_type == "choice":
            if card.answer_options:
                options = [opt.get("text", str(opt)) for opt in card.answer_options]
                selected = st.radio(
                    "Select your answer:",
                    options=options,
                    key=key,
                    help="Choose one option"
                )
                return selected
            else:
                return st.text_input(
                    "Your answer:",
                    key=key,
                    placeholder="Enter your choice",
                    help="Single choice answer"
                )

        elif answer_type == "multiple_choice":
            if card.answer_options:
                options = [opt.get("text", str(opt)) for opt in card.answer_options]
                selected = st.multiselect(
                    "Select your answers:",
                    options=options,
                    key=key,
                    help="Choose multiple options"
                )
                return ", ".join(selected)
            else:
                return st.text_input(
                    "Your answers:",
                    key=key,
                    placeholder="Enter answers separated by commas",
                    help="Multiple choice answer (comma-separated)"
                )

        elif answer_type == "short_text":
            return st.text_input(
                "Your answer:",
                key=key,
                placeholder="Short answer",
                help="Brief text answer"
            )

        else:
            # Fallback to text input
            return st.text_input(
                "Your answer:",
                key=key,
                placeholder="Enter your answer",
                help="Text answer"
            )

    @staticmethod
    def show_answer_info_line(card: models.Flashcard) -> None:
        """Show combined answer type and metadata information in one line."""
        answer_type = card.answer_type or "text"
        metadata = card.answer_metadata or {}

        # Get answer type description
        type_descriptions = {
            "text": "Enter free text",
            "integer": "Enter a whole number",
            "float": "Enter a decimal number",
            "range": "Enter a range (e.g., 5-10)",
            "boolean": "Select True or False",
            "choice": "Choose one option",
            "multiple_choice": "Select multiple options",
            "short_text": "Enter brief text",
        }

        type_desc = type_descriptions.get(answer_type, "Enter your answer")

        # Build info parts
        info_parts = [f"📝 {type_desc}"]

        # Add tolerance info if available
        if "tolerance" in metadata and metadata["tolerance"] > 0:
            tolerance = metadata["tolerance"]
            info_parts.append(f"📏 Tolerance: ±{tolerance}")

        # Add other metadata info
        if answer_type == "range" and "overlap_threshold" in metadata:
            threshold = metadata["overlap_threshold"]
            info_parts.append(f"📊 Overlap threshold: {threshold:.0%}")

        if answer_type == "multiple_choice" and metadata.get("order_matters", False):
            info_parts.append("🔢 Order matters")

        # Display combined info line
        info_text = " • ".join(info_parts)
        st.caption(info_text)

    @staticmethod
    def show_answer_explanation(card: models.Flashcard) -> None:
        """Show detailed explanation of the answer format."""
        answer_type = card.answer_type or "text"

        explanations = {
            "integer": "This question expects a whole number (no decimals).",
            "float": "This question expects a decimal number.",
            "range": "This question expects a range of values. Use formats like '5-10', '3 to 7', or '1..5'.",
            "boolean": "This is a True/False question.",
            "choice": "This is a single-choice question. Select one option.",
            "multiple_choice": "This is a multiple-choice question. You can select more than one option.",
            "short_text": "This question expects a brief text answer.",
        }

        explanation = explanations.get(answer_type)
        if explanation:
            with st.expander("ℹ️ Answer Format Help"):
                st.write(explanation)

                # Show examples if available
                if card.answer_metadata and "examples" in card.answer_metadata:
                    st.write("**Examples:**")
                    for example in card.answer_metadata["examples"]:
                        st.write(f"• {example}")


# Utility functions for answer type handling
class AnswerTypeUtils:
    """Utility functions for handling answer types."""

    @staticmethod
    def get_answer_type_display_name(answer_type: str) -> str:
        """Get human-readable display name for answer type."""
        display_names = {
            "text": "Free Text",
            "integer": "Whole Number",
            "float": "Decimal Number",
            "range": "Number Range",
            "boolean": "True/False",
            "choice": "Single Choice",
            "multiple_choice": "Multiple Choice",
            "short_text": "Short Text",
        }
        return display_names.get(answer_type, answer_type.title())

    @staticmethod
    def validate_answer_format(user_answer: str, answer_type: str) -> Dict[str, Any]:
        """Validate if user answer matches expected format."""
        validation_result = {
            "is_valid": True,
            "error_message": None,
            "parsed_value": user_answer
        }

        if answer_type == "integer":
            try:
                parsed = int(user_answer.strip())
                validation_result["parsed_value"] = parsed
            except ValueError:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Please enter a valid whole number"

        elif answer_type == "float":
            try:
                parsed = float(user_answer.strip())
                validation_result["parsed_value"] = parsed
            except ValueError:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Please enter a valid decimal number"

        elif answer_type == "boolean":
            true_values = {"true", "t", "yes", "y", "1", "correct", "right"}
            false_values = {"false", "f", "no", "n", "0", "incorrect", "wrong"}

            normalized = user_answer.strip().lower()
            if normalized in true_values:
                validation_result["parsed_value"] = True
            elif normalized in false_values:
                validation_result["parsed_value"] = False
            else:
                validation_result["is_valid"] = False
                validation_result["error_message"] = "Please enter True/False, Yes/No, or 1/0"

        # Add more validations as needed

        return validation_result

    @staticmethod
    def get_default_answer_metadata(answer_type: str) -> Dict[str, Any]:
        """Get default metadata for answer type."""
        defaults = {
            "integer": {"tolerance": 0},
            "float": {"tolerance": 0.01},
            "range": {"overlap_threshold": 0.5},
            "boolean": {},
            "choice": {"case_sensitive": False},
            "multiple_choice": {"case_sensitive": False, "order_matters": False},
            "short_text": {"max_length": 100},
            "text": {},
        }
        return defaults.get(answer_type, {})
