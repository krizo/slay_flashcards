import React, {useState} from 'react';
import {AnswerData} from '../types';

interface AnswerInputProps {
    answer: AnswerData;
    userAnswer: string | string[];
    onAnswerChange: (value: string | string[]) => void;
}

/**
 * AnswerInput - Component for displaying different answer input types
 *
 * Supports 8 answer types:
 * - text: Free-form text input
 * - short_text: Short text input
 * - integer: Numeric integer input
 * - float: Floating-point number input
 * - range: Numeric range (not directly input, but validated)
 * - boolean: True/False selection
 * - choice: Single choice from options
 * - multiple_choice: Multiple selections from options
 */
const AnswerInput: React.FC<AnswerInputProps> = ({answer, userAnswer, onAnswerChange}) => {
    const [selectedOptions, setSelectedOptions] = useState<string[]>(
        Array.isArray(userAnswer) ? userAnswer : []
    );

    const handleTextChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        onAnswerChange(event.target.value);
    };

    const handleNumberChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        onAnswerChange(event.target.value);
    };


    const handleChoiceChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        onAnswerChange(event.target.value);
    };

    const handleMultipleChoiceChange = (option: string) => {
        const newSelected = selectedOptions.includes(option)
            ? selectedOptions.filter(opt => opt !== option)
            : [...selectedOptions, option];

        setSelectedOptions(newSelected);
        onAnswerChange(newSelected);
    };

    // Render different input based on answer type
    switch (answer.type) {
        case 'text':
            return (
                <textarea
                    className="flashcard-input-field flashcard-textarea"
                    placeholder="Type your answer here..."
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleTextChange}
                    rows={4}
                />
            );

        case 'short_text':
            return (
                <input
                    type="text"
                    className="flashcard-input-field"
                    placeholder="Type your answer..."
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleTextChange}
                />
            );

        case 'integer':
            return (
                <input
                    type="number"
                    step="1"
                    className="flashcard-input-field"
                    placeholder="Enter a whole number..."
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleNumberChange}
                />
            );

        case 'float':
            return (
                <input
                    type="number"
                    step="0.01"
                    className="flashcard-input-field"
                    placeholder="Enter a number..."
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleNumberChange}
                />
            );

        case 'range':
            return (
                <input
                    type="number"
                    step="0.01"
                    className="flashcard-input-field"
                    placeholder={`Enter a number (${answer.metadata?.min || '?'} - ${answer.metadata?.max || '?'})...`}
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleNumberChange}
                />
            );

        case 'boolean':
            return (
                <div className="flashcard-option-group">
                    <label>
                        <input
                            type="radio"
                            name="boolean-answer"
                            value="true"
                            checked={userAnswer === 'true'}
                            onChange={handleChoiceChange}
                        />
                        <span>True</span>
                    </label>
                    <label>
                        <input
                            type="radio"
                            name="boolean-answer"
                            value="false"
                            checked={userAnswer === 'false'}
                            onChange={handleChoiceChange}
                        />
                        <span>False</span>
                    </label>
                </div>
            );

        case 'choice':
            return (
                <div className="flashcard-option-group">
                    {answer.options?.map((option, index) => (
                        <label key={index}>
                            <input
                                type="radio"
                                name="choice-answer"
                                value={option.value}
                                checked={userAnswer === option.value}
                                onChange={handleChoiceChange}
                            />
                            <span>{option.label}</span>
                        </label>
                    ))}
                </div>
            );

        case 'multiple_choice':
            return (
                <div className="flashcard-option-group">
                    {answer.options?.map((option, index) => (
                        <label key={index}>
                            <input
                                type="checkbox"
                                value={option.value}
                                checked={selectedOptions.includes(option.value)}
                                onChange={() => handleMultipleChoiceChange(option.value)}
                            />
                            <span>{option.label}</span>
                        </label>
                    ))}
                </div>
            );

        default:
            return (
                <input
                    type="text"
                    className="flashcard-input-field"
                    placeholder="Type your answer..."
                    value={typeof userAnswer === 'string' ? userAnswer : ''}
                    onChange={handleTextChange}
                />
            );
    }
};

export default AnswerInput;
