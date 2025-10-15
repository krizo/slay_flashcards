import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { QuestionData, AnswerData, AnswerType } from '../../types';
import './FlashcardEditor.css';

export interface FlashcardEditorData {
    question: QuestionData;
    answer: AnswerData;
}

interface FlashcardEditorProps {
    data: FlashcardEditorData;
    onChange: (data: FlashcardEditorData) => void;
    disabled?: boolean;
    showValidation?: boolean;
}

const MAX_IMAGE_SIZE = 102400; // 100KB

const ANSWER_TYPES: { value: AnswerType; label: string }[] = [
    { value: 'text', label: 'Text' },
    { value: 'short_text', label: 'Short Text' },
    { value: 'integer', label: 'Integer' },
    { value: 'float', label: 'Float' },
    { value: 'range', label: 'Range' },
    { value: 'boolean', label: 'Boolean (True/False)' },
    { value: 'choice', label: 'Single Choice' },
    { value: 'multiple_choice', label: 'Multiple Choice' },
];

const DIFFICULTY_OPTIONS = [
    { value: 1, label: '1 - Very Easy', emoji: '😊' },
    { value: 2, label: '2 - Easy', emoji: '🙂' },
    { value: 3, label: '3 - Medium', emoji: '😐' },
    { value: 4, label: '4 - Hard', emoji: '😰' },
    { value: 5, label: '5 - Very Hard', emoji: '😱' },
];

