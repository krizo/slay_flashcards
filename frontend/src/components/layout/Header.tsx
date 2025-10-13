import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faGear, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../../context/AuthContext';
import { useSessionContext } from '../../contexts/SessionContext';

function Header() {
    const { user, isLoading, logout } = useAuth();
    const { sessionInfo } = useSessionContext();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            logout();
            navigate('/login');
        } catch (error) {
            console.error('Logout failed:', error);
            // Still navigate to login even if server logout fails
            navigate('/login');
        }
    };

    // Format date helper (same as SessionHeader)
    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) return 'First time!';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
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
        return date.toLocaleDateString();
    };

    // Check if image is valid base64 data URL or emoji
    const hasValidImage = sessionInfo?.quizImage && sessionInfo.quizImage.startsWith('data:image');
    const hasEmoji = sessionInfo?.quizImage && !sessionInfo.quizImage.startsWith('data:image') && sessionInfo.quizImage.length < 10;

    return (
        <header className="app-header">
            {/* Session info (left side) */}
            {sessionInfo && (
                <div className="header-session-info">
                    <div className="header-session-title">
                        {hasValidImage ? (
                            <img
                                src={sessionInfo.quizImage!}
                                alt={sessionInfo.quizName}
                                className="header-session-image"
                            />
                        ) : hasEmoji ? (
                            <span className="header-session-icon">{sessionInfo.quizImage}</span>
                        ) : (
                            <span className="header-session-icon">📚</span>
                        )}
                        <span className="header-session-name">{sessionInfo.quizName}</span>
                    </div>
                    {/* Quiz metadata */}
                    <div className="header-quiz-metadata">
                        {sessionInfo.subject && (
                            <span className="quiz-meta-item">
                                📚 {sessionInfo.subject}
                            </span>
                        )}
                        {sessionInfo.category && (
                            <span className="quiz-meta-item">
                                📂 {sessionInfo.category}
                            </span>
                        )}
                        {sessionInfo.level && (
                            <span className="quiz-meta-item">
                                📊 {sessionInfo.level}
                            </span>
                        )}
                    </div>

                    {/* Stats tiles */}
                    <div className="header-session-metrics">
                        <div className="header-metric-tile">
                            <span className="metric-icon">⭐</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {sessionInfo.yourBest !== null && sessionInfo.yourBest !== undefined
                                        ? `${Math.round(sessionInfo.yourBest)}%`
                                        : '—'}
                                </span>
                                <span className="metric-label">Your Best</span>
                            </div>
                        </div>
                        <div className="header-metric-tile">
                            <span className="metric-icon">📊</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {sessionInfo.yourAverage !== null && sessionInfo.yourAverage !== undefined
                                        ? `${Math.round(sessionInfo.yourAverage)}%`
                                        : '—'}
                                </span>
                                <span className="metric-label">Your Avg</span>
                            </div>
                        </div>
                        <div className="header-metric-tile">
                            <span className="metric-icon">🎯</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {sessionInfo.lastScore !== null && sessionInfo.lastScore !== undefined
                                        ? `${Math.round(sessionInfo.lastScore)}%`
                                        : '—'}
                                </span>
                                <span className="metric-label">Last Score</span>
                            </div>
                        </div>
                        <div className="header-metric-tile">
                            <span className="metric-icon">🧪</span>
                            <div className="metric-content">
                                <span className="metric-value">
                                    {sessionInfo.testSessions && sessionInfo.testSessions > 0 ? sessionInfo.testSessions : '—'}
                                </span>
                                <span className="metric-label">Tests</span>
                            </div>
                        </div>
                        <div className="header-metric-tile">
                            <span className="metric-icon">🕒</span>
                            <div className="metric-content">
                                <span className="metric-value">{formatDate(sessionInfo.lastSessionDate)}</span>
                                <span className="metric-label">Last Session</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* User info (right side) */}
            <div className="header-user-info">
                {isLoading ? (
                    <span className="loading-shimmer">Loading...</span>
                ) : (
                    <>
                        <div className="header-user-name">
                            <div className="header-user-icon">
                                <FontAwesomeIcon icon={faUser} size="sm" />
                            </div>
                            <span>{user?.name || 'User'}</span>
                        </div>

                        <Link to="/settings" className="header-icon-button" title="Settings">
                            <FontAwesomeIcon icon={faGear} size="lg" />
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="header-icon-button"
                            title="Logout"
                            type="button"
                        >
                            <FontAwesomeIcon icon={faRightFromBracket} size="lg" />
                        </button>
                    </>
                )}
            </div>
        </header>
    );
}

export default Header;
