# SlayFlashcards – System Architecture

## Overview
SlayFlashcards is composed of three main layers:
- **CLI Application** – terminal interface for importing, learning, and testing.
- **Web Application (Streamlit)** – browser-based interface with flashcards and dashboards.
- **Core Services** – database layer, audio processing, and business logic shared across CLI and Web.

## Components

### 1) CLI (Typer)
- Commands for managing and running quizzes.
- Uses the DB layer (SQLAlchemy) for CRUD.
- Uses the audio module (gTTS) for TTS generation/playback.

### 2) Web App (Streamlit)
- Views: quiz list, flashcard slides, test forms, progress dashboard.
- Uses the same DB layer for data access.
- Embeds audio files generated via gTTS.

### 3) Database Layer (SQLAlchemy + SQLite/PostgreSQL)
- Models: **User, Quiz, Flashcard, Session**.
- CRUD operations shared by CLI & Web.
- Default backend: SQLite; migration path to PostgreSQL.

### 4) Audio Layer (gTTS)
- Generates `.mp3` audio for questions/answers.
- CLI playback via `playsound`/`pygame`.
- Web playback via embedded audio in Streamlit.

### 5) Packaging & Deployment
- CLI packaged as a standalone binary via **PyInstaller**.
- Web App deployable via **Docker**.
- Both share the same models and CRUD layer.

## Architecture Diagram
```mermaid
flowchart TD
    subgraph CLI[CLI Application (Typer)]
        CLI_Commands[Commands: import, list, learn, test, progress]
    end

    subgraph Web[Web Application (Streamlit)]
        Web_UI[Quiz List, Flashcards, Tests, Dashboard]
    end

    subgraph Core[Core Services]
        DB[(Database: SQLite/Postgres)]
        CRUD[SQLAlchemy ORM + CRUD]
        Audio[gTTS Audio Generator]
    end

    CLI_Commands --> CRUD
    Web_UI --> CRUD
    CRUD --> DB
    CLI_Commands --> Audio
    Web_UI --> Audio
```

## Data Flow Examples

### A) Import Quiz (CLI)
1. User runs `import-quiz file.json`.
2. CLI parses JSON → maps to SQLAlchemy models.
3. Inserts `Quiz` + `Flashcard` rows into SQLite.
4. Confirms import (quiz id, number of cards).

### B) Learning Mode (CLI/Web)
1. User starts learning session (`Session.mode = "learn"`).
2. App fetches flashcards by `quiz_id`.
3. Shows question → reveal answer; optional TTS playback.
4. Updates learning stats (e.g., last reviewed timestamps).

### C) Test Mode (CLI/Web)
1. User starts test session (`Session.mode = "test"`).
2. App fetches flashcards.
3. User submits answers; system evaluates correctness.
4. Saves `Session.score`, timestamps, and per-card outcomes (future extension).

## Deployment Options
- **CLI Binary**: PyInstaller → single executable for Win/Mac/Linux.
- **Web App**: Docker image → deploy to any container platform.
- Shared DB schema/models across both distributions.
