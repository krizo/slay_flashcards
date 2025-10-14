import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faGear, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { useSessionContext } from '../../contexts/SessionContext';

function Header() {
    const { t } = useTranslation();
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

    // Check if image is base64 string or emoji
    // Try to decode short base64 strings - they might be encoded emoji
    let displayEmoji = sessionInfo?.quizImage;
    if (sessionInfo?.quizImage && sessionInfo.quizImage.length < 50 && /^[A-Za-z0-9+/=]+$/.test(sessionInfo.quizImage)) {
        try {
            // Properly decode base64 to UTF-8 for emoji
            const binaryString = atob(sessionInfo.quizImage);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            displayEmoji = new TextDecoder('utf-8').decode(bytes);
        } catch (e) {
            // If decode fails, use as-is
            displayEmoji = sessionInfo.quizImage;
        }
    }

    // Base64 images are very long (500+ chars)
    const looksLikeBase64Image = sessionInfo?.quizImage
        && sessionInfo.quizImage.length > 50
        && /^[A-Za-z0-9+/=]+$/.test(sessionInfo.quizImage);
    const isBase64 = looksLikeBase64Image || (sessionInfo?.quizImage?.startsWith('data:image'));
    const isEmoji = sessionInfo?.quizImage && !looksLikeBase64Image && !sessionInfo.quizImage.startsWith('data:');

    // Add data URL prefix if it's base64 image without prefix
    const imageUrl = looksLikeBase64Image && sessionInfo?.quizImage
        ? `data:image/png;base64,${sessionInfo.quizImage}`
        : sessionInfo?.quizImage;

    return (
        <header className="app-header">
            {/* Session info (left side) */}
            {sessionInfo && (
                <div className="header-session-info">
                    <div className="header-session-left">
                        <div className="header-session-title">
                            {isBase64 ? (
                                <img
                                    src={imageUrl!}
                                    alt={sessionInfo.quizName}
                                    className="header-session-image"
                                />
                            ) : isEmoji ? (
                                <span className="header-session-icon">{displayEmoji}</span>
                            ) : (
                                <span className="header-session-icon">📚</span>
                            )}
                            <div className="header-title-and-meta">
                                <span className="header-session-name">{sessionInfo.quizName}</span>
                                {/* Quiz metadata inline */}
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
                            </div>
                        </div>
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
                    <span className="loading-shimmer">{t('common.loading')}</span>
                ) : (
                    <>
                        <div className="header-user-name">
                            <div className="header-user-icon">
                                <FontAwesomeIcon icon={faUser} size="sm" />
                            </div>
                            <span>{user?.name || t('common.user')}</span>
                        </div>

                        <Link to="/settings" className="header-icon-button" title={t('header.settings')}>
                            <FontAwesomeIcon icon={faGear} size="lg" />
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="header-icon-button"
                            title={t('header.logout')}
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
