# SlayFlashcards - Complete Setup and Usage Guide

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Creating the Command](#creating-the-command)
- [Basic Usage](#basic-usage)
- [Learning Sessions](#learning-sessions)
- [Quiz Management](#quiz-management)
- [Progress Tracking](#progress-tracking)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Overview

SlayFlashcards is a flashcard application designed to enhance learning efficiency through interactive and customizable flashcards. It supports spaced repetition, audio playback, and comprehensive progress tracking.

### Key Features
- 🎓 Interactive learning sessions with audio support
- 📊 Comprehensive progress tracking and statistics
- 🗣️ Text-to-Speech (TTS) for questions and answers
- 🌍 Multi-language support
- 📱 Both CLI and Web interfaces (CLI ready, Web planned)
- 💾 SQLite database with PostgreSQL migration path

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
git clone https://github.com/krizo/slayflashcards.git
cd slayflashcards
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `typer` - CLI framework
- `sqlalchemy` - Database ORM
- `gtts` - Google Text-to-Speech
- `pygame` - Audio playback
- `streamlit` - Web interface (planned)

### Step 3: Verify Installation
```bash
python main.py --help
```

## Creating the Command

To use `slayflashcards` as a global command, choose one of these methods:

### Method 1: Package Installation (Recommended)

1. **Create setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name="slayflashcards",
    version="1.0.0",
    description="An innovative flashcard application for enhanced learning",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "typer>=0.9.0",
        "sqlalchemy>=2.0.0",
        "gtts>=2.3.0",
        "pygame>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "slayflashcards=main:main",
        ],
    },
)
```

2. **Install the package**:
```bash
pip install -e .
```

3. **Test the command**:
```bash
slayflashcards --help
```

### Method 2: Shell Script (Quick Setup)

1. **Create a shell script**:
```bash
cat > slayflashcards.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/main.py" "$@"
EOF
```

2. **Make it executable and install**:
```bash
chmod +x slayflashcards.sh
sudo cp slayflashcards.sh /usr/local/bin/slayflashcards
```

### Method 3: Alias (Development)

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias slayflashcards="python /path/to/slayflashcards/main.py"
```

Then reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Method 4: PyInstaller Binary

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone binary
pyinstaller --onefile --name slayflashcards main.py

# Install globally
sudo cp dist/slayflashcards /usr/local/bin/
```

## Quick Start

### 1. Initialize Database
```bash
slayflashcards reset-db
```

### 2. Import Your First Quiz
```bash
# Use the provided example
slayflashcards import-quiz examples/example.json
```

### 3. List Available Quizzes
```bash
slayflashcards list-quizzes
```

### 4. Start Learning
```bash
slayflashcards learn 1
```

## Basic Usage

### Command Structure
```bash
slayflashcards [COMMAND] [OPTIONS] [ARGUMENTS]
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `import-quiz` | Import quiz from JSON file | `slayflashcards import-quiz quiz.json` |
| `list-quizzes` | Show all available quizzes | `slayflashcards list-quizzes` |
| `learn` | Start learning session | `slayflashcards learn 1` |
| `test` | Run quiz test (planned) | `slayflashcards test 1` |
| `progress` | Show user progress | `slayflashcards progress` |
| `reset-db` | Reset database | `slayflashcards reset-db` |

## Learning Sessions

### Basic Learning
```bash
# Start learning quiz with ID 1
slayflashcards learn 1
```

### Advanced Learning Options
```bash
# Learning with custom user
slayflashcards learn 1 --user "john"

# Learning without audio
slayflashcards learn 1 --no-audio

# Learning with custom languages
slayflashcards learn 1 --lang-question "en" --lang-answer "fr"

# Complete example
slayflashcards learn 1 --user "alice" --audio --lang-question "pl" --lang-answer "de"
```

### Learning Session Flow

1. **Session Header**:
```
🎓 Learning Mode: French Basics
👤 User: alice
📄 Cards: 3
🔊 Audio: Enabled
--------------------------------------------------
```

2. **Card Display**:
```
📋 Card 1/3

❓ dog
   🐶

⏸️  Press Enter to reveal answer...
```

3. **Answer Reveal**:
```
✅ Answer: chien

🔄 Continue? ([y]es/[n]o/[r]epeat):
```

### Session Controls
- **Enter**: Reveal answer
- **y/yes**: Continue to next card
- **n/no**: End session early
- **r/repeat**: Repeat current card
- **Ctrl+C**: Interrupt session

### Audio Features
- **Question Audio**: Plays in specified question language
- **Answer Audio**: Plays in specified answer language
- **Language Support**: Any language supported by Google TTS
- **Audio Toggle**: Can be enabled/disabled per session

## Quiz Management

### Quiz JSON Format
```json
{
  "quiz": {
    "name": "French Basics",
    "subject": "French",
    "created_at": "2025-09-17",
    "description": "Basic French vocabulary for beginners"
  },
  "flashcards": [
    {
      "question": {
        "title": "dog",
        "text": "dog",
        "lang": "en",
        "difficulty": 1,
        "emoji": "🐶",
        "image": "dog.png"
      },
      "answer": {
        "text": "chien",
        "lang": "fr"
      }
    }
  ]
}
```

### Creating Custom Quizzes

1. **Create JSON file** following the format above
2. **Import the quiz**:
```bash
slayflashcards import-quiz my-quiz.json
```

### Quiz Fields Explained

#### Quiz Metadata
- `name` (required): Quiz title
- `subject` (optional): Subject category
- `description` (optional): Quiz description
- `created_at` (optional): Creation date

#### Flashcard Fields
- `question.title` (required): Short question title
- `question.text` (required): Full question text
- `question.lang` (optional): Question language code
- `question.difficulty` (optional): Difficulty level (1-5)
- `question.emoji` (optional): Question emoji
- `question.image` (optional): Image filename
- `answer.text` (required): Answer text
- `answer.lang` (optional): Answer language code

## Progress Tracking

### View User Progress
```bash
# Default user progress
slayflashcards progress

# Specific user progress
slayflashcards progress --user "alice"
```

### Progress Report Example
```
📊 Progress Report for alice
--------------------------------------------------
Total sessions: 5
Learning sessions: 4
Test sessions: 1
Average test score: 85.0%

🕒 Recent Activity:
  🎓 French Basics - 2025-09-22 14:30
  🧪 Spanish Verbs (80%) - 2025-09-21 16:45
  🎓 German Numbers - 2025-09-21 10:15
```

### Tracked Statistics
- Total sessions count
- Learning vs test sessions
- Average test scores
- Recent activity timeline
- Study streaks
- Favorite subjects

## Advanced Features

### Multi-User Support
```bash
# Create sessions for different users
slayflashcards learn 1 --user "student1"
slayflashcards learn 1 --user "student2"

# View different user progress
slayflashcards progress --user "student1"
slayflashcards progress --user "student2"
```

### Language Configuration
```bash
# Polish questions, German answers
slayflashcards learn 1 --lang-question "pl" --lang-answer "de"

# Spanish questions, English answers
slayflashcards learn 1 --lang-question "es" --lang-answer "en"
```

### Supported Language Codes
- `en` - English
- `fr` - French
- `es` - Spanish
- `de` - German
- `it` - Italian
- `pl` - Polish
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- And many more...

### Database Management
```bash
# Reset entire database
slayflashcards reset-db

# Backup database
cp slayflashcards.db slayflashcards_backup.db

# View database location
ls -la *.db
```

## Troubleshooting

### Command Not Found
```bash
# Check if installed correctly
which slayflashcards

# If using pip installation
pip list | grep slayflashcards

# Reinstall if needed
pip uninstall slayflashcards
pip install -e .
```

### Audio Issues
```bash
# Test audio dependencies
python -c "import gtts, pygame; print('Audio dependencies OK')"

# Test audio service
python -c "
from services.audio_service import GTTSAudioService
service = GTTSAudioService()
print('Audio available:', service.is_available())
"

# Run without audio if issues persist
slayflashcards learn 1 --no-audio
```

### Database Issues
```bash
# Check database file
ls -la slayflashcards.db

# Reset if corrupted
slayflashcards reset-db

# Check database connection
python -c "
from db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database OK')
"
```

### Import Errors
```bash
# Validate JSON syntax
python -c "import json; json.load(open('your-quiz.json'))"

# Check file permissions
ls -la your-quiz.json

# Test with example file first
slayflashcards import-quiz examples/example.json
```

### Permission Issues
```bash
# If using system-wide installation
sudo pip install -e .

# Or use user installation
pip install --user -e .

# Check file permissions
chmod +x slayflashcards.sh
```

## Development Setup

### For Contributors
```bash
# Clone repository
git clone https://github.com/yourusername/slayflashcards.git
cd slayflashcards

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Project Structure
```
slayflashcards/
├── cli/                    # CLI interface
├── db/                     # Database models and CRUD
├── services/               # Business logic services
├── learning/               # Learning session management
├── tests/                  # Test suite
├── examples/               # Example quiz files
├── main.py                 # CLI entry point
├── setup.py               # Package configuration
└── requirements.txt       # Dependencies
```

## Web Interface (Planned)

The architecture supports a future Streamlit web interface:

```bash
# When available
streamlit run web_app.py
```

Features will include:
- Browser-based flashcard slides
- Interactive quiz interface
- Progress dashboard
- Audio playback via web player

## Support and Contributing

### Getting Help
- Check this guide for common issues
- Review the troubleshooting section
- Test with the provided example quiz
- Check Python and dependency versions

### Contributing
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request
