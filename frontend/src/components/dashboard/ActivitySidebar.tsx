import { Session } from '../../types';

interface ActivitySidebarProps {
    recentSessions: Session[] | null;
    isLoading?: boolean;
    error?: Error | null;
}

const ActivitySidebar = ({ recentSessions, isLoading, error }: ActivitySidebarProps) => {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 1) return 'Just now';
        if (diffInHours < 24) return `${diffInHours}h ago`;
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays === 1) return 'Yesterday';
        return `${diffInDays}d ago`;
    };

    return (
        <div className="activity-sidebar">
            {/* Recent Activity Section */}
            <div className="dashboard-card activity-card">
                <div className="card-header">
                    <h3 className="card-title">Recent Activity</h3>
                </div>

                {/* Loading state */}
                {isLoading && (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>Loading activity...</p>
                    </div>
                )}

                {/* Error state */}
                {!isLoading && error && (
                    <div className="error-state">
                        <span className="error-icon">⚠️</span>
                        <p className="error-message">Failed to load activity</p>
                        <p className="error-detail">{error.message}</p>
                    </div>
                )}

                {/* Empty state */}
                {!isLoading && !error && (!recentSessions || recentSessions.length === 0) && (
                    <div className="empty-state">
                        <span className="empty-icon">📝</span>
                        <p>No recent activity</p>
                    </div>
                )}

                {/* Data state */}
                {!isLoading && !error && recentSessions && recentSessions.length > 0 && (
                    <div className="activity-list">
                        {recentSessions.map((session) => (
                        <div key={session.id} className="activity-item">
                            <div className="activity-icon">
                                {session.mode === 'learn' ? '📖' : '✅'}
                            </div>
                            <div className="activity-content">
                                <div className="activity-quiz-name">
                                    {session.quiz_name || `Quiz #${session.quiz_id}`}
                                </div>
                                <div className="activity-meta">
                                    <span className="activity-mode">{session.mode}</span>
                                    {session.score !== null && (
                                        <span className="activity-score">{session.score}%</span>
                                    )}
                                </div>
                                <div className="activity-time">{formatDate(session.started_at)}</div>
                            </div>
                        </div>
                    ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActivitySidebar;
