import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faGear, faRightFromBracket, faTimes } from '@fortawesome/free-solid-svg-icons';
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

    return (
        <header className="app-header">
            {/* Session info (left side) */}
            {sessionInfo && (
                <div className="header-session-info">
                    <div className="header-session-title">
                        {sessionInfo.quizImage && (
                            <span className="header-session-icon">{sessionInfo.quizImage}</span>
                        )}
                        <span className="header-session-name">{sessionInfo.quizName}</span>
                    </div>
                    <div className="header-session-metrics">
                        <span className="header-metric">
                            Best: {sessionInfo.yourBest !== null ? `${sessionInfo.yourBest}%` : 'N/A'}
                        </span>
                        <span className="header-metric">
                            Avg: {sessionInfo.yourAverage !== null && sessionInfo.yourAverage !== undefined ? `${sessionInfo.yourAverage.toFixed(0)}%` : 'N/A'}
                        </span>
                        <span className="header-metric">
                            Tests: {sessionInfo.testSessions}
                        </span>
                        <span className="header-metric">
                            Last: {formatDate(sessionInfo.lastSessionDate)}
                        </span>
                    </div>
                    <button
                        onClick={sessionInfo.onCloseSession}
                        className="header-session-close"
                        title="Close session"
                        type="button"
                    >
                        <FontAwesomeIcon icon={faTimes} />
                    </button>
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
