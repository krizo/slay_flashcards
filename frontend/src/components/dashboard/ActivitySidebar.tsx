import { useTranslation } from 'react-i18next';
import {Session} from '../../types';

interface ActivitySidebarProps {
    recentSessions: Session[] | null;
    isLoading?: boolean;
    error?: Error | null;
}

const ActivitySidebar = ({recentSessions, isLoading, error}: ActivitySidebarProps) => {
    const { t } = useTranslation();

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 1) return t('dashboard.activity.justNow');
        if (diffInHours < 24) return t('dashboard.activity.hoursAgo', { count: diffInHours });
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays === 1) return t('dashboard.activity.yesterday');
        return t('dashboard.activity.daysAgo', { count: diffInDays });
    };

    return (
        <div className="activity-sidebar">
            {/* Recent Activity Section */}
            <div className="dashboard-card activity-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.activity.recentActivity')}</h3>
                </div>

                {/* Loading state */}
                {isLoading && (
                    <div className="loading-state">
                        <div className="loading-spinner"></div>
                        <p>{t('dashboard.loadingActivity')}</p>
                    </div>
                )}

                {/* Error state */}
                {!isLoading && error && (
                    <div className="error-state">
                        <span className="error-icon">⚠️</span>
                        <p className="error-message">{t('dashboard.failedToLoadActivity')}</p>
                        <p className="error-detail">{error.message}</p>
                    </div>
                )}

                {/* Empty state */}
                {!isLoading && !error && (!recentSessions || recentSessions.length === 0) && (
                    <div className="empty-state">
                        <span className="empty-icon">📝</span>
                        <p>{t('dashboard.noRecentActivity')}</p>
                    </div>
                )}

                {/* Data state */}
                {!isLoading && !error && recentSessions && recentSessions.length > 0 && (
                    <div className="activity-list">
                        {recentSessions.map((session) => {
                            // Build category/level subtitle if they exist
                            const subtitleParts: string[] = [];
                            if (session.quiz_category) subtitleParts.push(session.quiz_category);
                            if (session.quiz_level) subtitleParts.push(session.quiz_level);
                            const subtitle = subtitleParts.length > 0 ? subtitleParts.join(' • ') : null;

                            return (
                                <div key={session.id} className="activity-item">
                                    <div className="activity-icon">
                                        {session.mode === 'learn' ? '📖' : '✅'}
                                    </div>
                                    <div className="activity-content">
                                        <div className="activity-quiz-name">
                                            {session.quiz_name || t('dashboard.activity.quizNumber', { id: session.quiz_id })}
                                        </div>
                                        {subtitle && (
                                            <div className="activity-quiz-details">
                                                {subtitle}
                                            </div>
                                        )}
                                        <div className="activity-meta">
                                            <span className="activity-mode">{t(`session.${session.mode}`)}</span>
                                            {session.score !== null && (
                                                <span className="activity-score">{Math.round(session.score)}%</span>
                                            )}
                                        </div>
                                        <div className="activity-time">{formatDate(session.started_at)}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActivitySidebar;
