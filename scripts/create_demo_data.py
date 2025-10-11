#!/usr/bin/env python3
"""
Create comprehensive demo data for SlayFlashcards.

Creates two demo users with quizzes, flashcards, and learning history.
Target audience: Polish high school teenagers.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.db.database import get_db, engine, Base
from core.services.user_service import UserService
from core.services.quiz_service import QuizService
from core.db.crud.repository.quiz_repository import QuizRepository
from core.db.crud.repository.flashcard_repository import FlashcardRepository
from core.db.models import Session as SessionModel
from api.api_schemas import UserCreate


# User credentials (simple passwords for demo)
USERS = [
    {
        "username": "Emila",
        "email": "emila@demo.pl",
        "password": "Emila123!",
        "full_name": "Emila Kowalska"
    },
    {
        "username": "Kriz",
        "email": "kriz@demo.pl",
        "password": "Kriz123!",
        "full_name": "Kriz Nowak"
    }
]


# Quiz data for Polish high school students
QUIZZES = {
    "Emila": [
        {
            "file": "data/historia-praczłowiek.json",
            "category": "Prehistoria",
            "level": "Klasa 1"
        },
        {
            "name": "Funkcje kwadratowe",
            "subject": "Matematyka",
            "category": "Funkcje",
            "level": "Klasa 2",
            "description": "Podstawy funkcji kwadratowych",
            "flashcards": [
                {
                    "question": {"title": "Postać ogólna", "text": "Jaka jest postać ogólna funkcji kwadratowej?", "lang": "pl", "difficulty": 1, "emoji": "📐"},
                    "answer": {"text": "f(x) = ax² + bx + c", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Wierzchołek paraboli", "text": "Jak obliczyć współrzędną x wierzchołka paraboli?", "lang": "pl", "difficulty": 2, "emoji": "📊"},
                    "answer": {"text": "x = -b/(2a)", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Delta", "text": "Co to jest delta (wyróżnik) funkcji kwadratowej?", "lang": "pl", "difficulty": 2, "emoji": "🔺"},
                    "answer": {"text": "Δ = b² - 4ac", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Liczba pierwiastków", "text": "Ile pierwiastków ma funkcja kwadratowa gdy Δ > 0?", "lang": "pl", "difficulty": 1, "emoji": "✌️"},
                    "answer": {"text": "2", "type": "integer", "lang": "pl"}
                },
                {
                    "question": {"title": "Postać kanoniczna", "text": "Jaka jest postać kanoniczna funkcji kwadratowej?", "lang": "pl", "difficulty": 2, "emoji": "📝"},
                    "answer": {"text": "f(x) = a(x-p)² + q", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Oś symetrii", "text": "Jaka jest oś symetrii paraboli?", "lang": "pl", "difficulty": 2, "emoji": "↕️"},
                    "answer": {"text": "x = p", "type": "short_text", "lang": "pl", "metadata": {"case_sensitive": False}}
                },
                {
                    "question": {"title": "Kierunek ramion", "text": "Kiedy ramiona paraboli są skierowane w górę?", "lang": "pl", "difficulty": 1, "emoji": "⬆️"},
                    "answer": {"text": "Gdy a > 0", "type": "short_text", "lang": "pl", "metadata": {"case_sensitive": False}}
                },
                {
                    "question": {"title": "Miejsce zerowe", "text": "Co to są miejsca zerowe funkcji?", "lang": "pl", "difficulty": 1, "emoji": "0️⃣"},
                    "answer": {"text": "Punkty przecięcia wykresu z osią OX", "type": "short_text", "lang": "pl", "metadata": {"case_sensitive": False}}
                }
            ]
        },
        {
            "name": "Czasy gramatyczne",
            "subject": "Język angielski",
            "category": "Gramatyka",
            "level": "Klasa 2",
            "description": "Przegląd czasów gramatycznych w języku angielskim",
            "flashcards": [
                {
                    "question": {"title": "Present Simple", "text": "Kiedy używamy Present Simple?", "lang": "pl", "difficulty": 1, "emoji": "⏰"},
                    "answer": {"text": "Czynności regularne, fakty, prawdy ogólne", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Present Continuous", "text": "Jak tworzymy Present Continuous?", "lang": "pl", "difficulty": 1, "emoji": "🔄"},
                    "answer": {"text": "am/is/are + czasownik-ing", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Past Simple", "text": "Kiedy używamy Past Simple?", "lang": "pl", "difficulty": 1, "emoji": "📅"},
                    "answer": {"text": "Czynności zakończone w przeszłości", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Present Perfect", "text": "Jak tworzymy Present Perfect?", "lang": "pl", "difficulty": 2, "emoji": "✅"},
                    "answer": {"text": "have/has + past participle (III forma)", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Future Simple", "text": "Jak tworzymy Future Simple?", "lang": "pl", "difficulty": 1, "emoji": "🔮"},
                    "answer": {"text": "will + bezokolicznik", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Going to", "text": "Kiedy używamy 'going to'?", "lang": "pl", "difficulty": 2, "emoji": "🎯"},
                    "answer": {"text": "Plany, zamiary, przewidywania z dowodem", "type": "text", "lang": "pl"}
                }
            ]
        },
        {
            "name": "Budowa komórki",
            "subject": "Biologia",
            "category": "Cytologia",
            "level": "Klasa 1",
            "description": "Podstawowe struktury komórkowe",
            "flashcards": [
                {
                    "question": {"title": "Jądro komórkowe", "text": "Co zawiera jądro komórkowe?", "lang": "pl", "difficulty": 1, "emoji": "🧬"},
                    "answer": {"text": "Materiał genetyczny DNA", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Mitochondria", "text": "Jaką funkcję pełnią mitochondria?", "lang": "pl", "difficulty": 1, "emoji": "⚡"},
                    "answer": {"text": "Produkcja energii ATP", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Chloroplasty", "text": "W jakich komórkach występują chloroplasty?", "lang": "pl", "difficulty": 1, "emoji": "🌿"},
                    "answer": {"text": "W komórkach roślinnych", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Błona komórkowa", "text": "Jaką funkcję pełni błona komórkowa?", "lang": "pl", "difficulty": 1, "emoji": "🛡️"},
                    "answer": {"text": "Ochrona i transport substancji", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Rybosomy", "text": "Co syntetyzują rybosomy?", "lang": "pl", "difficulty": 2, "emoji": "🏭"},
                    "answer": {"text": "Białka", "type": "short_text", "lang": "pl"}
                }
            ]
        }
    ],
    "Kriz": [
        {
            "file": "data/french1.json",
            "category": "Podstawy",
            "level": "Klasa 1"
        },
        {
            "name": "Ruch i siły",
            "subject": "Fizyka",
            "category": "Mechanika",
            "level": "Klasa 1",
            "description": "Podstawy dynamiki i kinematyki",
            "flashcards": [
                {
                    "question": {"title": "Prędkość", "text": "Jaki jest wzór na prędkość?", "lang": "pl", "difficulty": 1, "emoji": "🏃"},
                    "answer": {"text": "v = s/t", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Przyspieszenie", "text": "Jaki jest wzór na przyspieszenie?", "lang": "pl", "difficulty": 2, "emoji": "🚀"},
                    "answer": {"text": "a = Δv/Δt", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "II zasada dynamiki", "text": "Jaka jest treść II zasady dynamiki Newtona?", "lang": "pl", "difficulty": 2, "emoji": "⚖️"},
                    "answer": {"text": "F = ma", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Energia kinetyczna", "text": "Jaki jest wzór na energię kinetyczną?", "lang": "pl", "difficulty": 2, "emoji": "💨"},
                    "answer": {"text": "Ek = mv²/2", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Energia potencjalna", "text": "Jaki jest wzór na energię potencjalną?", "lang": "pl", "difficulty": 2, "emoji": "⛰️"},
                    "answer": {"text": "Ep = mgh", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Siła tarcia", "text": "Od czego zależy siła tarcia?", "lang": "pl", "difficulty": 2, "emoji": "🔥"},
                    "answer": {"text": "Od siły nacisku i współczynnika tarcia", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Jednostka siły", "text": "Jaka jest jednostka siły w układzie SI?", "lang": "pl", "difficulty": 1, "emoji": "📏"},
                    "answer": {"text": "Niuton (N)", "type": "short_text", "lang": "pl"}
                }
            ]
        },
        {
            "name": "Układ okresowy pierwiastków",
            "subject": "Chemia",
            "category": "Chemia ogólna",
            "level": "Klasa 1",
            "description": "Podstawy układu okresowego",
            "flashcards": [
                {
                    "question": {"title": "Liczba atomowa", "text": "Co oznacza liczba atomowa pierwiastka?", "lang": "pl", "difficulty": 1, "emoji": "🔢"},
                    "answer": {"text": "Liczba protonów w jądrze", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Liczba masowa", "text": "Jak obliczamy liczbę masową?", "lang": "pl", "difficulty": 1, "emoji": "⚖️"},
                    "answer": {"text": "Protony + neutrony", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Okres", "text": "Co to jest okres w układzie okresowym?", "lang": "pl", "difficulty": 1, "emoji": "↔️"},
                    "answer": {"text": "Wiersz poziomy", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Grupa", "text": "Co to jest grupa w układzie okresowym?", "lang": "pl", "difficulty": 1, "emoji": "↕️"},
                    "answer": {"text": "Kolumna pionowa", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Metale", "text": "Gdzie w układzie okresowym znajdują się metale?", "lang": "pl", "difficulty": 1, "emoji": "🔨"},
                    "answer": {"text": "Po lewej stronie", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Niemetal", "text": "Gdzie w układzie okresowym znajdują się niemetale?", "lang": "pl", "difficulty": 1, "emoji": "💨"},
                    "answer": {"text": "Po prawej stronie", "type": "short_text", "lang": "pl"}
                }
            ]
        },
        {
            "name": "Algorytmy i struktury danych",
            "subject": "Informatyka",
            "category": "Algorytmika",
            "level": "Klasa 2",
            "description": "Podstawowe algorytmy i struktury danych",
            "flashcards": [
                {
                    "question": {"title": "Sortowanie bąbelkowe", "text": "Jaka jest złożoność obliczeniowa sortowania bąbelkowego?", "lang": "pl", "difficulty": 2, "emoji": "🫧"},
                    "answer": {"text": "O(n²)", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Stos", "text": "Jaka jest zasada działania stosu (stack)?", "lang": "pl", "difficulty": 1, "emoji": "📚"},
                    "answer": {"text": "LIFO - Last In First Out", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Kolejka", "text": "Jaka jest zasada działania kolejki (queue)?", "lang": "pl", "difficulty": 1, "emoji": "🚶"},
                    "answer": {"text": "FIFO - First In First Out", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Rekurencja", "text": "Co to jest rekurencja?", "lang": "pl", "difficulty": 2, "emoji": "🔄"},
                    "answer": {"text": "Funkcja wywołująca samą siebie", "type": "short_text", "lang": "pl"}
                },
                {
                    "question": {"title": "Wyszukiwanie binarne", "text": "Jaka jest złożoność wyszukiwania binarnego?", "lang": "pl", "difficulty": 2, "emoji": "🔍"},
                    "answer": {"text": "O(log n)", "type": "text", "lang": "pl"}
                }
            ]
        }
    ]
}


def create_users(db):
    """Create demo users and return them."""
    user_service = UserService(db)
    created_users = {}

    print("👥 Creating users...")
    for user_data in USERS:
        username = user_data["username"]

        # Check if user already exists
        existing_user = user_service.get_user_by_name(username)
        if existing_user:
            print(f"   ℹ️  User '{username}' already exists, using existing user")
            created_users[username] = existing_user
        else:
            # Create new user with password
            user_create = UserCreate(
                name=username,
                email=user_data["email"],
                password=user_data["password"]
            )
            user = user_service.create_user(user_create)
            created_users[username] = user
            print(f"   ✅ Created user: {username} ({user_data['email']})")

    return created_users


def import_quiz_from_file(db, file_path, user_id, category=None, level=None):
    """Import quiz from JSON file."""
    quiz_service = QuizService(db)

    # Read the file
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Add category and level if provided
    if category:
        data['quiz']['category'] = category
    if level:
        data['quiz']['level'] = level

    # Import quiz
    quiz = quiz_service.import_quiz_from_dict(data, user_id)
    return quiz


def create_quiz_from_data(db, quiz_data, user_id):
    """Create quiz from dictionary data."""
    quiz_service = QuizService(db)

    # Create quiz
    quiz = quiz_service.create_quiz(
        name=quiz_data["name"],
        user_id=user_id,
        subject=quiz_data["subject"],
        category=quiz_data.get("category"),
        level=quiz_data.get("level"),
        description=quiz_data.get("description")
    )

    # Add flashcards
    flashcard_repo = FlashcardRepository(db)
    flashcard_repo.bulk_create_flashcards(quiz.id, quiz_data["flashcards"])

    return quiz


def create_quizzes(db, users):
    """Create quizzes for all users."""
    print("\n📚 Creating quizzes...")
    user_quizzes = {}

    for username, quiz_list in QUIZZES.items():
        user = users[username]
        user_quizzes[username] = []

        print(f"\n   Creating quizzes for {username}:")

        for quiz_data in quiz_list:
            try:
                if "file" in quiz_data:
                    # Import from file
                    file_path = Path(project_root) / quiz_data["file"]
                    quiz = import_quiz_from_file(
                        db,
                        file_path,
                        user.id,
                        quiz_data.get("category"),
                        quiz_data.get("level")
                    )
                    print(f"      ✅ Imported: {quiz.name} (from {quiz_data['file']})")
                else:
                    # Create from data
                    quiz = create_quiz_from_data(db, quiz_data, user.id)
                    print(f"      ✅ Created: {quiz.name}")

                user_quizzes[username].append(quiz)
            except Exception as e:
                print(f"      ❌ Failed to create quiz: {e}")

    return user_quizzes


def create_learning_history(db, users, user_quizzes):
    """Create historical learning sessions for users."""
    print("\n📊 Creating learning history...")

    # Get current time
    now = datetime.utcnow()

    for username, quizzes in user_quizzes.items():
        user = users[username]
        print(f"\n   Creating history for {username}:")

        session_count = 0

        for quiz in quizzes:
            # Get flashcard count for this quiz
            quiz_repo = QuizRepository(db)
            flashcard_repo = FlashcardRepository(db)
            flashcards = flashcard_repo.get_by_quiz_id(quiz.id)
            flashcard_count = len(flashcards)

            if flashcard_count == 0:
                continue

            # Create 8-15 sessions for each quiz over the past 60 days
            num_sessions = random.randint(8, 15)

            for i in range(num_sessions):
                # Create more sessions in recent weeks for better stats
                # 40% in last 7 days, 30% in last 30 days, 30% in 30-60 days
                rand_val = random.random()
                if rand_val < 0.4:
                    days_ago = random.randint(0, 7)
                elif rand_val < 0.7:
                    days_ago = random.randint(8, 30)
                else:
                    days_ago = random.randint(31, 60)

                hours_ago = random.randint(0, 23)
                session_date = now - timedelta(days=days_ago, hours=hours_ago)

                # Determine session mode (65% learn, 35% test)
                mode = "learn" if random.random() < 0.65 else "test"

                # Calculate score for test sessions (improve over time with variation)
                score = None
                if mode == "test":
                    # Progressive improvement: older sessions have lower scores
                    progress_factor = i / num_sessions  # 0 to 1
                    base_score = 55 + (progress_factor * 35)  # 55-90 range
                    variation = random.uniform(-15, 15)
                    score = max(30, min(100, base_score + variation))

                # Create session
                session = SessionModel(
                    user_id=user.id,
                    quiz_id=quiz.id,
                    mode=mode,
                    started_at=session_date,
                    completed_at=session_date + timedelta(minutes=random.randint(5, 30)),
                    score=score
                )
                db.add(session)
                session_count += 1

        db.commit()
        print(f"      ✅ Created {session_count} learning sessions")


def reset_database():
    """Drop and recreate all tables."""
    print("🗑️  Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("   ✅ Database reset complete")


def main():
    """Main function to create demo data."""
    print("=" * 80)
    print("🎓 SlayFlashcards - Demo Data Generator")
    print("=" * 80)
    print("\nTarget: Polish high school students")
    print("Creating: 2 users with quizzes and learning history\n")

    # Ask if user wants to reset database
    response = input("⚠️  Reset database? This will DELETE ALL existing data! (yes/no/quit): ")
    if response.lower() == "yes":
        reset_database()
    elif response.lower() == "quit":
        print("Exiting without changes.")
        return


    db = next(get_db())

    try:
        # Create users
        users = create_users(db)

        # Create quizzes
        user_quizzes = create_quizzes(db, users)

        # Create learning history
        create_learning_history(db, users, user_quizzes)

        # Summary
        print("\n" + "=" * 80)
        print("✅ Demo data created successfully!")
        print("=" * 80)

        print("\n👥 User Credentials:")
        print("-" * 80)
        for user_data in USERS:
            user = users[user_data["username"]]
            quiz_count = len(user_quizzes.get(user_data["username"], []))
            print(f"\n   Username: {user_data['username']}")
            print(f"   Email:    {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Quizzes:  {quiz_count}")

        print("\n" + "=" * 80)
        print("🚀 You can now login with these credentials!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
