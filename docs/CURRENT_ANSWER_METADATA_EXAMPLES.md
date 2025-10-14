# Current Answer Metadata Examples

This document shows **actual working examples** from the SlayFlashcards codebase that you can use as templates for creating your own flashcards.

## Real Examples from Demo Data

All examples below are from `scripts/create_demo_data.py` and are **currently working** in the application.

---

## 1. TEXT (Long Answer) - Biology Example

**Use case:** Essay questions, detailed explanations

```python
{
    "question": {
        "title": "Pytanie otwarte (text)",
        "text": "Opisz proces fotosyntezy w roślinach.",
        "lang": "pl",
        "difficulty": 3,
        "emoji": "🌱",
        "examples": [
            "Rośliny wykorzystują światło słoneczne...",
            "Chlorofil w liściach pochłania energię..."
        ]
    },
    "answer": {
        "text": "Fotosynteza to proces, w którym rośliny przekształcają dwutlenek węgla i wodę w glukozę i tlen przy użyciu energii słonecznej. Zachodzi w chloroplastach, gdzie chlorofil pochłania światło.",
        "type": "text",
        "lang": "pl",
        "metadata": {
            "hint": "Opisz proces w 2-3 zdaniach",
            "rows": 4,
            "min_words": 15
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Opisz proces w 2-3 zdaniach
[Large text area with 4 rows]
```

**Available metadata fields:**
- `hint` - Custom message shown to user
- `rows` - Textarea height (default: 3)
- `min_words` - Minimum word count
- `placeholder` - Input placeholder text

---

## 2. SHORT_TEXT (Single Line) - Geography Example

**Use case:** Names, cities, short phrases

```python
{
    "question": {
        "title": "Krótka odpowiedź (short_text)",
        "text": "Jaka jest stolica Francji?",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "🇫🇷",
        "examples": ["Paryż", "Paris"]
    },
    "answer": {
        "text": "Paryż",
        "type": "short_text",
        "lang": "pl",
        "metadata": {
            "hint": "Wpisz nazwę miasta",
            "placeholder": "np. Warszawa",
            "case_sensitive": False
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wpisz nazwę miasta
[Single line input: "np. Warszawa"]
```

**Available metadata fields:**
- `hint` - Custom message
- `placeholder` - Placeholder text
- `case_sensitive` - Boolean (default: False)
- `max_length` - Maximum character count (default: 100)

---

## 3. INTEGER (Whole Numbers) - Calendar Example

**Use case:** Counts, years, quantities

```python
{
    "question": {
        "title": "Liczba całkowita (integer)",
        "text": "Ile dni ma rok przestępny?",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "📅",
        "examples": ["365", "366"]
    },
    "answer": {
        "text": "366",
        "type": "integer",
        "lang": "pl",
        "metadata": {
            "hint": "Wpisz liczbę całkowitą",
            "placeholder": "np. 365",
            "min": 365,
            "max": 366
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wpisz liczbę całkowitą
[Number input with min=365, max=366, step=1]
```

**Available metadata fields:**
- `hint` - Custom message
- `placeholder` - Placeholder text
- `min` - Minimum value
- `max` - Maximum value
- `example` - Example value

---

## 4. FLOAT (Decimal Numbers) - Math Example

**Use case:** Measurements, scientific values, percentages

```python
{
    "question": {
        "title": "Liczba dziesiętna (float)",
        "text": "Jaka jest wartość liczby π (pi) z dokładnością do 2 miejsc po przecinku?",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "🥧",
        "examples": ["3.14", "3.141", "3.1415"]
    },
    "answer": {
        "text": "3.14",
        "type": "float",
        "lang": "pl",
        "metadata": {
            "hint": "Wpisz liczbę z dokładnie 2 miejscami po przecinku",
            "decimal_places": 2,
            "step": 0.01,
            "example": "3.14"
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wpisz liczbę z dokładnie 2 miejscami po przecinku
[Number input with step=0.01]
```

**Available metadata fields:**
- `hint` - Custom message
- `decimal_places` - Required decimal places
- `step` - Increment step (e.g., 0.01, 0.1)
- `min` - Minimum value
- `max` - Maximum value
- `example` - Example value
- `unit` - Unit of measurement (e.g., "kg", "m/s²")

---

## 5. RANGE (Slider) - Medical Example

**Use case:** Ratings, scales, ranges

```python
{
    "question": {
        "title": "Zakres liczbowy (range)",
        "text": "Jaka jest normalna temperatura ciała człowieka w stopniach Celsjusza?",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "🌡️",
        "examples": ["36.6", "37.0"]
    },
    "answer": {
        "text": "36.6",
        "type": "range",
        "lang": "pl",
        "metadata": {
            "min": 36.0,
            "max": 37.5,
            "step": 0.1,
            "hint": "Wybierz temperaturę w zakresie 36.0-37.5°C",
            "labels": {
                "min": "Niska",
                "max": "Wysoka"
            }
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wybierz temperaturę w zakresie 36.0-37.5°C
[Slider: Niska ←--●----→ Wysoka]
Current value: 36.6
```

