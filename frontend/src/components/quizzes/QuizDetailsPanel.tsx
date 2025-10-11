import { useState } from 'react';
import { useQuiz } from '../../hooks/useQuiz';
import { useQuizPerformance } from '../../hooks/useQuizPerformance';
import { useQuizSessions } from '../../hooks/useQuizSessions';
import { useAuth } from '../../context/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

// Helper function to decode base64-encoded UTF-8 emoji
const decodeImage = (base64: string): string => {
    try {
        // Decode base64 to binary string
        const binaryString = atob(base64);
        // Convert binary string to UTF-8
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return new TextDecoder('utf-8').decode(bytes);
    } catch (e) {
        console.error('Failed to decode image:', e);
        return '📚';
    }
};
import {
    faGraduationCap,
    faClipboardCheck,
    faEdit,
    faTrash,
    faLayerGroup,
    faCalendarPlus,
    faClock,
    faTag,
    faSignal,
    faDownload,
    faChartLine,
    faChartBar,
    faHashtag,
    faTrophy,
    faChartSimple,
    faArrowTrendUp,
    faCalendarDays,
    faFire
} from '@fortawesome/free-solid-svg-icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface QuizDetailsPanelProps {
    selectedQuizId: number | null;
    onEditClick: (quizId: number) => void;
    onDeleteClick: (quizId: number) => void;
    onStartLearningSession: (quizId: number) => void;
    onStartTestSession: (quizId: number) => void;
}

/**
 * Right panel component for displaying quiz details and actions
 */
