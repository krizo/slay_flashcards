import { useQuiz } from '../../hooks/useQuiz';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGraduationCap, faClipboardCheck, faEdit, faTrash } from '@fortawesome/free-solid-svg-icons';

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

    // Show empty state when no quiz is selected
    if (selectedQuizId === null) {
        return (
            <div className="quiz-details-panel">
                <div className="quiz-details-empty-state">
                    <p>Select a quiz from the list to view details</p>
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
        <div className="quiz-details-panel">
            {/* Header Section */}
            <div className="quiz-details-header">
                <div className="quiz-details-title-section">
                    <h1 className="quiz-details-name">{quiz.name}</h1>
                    <span className="quiz-details-subject-badge">{quiz.subject}</span>
                </div>

                {/* Action Buttons */}
                <div className="quiz-details-actions">
                    <button
                        className="quiz-action-button quiz-action-button--primary"
                        onClick={() => onStartLearningSession(quiz.id)}
                        title="Start Learning Session"
                    >
                        <FontAwesomeIcon icon={faGraduationCap} /> Start Learning
                    </button>
                    <button
                        className="quiz-action-button quiz-action-button--primary"
                        onClick={() => onStartTestSession(quiz.id)}
                        title="Start Test Session"
                    >
                        <FontAwesomeIcon icon={faClipboardCheck} /> Start Test
                    </button>
                    <button
                        className="quiz-action-button quiz-action-button--secondary"
                        onClick={() => onEditClick(quiz.id)}
                        title="Edit Quiz"
                    >
                        <FontAwesomeIcon icon={faEdit} /> Edit
                    </button>
                    <button
                        className="quiz-action-button quiz-action-button--danger"
                        onClick={() => onDeleteClick(quiz.id)}
                        title="Delete Quiz"
                    >
                        <FontAwesomeIcon icon={faTrash} /> Delete
                    </button>
                </div>
            </div>

            {/* Details Cards */}
            <div className="quiz-details-content">
                {/* Description Card */}
                <div className="quiz-details-card">
                    <h2 className="quiz-details-card-title">Description</h2>
                    <p className="quiz-details-description">
                        {quiz.description || 'No description provided'}
                    </p>
                </div>

                {/* Statistics Card */}
                <div className="quiz-details-card">
                    <h2 className="quiz-details-card-title">Statistics</h2>
                    <div className="quiz-stats-grid">
                        <div className="quiz-stat-item">
                            <span className="quiz-stat-label">Flashcards</span>
                            <span className="quiz-stat-value">
                                {quiz.flashcard_count ?? 0}
                            </span>
                        </div>
                        {quiz.created_at && (
                            <div className="quiz-stat-item">
                                <span className="quiz-stat-label">Created</span>
                                <span className="quiz-stat-value">
                                    {new Date(quiz.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        )}
                        {quiz.updated_at && (
                            <div className="quiz-stat-item">
                                <span className="quiz-stat-label">Last Updated</span>
                                <span className="quiz-stat-value">
                                    {new Date(quiz.updated_at).toLocaleDateString()}
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default QuizDetailsPanel;
