#!/usr/bin/env python3
"""
Script to convert quiz JSON files to the current format
"""
import json
import sys
from pathlib import Path

def convert_options(options, answer_text):
    """Convert old options format to new format"""
    if not options:
        return None

    # Handle old format: {"key": "A", "text": "..."}
    # Convert to new format: {"value": "a", "label": "..."}
    new_options = []
    for i, opt in enumerate(options):
        if "key" in opt and "text" in opt:
            # Old format
            new_options.append({
                "value": chr(97 + i),  # a, b, c, d...
                "label": opt["text"]
            })
        elif "text" in opt and "value" not in opt:
            # Multiple choice without key/value
            new_options.append({
                "value": chr(97 + i),
                "label": opt["text"]
            })
        else:
            # Already in new format
            new_options.append(opt)

    return new_options

def convert_answer_text_for_choice(options, old_text):
    """Convert answer text to use new value format"""
    if not options:
        return old_text

    # Try to find matching option
    for opt in options:
        if "label" in opt and opt["label"] == old_text:
            return opt["value"]
        if "text" in opt and opt["text"] == old_text:
            # Find the index
            idx = next((i for i, o in enumerate(options) if o.get("text") == old_text), None)
            if idx is not None:
                return chr(97 + idx)

    return old_text

def convert_answer_text_for_multiple_choice(options, old_text):
    """Convert comma-separated answer text to new format"""
    if not options or not old_text:
        return old_text

    # Split by comma
    parts = [p.strip() for p in old_text.split(",")]
    new_parts = []

    for part in parts:
        # Find matching option
        found = False
        for i, opt in enumerate(options):
            label = opt.get("label") or opt.get("text")
            if label == part:
                new_parts.append(chr(97 + i))
                found = True
                break
        if not found:
            new_parts.append(part)

    return ",".join(new_parts)

def add_hints_and_examples(flashcard):
    """Add helpful hints and examples based on content"""
    answer = flashcard["answer"]
    question = flashcard["question"]
    answer_type = answer.get("type", "text")

    # Initialize metadata if not exists
    if "metadata" not in answer or not answer["metadata"]:
        answer["metadata"] = {}

    metadata = answer["metadata"]

    # Add examples to question if they exist in metadata
    if "examples" in metadata and "examples" not in question:
        question["examples"] = metadata["examples"]
        # Remove from answer metadata
        del metadata["examples"]

    # Add hints based on type
    if "hint" not in metadata:
        if answer_type == "text":
            metadata["hint"] = f"Opisz {question['title'].lower()} (min {metadata.get('min_words', 3)} słowa)"
            if "rows" not in metadata:
                metadata["rows"] = 3
        elif answer_type == "short_text":
            metadata["hint"] = "Wpisz krótką odpowiedź"
            if "placeholder" not in metadata:
                metadata["placeholder"] = "np. ..."
        elif answer_type == "integer":
            metadata["hint"] = "Wpisz liczbę całkowitą"
            if "placeholder" not in metadata:
                metadata["placeholder"] = f"np. {answer['text']}"
        elif answer_type == "float":
            metadata["hint"] = "Wpisz liczbę dziesiętną"
            if "decimal_places" not in metadata:
                # Try to detect decimal places from answer
                if "." in answer["text"]:
                    decimal_places = len(answer["text"].split(".")[1])
                    metadata["decimal_places"] = decimal_places
                    metadata["step"] = 10 ** (-decimal_places)
        elif answer_type == "boolean":
            metadata["true_label"] = "Prawda"
            metadata["false_label"] = "Fałsz"
            metadata["hint"] = "Wybierz Prawda lub Fałsz"
        elif answer_type == "choice":
            metadata["hint"] = "Wybierz jedną odpowiedź"
        elif answer_type == "multiple_choice":
            # Count expected answers
            answer_count = len(answer["text"].split(","))
            metadata["hint"] = f"Zaznacz wszystkie poprawne odpowiedzi ({answer_count} opcje)"
            if "exact_count" not in metadata:
                metadata["exact_count"] = answer_count

    # Clean up old metadata fields
    fields_to_remove = ["expects_explanation", "tolerance", "overlap_threshold", "order_matters"]
    for field in fields_to_remove:
        if field in metadata:
            del metadata[field]

    return flashcard

def convert_flashcard(flashcard):
    """Convert a single flashcard to new format"""
    answer = flashcard["answer"]
    question = flashcard["question"]

    # Convert boolean answers
    if answer.get("type") == "boolean":
        if answer["text"] == "True":
            answer["text"] = "true"
        elif answer["text"] == "False":
            answer["text"] = "false"

    # Convert choice options
    if answer.get("type") in ["choice", "multiple_choice"]:
        old_options = answer.get("options", [])
        if old_options:
            new_options = convert_options(old_options, answer["text"])
            answer["options"] = new_options

            # Convert answer text
            if answer.get("type") == "choice":
                answer["text"] = convert_answer_text_for_choice(new_options, answer["text"])
            elif answer.get("type") == "multiple_choice":
                answer["text"] = convert_answer_text_for_multiple_choice(new_options, answer["text"])

    # Add hints and examples
    flashcard = add_hints_and_examples(flashcard)

    return flashcard

def convert_quiz_file(input_file, output_file=None):
    """Convert quiz file to new format"""
    if output_file is None:
        output_file = input_file

    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert all flashcards
    for flashcard in data["flashcards"]:
        convert_flashcard(flashcard)

    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Converted {len(data['flashcards'])} flashcards")
    print(f"📝 Saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_quiz_format.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_quiz_file(input_file, output_file)
