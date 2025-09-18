# SlayFlashcards Project Requirements  

## Functional Requirements  
- Import quizzes from JSON files.  
- Manage quizzes and flashcards stored in a database.  
- Support multiple users.  
- Study flashcards in **learning mode** (show → reveal answer → play audio).  
- Run quizzes in **test mode** (user types answer → system checks correctness).  
- Collect statistics: number of sessions, repetitions, test results.  
- Support Text-to-Speech (TTS) for both questions and answers.  
- CLI commands:  
  - `import-quiz <file.json>`  
  - `list-quizzes`  
  - `learn <quiz_id>`  
  - `test <quiz_id>`  
  - `progress [user]`  
- Web App features (Streamlit):  
  - Browse quizzes as slides.  
  - Interactive quiz mode.  
  - Audio playback.  
  - Dashboard with progress statistics.  

---

## Non-Functional Requirements  
- Easy installation: packaged CLI binary (PyInstaller) and Docker container for web app.  
- Extensible DB layer (SQLite → PostgreSQL).  
- Cross-platform (Windows, Mac, Linux).  
- Efficient for datasets with hundreds of flashcards.  
- Codebase maintainable and modular (CLI + Web share the same DB and models).  

---

## Use Cases  
- **Import Quiz**: user imports JSON file → new quiz and flashcards stored in DB.  
- **List Quizzes**: display available quizzes and metadata.  
- **Learning Mode**: user reviews flashcards, listens to pronunciation.  
- **Test Mode**: user answers questions, system evaluates correctness.  
- **Track Progress**: user checks stats (sessions, average score).  

---

## Data Model  
- **User**  
  - `id`  
  - `name`  

- **Quiz**  
  - `id`  
  - `name`  
  - `subject`  
  - `created_at`  
  - `description`  

- **Flashcard**  
  - `id`  
  - `quiz_id` (FK)  
  - `question_title`  
  - `question_text`  
  - `question_lang`  
  - `answer_text`  
  - `answer_lang`  
  - `difficulty`, `emoji`, `image`  

- **Session**  
  - `id`  
  - `user_id` (FK)  
  - `quiz_id` (FK)  
  - `mode` ("learn" / "test")  
  - `started_at`  
  - `score` (optional, for test mode)  

---

## Components  
- **CLI (Typer)**  
  - Command-line interface for quiz management, learning, and testing.  

- **Web (Streamlit)**  
  - User-friendly UI with flashcard slides and interactive quizzes.  

- **Database Layer (SQLAlchemy)**  
  - ORM with SQLite backend, PostgreSQL-ready.  

- **Audio Layer (gTTS)**  
  - Generates `.mp3` audio for flashcards.  
  - CLI uses `playsound`/`pygame`, web uses embedded player.  

---

## Technology Stack  
- **Language**: Python 3.11+  
- **Database**: SQLite (default), PostgreSQL (future option)  
- **ORM**: SQLAlchemy  
- **CLI**: Typer  
- **Web App**: Streamlit  
- **TTS**: gTTS  
- **Binary Packaging**: PyInstaller  
- **Deployment**: Docker  