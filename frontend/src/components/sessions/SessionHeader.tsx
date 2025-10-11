interface SessionHeaderProps {
    quizName: string;
    quizImage?: string | null;
    onCloseSession: () => void;
}

function SessionHeader({ quizName, quizImage, onCloseSession }: SessionHeaderProps) {
    // Check if image is valid base64 and starts with data: prefix
    const hasValidImage = quizImage && quizImage.startsWith('data:image');

    return (
        <div className="session-header">
            <div className="session-title-wrapper">
                {hasValidImage ? (
                    <img
                        src={quizImage}
                        alt={quizName}
                        className="session-quiz-image"
                    />
                ) : (
                    <span className="session-quiz-icon">📚</span>
                )}
                <div className="session-title">{quizName}</div>
            </div>
            <button
                className="session-close-button"
                onClick={onCloseSession}
                aria-label="Close session"
            >
                ✕
            </button>
        </div>
    );
}

export default SessionHeader;
