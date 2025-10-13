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


def get_demo_users():
    """
    Get demo users configuration from environment variable or use defaults.

    Environment variable DEMO_SECRETS should contain JSON like:
    {
        "demo_users": [
            {
                "username": "Emila",
                "email": "emila@demo.pl",
                "password": "SecurePassword123!",
                "full_name": "Emila Kowalska"
            }
        ]
    }
    """
    import os
    import json

    # Default fallback users (for local development)
    default_users = [
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

    # Try to load from environment variable
    secrets_json = os.environ.get('DEMO_SECRETS')
    if secrets_json:
        try:
            secrets = json.loads(secrets_json)
            users = secrets.get('demo_users', [])
            if users:
                print("   ℹ️  Using demo users from DEMO_SECRETS environment variable")
                return users
            else:
                print("   ⚠️  No demo_users found in DEMO_SECRETS, using defaults")
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse DEMO_SECRETS JSON: {e}, using defaults")
    else:
        print("   ℹ️  DEMO_SECRETS not set, using default demo users")

    return default_users


# User credentials - loaded from environment or defaults
USERS = get_demo_users()


# Quiz data for Polish high school students
QUIZZES = {
    "Emila": [
        {
            "file": "data/historia-praczłowiek.json",
            "category": "Prehistoria",
            "level": "Klasa 1",
            "favourite": True,
            "image": "🏛️"
        },
        {
            "name": "Funkcje kwadratowe",
            "subject": "Matematyka",
            "category": "Funkcje",
            "level": "Klasa 2",
            "description": "Podstawy funkcji kwadratowych",
            "favourite": True,
            "image": "📐",
            "flashcards": [
                {
                    "question": {"title": "Postać ogólna", "text": "Jaka jest postać ogólna funkcji kwadratowej?", "lang": "pl", "difficulty": 1, "emoji": "📐", "examples": ["np. f(x) = 2x² + 3x - 5", "np. f(x) = -x² + 4x + 1"]},
                    "answer": {"text": "f(x) = ax² + bx + c", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Wierzchołek paraboli", "text": "Jak obliczyć współrzędną x wierzchołka paraboli?", "lang": "pl", "difficulty": 2, "emoji": "📊", "examples": ["dla f(x) = 2x² + 8x + 3, x = -8/(2×2) = -2"]},
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
                    "question": {"title": "Ramiona paraboli w górę", "text": "Czy ramiona paraboli są skierowane w górę gdy a > 0?", "lang": "pl", "difficulty": 1, "emoji": "⬆️"},
                    "answer": {"text": "true", "type": "boolean", "lang": "pl", "metadata": {"true_label": "Tak", "false_label": "Nie"}}
                },
                {
                    "question": {"title": "Postać kanoniczna", "text": "Wybierz poprawną postać kanoniczną funkcji kwadratowej:", "lang": "pl", "difficulty": 2, "emoji": "📝"},
                    "answer": {"text": "a", "type": "choice", "lang": "pl", "options": [
                        {"value": "a", "label": "f(x) = a(x-p)² + q"},
                        {"value": "b", "label": "f(x) = a(x+p)² - q"},
                        {"value": "c", "label": "f(x) = ax² + bx + c"},
                        {"value": "d", "label": "f(x) = (x-p)(x-q)"}
                    ]}
                },
                {
                    "question": {"title": "Właściwości paraboli", "text": "Wybierz wszystkie prawdziwe właściwości paraboli:", "lang": "pl", "difficulty": 3, "emoji": "✓"},
                    "answer": {"text": "a,b,d", "type": "multiple_choice", "lang": "pl", "options": [
                        {"value": "a", "label": "Ma oś symetrii"},
                        {"value": "b", "label": "Może przecinać oś OX w 0, 1 lub 2 punktach"},
                        {"value": "c", "label": "Zawsze przechodzi przez początek układu współrzędnych"},
                        {"value": "d", "label": "Ma wartość ekstremalną (minimum lub maksimum)"}
                    ]}
                },
                {
                    "question": {"title": "Ocena trudności", "text": "Oceń swoją znajomość funkcji kwadratowych (1-5):", "lang": "pl", "difficulty": 1, "emoji": "⭐"},
                    "answer": {"text": "3", "type": "range", "lang": "pl", "metadata": {"min": 1, "max": 5, "step": 1}}
                }
            ]
        },
        {
            "name": "Czasy gramatyczne",
            "subject": "Język angielski",
            "category": "Gramatyka",
            "level": "Klasa 2",
            "description": "Przegląd czasów gramatycznych w języku angielskim",
            "favourite": False,
            "image": "🇬🇧",
            "flashcards": [
                {
                    "question": {"title": "Present Simple", "text": "Kiedy używamy Present Simple?", "lang": "pl", "difficulty": 1, "emoji": "⏰", "examples": ["I play tennis every Sunday", "Water boils at 100°C"]},
                    "answer": {"text": "Czynności regularne, fakty, prawdy ogólne", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Present Continuous", "text": "Wybierz poprawną formę Present Continuous:", "lang": "pl", "difficulty": 1, "emoji": "🔄"},
                    "answer": {"text": "a", "type": "choice", "lang": "pl", "options": [
                        {"value": "a", "label": "am/is/are + czasownik-ing"},
                        {"value": "b", "label": "have/has + czasownik-ing"},
                        {"value": "c", "label": "was/were + czasownik-ed"},
                        {"value": "d", "label": "will + czasownik-ing"}
                    ]}
                },
                {
                    "question": {"title": "Past Simple", "text": "Kiedy używamy Past Simple?", "lang": "pl", "difficulty": 1, "emoji": "📅", "examples": ["I visited Paris last year", "She studied English yesterday"]},
                    "answer": {"text": "Czynności zakończone w przeszłości", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Present Perfect", "text": "Jak tworzymy Present Perfect?", "lang": "pl", "difficulty": 2, "emoji": "✅"},
                    "answer": {"text": "have/has + past participle (III forma)", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Używamy 'will'", "text": "Czy 'will' używamy do spontanicznych decyzji?", "lang": "pl", "difficulty": 1, "emoji": "💡"},
                    "answer": {"text": "true", "type": "boolean", "lang": "pl", "metadata": {"true_label": "Tak", "false_label": "Nie"}}
                },
                {
                    "question": {"title": "Słowa kluczowe", "text": "Wybierz wszystkie słowa, które często występują z Present Perfect:", "lang": "pl", "difficulty": 3, "emoji": "🔑"},
                    "answer": {"text": "a,c,d", "type": "multiple_choice", "lang": "pl", "options": [
                        {"value": "a", "label": "already"},
                        {"value": "b", "label": "yesterday"},
                        {"value": "c", "label": "yet"},
                        {"value": "d", "label": "just"},
                        {"value": "e", "label": "last week"}
                    ]}
                },
                {
                    "question": {"title": "Formy czasownika", "text": "Ile form czasownika nieregularnego musimy znać w angielskim?", "lang": "pl", "difficulty": 1, "emoji": "📝"},
                    "answer": {"text": "3", "type": "integer", "lang": "pl", "metadata": {"hint": "bezokolicznik, Past Simple, Past Participle"}}
                }
            ]
        },
        {
            "name": "Budowa komórki",
            "subject": "Biologia",
            "category": "Cytologia",
            "level": "Klasa 1",
            "description": "Podstawowe struktury komórkowe",
            "favourite": False,
            "image": "🧬",
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
            "level": "Klasa 1",
            "favourite": False,
            "image": "🇫🇷"
        },
        {
            "name": "Ruch i siły",
            "subject": "Fizyka",
            "category": "Mechanika",
            "level": "Klasa 1",
            "description": "Podstawy dynamiki i kinematyki",
            "favourite": True,
            "image": "⚛️",
            "flashcards": [
                {
                    "question": {"title": "Prędkość", "text": "Jaki jest wzór na prędkość?", "lang": "pl", "difficulty": 1, "emoji": "🏃", "examples": ["jeśli samochód przejedzie 100m w 5s, to v = 100/5 = 20 m/s"]},
                    "answer": {"text": "v = s/t", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Przyspieszenie", "text": "Jaki jest wzór na przyspieszenie?", "lang": "pl", "difficulty": 2, "emoji": "🚀"},
                    "answer": {"text": "a = Δv/Δt", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "II zasada dynamiki", "text": "Wybierz poprawne stwierdzenie dotyczące II zasady dynamiki Newtona:", "lang": "pl", "difficulty": 2, "emoji": "⚖️"},
                    "answer": {"text": "b", "type": "choice", "lang": "pl", "options": [
                        {"value": "a", "label": "Przyspieszenie jest odwrotnie proporcjonalne do siły"},
                        {"value": "b", "label": "F = ma (siła równa się masa razy przyspieszenie)"},
                        {"value": "c", "label": "Masa jest proporcjonalna do prędkości"},
                        {"value": "d", "label": "Siła jest stała dla każdego ciała"}
                    ]}
                },
                {
                    "question": {"title": "Energia kinetyczna", "text": "Jaki jest wzór na energię kinetyczną?", "lang": "pl", "difficulty": 2, "emoji": "💨", "examples": ["dla ciała o masie 4kg i prędkości 10m/s: Ek = 4×10²/2 = 200J"]},
                    "answer": {"text": "Ek = mv²/2", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Energia potencjalna", "text": "Jaki jest wzór na energię potencjalną grawitacji?", "lang": "pl", "difficulty": 2, "emoji": "⛰️"},
                    "answer": {"text": "Ep = mgh", "type": "text", "lang": "pl"}
                },
                {
                    "question": {"title": "Ruch jednostajny", "text": "Czy w ruchu jednostajnym prędkość jest stała?", "lang": "pl", "difficulty": 1, "emoji": "➡️"},
                    "answer": {"text": "true", "type": "boolean", "lang": "pl", "metadata": {"true_label": "Tak", "false_label": "Nie"}}
                },
                {
                    "question": {"title": "Zasady zachowania", "text": "Wybierz wszystkie wielkości, które zachowują się w układzie izolowanym:", "lang": "pl", "difficulty": 3, "emoji": "♻️"},
                    "answer": {"text": "a,b,c", "type": "multiple_choice", "lang": "pl", "options": [
                        {"value": "a", "label": "Energia całkowita"},
                        {"value": "b", "label": "Pęd"},
                        {"value": "c", "label": "Masa"},
                        {"value": "d", "label": "Temperatura"}
                    ]}
                },
                {
                    "question": {"title": "Przyspieszenie ziemskie", "text": "Ile wynosi przyspieszenie ziemskie w m/s²? (zaokrąglij do liczby całkowitej)", "lang": "pl", "difficulty": 1, "emoji": "🌍"},
                    "answer": {"text": "10", "type": "integer", "lang": "pl", "metadata": {"hint": "Dokładna wartość to ~9.81 m/s²"}}
                }
            ]
        },
        {
            "name": "Układ okresowy pierwiastków",
            "subject": "Chemia",
            "category": "Chemia ogólna",
            "level": "Klasa 1",
            "description": "Podstawy układu okresowego",
            "favourite": True,
            "image": "🧪",
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
            "favourite": False,
            "image": "💻",
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


def import_quiz_from_file(db, file_path, user_id, category=None, level=None, favourite=False, image=None):
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

    # Update favourite and image fields
    if favourite or image:
        quiz.favourite = favourite
        if image:
            quiz.image = image.encode('utf-8')  # Store emoji as bytes
        db.commit()
        db.refresh(quiz)

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

    # Update favourite and image fields
    quiz.favourite = quiz_data.get("favourite", False)
    if quiz_data.get("image"):
        quiz.image = quiz_data["image"].encode('utf-8')  # Store emoji as bytes
    db.commit()
    db.refresh(quiz)

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
                        quiz_data.get("level"),
                        quiz_data.get("favourite", False),
                        quiz_data.get("image")
                    )
                    fav_marker = "⭐" if quiz.favourite else ""
                    img_marker = quiz_data.get("image", "")
                    print(f"      ✅ Imported: {quiz.name} {img_marker} {fav_marker} (from {quiz_data['file']})")
                else:
                    # Create from data
                    quiz = create_quiz_from_data(db, quiz_data, user.id)
                    fav_marker = "⭐" if quiz.favourite else ""
                    img_marker = quiz_data.get("image", "")
                    print(f"      ✅ Created: {quiz.name} {img_marker} {fav_marker}")

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

            # Create more sessions spread over the past year for better time period filtering
            # Favourite quizzes get more sessions
            if quiz.favourite:
                num_sessions = random.randint(30, 50)  # More sessions for favourites
            else:
                num_sessions = random.randint(15, 30)

            for i in range(num_sessions):
                # Distribution across time periods:
                # 20% in last 7 days (week)
                # 30% in last 30 days (month)
                # 30% in 30-180 days (half year)
                # 20% in 180-365 days (rest of year)
                rand_val = random.random()
                if rand_val < 0.2:
                    days_ago = random.randint(0, 7)
                elif rand_val < 0.5:
                    days_ago = random.randint(8, 30)
                elif rand_val < 0.8:
                    days_ago = random.randint(31, 180)
                else:
                    days_ago = random.randint(181, 365)

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
                    score=score,
                    completed=True
                )
                db.add(session)
                session_count += 1

        db.commit()
        print(f"      ✅ Created {session_count} learning sessions spanning 1 year")


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

        # Only show credentials when not in CI environment
        import os
        is_ci = os.environ.get('VITE_IS_CI') == 'true' or os.environ.get('CI') == 'true'

        if not is_ci:
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
        else:
            print("\n📊 Summary:")
            print(f"   Users created: {len(users)}")
            total_quizzes = sum(len(quizzes) for quizzes in user_quizzes.values())
            print(f"   Total quizzes: {total_quizzes}")
            print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
