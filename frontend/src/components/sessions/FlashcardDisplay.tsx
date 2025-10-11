import { FlashcardData, SessionFeedback } from '../../types';

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
                    <h2 className="flashcard-question-title">{flashcard.question.title}</h2>
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
            </div>

            {/* Input/Answer Area */}
            <div className="flashcard-answer-area">
                {!feedback && !showAnswer && (
                    <textarea
                        className="flashcard-answer-input"
                        placeholder="Type your answer here..."
                        value={userAnswer}
                        onChange={(e) => onUserAnswerChange(e.target.value)}
                    />
                )}

                {feedback && (
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
                            {!feedback.is_correct && (
                                <div className="correct-answer-with-speaker">
                                    <p className="correct-answer-display">
                                        Correct answer: {feedback.correct_answer}
                                    </p>
                                    <button
                                        className="speaker-icon speaker-icon--small"
                                        onClick={() => onSpeak(feedback.correct_answer, flashcard.answer.lang)}
                                        aria-label="Read correct answer aloud"
                                        title={`Click to listen in ${flashcard.answer.lang || 'English'}`}
                                    >
                                        🔊 {getLanguageFlag(flashcard.answer.lang)} <span className="speaker-text">Listen</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {showAnswer && !feedback && (
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
                {feedback || showAnswer ? (
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
                )}
            </div>
        </div>
    );
}

export default FlashcardDisplay;
