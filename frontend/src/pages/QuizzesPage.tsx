import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import QuizListPanel from '../components/quizzes/QuizListPanel';
import QuizDetailsPanel from '../components/quizzes/QuizDetailsPanel';
import QuizCreateForm from '../components/quizzes/QuizCreateForm';
import QuizUpdateForm from '../components/quizzes/QuizUpdateForm';
import { useQuiz } from '../hooks/useQuiz';
import { useQuizList } from '../hooks/useQuizList';
import { useQuizFilters } from '../hooks/useQuizFilters';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

/**
 * Quiz Management Page with List-Detail layout
 */
function QuizzesPage() {
    const navigate = useNavigate();
    const { accessToken } = useAuth();
    const [selectedQuizId, setSelectedQuizId] = useState<number | null>(null);
    const [isCreatingNewQuiz, setIsCreatingNewQuiz] = useState(false);
    const [isEditingQuiz, setIsEditingQuiz] = useState(false);

    // Filter states
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [selectedSubject, setSelectedSubject] = useState<string>('');
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [selectedLevel, setSelectedLevel] = useState<string>('');

    // Fetch quiz list for refetching after operations
    const { refetch: refetchQuizList } = useQuizList();

    // Fetch filter options
    const { subjects, categories, levels, isLoading: filtersLoading } = useQuizFilters();

    // Fetch selected quiz for edit form
    const { quiz: selectedQuiz } = useQuiz(isEditingQuiz ? selectedQuizId : null);

    // Handle quiz selection from list
    const handleSelectQuiz = (quizId: number) => {
        setSelectedQuizId(quizId);
        setIsCreatingNewQuiz(false);
        setIsEditingQuiz(false);
    };

    // Handle new quiz button click
    const handleNewQuizClick = () => {
        setIsCreatingNewQuiz(true);
        setIsEditingQuiz(false);
        setSelectedQuizId(null);
    };

    // Handle quiz creation success
    const handleCreateSuccess = () => {
        setIsCreatingNewQuiz(false);
        refetchQuizList();
        // Optionally select the newly created quiz
    };

    // Handle quiz creation cancel
    const handleCreateCancel = () => {
        setIsCreatingNewQuiz(false);
    };

    // Handle edit button click
    const handleEditClick = (quizId: number) => {
        setSelectedQuizId(quizId);
        setIsEditingQuiz(true);
        setIsCreatingNewQuiz(false);
    };

    // Handle quiz update success
    const handleUpdateSuccess = () => {
        setIsEditingQuiz(false);
        refetchQuizList();
    };

    // Handle quiz update cancel
    const handleUpdateCancel = () => {
        setIsEditingQuiz(false);
    };

    // Handle delete button click
    const handleDeleteClick = async (quizId: number) => {
        if (!accessToken) {
            return;
        }

        // Confirm deletion
        const confirmDelete = window.confirm(
            'Are you sure you want to delete this quiz? This action cannot be undone.'
        );

        if (!confirmDelete) {
            return;
        }

        try {
            // Call API to delete quiz
            await api.delete(`/quizzes/${quizId}`, accessToken);

            // Clear selection and refetch list
            setSelectedQuizId(null);
            setIsEditingQuiz(false);
            refetchQuizList();
        } catch (error) {
            console.error('Failed to delete quiz:', error);
            alert('Failed to delete quiz. Please try again.');
        }
    };

    // Handle start learning session button click
    const handleStartLearningSession = (quizId: number) => {
        // Navigate to learning session page with quiz ID and mode=learn
        navigate(`/learning-session?quizId=${quizId}&mode=learn`);
    };

    // Handle start test session button click
    const handleStartTestSession = (quizId: number) => {
        // Navigate to learning session page with quiz ID and mode=test
        navigate(`/learning-session?quizId=${quizId}&mode=test`);
    };

    // Determine which component to show in right panel
    const renderRightPanel = () => {
        if (isCreatingNewQuiz) {
            return (
                <QuizCreateForm
                    onSuccess={handleCreateSuccess}
                    onCancel={handleCreateCancel}
                />
            );
        }

        if (isEditingQuiz && selectedQuiz) {
            return (
                <QuizUpdateForm
                    quiz={selectedQuiz}
                    onSuccess={handleUpdateSuccess}
                    onCancel={handleUpdateCancel}
                />
            );
        }

        return (
            <QuizDetailsPanel
                selectedQuizId={selectedQuizId}
                onEditClick={handleEditClick}
                onDeleteClick={handleDeleteClick}
                onStartLearningSession={handleStartLearningSession}
                onStartTestSession={handleStartTestSession}
            />
        );
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Quizzes</h1>
                <p className="page-description">
                    Manage your flashcard quizzes and start learning sessions
                </p>
            </div>

            {/* Filters Bar */}
            <div className="quiz-filters-bar">
                <input
                    type="text"
                    className="quiz-filter-input"
                    placeholder="🔍 Search quizzes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />

                <select
                    className="quiz-filter-select"
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    disabled={filtersLoading}
                >
                    <option value="">All Subjects</option>
                    {subjects?.map((subject) => (
                        <option key={subject} value={subject}>
                            {subject}
                        </option>
                    ))}
                </select>

                <select
                    className="quiz-filter-select"
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    disabled={filtersLoading}
                >
                    <option value="">All Categories</option>
                    {categories?.map((category) => (
                        <option key={category} value={category}>
                            {category}
                        </option>
                    ))}
                </select>

                <select
                    className="quiz-filter-select"
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    disabled={filtersLoading}
                >
                    <option value="">All Levels</option>
                    {levels?.map((level) => (
                        <option key={level} value={level}>
                            {level}
                        </option>
                    ))}
                </select>

                <button
                    className="quiz-action-button quiz-action-button--primary"
                    onClick={handleNewQuizClick}
                >
                    + New Quiz
                </button>
            </div>

            <div className="quiz-management-layout">
                {/* Left Panel: Quiz List */}
                <QuizListPanel
                    selectedQuizId={selectedQuizId}
                    onSelectQuiz={handleSelectQuiz}
                    searchQuery={searchQuery}
                    selectedSubject={selectedSubject}
                    selectedCategory={selectedCategory}
                    selectedLevel={selectedLevel}
                />

                {/* Right Panel: Details/Forms */}
                {renderRightPanel()}
            </div>
        </div>
    );
}

export default QuizzesPage;
