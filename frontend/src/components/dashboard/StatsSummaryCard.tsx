import { UserStats } from '../../types';

interface StatsSummaryCardProps {
    stats: UserStats;
    userName?: string;
}

const StatsSummaryCard = ({ stats, userName = 'User' }: StatsSummaryCardProps) => {
    return (
        <div className="dashboard-card stats-summary-card">
            <div className="stats-welcome">
                <h2 className="welcome-message">Welcome back, {userName}! 👋</h2>
                <p className="welcome-subtitle">Here's your learning progress</p>
            </div>

            <div className="stats-grid">
                <div className="stat-item stat-primary">
                    <div className="stat-icon">📚</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total_sessions}</div>
                        <div className="stat-label">Total Sessions</div>
                    </div>
                </div>

                <div className="stat-item stat-primary">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.average_score ?? 'N/A'}%</div>
                        <div className="stat-label">Average Score</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">🔥</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.study_streak}</div>
                        <div className="stat-label">Day Streak</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.best_score ?? 'N/A'}%</div>
                        <div className="stat-label">Best Score</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📖</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.learn_sessions}</div>
                        <div className="stat-label">Learn Sessions</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.test_sessions}</div>
                        <div className="stat-label">Test Sessions</div>
                    </div>
                </div>
            </div>

            <div className="quick-actions">
                <h3 className="quick-actions-title">Quick Actions</h3>
                <div className="action-buttons">
                    <button className="action-button action-primary">
                        <span className="action-icon">🎓</span>
                        <span>Start Learning</span>
                    </button>
                    <button className="action-button action-secondary">
                        <span className="action-icon">📝</span>
                        <span>Take a Test</span>
                    </button>
                    <button className="action-button action-secondary">
                        <span className="action-icon">➕</span>
                        <span>Create Quiz</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default StatsSummaryCard;