function QuizDetailsPanel({
    selectedQuizId,
    onEditClick,
    onDeleteClick,
    onStartLearningSession,
    onStartTestSession,
}: QuizDetailsPanelProps) {
    const { quiz, isLoading, error } = useQuiz(selectedQuizId);
    const { performance, isLoading: perfLoading } = useQuizPerformance(selectedQuizId, 30);
    const { sessions } = useQuizSessions(selectedQuizId, 50);
    const { accessToken } = useAuth();
    const [isExporting, setIsExporting] = useState(false);

    // Get latest test session for "Latest Score" stat
    const latestTestSession = sessions
        ?.filter(s => s.mode === 'test' && s.score !== null)
        .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())[0];

    // Find the date of peak score from activity_trend
    const getPeakScoreInfo = () => {
        if (!performance || Object.keys(performance.activity_trend).length === 0) {
            return { score: null, date: null };
        }

        let maxScore = -1;
        let maxDate = '';

        Object.entries(performance.activity_trend).forEach(([date, data]) => {
            if (data.average_score !== null && data.average_score > maxScore) {
                maxScore = data.average_score;
                maxDate = date;
            }
        });

        return { score: maxScore >= 0 ? Math.round(maxScore) : null, date: maxDate };
    };

    const peakScoreInfo = getPeakScoreInfo();

    // Calculate best streak from activity_trend
    const getBestStreakInfo = () => {
        if (!performance || Object.keys(performance.activity_trend).length === 0) {
            return { days: 0, endDate: null };
        }

        const dates = Object.keys(performance.activity_trend).sort();
        let maxStreak = 0;
        let currentStreak = 0;
        let streakEndDate = '';
        let maxStreakEndDate = '';

        for (let i = 0; i < dates.length; i++) {
            if (i === 0) {
                currentStreak = 1;
                streakEndDate = dates[i];
            } else {
                const prevDate = new Date(dates[i - 1]);
                const currDate = new Date(dates[i]);
                const diffDays = Math.round((currDate.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24));

                if (diffDays === 1) {
                    currentStreak++;
                    streakEndDate = dates[i];
                } else {
                    if (currentStreak > maxStreak) {
                        maxStreak = currentStreak;
                        maxStreakEndDate = streakEndDate;
                    }
                    currentStreak = 1;
                    streakEndDate = dates[i];
                }
            }
        }

        // Check the last streak
        if (currentStreak > maxStreak) {
            maxStreak = currentStreak;
            maxStreakEndDate = streakEndDate;
        }

        return { days: maxStreak, endDate: maxStreakEndDate || null };
    };

    const bestStreakInfo = getBestStreakInfo();

    // Helper function to format date relative to now
    const formatRelativeDate = (dateString: string): string => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInMs = now.getTime() - date.getTime();
        const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

        if (diffInDays === 0) return 'Today';
        if (diffInDays === 1) return 'Yesterday';
        if (diffInDays < 7) return `${diffInDays}d ago`;
        if (diffInDays < 30) return `${Math.floor(diffInDays / 7)}w ago`;
        if (diffInDays < 365) return `${Math.floor(diffInDays / 30)}mo ago`;
        return `${Math.floor(diffInDays / 365)}y ago`;
    };

    // Handle export quiz
    const handleExport = async () => {
        if (!quiz || !accessToken) return;

        setIsExporting(true);
        try {
            const response = await fetch(`/api/v1/quizzes/${quiz.id}/export`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to export quiz');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${quiz.name.replace(/[^a-z0-9]/gi, '_')}_export.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('Failed to export quiz:', err);
            alert('Failed to export quiz. Please try again.');
        } finally {
            setIsExporting(false);
        }
    };

    // Show empty state when no quiz is selected
    if (selectedQuizId === null) {
        return (
            <div className="quiz-details-panel quiz-details-panel--compact">
                <div className="quiz-details-empty-state quiz-details-empty-state--top">
                    <div className="empty-state-icon">📚</div>
                    <h3>No Quiz Selected</h3>
                    <p>Select a quiz from the list to view details and start learning</p>
                </div>
            </div>
        );
    }

    // Show loading state
    if (isLoading) {
        return (
            <div className="quiz-details-panel">
                <div className="loading-spinner">Loading quiz details...</div>
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className="quiz-details-panel">
                <div className="error-message">
                    Failed to load quiz details: {error.message}
                </div>
            </div>
        );
    }

    // Show quiz not found
    if (!quiz) {
        return (
            <div className="quiz-details-panel">
                <div className="error-message">Quiz not found</div>
            </div>
        );
    }

    // Show quiz details
    return (
        <div className="quiz-details-panel quiz-details-panel--compact">
            {/* Compact Header Section */}
            <div className="quiz-compact-header">
                <div className="quiz-compact-title-row">
                    <div className="quiz-compact-title-left">
                        <div className="quiz-compact-icon">{quiz.image ? decodeImage(quiz.image) : '📚'}</div>
                        <h1 className="quiz-compact-name">{quiz.name}</h1>
                    </div>
                    {quiz.created_at && (
                        <div className="quiz-compact-created">
                            <FontAwesomeIcon icon={faCalendarPlus} /> Created {new Date(quiz.created_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                            })}
                        </div>
                    )}
                </div>
                <div className="quiz-compact-badges">
                    <span className="quiz-badge quiz-badge--subject">{quiz.subject}</span>
                    {quiz.category && (
                        <span className="quiz-badge quiz-badge--category">
                            <FontAwesomeIcon icon={faTag} /> {quiz.category}
                        </span>
                    )}
                    {quiz.level && (
                        <span className="quiz-badge quiz-badge--level">
                            <FontAwesomeIcon icon={faSignal} /> {quiz.level}
                        </span>
                    )}
                    <span className="quiz-badge quiz-badge--cards">
                        <FontAwesomeIcon icon={faLayerGroup} /> {quiz.flashcard_count ?? 0} cards
                    </span>
                </div>
                {quiz.description && (
                    <p className="quiz-compact-description-inline">
                        {quiz.description}
                    </p>
                )}
            </div>

            {/* All Action Buttons in One Row */}
            <div className="quiz-all-actions">
                <button
                    className="quiz-action-btn quiz-action-btn--learn"
                    onClick={() => onStartLearningSession(quiz.id)}
                    title="Start Learning Session"
                >
                    <FontAwesomeIcon icon={faGraduationCap} />
                    <span>Learn</span>
                </button>
                <button
                    className="quiz-action-btn quiz-action-btn--test"
                    onClick={() => onStartTestSession(quiz.id)}
                    title="Start Test Session"
                >
                    <FontAwesomeIcon icon={faClipboardCheck} />
                    <span>Test</span>
                </button>
                <button
                    className="quiz-action-btn quiz-action-btn--edit"
                    onClick={() => onEditClick(quiz.id)}
                    title="Edit Quiz"
                >
                    <FontAwesomeIcon icon={faEdit} />
                    <span>Edit</span>
                </button>
                <button
                    className="quiz-action-btn quiz-action-btn--export"
                    onClick={handleExport}
                    disabled={isExporting}
                    title="Export Quiz"
                >
                    <FontAwesomeIcon icon={faDownload} />
                    <span>{isExporting ? '...' : 'Export'}</span>
                </button>
                <button
                    className="quiz-action-btn quiz-action-btn--delete"
                    onClick={() => onDeleteClick(quiz.id)}
                    title="Delete Quiz"
                >
                    <FontAwesomeIcon icon={faTrash} />
                    <span>Delete</span>
                </button>
            </div>

            {/* Statistics Section */}
            <div className="quiz-section">
                <div className="quiz-section-header">
                    <h3 className="quiz-section-title">Statistics</h3>
                    <p className="quiz-section-caption">Your performance metrics (last 30 days)</p>
                </div>
                {perfLoading ? (
                    <div className="loading-spinner">Loading statistics...</div>
                ) : (
                    <div className="quiz-stats-grid quiz-stats-grid--seven">
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faHashtag} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">{performance?.total_sessions ?? 0}</div>
                            <div className="quiz-stat-label">Total Sessions</div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faTrophy} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {latestTestSession?.score !== null && latestTestSession?.score !== undefined
                                    ? `${Math.round(latestTestSession.score)}%`
                                    : '—'}
                            </div>
                            <div className="quiz-stat-label">Latest Score</div>
                            <div className="quiz-stat-date">
                                {latestTestSession?.started_at
                                    ? formatRelativeDate(latestTestSession.started_at)
                                    : 'No data'}
                            </div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faArrowTrendUp} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {performance?.scores.highest !== null && performance?.scores.highest !== undefined
                                    ? `${Math.round(performance.scores.highest)}%`
                                    : '—'}
                            </div>
                            <div className="quiz-stat-label">Max Score</div>
                            <div className="quiz-stat-date">
                                {performance?.test_sessions ? 'Last 30 days' : 'No data'}
                            </div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faChartSimple} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {performance?.scores.lowest !== null && performance?.scores.lowest !== undefined
                                    ? `${Math.round(performance.scores.lowest)}%`
                                    : '—'}
                            </div>
                            <div className="quiz-stat-label">Min Score</div>
                            <div className="quiz-stat-date">
                                {performance?.test_sessions ? 'Last 30 days' : 'No data'}
                            </div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faChartLine} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {performance?.scores.average !== null && performance?.scores.average !== undefined
                                    ? `${Math.round(performance.scores.average)}%`
                                    : '—'}
                            </div>
                            <div className="quiz-stat-label">Avg Score</div>
                            <div className="quiz-stat-date">Last 30 days</div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faCalendarDays} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {performance && Object.keys(performance.activity_trend).length > 0
                                    ? Object.keys(performance.activity_trend).length
                                    : 0}
                            </div>
                            <div className="quiz-stat-label">Days Active</div>
                            <div className="quiz-stat-date">Last 30 days</div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faChartBar} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {peakScoreInfo.score !== null ? `${peakScoreInfo.score}%` : '—'}
                            </div>
                            <div className="quiz-stat-label">Peak Score</div>
                            <div className="quiz-stat-date">
                                {peakScoreInfo.date ? formatRelativeDate(peakScoreInfo.date) : 'No data'}
                            </div>
                        </div>
                        <div className="quiz-stat-card">
                            <FontAwesomeIcon icon={faFire} className="quiz-stat-icon" />
                            <div className="quiz-stat-value">
                                {bestStreakInfo.days > 0 ? bestStreakInfo.days : '—'}
                            </div>
                            <div className="quiz-stat-label">Best Streak</div>
                            <div className="quiz-stat-date">
                                {bestStreakInfo.endDate ? `Ended ${formatRelativeDate(bestStreakInfo.endDate)}` : 'No data'}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Performance Charts */}
            <div className="quiz-section">
                <div className="quiz-section-header">
                    <h3 className="quiz-section-title">Performance Analytics</h3>
                    <p className="quiz-section-caption">Your learning progress and statistics</p>
                </div>
                {perfLoading ? (
                    <div className="loading-spinner">Loading charts...</div>
                ) : (
                    <div className="quiz-charts-grid">
                        {/* Activity Trend Chart */}
                        <div className="quiz-chart-card">
                            <div className="quiz-chart-header">
                                <FontAwesomeIcon icon={faChartLine} className="quiz-chart-icon" />
                                <div>
                                    <h4 className="quiz-chart-title">Activity Trend</h4>
                                    <p className="quiz-chart-subtitle">Average scores over the last 30 days</p>
                                </div>
                            </div>
                            {performance && Object.keys(performance.activity_trend).length > 0 ? (
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={200}>
                                        <LineChart
                                            data={Object.entries(performance.activity_trend)
                                                .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
                                                .map(([date, data]) => ({
                                                    date,
                                                    score: data.average_score,
                                                    sessions: data.sessions
                                                }))}
                                            margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                                            <XAxis
                                                dataKey="date"
                                                stroke="#5B6D83"
                                                tick={{ fontSize: 11 }}
                                                tickFormatter={(value) => {
                                                    const date = new Date(value);
                                                    return `${date.getMonth() + 1}/${date.getDate()}`;
                                                }}
                                            />
                                            <YAxis
                                                stroke="#5B6D83"
                                                tick={{ fontSize: 11 }}
                                                domain={[0, 100]}
                                                width={35}
                                            />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: '#FFFFFF',
                                                    border: '1px solid #E5E7EB',
                                                    borderRadius: '8px',
                                                    padding: '10px',
                                                    fontSize: '12px'
                                                }}
                                                labelFormatter={(value) => {
                                                    const date = new Date(value);
                                                    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                                                }}
                                                formatter={(value: number | null, name: string) => {
                                                    if (name === 'score' && value !== null) {
                                                        return [`${Math.round(value)}%`, 'Avg Score'];
                                                    }
                                                    if (name === 'sessions') {
                                                        return [value, 'Sessions'];
                                                    }
                                                    return [value, name];
                                                }}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="score"
                                                stroke="#6A3FFB"
                                                strokeWidth={2}
                                                dot={{ fill: '#6A3FFB', r: 3 }}
                                                activeDot={{ r: 5 }}
                                                connectNulls
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            ) : (
                                <div className="quiz-chart-placeholder">
                                    <div className="quiz-chart-placeholder-icon">📈</div>
                                    <p className="quiz-chart-placeholder-text">No session data available yet</p>
                                    <p className="quiz-chart-placeholder-hint">Start a learning session to see your progress</p>
                                </div>
                            )}
                        </div>

                        {/* Session Distribution Chart */}
                        <div className="quiz-chart-card">
                            <div className="quiz-chart-header">
                                <FontAwesomeIcon icon={faChartBar} className="quiz-chart-icon" />
                                <div>
                                    <h4 className="quiz-chart-title">Session Distribution</h4>
                                    <p className="quiz-chart-subtitle">Learn vs Test sessions</p>
                                </div>
                            </div>
                            {performance && performance.total_sessions > 0 ? (
                                <div className="quiz-chart-visual">
                                    <div className="quiz-chart-distribution">
                                        <div className="distribution-bar-container">
                                            <div
                                                className="distribution-bar distribution-bar--learn"
                                                style={{
                                                    width: `${(performance.learn_sessions / performance.total_sessions) * 100}%`
                                                }}
                                                title={`Learn: ${performance.learn_sessions} sessions`}
                                            >
                                                {performance.learn_sessions > 0 && (
                                                    <span className="distribution-bar-label">{performance.learn_sessions}</span>
                                                )}
                                            </div>
                                            <div
                                                className="distribution-bar distribution-bar--test"
                                                style={{
                                                    width: `${(performance.test_sessions / performance.total_sessions) * 100}%`
                                                }}
                                                title={`Test: ${performance.test_sessions} sessions`}
                                            >
                                                {performance.test_sessions > 0 && (
                                                    <span className="distribution-bar-label">{performance.test_sessions}</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="distribution-legend">
                                            <div className="legend-item">
                                                <span className="legend-color legend-color--learn"></span>
                                                <span>Learn ({performance.learn_sessions})</span>
                                            </div>
                                            <div className="legend-item">
                                                <span className="legend-color legend-color--test"></span>
                                                <span>Test ({performance.test_sessions})</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="quiz-chart-placeholder">
                                    <div className="quiz-chart-placeholder-icon">📊</div>
                                    <p className="quiz-chart-placeholder-text">No session data available yet</p>
                                    <p className="quiz-chart-placeholder-hint">Complete sessions to view distribution</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default QuizDetailsPanel;
