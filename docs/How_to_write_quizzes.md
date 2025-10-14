# How to Write Quizzes for SlayFlashcards

This guide explains how to create quiz JSON files for SlayFlashcards, covering all 8 supported answer types and their metadata options.

## Table of Contents

1. [Basic Structure](#basic-structure)
2. [Quiz Metadata](#quiz-metadata)
3. [Flashcard Structure](#flashcard-structure)
4. [Answer Types](#answer-types)
   - [1. Text (Free-form)](#1-text-free-form)
   - [2. Short Text](#2-short-text)
   - [3. Integer](#3-integer)
   - [4. Float (Decimal)](#4-float-decimal)
   - [5. Range](#5-range)
   - [6. Boolean (True/False)](#6-boolean-truefalse)
   - [7. Choice (Single Selection)](#7-choice-single-selection)
   - [8. Multiple Choice](#8-multiple-choice)
5. [Advanced Options](#advanced-options)
6. [Complete Example](#complete-example)

---

## Basic Structure

Every quiz JSON file must follow this structure:

```json
{
  "quiz": {
    "name": "Quiz Name",
    "subject": "Subject",
    "created_at": "YYYY-MM-DD",
    "description": "Quiz description"
  },
  "flashcards": [
    // Array of flashcard objects
  ]
}
```

---

## Quiz Metadata

The `quiz` object contains information about the entire quiz:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name of the quiz |
| `subject` | string | Yes | Subject category (e.g., "History", "Math", "French") |
| `created_at` | string | No | Creation date in YYYY-MM-DD format |
| `description` | string | No | Brief description of the quiz content |
| `image` | string | No | Image filename or path |
| `lang` | string | No | Primary language code (e.g., "en", "pl", "fr") |

---

## Flashcard Structure

Each flashcard has two main components: **question** and **answer**.

### Question Object

```json
{
  "question": {
    "title": "Short title",
    "text": "Full question text",
    "lang": "en",
    "difficulty": 1,
    "emoji": "📝",
    "image": "optional_image.png"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Short title/identifier for the question |
| `text` | string | Yes | Full question text shown to user |
| `lang` | string | No | Language code for this question |
| `difficulty` | integer | Yes | Difficulty level (1-5 typically) |
| `emoji` | string | No | Emoji to display with question |
| `image` | string | No | Image filename or path |
| `examples` | array | No | Array of example answers for user reference |

### Answer Object

```json
{
  "answer": {
    "text": "Correct answer",
    "type": "answer_type",
    "lang": "en",
    "options": null,
    "metadata": {}
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The correct answer |
| `type` | string | Yes | Answer type (see types below) |
| `lang` | string | No | Language code for answer |
| `options` | array/null | Conditional | Required for choice/multiple_choice types |
| `metadata` | object | No | Additional configuration options |

---

## Answer Types

### 1. Text (Free-form)

**Type:** `"text"`

For long, detailed text answers. Displays as a multi-line textarea.

**Example:**
```json
{
  "answer": {
    "text": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
    "type": "text",
    "lang": "en",
    "options": null,
    "metadata": {
      "min_words": 5,
      "hint": "Write a detailed answer (at least 5 words)",
      "rows": 4
    }
  }
}
```

**Metadata Options:**
- `min_words` (integer): Minimum number of words required
- `hint` (string): Help text shown to user
- `rows` (integer): Number of rows in textarea (default: 4)

---

### 2. Short Text

**Type:** `"short_text"`

For brief text answers (single line). Good for names, short phrases, etc.

**Example:**
```json
{
  "answer": {
    "text": "Paris",
    "type": "short_text",
    "lang": "en",
    "options": null,
    "metadata": {
      "max_length": 20,
      "case_sensitive": false,
      "hint": "Enter a short answer",
      "placeholder": "e.g., Paris"
    }
  }
}
```

**Metadata Options:**
- `max_length` (integer): Maximum character length
- `case_sensitive` (boolean): Whether answer is case-sensitive (default: false)
- `hint` (string): Help text
- `placeholder` (string): Placeholder text in input field

---

### 3. Integer

**Type:** `"integer"`

For whole number answers. Displays a number input field.

**Example:**
```json
{
  "answer": {
    "text": "1945",
    "type": "integer",
    "lang": "en",
    "options": null,
    "metadata": {
      "tolerance": 0,
      "hint": "Enter a whole number (year)",
      "placeholder": "e.g., 1945"
    }
  }
}
```

**Metadata Options:**
- `tolerance` (integer): Acceptable margin of error (e.g., ±2 years)
- `hint` (string): Help text
- `placeholder` (string): Placeholder text

---

### 4. Float (Decimal)

**Type:** `"float"`

For decimal number answers. Displays a number input with decimal support.

**Example:**
```json
{
  "answer": {
    "text": "3.14",
    "type": "float",
    "lang": "en",
    "options": null,
    "metadata": {
      "tolerance": 0.01,
      "hint": "Enter a decimal number",
      "decimal_places": 2,
      "step": 0.01,
      "placeholder": "e.g., 3.14"
    }
  }
}
```

**Metadata Options:**
- `tolerance` (float): Acceptable margin of error
- `decimal_places` (integer): Number of decimal places expected
- `step` (float): Step size for number input
- `hint` (string): Help text
- `placeholder` (string): Placeholder text

---

### 5. Range

**Type:** `"range"`

For numeric range answers (e.g., "5-10", "36.5 to 37.5").

**Example:**
```json
{
  "answer": {
    "text": "36.5-37.5",
    "type": "range",
    "lang": "en",
    "options": null,
    "metadata": {
      "hint": "Enter a range (e.g., 36.5-37.5)",
      "overlap_threshold": 0.5,
      "placeholder": "e.g., 36.5-37.5"
    }
  }
}
```

**Supported Range Formats:**
- `5-10`
- `5 to 10`
- `5..10`
- `from 5 to 10`

**Metadata Options:**
- `overlap_threshold` (float): Minimum overlap ratio for partial credit (0.0-1.0)
- `hint` (string): Help text
- `placeholder` (string): Placeholder text

---

### 6. Boolean (True/False)

**Type:** `"boolean"`

For true/false questions. Displays radio buttons.

**Example:**
```json
{
  "answer": {
    "text": "true",
    "type": "boolean",
    "lang": "en",
    "options": null,
    "metadata": {
      "true_label": "True",
      "false_label": "False",
      "hint": "Select True or False"
    }
  }
}
```

**Valid Answer Values:**
- True: `"true"`, `"t"`, `"yes"`, `"y"`, `"1"`
- False: `"false"`, `"f"`, `"no"`, `"n"`, `"0"`

**Metadata Options:**
- `true_label` (string): Custom label for true option (default: "True")
- `false_label` (string): Custom label for false option (default: "False")
- `hint` (string): Help text

---

### 7. Choice (Single Selection)

**Type:** `"choice"`

For single-choice questions. User selects one option from a list.

**Simple Format (Recommended):**
```json
{
  "answer": {
    "text": "Mars",
    "type": "choice",
    "lang": "en",
    "options": [
      "Venus",
      "Mars",
      "Jupiter",
      "Saturn"
    ],
    "metadata": {
      "case_sensitive": false,
      "hint": "Choose one option"
    }
  }
}
```

**Advanced Format (Value/Label Objects):**
```json
{
  "answer": {
    "text": "Au",
    "type": "choice",
    "lang": "en",
    "options": [
      {"value": "Au", "label": "Au (Gold)"},
      {"value": "Ag", "label": "Ag (Silver)"},
      {"value": "Fe", "label": "Fe (Iron)"},
      {"value": "Cu", "label": "Cu (Copper)"}
    ],
    "metadata": {
      "case_sensitive": true,
      "hint": "Choose one option"
    }
  }
}
```

**Metadata Options:**
- `case_sensitive` (boolean): Whether answer matching is case-sensitive
- `hint` (string): Help text

---

### 8. Multiple Choice

**Type:** `"multiple_choice"`

For questions where multiple options can be correct. User can select multiple options.

**Simple Format (Recommended):**
```json
{
  "answer": {
    "text": "Python,JavaScript,Java",
    "type": "multiple_choice",
    "lang": "en",
    "options": [
      "Python",
      "JavaScript",
      "HTML",
      "Java",
      "CSS"
    ],
    "metadata": {
      "case_sensitive": false,
      "order_matters": false,
      "min_selections": 1,
      "exact_count": 3,
      "hint": "Select all correct answers (3 options)"
    }
  }
}
```

**Advanced Format (Value/Label Objects):**
```json
{
  "answer": {
    "text": "He,Ne,Ar",
    "type": "multiple_choice",
    "lang": "en",
    "options": [
      {"value": "He", "label": "Helium (He)"},
      {"value": "Ne", "label": "Neon (Ne)"},
      {"value": "O", "label": "Oxygen (O)"},
      {"value": "Ar", "label": "Argon (Ar)"},
      {"value": "N", "label": "Nitrogen (N)"}
    ],
    "metadata": {
      "case_sensitive": false,
      "order_matters": false,
      "min_selections": 2,
      "exact_count": 3,
      "hint": "Select all correct answers (3 options)"
    }
  }
}
```

**Answer Format:** Comma-separated values in the `text` field.

**Metadata Options:**
- `case_sensitive` (boolean): Whether matching is case-sensitive
- `order_matters` (boolean): Whether the order of selections matters
- `min_selections` (integer): Minimum number of selections required
- `exact_count` (integer): Exact number of correct answers
- `hint` (string): Help text

---

## Advanced Options

### Options Format for Choice Questions

Both `choice` and `multiple_choice` types support two option formats:

#### 1. Simple String Array (Recommended)
```json
"options": ["Option 1", "Option 2", "Option 3"]
```

#### 2. Value/Label Objects (Advanced)
```json
"options": [
  {"value": "opt1", "label": "Option 1 Display"},
  {"value": "opt2", "label": "Option 2 Display"}
]
```

Use value/label objects when:
- You need a short value for comparison but detailed label for display
- Values need to be different from display text (e.g., chemical symbols)
- You want consistent internal values regardless of display language

### Language Support

Set language codes at different levels:
```json
{
  "quiz": {
    "lang": "en"  // Default for entire quiz
  },
  "flashcards": [
    {
      "question": {
        "lang": "pl"  // Override for this question
      },
      "answer": {
        "lang": "en"  // Language for answer
      }
    }
  ]
}
```

### Difficulty Levels

Use integers 1-5 (or higher) for difficulty:
- 1: Very Easy
- 2: Easy
- 3: Medium
- 4: Hard
- 5: Very Hard

---

## Complete Example

See the complete reference file at:
```
data/all_answer_types_reference.json
```

This file contains working examples of all 8 answer types with all common metadata options.

---

## Best Practices

1. **Always validate JSON syntax** before importing into SlayFlashcards
2. **Use simple string options** unless you specifically need value/label separation
3. **Provide helpful hints** in metadata to guide users
4. **Use appropriate answer types** - don't use `text` for simple yes/no questions
5. **Test your quizzes** after importing to ensure all questions work as expected
6. **Use consistent difficulty scaling** across your quizzes
7. **Add emojis** for better visual engagement
8. **Use appropriate case sensitivity** - usually `false` for most text answers

---

## Validation

Use Python to validate your JSON:
```bash
python3 -m json.tool your_quiz.json > /dev/null
```

Or use online validators:
- https://jsonlint.com/
- https://jsonformatter.curiousconcept.com/

---

## Troubleshooting

### Options not showing up?
- Check that `type` is `"choice"` or `"multiple_choice"`
- Ensure `options` array is properly formatted
- Verify JSON syntax is valid

### Answers not matching correctly?
- Check `case_sensitive` metadata setting
- Verify answer `text` field matches one of the options exactly
- For multiple choice, ensure comma-separated format

### Metadata not working?
- Ensure metadata keys are spelled correctly
- Check that metadata values are appropriate types (string, integer, boolean)
- Some metadata options only work with specific answer types

---

## Questions or Issues?

If you encounter problems or have questions about quiz creation, please:
1. Check the reference file: `data/all_answer_types_reference.json`
2. Validate your JSON syntax
3. Review the answer type specific sections above
4. Check existing quiz files in the `data/` directory for examples

---

*Last updated: 2025-10-14*
