# Quiz JSON Files

Ten katalog zawiera pliki JSON z quizami, które mogą być importowane do systemu SlayFlashcards.

## 📚 Pliki Referencyjne

### `answer_types_reference.json` ⭐ **REFERENCJA**

**Kompletny quiz pokazujący wszystkie 8 typów odpowiedzi z pełną metadaną.**

Zawiera 15 przykładowych fiszek demonstracyjnych:
- **TEXT** (2 przykłady) - długie odpowiedzi tekstowe z min_words
- **SHORT_TEXT** (3 przykłady) - krótkie odpowiedzi (case_sensitive/insensitive)
- **INTEGER** (2 przykłady) - liczby całkowite z zakresem min/max
- **FLOAT** (2 przykłady) - liczby dziesiętne z decimal_places i jednostkami
- **RANGE** (1 przykład) - suwak z min/max/step i labelami
- **BOOLEAN** (2 przykłady) - prawda/fałsz z custom labels
- **CHOICE** (2 przykłady) - wybór jednej opcji (z/bez randomizacji)
- **MULTIPLE_CHOICE** (2 przykłady) - wybór wielu opcji (exact_count/min_max)

**Użyj tego pliku jako wzorca** do tworzenia nowych quizów!

### `new_schema_example.json`

Stary format - wymaga konwersji za pomocą `scripts/convert_quiz_format.py`

## 🌍 Quizy Produkcyjne

### Historia
- **`starożytny_egipt.json`** - Rozszerzony quiz o Starożytnym Egipcie (30 pytań)
- **`historia-praczłowiek.json`** - Quiz o praczłowieku

### Języki
- **`french1.json`** - Quiz języka francuskiego
- **`polish-fra.json`** - Polski-francuski (pełny)
- **`polish-fra-mini.json`** - Polski-francuski (mini wersja)

### Inne
- **`example.json`** - Prosty przykład quizu

## 🔧 Format Pliku JSON

```json
{
  "quiz": {
    "name": "Nazwa quizu",
    "subject": "Przedmiot",
    "created_at": "2025-10-13",
    "category": "Kategoria",
    "level": "Poziom",
    "description": "Opis quizu",
    "lang": "pl",
    "image": "🧪"
  },
  "flashcards": [
    {
      "question": {
        "title": "Tytuł pytania",
        "text": "Treść pytania",
        "lang": "pl",
        "difficulty": 2,
        "emoji": "📚",
        "examples": ["przykład 1", "przykład 2"]
      },
      "answer": {
        "text": "Odpowiedź",
        "type": "text|short_text|integer|float|range|boolean|choice|multiple_choice",
        "lang": "pl",
        "options": [
          {"value": "a", "label": "Opcja A"},
          {"value": "b", "label": "Opcja B"}
        ],
        "metadata": {
          "hint": "Podpowiedź dla użytkownika",
          ...inne pola metadanych
        }
      }
    }
  ]
}
```

## 📖 Metadata Fields by Answer Type

### TEXT (długi tekst)
```json
"metadata": {
  "hint": "Opisz w 2-3 zdaniach",
  "rows": 4,
  "min_words": 15,
  "placeholder": "Wpisz odpowiedź..."
}
```

### SHORT_TEXT (krótki tekst)
```json
"metadata": {
  "hint": "Wpisz nazwę",
  "placeholder": "np. Warszawa",
  "case_sensitive": false,
  "max_length": 50
}
```

### INTEGER (liczba całkowita)
```json
"metadata": {
  "hint": "Wpisz liczbę całkowitą",
  "placeholder": "np. 42",
  "min": 0,
  "max": 100,
  "example": "42"
}
```

### FLOAT (liczba dziesiętna)
```json
"metadata": {
  "hint": "Wpisz z 2 miejscami po przecinku",
  "decimal_places": 2,
  "step": 0.01,
  "example": "3.14",
  "unit": "m/s²",
  "min": 0.0,
  "max": 10.0
}
```

### RANGE (suwak)
```json
"metadata": {
  "min": 36.0,          // WYMAGANE
  "max": 37.5,          // WYMAGANE
  "step": 0.1,
  "hint": "Wybierz wartość",
  "labels": {
    "min": "Niska",
    "max": "Wysoka"
  }
}
```

