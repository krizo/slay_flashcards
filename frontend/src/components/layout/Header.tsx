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

    // Format date helper
    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) return 'Never';
        const date = new Date(dateString);
        const now = new Date();
        const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

        if (diffInDays === 0) return 'Today';
        if (diffInDays === 1) return 'Yesterday';
        if (diffInDays < 7) return `${diffInDays} days ago`;
        return date.toLocaleDateString();
    };

    // Check if image is valid base64 data URL
    const hasValidImage = sessionInfo?.quizImage && sessionInfo.quizImage.startsWith('data:image');

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
                        ) : (
                            <span className="header-session-icon">📚</span>
                        )}
                        <span className="header-session-name">{sessionInfo.quizName}</span>
                    </div>
                    <div className="header-session-metrics">
                        <span className="header-metric">
                            <span className="metric-icon">⭐</span>
                            {sessionInfo.yourBest !== null && sessionInfo.yourBest !== undefined
                                ? `${Math.round(sessionInfo.yourBest)}%`
                                : '—'}
                        </span>
                        <span className="header-metric">
                            <span className="metric-icon">📊</span>
                            {sessionInfo.yourAverage !== null && sessionInfo.yourAverage !== undefined
                                ? `${Math.round(sessionInfo.yourAverage)}%`
                                : '—'}
                        </span>
                        <span className="header-metric">
                            <span className="metric-icon">🎯</span>
                            {sessionInfo.testSessions && sessionInfo.testSessions > 0 ? sessionInfo.testSessions : '—'}
                        </span>
                        <span className="header-metric">
                            <span className="metric-icon">🕒</span>
                            {formatDate(sessionInfo.lastSessionDate)}
                        </span>
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