**Required metadata fields:**
- `min` - Minimum value **(REQUIRED)**
- `max` - Maximum value **(REQUIRED)**

**Optional metadata fields:**
- `step` - Step increment (default: 1)
- `hint` - Custom message
- `labels` - Object with `min` and `max` labels

---

## 6. BOOLEAN (True/False) - Science Example

**Use case:** Yes/No questions, true/false statements

```python
{
    "question": {
        "title": "Prawda/Fałsz (boolean)",
        "text": "Czy Ziemia jest płaska?",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "🌍"
    },
    "answer": {
        "text": "false",
        "type": "boolean",
        "lang": "pl",
        "metadata": {
            "true_label": "Tak",
            "false_label": "Nie",
            "hint": "Wybierz Tak lub Nie"
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wybierz Tak lub Nie
[✓ Tak] [✗ Nie]
```

**Available metadata fields:**
- `true_label` - Label for true button (default: "True")
- `false_label` - Label for false button (default: "False")
- `hint` - Custom message

---

## 7. CHOICE (Single Selection) - Astronomy Example

**Use case:** Multiple choice questions (one answer)

```python
{
    "question": {
        "title": "Wybór jednej opcji (choice)",
        "text": "Który planet jest największy w Układzie Słonecznym?",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "🪐"
    },
    "answer": {
        "text": "b",
        "type": "choice",
        "lang": "pl",
        "options": [
            {"value": "a", "label": "Mars"},
            {"value": "b", "label": "Jowisz"},
            {"value": "c", "label": "Saturn"},
            {"value": "d", "label": "Ziemia"}
        ],
        "metadata": {
            "hint": "Wybierz jedną poprawną odpowiedź"
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Wybierz jedną poprawną odpowiedź
○ Mars
● Jowisz
○ Saturn
○ Ziemia
```

**Required fields:**
- `options` - Array of `{value, label}` objects **(REQUIRED)**

**Available metadata fields:**
- `hint` - Custom message
- `randomize_options` - Shuffle options (Boolean)

---

## 8. MULTIPLE_CHOICE (Multiple Selections) - Programming Example

**Use case:** Select all that apply questions

```python
{
    "question": {
        "title": "Wybór wielu opcji (multiple_choice)",
        "text": "Które z poniższych są językami programowania?",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "💻"
    },
    "answer": {
        "text": "a,c,d",  # Comma-separated values
        "type": "multiple_choice",
        "lang": "pl",
        "options": [
            {"value": "a", "label": "Python"},
            {"value": "b", "label": "HTML"},
            {"value": "c", "label": "JavaScript"},
            {"value": "d", "label": "Java"},
            {"value": "e", "label": "CSS"}
        ],
        "metadata": {
            "hint": "Zaznacz wszystkie poprawne odpowiedzi (3 opcje)",
            "exact_count": 3
        }
    }
}
```

**What user sees:**
```
💡 Expected format: Zaznacz wszystkie poprawne odpowiedzi (3 opcje)
☑ Python
☐ HTML
☑ JavaScript
☑ Java
☐ CSS
```

**Required fields:**
- `options` - Array of `{value, label}` objects **(REQUIRED)**
- `text` - Comma-separated answer values (e.g., "a,c,d")

**Available metadata fields:**
- `hint` - Custom message
- `exact_count` - Exact number of required selections
- `min_selections` - Minimum selections
- `max_selections` - Maximum selections
- `randomize_options` - Shuffle options (Boolean)

---

## Common Patterns

### Pattern 1: Numeric Answer with Range
```python
"metadata": {
    "hint": "Enter a value between 0 and 100",
    "min": 0,
    "max": 100
}
```

### Pattern 2: Text with Length Requirement
```python
"metadata": {
    "hint": "Write 2-3 sentences (min 20 words)",
    "rows": 4,
    "min_words": 20
}
```

### Pattern 3: Case-Insensitive Short Answer
```python
"metadata": {
    "hint": "Type the name (not case sensitive)",
    "case_sensitive": False,
    "placeholder": "e.g., Example"
}
```

### Pattern 4: Multiple Choice with Count
```python
"metadata": {
    "hint": "Select exactly 3 correct options",
    "exact_count": 3
}
```

### Pattern 5: Float with Precision
```python
"metadata": {
    "hint": "Enter with 2 decimal places",
    "decimal_places": 2,
    "step": 0.01,
    "example": "12.34"
}
```

---

## Real-World Subject Examples

