import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation();

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
            case 'week': return t('dashboard.timePeriods.lastWeek');
            case 'month': return t('dashboard.timePeriods.lastMonth');
            case 'year': return t('dashboard.timePeriods.lastYear');
            case 'all': return t('dashboard.timePeriods.allTimeLower');
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="dashboard-card stats-summary-card">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>{t('dashboard.loadingStatistics')}</p>
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
                    <p className="error-message">{t('dashboard.failedToLoadStatistics')}</p>
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
                    <p>{t('dashboard.noStatisticsAvailable')}</p>
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
                            {t('dashboard.welcomeBack', { name: capitalize(userName) })}
                        </h2>
                        <p className="welcome-subtitle">{t('dashboard.learningProgress')}</p>
                    </div>
                    <div className="time-period-filter">
                        <button
                            className={`period-btn ${timePeriod === 'week' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('week')}
                        >
                            {t('dashboard.timePeriods.week')}
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'month' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('month')}
                        >
                            {t('dashboard.timePeriods.month')}
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'year' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('year')}
                        >
                            {t('dashboard.timePeriods.year')}
                        </button>
                        <button
                            className={`period-btn ${timePeriod === 'all' ? 'active' : ''}`}
                            onClick={() => onTimePeriodChange('all')}
                        >
                            {t('dashboard.timePeriods.allTime')}
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
                        <div className="stat-label">{t('dashboard.stats.totalSessions')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📖</div>
                    <div className="stat-content">
                        <div className="stat-value">{getLearnSessions()}</div>
                        <div className="stat-label">{t('dashboard.stats.learnSessions')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-value">{getTestSessions()}</div>
                        <div className="stat-label">{t('dashboard.stats.testSessions')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">🎯</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.unique_quizzes}</div>
                        <div className="stat-label">{t('dashboard.stats.uniqueQuizzes')}</div>
                        <div className="stat-subtitle">{t('dashboard.subtitles.allTime')}</div>
                    </div>
                </div>

                {/* Row 2: Performance Metrics */}
                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {getAverageScore() !== null ? `${getAverageScore()}%` : '—'}
                        </div>
                        <div className="stat-label">{t('dashboard.stats.averageScore')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {getBestScore() !== null ? `${getBestScore()}%` : '—'}
                        </div>
                        <div className="stat-label">{t('dashboard.stats.bestScore')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">📝</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {latestScore !== null ? `${Math.round(latestScore)}%` : '—'}
                        </div>
                        <div className="stat-label">{t('dashboard.stats.latestScore')}</div>
                        <div className="stat-subtitle">{t('dashboard.subtitles.mostRecentTest')}</div>
                    </div>
                </div>

                <div className="stat-item stat-item--highlight">
                    <div className="stat-icon">🔥</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats.study_streak}</div>
                        <div className="stat-label">{t('dashboard.stats.studyStreak')}</div>
                        <div className="stat-subtitle">{t('dashboard.subtitles.consecutiveDays')}</div>
                    </div>
                </div>

                {/* Row 3: Recent Activity */}
                <div className="stat-item">
                    <div className="stat-icon">📅</div>
                    <div className="stat-content">
                        <div className="stat-value">{daysActive}</div>
                        <div className="stat-label">{t('dashboard.stats.daysActive')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📉</div>
                    <div className="stat-content">
                        <div className="stat-value">
                            {getMinScore() !== null ? `${getMinScore()}%` : '—'}
                        </div>
                        <div className="stat-label">{t('dashboard.stats.minScore')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">📆</div>
                    <div className="stat-content">
                        <div className="stat-value">{getPeriodSessions()}</div>
                        <div className="stat-label">{t('dashboard.stats.recentActivity')}</div>
                        <div className="stat-subtitle">{getTimePeriodLabel().toLowerCase()}</div>
                    </div>
                </div>

                <div className="stat-item">
                    <div className="stat-icon">⚡</div>
                    <div className="stat-content">
                        <div className="stat-value">{getDailyAverage()}</div>
                        <div className="stat-label">{t('dashboard.stats.dailyAverage')}</div>
                        <div className="stat-subtitle">{t('dashboard.subtitles.sessionsPerDay')}</div>
                    </div>
                </div>
            </div>

            <div className="quick-actions">
                <h3 className="quick-actions-title">{t('dashboard.quickActions.title')}</h3>
                <div className="action-buttons">
                    <button className="action-button action-primary">
                        <span className="action-icon">🎓</span>
                        <span>{t('dashboard.quickActions.startLearning')}</span>
                    </button>
                    <button className="action-button action-secondary">
                        <span className="action-icon">📝</span>
                        <span>{t('dashboard.quickActions.takeTest')}</span>
                    </button>
                    <button className="action-button action-secondary">
                        <span className="action-icon">➕</span>
                        <span>{t('dashboard.quickActions.createQuiz')}</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default StatsSummaryCard;
