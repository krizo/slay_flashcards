interface SessionHeaderProps {
    quizName: string;
    quizImage?: string | null;
    yourBest?: number | null;
    yourAverage?: number | null;
    testSessions?: number;
    lastSessionDate?: string | null;
    onCloseSession: () => void;
}

function SessionHeader({
    quizName,
    quizImage,
    yourBest,
    yourAverage,
    testSessions = 0,
    lastSessionDate,
    onCloseSession
}: SessionHeaderProps) {
    // Check if image is valid base64 and starts with data: prefix
    const hasValidImage = quizImage && quizImage.startsWith('data:image');

    // Format last session date
    const formatLastSession = (date: string | null | undefined) => {
        if (!date) return 'First time!';
        const sessionDate = new Date(date);
        const now = new Date();
        const diffMs = now.getTime() - sessionDate.getTime();
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffSecs < 30) return 'Just now';
        if (diffMins < 1) return `${diffSecs} sec ago`;
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        return sessionDate.toLocaleDateString();
    };

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
                <div className="session-header-content">
                    <div className="session-title">{quizName}</div>
                    <div className="session-metrics">
                        <div className="session-metric">
                            <span className="metric-icon">⭐</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {yourBest !== null && yourBest !== undefined
                                        ? `${Math.round(yourBest)}%`
                                        : '—'}
                                </span>
                                <span className="metric-label">Your Best</span>
                            </div>
                        </div>
                        <div className="session-metric">
                            <span className="metric-icon">📊</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {yourAverage !== null && yourAverage !== undefined
                                        ? `${Math.round(yourAverage)}%`
                                        : '—'}
                                </span>
                                <span className="metric-label">Your Avg</span>
                            </div>
                        </div>
                        <div className="session-metric">
                            <span className="metric-icon">🎯</span>
                            <div className="metric-content">
                                <span className="metric-value">{testSessions > 0 ? testSessions : '—'}</span>
                                <span className="metric-label">Test Sessions</span>
                            </div>
                        </div>
                        <div className="session-metric">
                            <span className="metric-icon">🕒</span>
                            <div className="metric-content">
                                <span className="metric-value">{formatLastSession(lastSessionDate)}</span>
                                <span className="metric-label">Last Session</span>
                            </div>
                        </div>
                    </div>
                </div>
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
