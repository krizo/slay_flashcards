import { useTranslation } from 'react-i18next';

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
    const { t } = useTranslation();

    // Check if image is valid base64 and starts with data: prefix
    const hasValidImage = quizImage && quizImage.startsWith('data:image');

    // Format last session date
    const formatLastSession = (date: string | null | undefined) => {
        if (!date) return t('session.header.firstTime');
        const sessionDate = new Date(date);
        const now = new Date();
        const diffMs = now.getTime() - sessionDate.getTime();
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffSecs < 30) return t('session.header.justNow');
        if (diffMins < 1) return t('session.header.secAgo', { count: diffSecs });
        if (diffMins < 60) return t('session.header.minAgo', { count: diffMins });
        if (diffHours < 24) return t('session.header.hoursAgo', { count: diffHours });
        if (diffDays === 1) return t('session.header.yesterday');
        if (diffDays < 7) return t('session.header.daysAgo', { count: diffDays });
        if (diffDays < 30) return t('session.header.weeksAgo', { count: Math.floor(diffDays / 7) });
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
                                <span className="metric-label">{t('session.header.yourBest')}</span>
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
                                <span className="metric-label">{t('session.header.yourAvg')}</span>
                            </div>
                        </div>
                        <div className="session-metric">
                            <span className="metric-icon">🎯</span>
                            <div className="metric-content">
                                <span className="metric-value">{testSessions > 0 ? testSessions : '—'}</span>
                                <span className="metric-label">{t('session.header.testSessions')}</span>
                            </div>
                        </div>
                        <div className="session-metric">
                            <span className="metric-icon">🕒</span>
                            <div className="metric-content">
                                <span className="metric-value">{formatLastSession(lastSessionDate)}</span>
                                <span className="metric-label">{t('session.header.lastSession')}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <button
                className="session-close-button"
                onClick={onCloseSession}
                aria-label={t('session.closeSession')}
            >
                ✕
            </button>
        </div>
    );
}

export default SessionHeader;
