#!/usr/bin/env python3
"""
Script to create a comprehensive quiz testing all answer types
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db.database import SessionLocal
from core.db.models import Quiz, Flashcard
from datetime import datetime


def create_answer_types_quiz(user_id=None):
    """Create a quiz with examples of all answer types

    Args:
        user_id: ID of the user who will own the quiz. If None, prompts for selection.
    """
    db = SessionLocal()

    try:
        # Select user if not provided
        if user_id is None:
            users = db.query(Quiz).distinct(Quiz.user_id).all()
            user_ids = list(set([q.user_id for q in users]))

            # Get all users
            from core.db.models import User
            all_users = db.query(User).all()

            if not all_users:
                print("❌ No users found in database!")
                return

            print("\n👥 Available users:")
            for user in all_users:
                print(f"   {user.id}: {user.name}")

            while True:
                try:
                    user_input = input("\nEnter user ID (or press Enter for user 1): ").strip()
                    if user_input == "":
                        user_id = 1
                        break
                    user_id = int(user_input)
                    if any(u.id == user_id for u in all_users):
                        break
                    print(f"❌ User ID {user_id} not found. Try again.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")

        # Verify user exists
        from core.db.models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User with ID {user_id} not found!")
            return

        print(f"\n✅ Creating quiz for user: {user.name} (ID: {user_id})")

        # Create quiz
        quiz = Quiz(
            name="Test wszystkich typów odpowiedzi",
            subject="Testowanie",
            category="Typy odpowiedzi",
            level="Wszystkie",
            description="Quiz demonstracyjny pokazujący wszystkie możliwe typy odpowiedzi",
            user_id=user_id,
            created_at=datetime.now(),
            image="🧪".encode('utf-8')
        )
        db.add(quiz)
        db.flush()  # Get quiz.id

        flashcards_data = [
            # 1. TEXT - Long text answer
            {
                "question_title": "Pytanie otwarte (text)",
                "question_text": "Opisz proces fotosyntezy w roślinach.",
                "question_emoji": "🌱",
                "question_difficulty": 3,
                "question_examples": [
                    "Rośliny wykorzystują światło słoneczne...",
                    "Chlorofil w liściach pochłania energię..."
                ],
                "answer_text": "Fotosynteza to proces, w którym rośliny przekształcają dwutlenek węgla i wodę w glukozę i tlen przy użyciu energii słonecznej. Zachodzi w chloroplastach, gdzie chlorofil pochłania światło.",
                "answer_type": "text",
                "answer_options": None,
                "answer_metadata": {"hint": "Opisz proces w 2-3 zdaniach", "rows": 4, "min_words": 15}
            },

            # 2. SHORT_TEXT - Short answer
            {
                "question_title": "Krótka odpowiedź (short_text)",
                "question_text": "Jaka jest stolica Francji?",
                "question_emoji": "🇫🇷",
                "question_difficulty": 1,
                "question_examples": ["Paryż", "Paris"],
                "answer_text": "Paryż",
                "answer_type": "short_text",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz nazwę miasta", "placeholder": "np. Warszawa", "case_sensitive": False}
            },

            # 3. INTEGER - Whole number
            {
                "question_title": "Liczba całkowita (integer)",
                "question_text": "Ile dni ma rok przestępny?",
                "question_emoji": "📅",
                "question_difficulty": 1,
                "question_examples": ["365", "366"],
                "answer_text": "366",
                "answer_type": "integer",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz liczbę całkowitą", "placeholder": "np. 365", "min": 365, "max": 366}
            },

            # 4. FLOAT - Decimal number
            {
                "question_title": "Liczba dziesiętna (float)",
                "question_text": "Jaka jest wartość liczby π (pi) z dokładnością do 2 miejsc po przecinku?",
                "question_emoji": "🥧",
                "question_difficulty": 2,
                "question_examples": ["3.14", "3.141", "3.1415"],
                "answer_text": "3.14",
                "answer_type": "float",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz liczbę z dokładnie 2 miejscami po przecinku", "decimal_places": 2, "step": 0.01, "example": "3.14"}
            },

            # 5. RANGE - Number within range
            {
                "question_title": "Zakres liczbowy (range)",
                "question_text": "Jaka jest normalna temperatura ciała człowieka w stopniach Celsjusza?",
                "question_emoji": "🌡️",
                "question_difficulty": 2,
                "question_examples": ["36.6", "37.0"],
                "answer_text": "36.6",
                "answer_type": "range",
                "answer_options": None,
                "answer_metadata": {"min": 36.0, "max": 37.5, "step": 0.1, "hint": "Wybierz temperaturę w zakresie 36.0-37.5°C", "labels": {"min": "Niska", "max": "Wysoka"}}
            },

            # 6. BOOLEAN - True/False
            {
                "question_title": "Prawda/Fałsz (boolean)",
                "question_text": "Czy Ziemia jest płaska?",
                "question_emoji": "🌍",
                "question_difficulty": 1,
                "question_examples": None,
                "answer_text": "false",
                "answer_type": "boolean",
                "answer_options": None,
                "answer_metadata": {"true_label": "Tak", "false_label": "Nie", "hint": "Wybierz Tak lub Nie"}
            },

            # 7. CHOICE - Single choice
            {
                "question_title": "Wybór jednej opcji (choice)",
                "question_text": "Który planet jest największy w Układzie Słonecznym?",
                "question_emoji": "🪐",
                "question_difficulty": 2,
                "question_examples": None,
                "answer_text": "b",
                "answer_type": "choice",
                "answer_options": [
                    {"value": "a", "label": "Mars"},
                    {"value": "b", "label": "Jowisz"},
                    {"value": "c", "label": "Saturn"},
                    {"value": "d", "label": "Ziemia"}
                ],
                "answer_metadata": {"hint": "Wybierz jedną poprawną odpowiedź"}
            },

            # 8. MULTIPLE_CHOICE - Multiple selections
            {
                "question_title": "Wybór wielu opcji (multiple_choice)",
                "question_text": "Które z poniższych są językami programowania?",
                "question_emoji": "💻",
                "question_difficulty": 2,
                "question_examples": None,
                "answer_text": "a,c,d",
                "answer_type": "multiple_choice",
                "answer_options": [
                    {"value": "a", "label": "Python"},
                    {"value": "b", "label": "HTML"},
                    {"value": "c", "label": "JavaScript"},
                    {"value": "d", "label": "Java"},
                    {"value": "e", "label": "CSS"}
                ],
                "answer_metadata": {"hint": "Zaznacz wszystkie poprawne odpowiedzi (3 opcje)", "exact_count": 3}
            },

            # 9. TEXT - Another variant
            {
                "question_title": "Pytanie otwarte 2 (text)",
                "question_text": "Wyjaśnij różnicę między sztuczną inteligencją a uczeniem maszynowym.",
                "question_emoji": "🤖",
                "question_difficulty": 4,
                "question_examples": [
                    "AI to szersze pojęcie obejmujące...",
                    "Uczenie maszynowe jest podzbiorem AI..."
                ],
                "answer_text": "Sztuczna inteligencja (AI) to szeroka dziedzina obejmująca wszelkie systemy symulujące ludzką inteligencję. Uczenie maszynowe (ML) jest podzbiorem AI, skupiającym się na algorytmach uczących się z danych bez jawnego programowania.",
                "answer_type": "text",
                "answer_options": None,
                "answer_metadata": {"hint": "Opisz obie koncepcje i ich związek", "rows": 5, "min_words": 20}
            },

            # 10. SHORT_TEXT - Another variant
            {
                "question_title": "Krótka odpowiedź 2 (short_text)",
                "question_text": "Jaki język programowania używa interpretera CPython?",
                "question_emoji": "🐍",
                "question_difficulty": 2,
                "question_examples": ["Python"],
                "answer_text": "Python",
                "answer_type": "short_text",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz nazwę języka programowania", "placeholder": "np. Java", "max_length": 20}
            },

            # 11. INTEGER - Another variant
            {
                "question_title": "Liczba całkowita 2 (integer)",
                "question_text": "Ile chromosomów ma człowiek?",
                "question_emoji": "🧬",
                "question_difficulty": 2,
                "question_examples": ["46"],
                "answer_text": "46",
                "answer_type": "integer",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz liczbę całkowitą chromosomów", "min": 1, "max": 100, "example": "23"}
            },

            # 12. FLOAT - Another variant
            {
                "question_title": "Liczba dziesiętna 2 (float)",
                "question_text": "Jaka jest wartość przyspieszenia ziemskiego w m/s² (zaokrąglone do 1 miejsca)?",
                "question_emoji": "🍎",
                "question_difficulty": 2,
                "question_examples": ["9.8", "9.81"],
                "answer_text": "9.8",
                "answer_type": "float",
                "answer_options": None,
                "answer_metadata": {"hint": "Wpisz wartość z 1 miejscem po przecinku", "decimal_places": 1, "step": 0.1, "unit": "m/s²", "example": "9.8"}
            },

            # 13. BOOLEAN - Another variant
            {
                "question_title": "Prawda/Fałsz 2 (boolean)",
                "question_text": "Czy wieloryby są rybami?",
                "question_emoji": "🐋",
                "question_difficulty": 2,
                "question_examples": None,
                "answer_text": "false",
                "answer_type": "boolean",
                "answer_options": None,
                "answer_metadata": {"true_label": "Prawda", "false_label": "Fałsz"}
            },

            # 14. CHOICE - Another variant
            {
                "question_title": "Wybór jednej opcji 2 (choice)",
                "question_text": "W którym roku upadł Mur Berliński?",
                "question_emoji": "🧱",
                "question_difficulty": 3,
                "question_examples": None,
                "answer_text": "c",
                "answer_type": "choice",
                "answer_options": [
                    {"value": "a", "label": "1987"},
                    {"value": "b", "label": "1988"},
                    {"value": "c", "label": "1989"},
                    {"value": "d", "label": "1990"}
                ],
                "answer_metadata": {"hint": "Wybierz rok (4 cyfry)"}
            },

            # 15. MULTIPLE_CHOICE - Another variant
            {
                "question_title": "Wybór wielu opcji 2 (multiple_choice)",
                "question_text": "Które z poniższych to gazy szlachetne?",
                "question_emoji": "⚗️",
                "question_difficulty": 3,
                "question_examples": None,
                "answer_text": "a,c,e",
                "answer_type": "multiple_choice",
                "answer_options": [
                    {"value": "a", "label": "Hel (He)"},
                    {"value": "b", "label": "Tlen (O₂)"},
                    {"value": "c", "label": "Neon (Ne)"},
                    {"value": "d", "label": "Azot (N₂)"},
                    {"value": "e", "label": "Argon (Ar)"}
                ],
                "answer_metadata": {"hint": "Zaznacz wszystkie gazy szlachetne", "min_selections": 1, "max_selections": 5}
            },
        ]

        # Create flashcards
        for idx, card_data in enumerate(flashcards_data, 1):
            flashcard = Flashcard(
                quiz_id=quiz.id,
                question_title=card_data["question_title"],
                question_text=card_data["question_text"],
                question_emoji=card_data["question_emoji"],
                question_difficulty=card_data["question_difficulty"],
                question_examples=card_data["question_examples"],
                answer_text=card_data["answer_text"],
                answer_type=card_data["answer_type"],
                answer_options=card_data["answer_options"],
                answer_metadata=card_data["answer_metadata"]
            )
            db.add(flashcard)
            print(f"Created flashcard {idx}/15: {card_data['question_title']}")

        db.commit()
        print(f"\n✅ Quiz created successfully with ID: {quiz.id}")
        print(f"📊 Total flashcards: 15")
        print(f"🧪 Answer types covered:")
        print("   - text (2 examples)")
        print("   - short_text (2 examples)")
        print("   - integer (2 examples)")
        print("   - float (2 examples)")
        print("   - range (1 example)")
        print("   - boolean (2 examples)")
        print("   - choice (2 examples)")
        print("   - multiple_choice (2 examples)")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating quiz: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Create a comprehensive answer types test quiz')
    parser.add_argument('--user-id', type=int, help='User ID who will own the quiz')
    args = parser.parse_args()

    create_answer_types_quiz(user_id=args.user_id)
