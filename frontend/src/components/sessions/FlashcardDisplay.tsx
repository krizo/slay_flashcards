import { useTranslation } from 'react-i18next';
import { FlashcardData, SessionFeedback } from '../../types';
import AnswerInput from './AnswerInput';
import './AnswerInput.css';

interface FlashcardDisplayProps {
    flashcard: FlashcardData | null;
    feedback: SessionFeedback | null;
    userAnswer: string;
    showAnswer: boolean;
    totalFlashcards: number;
    flashcardsCompleted: number;
    quizName: string;
    mode: string;
    isSubmitting: boolean;
    onUserAnswerChange: (answer: string) => void;
    onSpeak: (text: string, lang?: string | null) => void;
    onSubmitAnswer: () => void;
    onRevealAnswer: () => void;
    onNextFlashcard: () => void;
}

// Helper function to get flag emoji based on language code
function getLanguageFlag(lang: string | null | undefined): string {
    const flagMap: Record<string, string> = {
        'en': '🇬🇧',
        'es': '🇪🇸',
        'fr': '🇫🇷',
        'de': '🇩🇪',
        'it': '🇮🇹',
        'pt': '🇵🇹',
        'ru': '🇷🇺',
        'ja': '🇯🇵',
        'zh': '🇨🇳',
        'ko': '🇰🇷',
        'ar': '🇸🇦',
        'hi': '🇮🇳',
        'pl': '🇵🇱',
        'nl': '🇳🇱',
        'sv': '🇸🇪',
        'tr': '🇹🇷',
    };

    return flagMap[lang || 'en'] || '🇬🇧';
}

// Helper function to get difficulty stars
function getDifficultyStars(difficulty: number | null | undefined) {
    if (!difficulty) return null;

    const difficultyConfig: Record<number, { stars: number; label: string; className: string }> = {
        1: { stars: 1, label: 'Easy', className: 'difficulty-easy' },
        2: { stars: 2, label: 'Medium', className: 'difficulty-medium' },
        3: { stars: 3, label: 'Medium+', className: 'difficulty-medium-plus' },
        4: { stars: 4, label: 'Hard', className: 'difficulty-hard' },
        5: { stars: 5, label: 'Very Hard', className: 'difficulty-very-hard' },
    };

    const config = difficultyConfig[difficulty];
    if (!config) return null;

    return (
        <span className={`difficulty-stars ${config.className}`}>
            <span className="difficulty-label">Difficulty:</span>
            {Array.from({ length: 5 }).map((_, index) => (
                <span key={index} className={index < config.stars ? 'star-filled' : 'star-empty'}>
                    ★
                </span>
            ))}
        </span>
    );
}

// Helper function to format answer text for choice/multiple_choice types
function getFormattedAnswerText(answer: any): string {
    const { type, text, options } = answer;

    // For choice and multiple_choice, format with full option labels
    if ((type === 'choice' || type === 'multiple_choice') && options && options.length > 0) {
        const answerValues = type === 'multiple_choice'
            ? text.split(',').map((v: string) => v.trim())
            : [text];

        const formattedOptions = answerValues
            .map((value: string) => {
                const option = options.find((opt: any) => opt.value === value);
                return option ? `${value}. ${option.label}` : value;
            })
            .join('\n');

        return formattedOptions;
    }

    // For all other types, return text as-is
    return text;
}

