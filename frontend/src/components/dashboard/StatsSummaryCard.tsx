import {UserStats, Session, ProgressDataPoint} from '../../types';
import {capitalize} from '../../utils/textUtils';

type TimePeriod = 'week' | 'month' | 'year' | 'all';

interface SessionDataPoint {
    date: string;
    learn: number;
    test: number;
}

interface StatsSummaryCardProps {
    stats: UserStats | null;
    userName?: string;
    isLoading?: boolean;
    error?: Error | null;
    recentSessions?: Session[] | null;
    timePeriod: TimePeriod;
    onTimePeriodChange: (period: TimePeriod) => void;
    progressData?: ProgressDataPoint[] | null;
    sessionsData?: SessionDataPoint[] | null;
}

const StatsSummaryCard = ({stats, userName = 'User', isLoading, error, recentSessions, timePeriod, onTimePeriodChange, progressData, sessionsData}: StatsSummaryCardProps) => {

    // Get latest test score from recent sessions
    const getLatestScore = (): number | null => {
        if (!recentSessions || recentSessions.length === 0) return null;
        const testSessions = recentSessions
            .filter(s => s.mode === 'test' && s.score !== null)
            .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime());
        return testSessions.length > 0 ? testSessions[0].score : null;
    };

    // Calculate days active from sessionsData (count days with any sessions)
    const getDaysActive = (): number => {
        if (sessionsData && sessionsData.length > 0) {
            // Count days that have at least one session
            return sessionsData.filter(day => day.learn > 0 || day.test > 0).length;
        }
        // Fallback to old calculation if sessionsData not available
        if (!stats) return 0;
        if (timePeriod === 'week') {
            return Math.min(stats.sessions_this_week, 7);
        } else if (timePeriod === 'month') {
            return Math.min(stats.sessions_this_month, 30);
        }
        return stats.study_streak;
    };

    // Calculate total sessions for the selected period
    const getPeriodSessions = (): number => {
        if (sessionsData && sessionsData.length > 0) {
            return sessionsData.reduce((total, day) => total + day.learn + day.test, 0);
        }
        // Fallback
        if (!stats) return 0;
        if (timePeriod === 'week') return stats.sessions_this_week;
        if (timePeriod === 'month') return stats.sessions_this_month;
        return stats.total_sessions;
    };

    // Calculate daily average for the selected period
    const getDailyAverage = (): string => {
        if (sessionsData && sessionsData.length > 0) {
            const totalSessions = sessionsData.reduce((total, day) => total + day.learn + day.test, 0);
            const daysWithSessions = sessionsData.filter(day => day.learn > 0 || day.test > 0).length;
            if (daysWithSessions === 0) return '0.0';
            return (totalSessions / daysWithSessions).toFixed(1);
        }
        // Fallback
        if (!stats) return '0.0';
        return stats.sessions_this_month > 0 ? (stats.sessions_this_month / 30).toFixed(1) : '0.0';
    };

    // Calculate learn sessions for the selected period
    const getLearnSessions = (): number => {
        if (sessionsData && sessionsData.length > 0) {
            return sessionsData.reduce((total, day) => total + day.learn, 0);
        }
        // Fallback to all-time
        return stats?.learn_sessions || 0;
    };

    // Calculate test sessions for the selected period
    const getTestSessions = (): number => {
        if (sessionsData && sessionsData.length > 0) {
            return sessionsData.reduce((total, day) => total + day.test, 0);
        }
        // Fallback to all-time
        return stats?.test_sessions || 0;
    };

    // Calculate average score for the selected period
    const getAverageScore = (): number | null => {
        if (progressData && progressData.length > 0) {
            const totalScore = progressData.reduce((sum, point) => sum + point.score, 0);
            return Math.round(totalScore / progressData.length);
        }
        // Fallback to all-time
        return stats?.average_score ? Math.round(stats.average_score) : null;
    };

    // Calculate best score for the selected period
    const getBestScore = (): number | null => {
        if (progressData && progressData.length > 0) {
            return Math.max(...progressData.map(point => point.score));
        }
        // Fallback to all-time
        return stats?.best_score ? Math.round(stats.best_score) : null;
    };

    // Calculate minimum score for the selected period
    const getMinScore = (): number | null => {
        if (progressData && progressData.length > 0) {
            return Math.min(...progressData.map(point => point.score));
        }
        // Fallback to estimated calculation
        if (stats?.average_score && stats?.best_score) {
            return Math.round(stats.best_score - (stats.best_score - stats.average_score) * 2);
        }
        return null;
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
                            onClick={() => onTimePeriodChange('week')}
                        >
                            Week
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'month' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('month')}
                        >
                            Month
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'year' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('year')}
                        >
                            Year
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'all' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('all')}
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
                        <div className="stat-value">{getPeriodSessions()}</div>
                        <div className="stat-label">Total Sessions</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📖</div>
                    <div className="stat-content">
                        <div className="stat-value">{getLearnSessions()}</div>
                        <div className="stat-label">Learn Sessions</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-value">{getTestSessions()}</div>
                        <div className="stat-label">Test Sessions</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">🎯</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.unique_quizzes}</div>
                        <div className="stat-label">Unique Quizzes</div>
                        <div className="stat-subtitle">all time</div>
                    </div>
                </div>

                {/* Row 2: Performance Metrics */}
                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {getAverageScore() !== null ? `${getAverageScore()}%` : '—'}
                        </div>
                        <div className="stat-label">Average Score</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {getBestScore() !== null ? `${getBestScore()}%` : '—'}
                        </div>
                        <div className="stat-label">Best Score</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
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
                            {getMinScore() !== null ? `${getMinScore()}%` : '—'}
                        </div>
                        <div className="stat-label">Min Score</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📆</div>
                    <div className="stat-content">
                        <div className="stat-value">{getPeriodSessions()}</div>
                        <div className="stat-label">Recent Activity</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-content">
                        <div className="stat-value">{getDailyAverage()}</div>
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
