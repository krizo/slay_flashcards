import { useState } from 'react';
import { TestResult } from '../../types';

interface TestResultsPageProps {
    testResults: TestResult;
    lastScore?: number | null;
    averageScore?: number | null;
    onGoToQuizzes: () => void;
    onRetry: () => void;
    onLearn: () => void;
}

function TestResultsPage({
    testResults,
    lastScore,
    averageScore,
    onGoToQuizzes,
    onRetry,
    onLearn
}: TestResultsPageProps) {
    const { final_score, correct, total, breakdown } = testResults;

    // State for interactive cards
    const [selectedCardId, setSelectedCardId] = useState<number | null>(null);
    const [hoveredCardId, setHoveredCardId] = useState<number | null>(null);
    const [showOnlyMistakes, setShowOnlyMistakes] = useState(false);

    // Calculate total from breakdown array if total is not provided or is 0
    const totalCount = (typeof total === 'number' && total > 0) ? total : breakdown.length;

    // Ensure correct is a valid number
    const correctCount = typeof correct === 'number' ? correct : 0;

    // Calculate incorrect count
    const incorrectCount = totalCount - correctCount;
    const hasMistakes = incorrectCount > 0;

    // Calculate comparison to last score
    const scoreDiff = lastScore !== null && lastScore !== undefined
        ? final_score - lastScore
        : null;

    // Determine score color class
    const getScoreColorClass = (score: number) => {
        if (score >= 80) return 'test-score-value--excellent';
        if (score >= 60) return 'test-score-value--good';
        if (score >= 50) return 'test-score-value--fair';
        return 'test-score-value--poor';
    };

    // Handle card click - toggle selected state
    const handleCardClick = (flashcardId: number) => {
        setSelectedCardId(selectedCardId === flashcardId ? null : flashcardId);
    };

    // Check if card should show answers
    const shouldShowAnswers = (flashcardId: number) => {
        return selectedCardId === flashcardId || hoveredCardId === flashcardId;
    };

    // Filter breakdown based on showOnlyMistakes
    const filteredBreakdown = showOnlyMistakes
        ? breakdown.filter(item => item.evaluation === 'incorrect')
        : breakdown;

    return (
        <div className="test-results-page">
            {/* Main Summary Area */}
            <div className="test-results-main">
                <div className="test-results-header">
                    <span className="test-results-icon">
                        {final_score >= 80 ? '🎉' : final_score >= 60 ? '👍' : '💪'}
                    </span>
                    <h1 className="test-results-title">Test Complete!</h1>
                    <div className="test-results-score">
                        <span className={`test-score-value ${getScoreColorClass(final_score)}`}>
                            {Math.round(final_score)}%
                        </span>
                        <span className="test-score-label">
                            {correctCount} out of {totalCount} correct
                        </span>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="test-stats-grid">
                    <div className="test-stat-card">
                        <div className="test-stat-icon">✓</div>
                        <div className="test-stat-content">
                            <div className="test-stat-value">{correctCount}</div>
                            <div className="test-stat-label">Correct Answers</div>
                        </div>
                    </div>

                    <div className="test-stat-card">
                        <div className="test-stat-icon">✗</div>
                        <div className="test-stat-content">
                            <div className="test-stat-value">{incorrectCount}</div>
                            <div className="test-stat-label">Incorrect Answers</div>
                        </div>
                    </div>

                    <div className="test-stat-card">
                        <div className="test-stat-icon">📊</div>
                        <div className="test-stat-content">
                            <div className="test-stat-value">
                                {averageScore !== null && averageScore !== undefined
                                    ? `${Math.round(averageScore)}%`
                                    : '—'}
                            </div>
                            <div className="test-stat-label">Your Average</div>
                        </div>
                    </div>

                    <div className="test-stat-card">
                        <div className="test-stat-icon">🎯</div>
                        <div className="test-stat-content">
                            <div className="test-stat-value">
                                {totalCount}
                            </div>
                            <div className="test-stat-label">Total Questions</div>
                        </div>
                    </div>

                    <div className="test-stat-card">
                        <div className="test-stat-icon">⏱️</div>
                        <div className="test-stat-content">
                            <div className="test-stat-value">
                                {testResults.duration
                                    ? `${Math.floor(testResults.duration / 60)}:${String(testResults.duration % 60).padStart(2, '0')}`
                                    : '—'}
                            </div>
                            <div className="test-stat-label">Time Taken</div>
                        </div>
                    </div>

                    <div className="test-stat-card">
                        <div className="test-stat-icon">
                            {lastScore !== null && lastScore !== undefined
                                ? (scoreDiff! > 0 ? '📈' : scoreDiff! < 0 ? '📉' : '➡️')
                                : '📋'}
                        </div>
                        <div className="test-stat-content">
                            <div className={`test-stat-value ${scoreDiff !== null && scoreDiff > 0 ? 'test-stat-value--positive' : scoreDiff !== null && scoreDiff < 0 ? 'test-stat-value--negative' : ''}`}>
                                {lastScore !== null && lastScore !== undefined
                                    ? `${Math.round(lastScore)}%`
                                    : '—'}
                            </div>
                            <div className="test-stat-label">Last Score</div>
                        </div>
                    </div>
                </div>

                {/* Performance Message */}
                <div className="test-performance-message">
                    {final_score >= 80 ? (
                        <p>🌟 Excellent work! You've mastered this quiz!</p>
                    ) : final_score >= 60 ? (
                        <p>👏 Good job! Keep practicing to improve your score.</p>
                    ) : (
                        <p>💪 Keep going! Review the mistakes and try again.</p>
                    )}
                </div>

                {/* Action Buttons */}
                <div className="test-results-actions">
                    <button
                        className="control-button control-button--primary"
                        onClick={onRetry}
                    >
                        Retry Test
                    </button>
                    <button
                        className="control-button control-button--primary"
                        onClick={onLearn}
                    >
                        Learn Mode
                    </button>
                    <button
                        className="control-button control-button--secondary"
                        onClick={onGoToQuizzes}
                    >
                        Go to Quizzes
                    </button>
                </div>
            </div>

            {/* Timeline Sidebar with Results */}
            <div className="test-results-timeline">
                <div className="timeline-content">
                    <div className="timeline-progress-badge">
                        Test Results {showOnlyMistakes && `(${filteredBreakdown.length} mistakes)`}
                    </div>
                    {filteredBreakdown.map((item) => {
                        const showAnswers = shouldShowAnswers(item.flashcard_id);
                        // Find original index in full breakdown
                        const originalIndex = breakdown.findIndex(b => b.flashcard_id === item.flashcard_id);
                        return (
                            <div
                                key={item.flashcard_id}
                                className={`timeline-card timeline-card--${item.evaluation} timeline-card--interactive`}
                                onClick={() => handleCardClick(item.flashcard_id)}
                                onMouseEnter={() => setHoveredCardId(item.flashcard_id)}
                                onMouseLeave={() => setHoveredCardId(null)}
                            >
                                <div className="timeline-card-header">
                                    <span className="timeline-card-number">
                                        {originalIndex + 1}
                                    </span>
                                    <span className="timeline-card-result-icon">
                                        {item.evaluation === 'correct' ? '✓' : '✗'}
                                    </span>
                                </div>
                                <div className="timeline-card-title">
                                    {item.question}
                                </div>
                                {showAnswers && (
                                    <>
                                        <div className="timeline-card-answer">
                                            <span className="timeline-answer-label">Your answer:</span>
                                            <span className="timeline-answer-text">
                                                {item.user_answer || '(no answer)'}
                                            </span>
                                        </div>
                                        <div className="timeline-card-answer">
                                            <span className="timeline-answer-label">Correct answer:</span>
                                            <span className="timeline-answer-text timeline-answer-text--correct">
                                                {item.correct_answer}
                                            </span>
                                        </div>
                                    </>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Filter Button */}
                {hasMistakes && (
                    <div className="timeline-filter-controls">
                        <button
                            className={`timeline-filter-button ${showOnlyMistakes ? 'timeline-filter-button--active' : ''}`}
                            onClick={() => setShowOnlyMistakes(!showOnlyMistakes)}
                        >
                            {showOnlyMistakes ? (
                                <>
                                    <span className="filter-icon">✓</span> Show All ({totalCount})
                                </>
                            ) : (
                                <>
                                    <span className="filter-icon">✗</span> Show Mistakes Only ({incorrectCount})
                                </>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default TestResultsPage;