### BOOLEAN (prawda/fałsz)
```json
"answer": {
  "text": "true",  // lub "false" (lowercase!)
  "type": "boolean",
  "metadata": {
    "true_label": "Tak",
    "false_label": "Nie",
    "hint": "Wybierz Tak lub Nie"
  }
}
```

### CHOICE (wybór jednej opcji)
```json
"answer": {
  "text": "b",  // wartość wybranej opcji (lowercase!)
  "type": "choice",
  "options": [
    {"value": "a", "label": "Opcja A"},
    {"value": "b", "label": "Opcja B"},
    {"value": "c", "label": "Opcja C"}
  ],
  "metadata": {
    "hint": "Wybierz jedną odpowiedź",
    "randomize_options": false
  }
}
```

### MULTIPLE_CHOICE (wybór wielu opcji)
```json
"answer": {
  "text": "a,c,d",  // coma-separated (lowercase!)
  "type": "multiple_choice",
  "options": [
    {"value": "a", "label": "Opcja A"},
    {"value": "b", "label": "Opcja B"},
    {"value": "c", "label": "Opcja C"},
    {"value": "d", "label": "Opcja D"}
  ],
  "metadata": {
    "hint": "Zaznacz wszystkie poprawne (3 opcje)",
    "exact_count": 3,
    // LUB
    "min_selections": 1,
    "max_selections": 4,
    "randomize_options": false
  }
}
```

## 🔄 Konwersja Starych Formatów

Jeśli masz quiz w starym formacie (z `{"key": "A", "text": "..."}` zamiast `{"value": "a", "label": "..."}`), użyj skryptu konwersji:

```bash
python scripts/convert_quiz_format.py data/stary_quiz.json
```

Skrypt automatycznie:
- Konwertuje format opcji
- Zmienia `"True"/"False"` → `"true"/"false"`
- Dodaje metadane z hints
- Przenosi examples z metadata do question

## 📋 Import Quizów

### Via API
```python
from api.utils.bulk_import import import_quiz_from_json

with open("data/answer_types_reference.json", "r", encoding="utf-8") as f:
    quiz_data = json.load(f)

imported_quiz = import_quiz_from_json(quiz_data, user_id=1)
print(f"Quiz imported with ID: {imported_quiz.id}")
```

### Via Script
```bash
python scripts/import_quiz.py --file data/answer_types_reference.json --user-id 1
```

## ✨ Best Practices

1. **Zawsze dodawaj `hint`** - to najważniejsze pole dla użytkownika
2. **Używaj `examples`** w `question` - pokazują format odpowiedzi
3. **Dla CHOICE/MULTIPLE_CHOICE**: wartości `value` zawsze lowercase (`a`, `b`, `c`...)
4. **Dla BOOLEAN**: zawsze lowercase (`true`, `false`)
5. **Dla MULTIPLE_CHOICE**: odpowiedź `text` to comma-separated values (`a,c,d`)
6. **Dla FLOAT**: określ `decimal_places` i `step`
7. **Dla RANGE**: `min` i `max` są WYMAGANE
8. **Tłumacz metadata** dla polskich quizów

## 📚 Więcej Informacji

- **Complete docs**: `docs/ANSWER_METADATA.md`
- **Quick reference**: `docs/ANSWER_FORMAT_HINTS_QUICK_REFERENCE.md`
- **Real examples**: `docs/CURRENT_ANSWER_METADATA_EXAMPLES.md`
- **Conversion script**: `scripts/convert_quiz_format.py`
- **Demo data**: `scripts/create_demo_data.py`

## 🎯 Przykłady Użycia

### Tworzenie nowego quizu matematycznego
```bash
# 1. Skopiuj szablon
cp data/answer_types_reference.json data/matematyka_klasa1.json

# 2. Edytuj plik, zmieniając:
#    - quiz.name, quiz.subject, quiz.description
#    - flashcards (pytania i odpowiedzi)

# 3. Import do systemu
python scripts/import_quiz.py --file data/matematyka_klasa1.json --user-id 1
```

### Konwersja starego quizu
```bash
# Konwertuj stary format do nowego
python scripts/convert_quiz_format.py data/stary_quiz.json

# Quiz zostanie automatycznie zaktualizowany w miejscu
```

---

**Last updated**: 2025-10-13
**SlayFlashcards version**: Current production
**Format version**: 2.0 (with comprehensive metadata)
