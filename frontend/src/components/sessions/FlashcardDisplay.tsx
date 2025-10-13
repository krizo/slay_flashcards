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

// Helper function to get difficulty badge
function getDifficultyBadge(difficulty: number | null | undefined) {
    if (!difficulty) return null;

    const difficultyConfig: Record<number, { label: string; emoji: string; className: string }> = {
        1: { label: 'Easy', emoji: '🟢', className: 'difficulty-easy' },
        2: { label: 'Medium', emoji: '🟡', className: 'difficulty-medium' },
        3: { label: 'Medium+', emoji: '🟠', className: 'difficulty-medium-plus' },
        4: { label: 'Hard', emoji: '🔴', className: 'difficulty-hard' },
        5: { label: 'Very Hard', emoji: '⚫', className: 'difficulty-very-hard' },
    };

    const config = difficultyConfig[difficulty];
    if (!config) return null;

    return (
        <span className={`difficulty-badge ${config.className}`}>
            {config.emoji} {config.label}
        </span>
    );
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
    if (!flashcard) {
        return (
            <div className="flashcard-card">
                <p>Loading flashcard...</p>
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
            hints.push(`${letterCount} ${letterCount === 1 ? 'letter' : 'letters'}`);
        } else if (wordCount > 1) {
            // Multiple words - show word count
            hints.push(`${wordCount} words`);
        }

        // Add type information
        hints.push(`type: ${answerTypeDisplay}`);

        // Add specific constraints based on metadata
        if (metadata.range) {
            if (Array.isArray(metadata.range) && metadata.range.length === 2) {
                hints.push(`between ${metadata.range[0]} and ${metadata.range[1]}`);
            } else if (typeof metadata.range === 'string') {
                hints.push(metadata.range);
            }
        }

        if (metadata.format) {
            hints.push(metadata.format);
        }

        if (metadata.decimal_places !== undefined) {
            hints.push(`${metadata.decimal_places} decimal places`);
        }

        if (metadata.case_sensitive) {
            hints.push('case sensitive');
        }

        if (metadata.example) {
            hints.push(`e.g., "${metadata.example}"`);
        }

        return hints.join(' • ');
    };

    return (
        <div className="flashcard-card">
            {/* Header with Quiz Info and Progress */}
            <div className="flashcard-header-row">
                <div className="flashcard-quiz-info">
                    <span className="flashcard-mode-badge">
                        {mode === 'learn' ? '📚 Learn' : '🎯 Test'}
                    </span>
                    <span className="flashcard-quiz-name">{quizName}</span>
                </div>
                <div className="flashcard-progress-dots">
                    {Array.from({ length: totalFlashcards }).map((_, index) => (
                        <div
                            key={index}
                            className={`progress-dot ${
                                index < flashcardsCompleted ? 'progress-dot--active' : ''
                            }`}
                        />
                    ))}
                </div>
            </div>

            {/* Progress Counter */}
            <div className="flashcard-progress-counter">
                {flashcardsCompleted} / {totalFlashcards} cards ({percentage}%)
            </div>

            {/* Question Section */}
            <div className="flashcard-question-section">
                <div className="flashcard-question-header">
                    <div className="flashcard-emoji">{flashcard.question.emoji}</div>
                    <h2 className="flashcard-question-title">
                        {flashcard.question.title}
                        {getDifficultyBadge(flashcard.question.difficulty)}
                    </h2>
                    <button
                        className="speaker-icon"
                        onClick={() => onSpeak(flashcard.question.text, flashcard.question.lang)}
                        aria-label="Read question aloud"
                        title={`Click to listen in ${flashcard.question.lang || 'English'}`}
                    >
                        🔊 {getLanguageFlag(flashcard.question.lang)} <span className="speaker-text">Click to listen</span>
                    </button>
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
                        <strong>Expected format:</strong> {getAnswerHint()}
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
                            <strong>Answer:</strong>
                            <button
                                className="speaker-icon speaker-icon--small"
                                onClick={() => onSpeak(flashcard.answer.text, flashcard.answer.lang)}
                                aria-label="Read answer aloud"
                                title={`Click to listen in ${flashcard.answer.lang || 'English'}`}
                            >
                                🔊 {getLanguageFlag(flashcard.answer.lang)} <span className="speaker-text">Listen</span>
                            </button>
                        </div>
                        <p>{flashcard.answer.text}</p>
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
                            Next Flashcard →
                        </button>
                    ) : feedback ? (
                        /* After submitting answer: Show Answer and Next buttons */
                        <>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                            >
                                Show Answer
                            </button>
                            <button
                                className="control-button control-button--primary"
                                onClick={onNextFlashcard}
                            >
                                Next Flashcard →
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
                                Don't Know
                            </button>
                            {userAnswer.trim() && (
                                <button
                                    className="control-button control-button--primary"
                                    onClick={onSubmitAnswer}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Submitting...' : 'Submit Answer'}
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
                            Next Flashcard →
                        </button>
                    ) : (
                        <>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                                disabled={isSubmitting}
                            >
                                Don't Know
                            </button>
                            <button
                                className="control-button control-button--secondary"
                                onClick={onRevealAnswer}
                                disabled={isSubmitting}
                            >
                                Show Answer
                            </button>
                            {userAnswer.trim() && (
                                <button
                                    className="control-button control-button--primary"
                                    onClick={onSubmitAnswer}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Checking...' : 'Check Answer'}
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
