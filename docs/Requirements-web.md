# SlayFlashcards Project Requirements

## Functional Requirements

- Users can create, edit, and delete flashcards.
- Flashcards consist of a question and an answer.
- Users can organize flashcards into decks.
- Users can review flashcards in a deck using spaced repetition.
- Users can mark flashcards as "known" or "unknown" during review.
- The system tracks user progress and adjusts flashcard review intervals.
- Users can search for flashcards by keywords.
- Users can share decks with other users.
- User authentication and profile management.
- Support for importing and exporting decks in common formats (e.g., CSV, JSON).

## Non-Functional Requirements

- The application should be responsive and usable on desktop and mobile devices.
- The system should handle concurrent users efficiently.
- Data should be stored securely with backups.
- The interface should be intuitive and user-friendly.
- The system should provide fast search and retrieval of flashcards.
- The application should be scalable to support a growing user base.
- The codebase should be maintainable and well-documented.

## Use Cases

- **Create Flashcard:** User creates a new flashcard with a question and answer.
- **Edit Flashcard:** User modifies the content of an existing flashcard.
- **Delete Flashcard:** User removes a flashcard from a deck.
- **Review Deck:** User reviews flashcards in a deck using spaced repetition.
- **Mark Flashcard:** User marks flashcards as known or unknown during review.
- **Search Flashcards:** User searches for flashcards by keyword.
- **Share Deck:** User shares a deck with other users via link or platform.
- **Import Deck:** User imports flashcards from a file.
- **Export Deck:** User exports flashcards to a file.
- **User Authentication:** User registers, logs in, and manages profile.

## Data Model

- **User**
  - `user_id`: unique identifier
  - `username`
  - `email`
  - `password_hash`
  - `profile_settings`

- **Deck**
  - `deck_id`: unique identifier
  - `user_id`: owner reference
  - `title`
  - `description`
  - `created_at`
  - `updated_at`

- **Flashcard**
  - `flashcard_id`: unique identifier
  - `deck_id`: reference to deck
  - `question`
  - `answer`
  - `created_at`
  - `updated_at`
  - `review_status` (known/unknown)
  - `last_reviewed`
  - `next_review_due`

- **ReviewSession**
  - `session_id`: unique identifier
  - `user_id`
  - `deck_id`
  - `start_time`
  - `end_time`
  - `results` (summary of known/unknown flashcards)

## Components

- **Frontend**
  - User interface for managing decks and flashcards
  - Review interface with spaced repetition
  - Authentication and profile management

- **Backend**
  - API for CRUD operations on users, decks, flashcards
  - Authentication and authorization
  - Spaced repetition algorithm implementation
  - Data storage and retrieval

- **Database**
  - Persistent storage of users, decks, flashcards, and review sessions

- **Import/Export Module**
  - Handling file formats for deck import/export

## Technology Stack

- **Frontend:** React.js or Vue.js, HTML5, CSS3
- **Backend:** Node.js with Express or Python with Django/Flask
- **Database:** PostgreSQL or MongoDB
- **Authentication:** JWT or OAuth 2.0
- **Hosting:** Cloud provider such as AWS, Azure, or Heroku
- **Version Control:** Git with GitHub or GitLab
- **Others:** Docker for containerization, Jest or Mocha for testing
