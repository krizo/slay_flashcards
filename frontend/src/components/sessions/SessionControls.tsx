import { SessionFeedback } from '../../types';

interface SessionControlsProps {
    feedback: SessionFeedback | null;
    showAnswer: boolean;
    userAnswer: string;
    isSubmitting: boolean;
    onSubmitAnswer: () => void;
    onRevealAnswer: () => void;
    onNextFlashcard: () => void;
}

function SessionControls({
    feedback,
    showAnswer,
    userAnswer,
    isSubmitting,
    onSubmitAnswer,
    onRevealAnswer,
    onNextFlashcard,
}: SessionControlsProps) {
    // After answer is submitted or revealed, show "Next" button
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

    // Initial state: show input controls
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
