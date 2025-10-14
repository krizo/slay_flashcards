# Answer Format Hints - Quick Reference

## Overview

The answer metadata system helps users understand what format their answer should be in. This is displayed as a hint before they answer the question.

## How It Works

1. **Flashcard contains metadata** - The `answer.metadata` field contains guidance information
2. **Hint is generated** - `FlashcardDisplay.tsx` generates a hint from metadata
3. **User sees hint** - Format hint displayed with 💡 icon above the answer input
4. **Input configured** - `AnswerInput.tsx` uses metadata to configure the input field

## Quick Metadata Examples

### Text (Long Answer)
```json
{
  "metadata": {
    "hint": "Describe the process in 2-3 sentences",
    "rows": 4,
    "min_words": 15
  }
}
```
**User sees:** "Describe the process in 2-3 sentences"

### Short Text
```json
{
  "metadata": {
    "hint": "Enter the city name",
    "placeholder": "e.g., Warsaw",
    "case_sensitive": false
  }
}
```
**User sees:** "Enter the city name"

### Integer
```json
{
  "metadata": {
    "hint": "Enter a whole number",
    "min": 0,
    "max": 100,
    "example": "42"
  }
}
```
**User sees:** "Enter a whole number"

### Float
```json
{
  "metadata": {
    "hint": "Enter a number with exactly 2 decimal places",
    "decimal_places": 2,
    "step": 0.01,
    "example": "3.14"
  }
}
```
**User sees:** "Enter a number with exactly 2 decimal places"

### Range (Slider)
```json
{
  "metadata": {
    "min": 36.0,
    "max": 37.5,
    "step": 0.1,
    "hint": "Choose temperature in range 36.0-37.5°C"
  }
}
```
**User sees:** "Choose temperature in range 36.0-37.5°C"

### Boolean
```json
{
  "metadata": {
    "true_label": "Yes",
    "false_label": "No",
    "hint": "Select Yes or No"
  }
}
```
**User sees:** "Select Yes or No"

### Choice (Single Selection)
```json
{
  "metadata": {
    "hint": "Select the best answer"
  }
}
```
**User sees:** "Select the best answer"

### Multiple Choice
```json
{
  "metadata": {
    "hint": "Select all correct answers (3 options)",
    "exact_count": 3
  }
}
```
**User sees:** "Select all correct answers (3 options)"

## Most Important Metadata Fields

### All Types
- **`hint`** (string) - **MOST IMPORTANT** - Custom message shown to user

### Numeric Types (integer, float, range)
- **`min`** (number) - Minimum allowed value
- **`max`** (number) - Maximum allowed value
- **`step`** (number) - Increment step
- **`example`** (string) - Example value

### Float Specific
- **`decimal_places`** (number) - Required decimal places
- **`unit`** (string) - Unit of measurement (e.g., "kg", "°C")

### Text Types (text, short_text)
- **`placeholder`** (string) - Input placeholder
- **`case_sensitive`** (boolean) - Case-sensitive matching
- **`max_length`** (number) - Maximum character count

### Boolean
- **`true_label`** (string) - Label for true option
- **`false_label`** (string) - Label for false option

### Multiple Choice
- **`exact_count`** (number) - Exact number of required selections
- **`min_selections`** (number) - Minimum selections
- **`max_selections`** (number) - Maximum selections

## Best Practice: Always Set `hint`

The `hint` field is the most important. It's displayed directly to the user.

### Good Hints
```json
{"hint": "Enter a year (4 digits)"}
{"hint": "Write 2-3 sentences explaining the concept"}
{"hint": "Type the capital city name"}
{"hint": "Select all programming languages"}
{"hint": "Choose a temperature between 36-38°C"}
```

### Auto-Generated Hints

If you don't provide a custom `hint`, the system generates one from:
- Answer length (word count, letter count)
- Answer type (text, integer, float, etc.)
- Metadata constraints (range, decimal places)

Example auto-generated hint:
> "7 letters • type: float • 2 decimal places • e.g., 3.14"

## Implementation Files

- **`/docs/ANSWER_METADATA.md`** - Complete documentation
- **`frontend/src/components/sessions/FlashcardDisplay.tsx:121-177`** - Hint generation logic
- **`frontend/src/components/sessions/AnswerInput.tsx`** - Input configuration
- **`api/api_schemas.py:265-273`** - API schema definition
- **`scripts/create_demo_data.py:84-193`** - Example quiz with all metadata types

## Testing

To see all answer types with metadata in action:

1. Run demo data script (creates answer types quiz):
   ```bash
   python3 scripts/create_demo_data.py
   ```

2. Login as Emila or Kriz

3. Find quiz "Test wszystkich typów odpowiedzi" 🧪

4. Start a learning or test session

5. Observe the format hints for each answer type

## Adding Metadata to Existing Flashcards

### Via API
```python
flashcard_repo.update(
    flashcard,
    answer_metadata={
        "hint": "Enter a whole number between 1 and 100",
        "min": 1,
        "max": 100
    }
)
```

### Via Direct SQL
```sql
UPDATE flashcard
SET answer_metadata = '{"hint": "Enter a whole number", "min": 1, "max": 100}'
WHERE id = 123;
```

## Common Patterns

### Numeric Answer with Range
```json
{
  "hint": "Enter a value between X and Y",
  "min": X,
  "max": Y
}
```

### Text Answer with Length Requirement
```json
{
  "hint": "Write 2-3 sentences (min 20 words)",
  "rows": 4,
  "min_words": 20
}
```

### Case-Insensitive Short Answer
```json
{
  "hint": "Type the name (not case sensitive)",
  "case_sensitive": false,
  "placeholder": "e.g., Example"
}
```

### Multiple Choice with Count
```json
{
  "hint": "Select exactly 3 correct options",
  "exact_count": 3
}
```

## Translation

For Polish content, translate metadata:

```json
{
  "hint": "Wpisz liczbę całkowitą od 1 do 10",
  "placeholder": "np. 5",
  "example": "7"
}
```

## Summary

**Key Points:**
1. ✓ Always provide a custom `hint` field
2. ✓ Set appropriate constraints (min/max, decimal_places, etc.)
3. ✓ Use placeholders for text inputs
4. ✓ Translate metadata for non-English content
5. ✓ Test with the answer types demo quiz

**Result:** Users know exactly what format is expected before they answer!
