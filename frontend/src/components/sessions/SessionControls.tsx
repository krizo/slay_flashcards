import { SessionFeedback, SessionMode } from '../../types';

interface SessionControlsProps {
    feedback: SessionFeedback | null;
    showAnswer: boolean;
    userAnswer: string;
    isSubmitting: boolean;
    mode: SessionMode;
    onSubmitAnswer: () => void;
    onRevealAnswer: () => void;
    onNextFlashcard: () => void;
    onUserAnswerChange?: (answer: string) => void;
}

function SessionControls({
    feedback,
    showAnswer,
    userAnswer,
    isSubmitting,
    mode,
    onSubmitAnswer,
    onRevealAnswer,
    onNextFlashcard,
    onUserAnswerChange,
}: SessionControlsProps) {
    // Test mode: Show different buttons based on state
    if (mode === 'test') {
        if (showAnswer) {
            // After showing answer: only Next button
            return (
                <div className="session-controls">
                    <button
                        className="control-button control-button--primary"
                        onClick={onNextFlashcard}
                    >
                        Next Flashcard →
                    </button>
                </div>
            );
        }

        if (feedback) {
            // After submitting answer: Show Answer and Next buttons
            return (
                <div className="session-controls">
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
                </div>
            );
        }

        // Before submitting: Don't Know and Submit Answer
        return (
            <div className="session-controls">
                <button
                    className="control-button control-button--secondary"
                    onClick={() => {
                        if (onUserAnswerChange) {
                            onUserAnswerChange(''); // Clear answer
                        }
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
            </div>
        );
    }

    // Learn mode: After answer is submitted or revealed, show "Next" button
    if (feedback || showAnswer) {
        return (
            <div className="session-controls">
                <button
                    className="control-button control-button--primary"
                    onClick={onNextFlashcard}
                >
                    Next Flashcard →
                </button>
            </div>
        );
    }

    // Learn mode: Initial state - show input controls
    return (
        <div className="session-controls">
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
        </div>
    );
}

export default SessionControls;
