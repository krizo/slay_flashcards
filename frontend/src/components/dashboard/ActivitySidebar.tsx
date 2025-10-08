import { Session } from '../../types';
import { TrendingQuiz } from '../../data/mockData';

interface ActivitySidebarProps {
    recentSessions: Session[];
    trendingQuizzes: TrendingQuiz[];
}

const ActivitySidebar = ({ recentSessions, trendingQuizzes }: ActivitySidebarProps) => {
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
                <div className="activity-list">
                    {recentSessions.map((session) => (
                        <div key={session.id} className="activity-item">
                            <div className="activity-icon">
                                {session.mode === 'learn' ? '📖' : '✅'}
                            </div>
                            <div className="activity-content">
                                <div className="activity-quiz-name">{session.quiz_name}</div>
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
            </div>

            {/* Trending Quizzes Section */}
            <div className="dashboard-card trending-card">
                <div className="card-header">
                    <h3 className="card-title">Trending Quizzes</h3>
                </div>
                <div className="trending-list">
                    {trendingQuizzes.map((quiz) => (
                        <div key={quiz.id} className="trending-item">
                            <div className="trending-icon">{quiz.emoji}</div>
                            <div className="trending-content">
                                <div className="trending-quiz-name">{quiz.name}</div>
                                <div className="trending-popularity">
                                    <div className="popularity-bar">
                                        <div
                                            className="popularity-fill"
                                            style={{ width: `${quiz.popularity}%` }}
                                        ></div>
                                    </div>
                                    <span className="popularity-value">{quiz.popularity}%</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ActivitySidebar;
