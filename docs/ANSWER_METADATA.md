# Answer Metadata Guide

This document describes the metadata system for flashcard answers, which helps users understand the expected answer format.

## Overview

Each flashcard answer can include a `metadata` field (JSON object) that provides additional information about the expected answer format. This metadata is used to:

1. **Generate format hints** - Display helpful guidance to users before they answer
2. **Configure input fields** - Customize the input UI (placeholders, step values, etc.)
3. **Set validation rules** - Define acceptable value ranges and formats

## Metadata Fields by Answer Type

### 1. TEXT (Long Text)

For essays, explanations, and multi-sentence answers.

```json
{
  "answer": {
    "text": "The answer text...",
    "type": "text",
    "metadata": {
      "hint": "Describe the process in 2-3 sentences",
      "placeholder": "Type your detailed answer here...",
      "rows": 5,
      "min_words": 10,
      "max_words": 100,
      "case_sensitive": false
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint text shown to user
- `placeholder` (string): Input placeholder text
- `rows` (number): Textarea height in rows (default: 3)
- `min_words` (number): Minimum word count
- `max_words` (number): Maximum word count
- `case_sensitive` (boolean): Whether answer checking is case-sensitive

### 2. SHORT_TEXT (Short Answer)

For single words, names, or short phrases.

```json
{
  "answer": {
    "text": "Paris",
    "type": "short_text",
    "metadata": {
      "hint": "Enter the city name",
      "placeholder": "Type the city name...",
      "max_length": 50,
      "case_sensitive": false,
      "example": "London"
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint text
- `placeholder` (string): Input placeholder
- `max_length` (number): Maximum character count (default: 100)
- `case_sensitive` (boolean): Case-sensitive matching
- `example` (string): Example answer to show in hint

### 3. INTEGER (Whole Numbers)

For counting, years, quantities.

```json
{
  "answer": {
    "text": "42",
    "type": "integer",
    "metadata": {
      "hint": "Enter a whole number",
      "placeholder": "Enter a number...",
      "min": 0,
      "max": 100,
      "example": "42"
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint text
- `placeholder` (string): Input placeholder
- `min` (number): Minimum allowed value
- `max` (number): Maximum allowed value
- `example` (string): Example value
- `unit` (string): Unit of measurement (e.g., "years", "items")

### 4. FLOAT (Decimal Numbers)

For measurements, percentages, scientific values.

```json
{
  "answer": {
    "text": "3.14",
    "type": "float",
    "metadata": {
      "hint": "Enter a decimal number with 2 places",
      "placeholder": "e.g., 3.14",
      "step": 0.01,
      "decimal_places": 2,
      "min": 0,
      "max": 10,
      "example": "3.14",
      "unit": "meters"
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint
- `placeholder` (string): Input placeholder
- `step` (number): Increment step (default: 0.01)
- `decimal_places` (number): Required decimal places
- `min` (number): Minimum value
- `max` (number): Maximum value
- `example` (string): Example value
- `unit` (string): Unit of measurement

### 5. RANGE (Numeric Range)

For sliders and range-based answers.

```json
{
  "answer": {
    "text": "7",
    "type": "range",
    "metadata": {
      "min": 1,
      "max": 10,
      "step": 1,
      "hint": "Rate from 1 to 10",
      "labels": {
        "min": "Poor",
        "max": "Excellent"
      }
    }
  }
}
```

**Supported fields:**
- `min` (number, **required**): Minimum value
- `max` (number, **required**): Maximum value
- `step` (number): Step increment (default: 1)
- `hint` (string): Custom hint
- `labels` (object): Labels for min/max ends
  - `min` (string): Label for minimum value
  - `max` (string): Label for maximum value

### 6. BOOLEAN (True/False)

For yes/no questions, true/false statements.

```json
{
  "answer": {
    "text": "true",
    "type": "boolean",
    "metadata": {
      "true_label": "Yes",
      "false_label": "No",
      "hint": "Select Yes or No"
    }
  }
}
```

**Supported fields:**
- `true_label` (string): Label for true button (default: "True")
- `false_label` (string): Label for false button (default: "False")
- `hint` (string): Custom hint

### 7. CHOICE (Single Selection)

For multiple-choice questions with one correct answer.

```json
{
  "answer": {
    "text": "b",
    "type": "choice",
    "options": [
      {"value": "a", "label": "Option A"},
      {"value": "b", "label": "Option B"},
      {"value": "c", "label": "Option C"},
      {"value": "d", "label": "Option D"}
    ],
    "metadata": {
      "hint": "Select the best answer",
      "randomize_options": true
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint
- `randomize_options` (boolean): Shuffle options on display

### 8. MULTIPLE_CHOICE (Multiple Selections)

For questions with multiple correct answers.

```json
{
  "answer": {
    "text": "a,c,d",
    "type": "multiple_choice",
    "options": [
      {"value": "a", "label": "Option A"},
      {"value": "b", "label": "Option B"},
      {"value": "c", "label": "Option C"},
      {"value": "d", "label": "Option D"},
      {"value": "e", "label": "Option E"}
    ],
    "metadata": {
      "hint": "Select all correct answers",
      "min_selections": 1,
      "max_selections": 3,
      "exact_count": 3,
      "randomize_options": false
    }
  }
}
```

**Supported fields:**
- `hint` (string): Custom hint
- `min_selections` (number): Minimum required selections
- `max_selections` (number): Maximum allowed selections
- `exact_count` (number): Exact number of required selections
- `randomize_options` (boolean): Shuffle options

## Format Hint Generation

The system automatically generates format hints based on:

1. **Custom hint** - If `metadata.hint` is provided, it's displayed directly
2. **Answer analysis** - Word count, letter count from the actual answer
3. **Type information** - Answer type displayed in readable format
4. **Metadata constraints** - Range, format, decimal places, etc.

### Example Hint Output

For this flashcard:
```json
{
  "answer": {
    "text": "3.14159",
    "type": "float",
    "metadata": {
      "decimal_places": 5,
      "min": 3,
      "max": 4,
      "example": "3.14159"
    }
  }
}
```

The hint displayed would be:
> **Expected format:** 7 letters • type: float • 5 decimal places • e.g., "3.14159"

## Best Practices

### 1. Always Provide Custom Hints

Instead of relying on automatic generation, provide clear custom hints:

```json
{
  "metadata": {
    "hint": "Enter the year (4 digits)"
  }
}
```

### 2. Use Examples Effectively

Combine question examples with metadata examples:

```json
{
  "question": {
    "examples": ["e.g., 2024", "e.g., 1989"]
  },
  "answer": {
    "metadata": {
      "example": "2024"
    }
  }
}
```

### 3. Set Reasonable Constraints

For numeric types, always set min/max when relevant:

```json
{
  "metadata": {
    "min": 0,
    "max": 100,
    "hint": "Enter a percentage (0-100)"
  }
}
```

### 4. Use Appropriate Placeholders

Make placeholders descriptive:

```json
{
  "metadata": {
    "placeholder": "Enter city name (e.g., Warsaw, Krakow)"
  }
}
```

### 5. Consider Language and Context

For non-English content, translate metadata:

```json
{
  "metadata": {
    "hint": "Wpisz liczbę całkowitą od 1 do 10",
    "placeholder": "np. 5"
  }
}
```

## Usage in API

When creating flashcards via API:

```python
flashcard_data = {
    "quiz_id": 1,
    "question": {
        "title": "Pi Value",
        "text": "What is the value of pi to 2 decimal places?",
        "lang": "en",
        "difficulty": 2,
        "emoji": "🥧",
        "examples": ["3.14", "3.141"]
    },
    "answer": {
        "text": "3.14",
        "type": "float",
        "lang": "en",
        "metadata": {
            "hint": "Enter pi with exactly 2 decimal places",
            "decimal_places": 2,
            "step": 0.01,
            "example": "3.14"
        }
    }
}
```

## Database Schema

The `answer_metadata` field is stored as JSON in the database:

```sql
CREATE TABLE flashcard (
    ...
    answer_metadata TEXT,  -- JSON string
    ...
);
```

Python/SQLAlchemy automatically handles JSON serialization:

```python
from sqlalchemy import JSON

class Flashcard(Base):
    answer_metadata = Column(JSON)  # Automatically serialized
```

## Frontend Integration

The `AnswerInput.tsx` component reads metadata to configure inputs:

```typescript
// Boolean labels
const trueLabel = metadata?.true_label || 'True';

// Range slider
<input
    type="range"
    min={metadata.min}
    max={metadata.max}
    step={metadata.step || 1}
/>

// Text input placeholder
<input
    placeholder={metadata?.placeholder || "Type your answer..."}
/>
```

The `FlashcardDisplay.tsx` component generates hints:

```typescript
const getAnswerHint = () => {
    const metadata = answer.metadata || {};

    // Use custom hint if provided
    if (metadata.hint) {
        return metadata.hint;
    }

    // Generate hint from analysis
    // ...
};
```

## Migration Path

If you have existing flashcards without metadata, you can add it:

```python
# Update existing flashcard
flashcard_repo.update(
    flashcard,
    answer_metadata={
        "hint": "Enter a whole number",
        "placeholder": "e.g., 42"
    }
)
```

## Examples by Subject

### Mathematics

```json
{
  "metadata": {
    "hint": "Enter result as decimal number with 2 places",
    "decimal_places": 2,
    "example": "12.50"
  }
}
```

### Language Learning

```json
{
  "metadata": {
    "hint": "Type the word in French",
    "case_sensitive": false,
    "placeholder": "e.g., bonjour"
  }
}
```

### Science

```json
{
  "metadata": {
    "hint": "Enter temperature in Celsius (36-38)",
    "min": 36,
    "max": 38,
    "unit": "°C",
    "decimal_places": 1
  }
}
```

### History

```json
{
  "metadata": {
    "hint": "Enter the year (4 digits)",
    "min": 1000,
    "max": 2024,
    "example": "1989"
  }
}
```

## Conclusion

The metadata system provides flexible, type-specific guidance to users. Always strive to make the expected answer format as clear as possible through:

1. **Custom hints** - Clear, concise format descriptions
2. **Examples** - Both in questions and metadata
3. **Constraints** - Appropriate min/max, step values
4. **Placeholders** - Descriptive input placeholders
5. **Localization** - Translated metadata for non-English content
