import {useState} from 'react';
import {UserStats, Session} from '../../types';
import {capitalize} from '../../utils/textUtils';

interface StatsSummaryCardProps {
    stats: UserStats | null;
    userName?: string;
    isLoading?: boolean;
    error?: Error | null;
    recentSessions?: Session[] | null;
}

type TimePeriod = 'week' | 'month' | 'year' | 'all';

const StatsSummaryCard = ({stats, userName = 'User', isLoading, error, recentSessions}: StatsSummaryCardProps) => {
    const [timePeriod, setTimePeriod] = useState<TimePeriod>('all');

    // Get latest test score from recent sessions
    const getLatestScore = (): number | null => {
        if (!recentSessions || recentSessions.length === 0) return null;
        const testSessions = recentSessions
            .filter(s => s.mode === 'test' && s.score !== null)
            .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime());
        return testSessions.length > 0 ? testSessions[0].score : null;
    };

    // Calculate days active based on sessions_this_week and sessions_this_month
    const getDaysActive = (): number => {
        if (!stats) return 0;
        // Estimate days active: if you have sessions, you're active
        // For simplicity, we'll use a heuristic based on sessions
        if (timePeriod === 'week') {
            return Math.min(stats.sessions_this_week, 7);
        } else if (timePeriod === 'month') {
            return Math.min(stats.sessions_this_month, 30);
        }
        // For year and all time, we don't have exact data, so show study streak
        return stats.study_streak;
    };

    const getTimePeriodLabel = (): string => {
        switch (timePeriod) {
            case 'week': return 'Last Week';
            case 'month': return 'Last Month';
            case 'year': return 'Last Year';
            case 'all': return 'All Time';
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="dashboard-card stats-summary-card">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading statistics...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="dashboard-card stats-summary-card">
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <p className="error-message">Failed to load statistics</p>
                    <p className="error-detail">{error.message}</p>
                </div>
            </div>
        );
    }

    // No data state
    if (!stats) {
        return (
            <div className="dashboard-card stats-summary-card">
                <div className="empty-state">
                    <span className="empty-icon">📊</span>
                    <p>No statistics available</p>
                </div>
            </div>
        );
    }

    const latestScore = getLatestScore();
    const daysActive = getDaysActive();

    return (
        <div className="dashboard-card stats-summary-card">
            <div className="stats-welcome">
                <div className="welcome-header">
                    <div>
                        <h2 className="welcome-message">
                            Welcome back, {capitalize(userName)}! 👋
                        </h2>
                        <p className="welcome-subtitle">Here's your learning progress</p>
                    </div>
                    <div className="time-period-filter">
                        <button
                            className={`period-btn ${timePeriod === 'week' ? 'active' : ''}`}
                            onClick={() => setTimePeriod('week')}
                        >
                            Week
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'month' ? 'active' : ''}`}
                            onClick={() => setTimePeriod('month')}
                        >
                            Month
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'year' ? 'active' : ''}`}
                            onClick={() => setTimePeriod('year')}
                        >
                            Year
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'all' ? 'active' : ''}`}
                            onClick={() => setTimePeriod('all')}
                        >
                            All Time
                        </button>
                    </div>
                </div>
            </div>

            <div className="stats-grid stats-grid--extended">
                {/* Row 1: Session Overview */}
                <div className="stat-item">
                    <div className="stat-icon">📚</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.total_sessions}</div>
                        <div className="stat-label">Total Sessions</div>
                        <div className="stat-subtitle">all time activity</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📖</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.learn_sessions}</div>
                        <div className="stat-label">Learn Sessions</div>
                        <div className="stat-subtitle">practice mode</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.test_sessions}</div>
                        <div className="stat-label">Test Sessions</div>
                        <div className="stat-subtitle">graded attempts</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">🎯</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.unique_quizzes}</div>
                        <div className="stat-label">Unique Quizzes</div>
                        <div className="stat-subtitle">subjects studied</div>
                    </div>
                </div>

                {/* Row 2: Performance Metrics */}
                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {stats.average_score ? Math.round(stats.average_score) : '—'}%
                        </div>
                        <div className="stat-label">Average Score</div>
                        <div className="stat-subtitle">across all tests</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {stats.best_score ? Math.round(stats.best_score) : '—'}%
                        </div>
                        <div className="stat-label">Best Score</div>
                        <div className="stat-subtitle">personal record</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">📝</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {latestScore !== null ? `${Math.round(latestScore)}%` : '—'}
                        </div>
                        <div className="stat-label">Latest Score</div>
                        <div className="stat-subtitle">most recent test</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">🔥</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.study_streak}</div>
                        <div className="stat-label">Study Streak</div>
                        <div className="stat-subtitle">consecutive days</div>
                    </div>
                </div>

                {/* Row 3: Recent Activity */}
                <div className="stat-item">
                    <div className="stat-icon">📅</div>
                    <div className="stat-content">
                        <div className="stat-value">{daysActive}</div>
                        <div className="stat-label">Days Active</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📉</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {stats.average_score && stats.best_score
                                ? `${Math.round(stats.best_score - (stats.best_score - stats.average_score) * 2)}%`
                                : '—'
                            }
                        </div>
                        <div className="stat-label">Min Score</div>
                        <div className="stat-subtitle">lowest recorded</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📆</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.sessions_this_month}</div>
                        <div className="stat-label">Recent Activity</div>
                        <div className="stat-subtitle">last 30 days</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {stats.sessions_this_month > 0
                                ? `${(stats.sessions_this_month / 30).toFixed(1)}`
                                : '0.0'
                            }
                        </div>
                        <div className="stat-label">Daily Average</div>
                        <div className="stat-subtitle">sessions per day</div>
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
