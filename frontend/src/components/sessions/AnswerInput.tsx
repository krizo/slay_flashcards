import { AnswerData } from '../../types';

interface AnswerInputProps {
    answer: AnswerData;
    userAnswer: string;
    onAnswerChange: (answer: string) => void;
    disabled?: boolean;
}

function AnswerInput({ answer, userAnswer, onAnswerChange, disabled = false }: AnswerInputProps) {
    const { type, options, metadata } = answer;

    // Boolean/True-False questions
    if (type === 'boolean') {
        const trueLabel = metadata?.true_label || 'True';
        const falseLabel = metadata?.false_label || 'False';

        return (
            <div className="answer-input answer-input--boolean">
                <button
                    type="button"
                    className={`boolean-button ${userAnswer === 'true' ? 'boolean-button--selected' : ''}`}
                    onClick={() => onAnswerChange('true')}
                    disabled={disabled}
                >
                    ✓ {trueLabel}
                </button>
                <button
                    type="button"
                    className={`boolean-button ${userAnswer === 'false' ? 'boolean-button--selected' : ''}`}
                    onClick={() => onAnswerChange('false')}
                    disabled={disabled}
                >
                    ✗ {falseLabel}
                </button>
            </div>
        );
    }

    // Single choice (radio buttons)
    if (type === 'choice' && options && options.length > 0) {
        return (
            <div className="answer-input answer-input--choice">
                {options.map((option, index) => {
                    // Support both string options and {value, label} objects
                    const optionValue = typeof option === 'string' ? option : option.value;
                    const optionLabel = typeof option === 'string' ? option : option.label;

                    return (
                        <label key={index} className="choice-option">
                            <input
                                type="radio"
                                name="answer-choice"
                                value={optionValue}
                                checked={userAnswer === optionValue}
                                onChange={(e) => onAnswerChange(e.target.value)}
                                disabled={disabled}
                            />
                            <span className="choice-label">{optionLabel}</span>
                        </label>
                    );
                })}
            </div>
        );
    }

    // Multiple choice (checkboxes)
    if (type === 'multiple_choice' && options && options.length > 0) {
        const selectedValues = userAnswer ? userAnswer.split(',').filter(v => v) : [];

        const handleCheckboxChange = (value: string) => {
            const newSelection = selectedValues.includes(value)
                ? selectedValues.filter(v => v !== value)
                : [...selectedValues, value];
            onAnswerChange(newSelection.join(','));
        };

        return (
            <div className="answer-input answer-input--multiple-choice">
                {options.map((option, index) => {
                    // Support both string options and {value, label} objects
                    const optionValue = typeof option === 'string' ? option : option.value;
                    const optionLabel = typeof option === 'string' ? option : option.label;

                    return (
                        <label key={index} className="choice-option">
                            <input
                                type="checkbox"
                                value={optionValue}
                                checked={selectedValues.includes(optionValue)}
                                onChange={() => handleCheckboxChange(optionValue)}
                                disabled={disabled}
                            />
                            <span className="choice-label">{optionLabel}</span>
                        </label>
                    );
                })}
            </div>
        );
    }

    // Range input for numbers
    if (type === 'range' && metadata?.min !== undefined && metadata?.max !== undefined) {
        return (
            <div className="answer-input answer-input--range">
                <input
                    type="range"
                    min={metadata.min}
                    max={metadata.max}
                    step={metadata.step || 1}
                    value={userAnswer || metadata.min}
                    onChange={(e) => onAnswerChange(e.target.value)}
                    disabled={disabled}
                    className="range-slider"
                />
                <div className="range-value">{userAnswer || metadata.min}</div>
            </div>
        );
    }

    // Integer input
    if (type === 'integer') {
        return (
            <input
                type="number"
                className="answer-input answer-input--integer"
                placeholder={metadata?.placeholder || "Enter a whole number..."}
                value={userAnswer}
                onChange={(e) => onAnswerChange(e.target.value)}
                disabled={disabled}
                step="1"
            />
        );
    }

    // Float input
    if (type === 'float') {
        const step = metadata?.step || 0.01;
        const decimalPlaces = metadata?.decimal_places;

        return (
            <input
                type="number"
                className="answer-input answer-input--float"
                placeholder={metadata?.placeholder || "Enter a number..."}
                value={userAnswer}
                onChange={(e) => onAnswerChange(e.target.value)}
                disabled={disabled}
                step={step}
                {...(decimalPlaces && { step: `0.${'0'.repeat(decimalPlaces - 1)}1` })}
            />
        );
    }

    // Short text (single line)
    if (type === 'short_text') {
        const maxLength = metadata?.max_length || 100;

        return (
            <input
                type="text"
                className="answer-input answer-input--short-text"
                placeholder={metadata?.placeholder || "Type your answer..."}
                value={userAnswer}
                onChange={(e) => onAnswerChange(e.target.value)}
                disabled={disabled}
                maxLength={maxLength}
            />
        );
    }

    // Default: long text (textarea)
    return (
        <textarea
            className="answer-input answer-input--text"
            placeholder={metadata?.placeholder || "Type your answer here..."}
            value={userAnswer}
            onChange={(e) => onAnswerChange(e.target.value)}
            disabled={disabled}
            rows={metadata?.rows || 3}
        />
    );
}

export default AnswerInput;