### Mathematics Quiz - Quadratic Functions
```python
{
    "question": {
        "title": "Wierzchołek paraboli",
        "text": "Jak obliczyć współrzędną x wierzchołka paraboli?",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "📊",
        "examples": ["dla f(x) = 2x² + 8x + 3, x = -8/(2×2) = -2"]
    },
    "answer": {
        "text": "x = -b/(2a)",
        "type": "text",
        "lang": "pl",
        "metadata": {
            "hint": "Wpisz wzór (użyj zmiennych a i b)",
            "placeholder": "np. x = ...",
            "max_length": 50
        }
    }
}
```

### English Grammar Quiz - Present Continuous
```python
{
    "question": {
        "title": "Present Continuous",
        "text": "Wybierz poprawną formę Present Continuous:",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "🔄"
    },
    "answer": {
        "text": "a",
        "type": "choice",
        "lang": "pl",
        "options": [
            {"value": "a", "label": "am/is/are + czasownik-ing"},
            {"value": "b", "label": "have/has + czasownik-ing"},
            {"value": "c", "label": "was/were + czasownik-ed"},
            {"value": "d", "label": "will + czasownik-ing"}
        ],
        "metadata": {
            "hint": "Wybierz strukturę gramatyczną"
        }
    }
}
```

### Physics Quiz - Motion
```python
{
    "question": {
        "title": "Przyspieszenie ziemskie",
        "text": "Ile wynosi przyspieszenie ziemskie w m/s²? (zaokrąglij do liczby całkowitej)",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "🌍"
    },
    "answer": {
        "text": "10",
        "type": "integer",
        "lang": "pl",
        "metadata": {
            "hint": "Dokładna wartość to ~9.81 m/s²",
            "min": 9,
            "max": 11,
            "example": "10"
        }
    }
}
```

### Biology Quiz - Cell Structure
```python
{
    "question": {
        "title": "Jądro komórkowe",
        "text": "Co zawiera jądro komórkowe?",
        "lang": "pl",
        "difficulty": 1,
        "emoji": "🧬"
    },
    "answer": {
        "text": "Materiał genetyczny DNA",
        "type": "short_text",
        "lang": "pl",
        "metadata": {
            "hint": "Wpisz krótką odpowiedź (1-5 słów)",
            "placeholder": "np. DNA, RNA, ...",
            "case_sensitive": False,
            "max_length": 50
        }
    }
}
```

---

## How to Use These Examples

### For Creating New Flashcards via API:

```python
from core.db.crud.repository.flashcard_repository import FlashcardRepository

flashcard_repo = FlashcardRepository(db)

# Copy any example above and use:
flashcard_repo.create_flashcard(
    quiz_id=your_quiz_id,
    question_dict={
        "title": "...",
        "text": "...",
        # ... other question fields
    },
    answer_dict={
        "text": "...",
        "type": "...",
        "metadata": {
            "hint": "...",
            # ... other metadata fields
        }
    }
)
```

### For Bulk Import via JSON:

```json
{
  "quiz": {
    "name": "My Quiz",
    "subject": "Mathematics"
  },
  "flashcards": [
    {
      "question": {
        "title": "...",
        "text": "..."
      },
      "answer": {
        "text": "...",
        "type": "float",
        "metadata": {
          "hint": "Enter with 2 decimal places",
          "decimal_places": 2,
          "step": 0.01
        }
      }
    }
  ]
}
```

---

## Testing

All these examples are available in the demo data. To test them:

```bash
# 1. Generate demo data
python3 scripts/create_demo_data.py

# 2. Login as Emila or Kriz
# 3. Find quiz "Test wszystkich typów odpowiedzi" 🧪
# 4. Start a session and see the hints in action!
```

---

## Quick Reference: Most Important Fields

| Answer Type | Must Have | Should Have | Nice to Have |
|-------------|-----------|-------------|--------------|
| text | hint | rows, min_words | placeholder |
| short_text | hint | placeholder, case_sensitive | max_length |
| integer | hint | min, max | example, placeholder |
| float | hint, decimal_places | step, example | min, max, unit |
| range | **min, max** | hint, step | labels |
| boolean | - | true_label, false_label | hint |
| choice | **options** | hint | randomize_options |
| multiple_choice | **options** | hint, exact_count | min/max_selections |

**Bold** = Required fields

---

## Current Files Reference

- **Source of examples:** `scripts/create_demo_data.py:84-193`
- **Standalone script:** `scripts/create_answer_types_quiz.py`
- **API schema:** `api/api_schemas.py:265-273`
- **Frontend display:** `frontend/src/components/sessions/FlashcardDisplay.tsx:121-177`
- **Frontend input:** `frontend/src/components/sessions/AnswerInput.tsx`

---

## Last Updated

Document generated: 2025-10-13
SlayFlashcards version: Current production
All examples tested and working ✓