function FlashcardDisplay({
    flashcard,
    feedback,
    userAnswer,
    showAnswer,
    totalFlashcards,
    flashcardsCompleted,
    quizName,
    mode,
    isSubmitting,
    onUserAnswerChange,
    onSpeak,
    onSubmitAnswer,
    onRevealAnswer,
    onNextFlashcard,
}: FlashcardDisplayProps) {
    const { t } = useTranslation();

    if (!flashcard) {
        return (
            <div className="flashcard-card">
                <p>{t('session.loadingFlashcard')}</p>
            </div>
        );
    }

    const percentage = totalFlashcards > 0
        ? Math.round((flashcardsCompleted / totalFlashcards) * 100)
        : 0;

    // Generate answer format hint from analyzing the answer
    const getAnswerHint = () => {
        const { answer } = flashcard;
        const metadata = answer.metadata || {};

        // If there's a custom hint, use it
        if (metadata.hint) {
            return metadata.hint;
        }

        // Build hint from analyzing the actual answer
        const hints: string[] = [];
        const answerTypeDisplay = answer.type.replace(/_/g, ' ');

        // Analyze the answer text for word/letter count
        const answerText = answer.text.trim();
        const words = answerText.split(/\s+/).filter(w => w.length > 0);
        const wordCount = words.length;

        if (wordCount === 1) {
            // Single word - show letter count
            const letterCount = answerText.length;
            hints.push(t('session.letterCount', { count: letterCount }));
        } else if (wordCount > 1) {
            // Multiple words - show word count
            hints.push(t('session.wordCount', { count: wordCount }));
        }

        // Add type information
        hints.push(`${t('session.type')}: ${answerTypeDisplay}`);

        // Add specific constraints based on metadata
        if (metadata.range) {
            if (Array.isArray(metadata.range) && metadata.range.length === 2) {
                hints.push(t('session.between', { min: metadata.range[0], max: metadata.range[1] }));
            } else if (typeof metadata.range === 'string') {
                hints.push(metadata.range);
            }
        }

        if (metadata.format) {
            hints.push(metadata.format);
        }

        if (metadata.decimal_places !== undefined) {
            hints.push(t('session.decimalPlaces', { count: metadata.decimal_places }));
        }

        if (metadata.case_sensitive) {
            hints.push(t('session.caseSensitive'));
        }

        if (metadata.example) {
            hints.push(t('session.exampleFormat', { example: metadata.example }));
        }

        return hints.join(' • ');
    };

    return (
        <div className="flashcard-card">
            {/* Header with Quiz Info and Progress */}
            <div className="flashcard-header-row">
                <div className="flashcard-quiz-info">
                    <span className="flashcard-mode-badge">
                        {mode === 'learn' ? t('session.modeLearn') : t('session.modeTest')}
                    </span>
                    <span className="flashcard-quiz-name">{quizName}</span>
                </div>
                {/* Progress Counter */}
                <div className="flashcard-progress-counter">
                    {flashcardsCompleted} / {totalFlashcards} cards ({percentage}%)
                </div>
            </div>

            {/* Question Section */}
            <div className="flashcard-question-section">
                <div className="flashcard-question-header">
                    <div className="flashcard-emoji">{flashcard.question.emoji}</div>
                    <h2 className="flashcard-question-title">
                        {flashcard.question.title}
                    </h2>
                    <button
                        className="speaker-icon"
                        onClick={() => onSpeak(flashcard.question.text, flashcard.question.lang)}
                        aria-label={t('session.readQuestionAloud')}
                        title={t('session.clickToListenIn', { language: flashcard.question.lang || 'English' })}
                    >
                        🔊 {getLanguageFlag(flashcard.question.lang)} <span className="speaker-text">{t('session.clickToListen')}</span>
                    </button>
                    {getDifficultyStars(flashcard.question.difficulty)}
                </div>
                <p className="flashcard-question-text">{flashcard.question.text}</p>

                {/* Examples Section */}
                {flashcard.question.examples && flashcard.question.examples.length > 0 && (
                    <div className="flashcard-examples">
                        <div className="examples-header">
                            <span className="examples-icon">💭</span>
                            <strong>Examples:</strong>
                        </div>
                        <ul className="examples-list">
                            {flashcard.question.examples.map((example, index) => (
                                <li key={index} className="example-item">
                                    {example}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* Answer Format Hint */}
            {!feedback && !showAnswer && (
                <div className="flashcard-answer-hint">
                    <span className="hint-icon">💡</span>
                    <span className="hint-text">
                        <strong>{t('session.expectedFormat')}</strong> {getAnswerHint()}
                    </span>
                </div>
            )}

            {/* Input/Answer Area */}
            <div className="flashcard-answer-area">
                {/* Show input unless there's feedback or answer is revealed */}
                {!feedback && !showAnswer && (
                    <AnswerInput
                        answer={flashcard.answer}
                        userAnswer={userAnswer}
                        onAnswerChange={onUserAnswerChange}
                        disabled={isSubmitting}
                    />
                )}

                {/* Show feedback in both modes after submitting */}
                {feedback && !showAnswer && (
                    <div
                        className={
                            feedback.is_correct
                                ? 'flashcard-correct-answer'
                                : 'flashcard-incorrect-answer'
                        }
                    >
                        <div className="feedback-icon">
                            {feedback.is_correct ? '✓' : '✗'}
                        </div>
                        <div className="feedback-text">
                            <strong>{feedback.feedback}</strong>
                        </div>
                    </div>
                )}

                {/* Show revealed answer in both modes when "Show Answer" is clicked */}
                {showAnswer && (
                    <div className="flashcard-revealed-answer">
                        <div className="revealed-answer-header">
                            <strong>{t('session.answer')}</strong>
                            <button
                                className="speaker-icon speaker-icon--small"
                                onClick={() => onSpeak(flashcard.answer.text, flashcard.answer.lang)}
                                aria-label={t('session.readAnswerAloud')}
                                title={t('session.clickToListenIn', { language: flashcard.answer.lang || 'English' })}
                            >
                                🔊 {getLanguageFlag(flashcard.answer.lang)} <span className="speaker-text">{t('session.listen')}</span>
                            </button>
                        </div>
                        <p style={{ whiteSpace: 'pre-line' }}>{getFormattedAnswerText(flashcard.answer)}</p>
                    </div>
                )}
            </div>

            {/* Control Buttons */}
            <div className="flashcard-controls">
                {mode === 'test' ? (
                    /* Test mode: Show different buttons based on state */
                    showAnswer ? (
                        /* After showing answer: only Next button */
                        <button
                            className="control-button control-button--primary"
                            onClick={onNextFlashcard}
                        >
                            {t('session.nextFlashcard')}
                        </button>
                    ) : feedback ? (
                        /* After submitting answer: Show Answer and Next buttons */
                        <>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                            >
                                {t('session.showAnswer')}
                            </button>
                            <button
                                className="control-button control-button--primary"
                                onClick={onNextFlashcard}
                            >
                                {t('session.nextFlashcard')}
                            </button>
                        </>
                    ) : (
                        /* Before submitting: Don't Know and Submit Answer */
                        <>
                            <button
                                className="control-button control-button--secondary"
                                onClick={() => {
                                    onUserAnswerChange(''); // Clear answer
                                    onSubmitAnswer(); // Submit empty answer
                                }}
                                disabled={isSubmitting}
                            >
                                {t('session.dontKnow')}
                            </button>
                            {userAnswer.trim() && (
                                <button
                                    className="control-button control-button--primary"
                                    onClick={onSubmitAnswer}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? t('session.submitting') : t('session.submitAnswer')}
                                </button>
                            )}
                        </>
                    )
                ) : (
                    /* Learn mode: Show all controls with feedback */
                    feedback || showAnswer ? (
                        <button
                            className="control-button control-button--primary"
                            onClick={onNextFlashcard}
                        >
                            {t('session.nextFlashcard')}
                        </button>
                    ) : (
                        <>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                                disabled={isSubmitting}
                            >
                                {t('session.dontKnow')}
                            </button>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                                disabled={isSubmitting}
                            >
                                {t('session.showAnswer')}
                            </button>
                            {userAnswer.trim() && (
                                <button
                                    className="control-button control-button--primary"
                                    onClick={onSubmitAnswer}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? t('session.checking') : t('session.checkAnswer')}
                                </button>
                            )}
                        </>
                    )
                )}
            </div>
        </div>
    );
}

export default FlashcardDisplay;