export const FlashcardEditor: React.FC<FlashcardEditorProps> = ({
    data,
    onChange,
    disabled = false,
    showValidation = false,
}) => {
    const { t } = useTranslation();
    const questionImageRef = useRef<HTMLInputElement>(null);
    const [imageError, setImageError] = useState<string | null>(null);
    const [newOption, setNewOption] = useState('');
    const [newExample, setNewExample] = useState('');

    // Handlers for Question fields
    const handleQuestionChange = (field: keyof QuestionData, value: any) => {
        onChange({
            ...data,
            question: {
                ...data.question,
                [field]: value,
            },
        });
    };

    // Handlers for Answer fields
    const handleAnswerChange = (field: keyof AnswerData, value: any) => {
        onChange({
            ...data,
            answer: {
                ...data.answer,
                [field]: value,
            },
        });
    };

    // Handle answer type change
    const handleAnswerTypeChange = (type: AnswerType) => {
        // Reset options and metadata when changing type
        let options = null;
        let metadata = null;

        if (type === 'choice' || type === 'multiple_choice') {
            options = [];
        }

        if (type === 'short_text' || type === 'text') {
            metadata = { case_sensitive: false };
        } else if (type === 'range') {
            metadata = { min: 0, max: 100 };
        } else if (type === 'integer' || type === 'float') {
            metadata = {};
        }

        onChange({
            ...data,
            answer: {
                ...data.answer,
                type,
                options,
                metadata,
            },
        });
    };

    // Handle question image upload
    const handleQuestionImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setImageError(null);

        if (!file.type.startsWith('image/')) {
            setImageError('Invalid image format');
            return;
        }

        if (file.size > MAX_IMAGE_SIZE) {
            setImageError('Image is too large (max 100KB)');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            const base64String = event.target?.result as string;
            const base64Data = base64String.split(',')[1];
            handleQuestionChange('image', base64Data);
        };
        reader.onerror = () => {
            setImageError('Failed to read image file');
        };
        reader.readAsDataURL(file);
    };

    const handleRemoveQuestionImage = () => {
        handleQuestionChange('image', null);
        if (questionImageRef.current) {
            questionImageRef.current.value = '';
        }
        setImageError(null);
    };

    const getQuestionImagePreviewUrl = () => {
        if (!data.question.image) return null;
        return `data:image/png;base64,${data.question.image}`;
    };

    // Handle options for choice/multiple_choice
    const handleAddOption = () => {
        if (!newOption.trim()) return;
        const currentOptions = data.answer.options || [];
        handleAnswerChange('options', [...currentOptions, newOption.trim()]);
        setNewOption('');
    };

    const handleRemoveOption = (index: number) => {
        const currentOptions = data.answer.options || [];
        handleAnswerChange('options', currentOptions.filter((_, i) => i !== index));
    };

    // Handle examples
    const handleAddExample = () => {
        if (!newExample.trim()) return;
        const currentExamples = data.question.examples || [];
        handleQuestionChange('examples', [...currentExamples, newExample.trim()]);
        setNewExample('');
    };

    const handleRemoveExample = (index: number) => {
        const currentExamples = data.question.examples || [];
        handleQuestionChange('examples', currentExamples.filter((_, i) => i !== index));
    };

    // Handle metadata fields
    const handleMetadataChange = (key: string, value: any) => {
        handleAnswerChange('metadata', {
            ...(data.answer.metadata || {}),
            [key]: value,
        });
    };

    const isQuestionTitleValid = data.question.title.trim().length > 0;
    const isQuestionTextValid = data.question.text.trim().length > 0;
    const isAnswerTextValid = data.answer.text.trim().length > 0;

    return (
        <div className="flashcard-editor">
            {/* Question Section */}
            <div className="editor-section">
                <h3 className="editor-section-title">{t('flashcardEditor.questionSection')}</h3>

                {/* Question Title */}
                <div className="form-group">
                    <label htmlFor="question-title" className="form-label required">
                        {t('flashcardEditor.questionTitle')}
                    </label>
                    <input
                        type="text"
                        id="question-title"
                        className={`form-input ${showValidation && !isQuestionTitleValid ? 'invalid' : ''}`}
                        value={data.question.title}
                        onChange={(e) => handleQuestionChange('title', e.target.value)}
                        placeholder={t('flashcardEditor.questionTitlePlaceholder')}
                        disabled={disabled}
                        required
                    />
                    {showValidation && !isQuestionTitleValid && (
                        <span className="form-error">{t('flashcardEditor.questionTitleRequired')}</span>
                    )}
                </div>

                {/* Question Text */}
                <div className="form-group">
                    <label htmlFor="question-text" className="form-label required">
                        {t('flashcardEditor.questionText')}
                    </label>
                    <textarea
                        id="question-text"
                        className={`form-input form-textarea ${showValidation && !isQuestionTextValid ? 'invalid' : ''}`}
                        value={data.question.text}
                        onChange={(e) => handleQuestionChange('text', e.target.value)}
                        placeholder={t('flashcardEditor.questionTextPlaceholder')}
                        rows={4}
                        disabled={disabled}
                        required
                    />
                    {showValidation && !isQuestionTextValid && (
                        <span className="form-error">{t('flashcardEditor.questionTextRequired')}</span>
                    )}
                </div>

                {/* Question Language & Emoji & Difficulty */}
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="question-lang" className="form-label">
                            {t('flashcardEditor.questionLanguage')}
                        </label>
                        <input
                            type="text"
                            id="question-lang"
                            className="form-input"
                            value={data.question.lang || ''}
                            onChange={(e) => handleQuestionChange('lang', e.target.value || null)}
                            placeholder="en, es, fr..."
                            disabled={disabled}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="question-emoji" className="form-label">
                            {t('flashcardEditor.emoji')}
                        </label>
                        <input
                            type="text"
                            id="question-emoji"
                            className="form-input"
                            value={data.question.emoji}
                            onChange={(e) => handleQuestionChange('emoji', e.target.value)}
                            placeholder="📝"
                            disabled={disabled}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="question-difficulty" className="form-label">
                            {t('flashcardEditor.difficulty')}
                        </label>
                        <select
                            id="question-difficulty"
                            className="form-input form-select"
                            value={data.question.difficulty || ''}
                            onChange={(e) => handleQuestionChange('difficulty', e.target.value ? parseInt(e.target.value) : null)}
                            disabled={disabled}
                        >
                            <option value="">{t('flashcardEditor.noDifficulty')}</option>
                            {DIFFICULTY_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.emoji} {opt.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Question Image */}
                <div className="form-group">
                    <label className="form-label">{t('flashcardEditor.questionImage')}</label>
                    <p className="form-hint">{t('flashcardEditor.imageDescription')}</p>

                    {data.question.image ? (
                        <div className="image-preview-container">
                            <img
                                src={getQuestionImagePreviewUrl() || ''}
                                alt="Question preview"
                                className="image-preview"
                            />
                            <button
                                type="button"
                                className="image-remove-button"
                                onClick={handleRemoveQuestionImage}
                                disabled={disabled}
                            >
                                {t('quizEditor.removeImage')}
                            </button>
                        </div>
                    ) : (
                        <div className="image-upload-area">
                            <input
                                ref={questionImageRef}
                                type="file"
                                id="question-image"
                                accept="image/*"
                                onChange={handleQuestionImageChange}
                                disabled={disabled}
                                className="image-input"
                            />
                            <label htmlFor="question-image" className="image-upload-label">
                                {t('quizEditor.uploadImage')}
                            </label>
                        </div>
                    )}

                    {imageError && (
                        <span className="form-error">{imageError}</span>
                    )}
                </div>

                {/* Examples */}
                <div className="form-group">
                    <label className="form-label">{t('flashcardEditor.examples')}</label>
                    <p className="form-hint">{t('flashcardEditor.examplesHint')}</p>

                    <div className="list-container">
                        {data.question.examples && data.question.examples.length > 0 && (
                            <div className="list-items">
                                {data.question.examples.map((example, index) => (
                                    <div key={index} className="list-item">
                                        <span className="list-item-text">{example}</span>
                                        <button
                                            type="button"
                                            className="list-item-remove"
                                            onClick={() => handleRemoveExample(index)}
                                            disabled={disabled}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="list-add-form">
                            <input
                                type="text"
                                className="form-input"
                                value={newExample}
                                onChange={(e) => setNewExample(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        handleAddExample();
                                    }
                                }}
                                placeholder={t('flashcardEditor.addExample')}
                                disabled={disabled}
                            />
                            <button
                                type="button"
                                className="list-add-button"
                                onClick={handleAddExample}
                                disabled={disabled || !newExample.trim()}
                            >
                                +
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Answer Section */}
            <div className="editor-section">
                <h3 className="editor-section-title">{t('flashcardEditor.answerSection')}</h3>

                {/* Answer Type */}
                <div className="form-group">
                    <label htmlFor="answer-type" className="form-label required">
                        {t('flashcardEditor.answerType')}
                    </label>
                    <select
                        id="answer-type"
                        className="form-input form-select"
                        value={data.answer.type}
                        onChange={(e) => handleAnswerTypeChange(e.target.value as AnswerType)}
                        disabled={disabled}
                        required
                    >
                        {ANSWER_TYPES.map(type => (
                            <option key={type.value} value={type.value}>
                                {type.label}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Answer Text */}
                <div className="form-group">
                    <label htmlFor="answer-text" className="form-label required">
                        {t('flashcardEditor.answerText')}
                    </label>
                    <textarea
                        id="answer-text"
                        className={`form-input form-textarea ${showValidation && !isAnswerTextValid ? 'invalid' : ''}`}
                        value={data.answer.text}
                        onChange={(e) => handleAnswerChange('text', e.target.value)}
                        placeholder={t('flashcardEditor.answerTextPlaceholder')}
                        rows={3}
                        disabled={disabled}
                        required
                    />
                    {showValidation && !isAnswerTextValid && (
                        <span className="form-error">{t('flashcardEditor.answerTextRequired')}</span>
                    )}
                </div>

                {/* Answer Language */}
                <div className="form-group">
                    <label htmlFor="answer-lang" className="form-label">
                        {t('flashcardEditor.answerLanguage')}
                    </label>
                    <input
                        type="text"
                        id="answer-lang"
                        className="form-input"
                        value={data.answer.lang || ''}
                        onChange={(e) => handleAnswerChange('lang', e.target.value || null)}
                        placeholder="en, es, fr..."
                        disabled={disabled}
                    />
                </div>

                {/* Options for choice/multiple_choice */}
                {(data.answer.type === 'choice' || data.answer.type === 'multiple_choice') && (
                    <div className="form-group">
                        <label className="form-label required">
                            {t('flashcardEditor.answerOptions')}
                        </label>
                        <p className="form-hint">{t('flashcardEditor.answerOptionsHint')}</p>

                        <div className="list-container">
                            {data.answer.options && data.answer.options.length > 0 && (
                                <div className="list-items">
                                    {data.answer.options.map((option, index) => (
                                        <div key={index} className="list-item">
                                            <span className="list-item-text">
                                                {typeof option === 'string' ? option : option.label}
                                            </span>
                                            <button
                                                type="button"
                                                className="list-item-remove"
                                                onClick={() => handleRemoveOption(index)}
                                                disabled={disabled}
                                            >
                                                ✕
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="list-add-form">
                                <input
                                    type="text"
                                    className="form-input"
                                    value={newOption}
                                    onChange={(e) => setNewOption(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') {
                                            e.preventDefault();
                                            handleAddOption();
                                        }
                                    }}
                                    placeholder={t('flashcardEditor.addOption')}
                                    disabled={disabled}
                                />
                                <button
                                    type="button"
                                    className="list-add-button"
                                    onClick={handleAddOption}
                                    disabled={disabled || !newOption.trim()}
                                >
                                    +
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Metadata for text/short_text */}
                {(data.answer.type === 'text' || data.answer.type === 'short_text') && (
                    <div className="form-group">
                        <label className="checkbox-label">
                            <input
                                type="checkbox"
                                checked={data.answer.metadata?.case_sensitive || false}
                                onChange={(e) => handleMetadataChange('case_sensitive', e.target.checked)}
                                disabled={disabled}
                            />
                            <span className="checkbox-text">
                                {t('flashcardEditor.caseSensitive')}
                            </span>
                        </label>
                    </div>
                )}

                {/* Metadata for range */}
                {data.answer.type === 'range' && (
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="range-min" className="form-label">
                                {t('flashcardEditor.rangeMin')}
                            </label>
                            <input
                                type="number"
                                id="range-min"
                                className="form-input"
                                value={data.answer.metadata?.min || 0}
                                onChange={(e) => handleMetadataChange('min', parseFloat(e.target.value))}
                                disabled={disabled}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="range-max" className="form-label">
                                {t('flashcardEditor.rangeMax')}
                            </label>
                            <input
                                type="number"
                                id="range-max"
                                className="form-input"
                                value={data.answer.metadata?.max || 100}
                                onChange={(e) => handleMetadataChange('max', parseFloat(e.target.value))}
                                disabled={disabled}
                            />
                        </div>
                    </div>
                )}

                {/* Metadata for float */}
                {data.answer.type === 'float' && (
                    <div className="form-group">
                        <label htmlFor="decimal-places" className="form-label">
                            {t('flashcardEditor.decimalPlaces')}
                        </label>
                        <input
                            type="number"
                            id="decimal-places"
                            className="form-input"
                            value={data.answer.metadata?.decimal_places || 2}
                            onChange={(e) => handleMetadataChange('decimal_places', parseInt(e.target.value))}
                            min="0"
                            max="10"
                            disabled={disabled}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};
