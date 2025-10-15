import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import QuizListPanel from '../components/quizzes/QuizListPanel';
import QuizDetailsPanel from '../components/quizzes/QuizDetailsPanel';
import { useQuizFilters } from '../hooks/useQuizFilters';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

/**
 * Quiz Management Page with List-Detail layout
 */
function QuizzesPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { accessToken } = useAuth();
    const [selectedQuizId, setSelectedQuizId] = useState<number | null>(null);
    const [quizListKey, setQuizListKey] = useState(0);

    // Filter states
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [selectedSubject, setSelectedSubject] = useState<string>('');
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [selectedLevel, setSelectedLevel] = useState<string>('');

    // Fetch filter options
    const { subjects, categories, levels, isLoading: filtersLoading } = useQuizFilters();

    // Handle quiz selection from list
    const handleSelectQuiz = (quizId: number) => {
        setSelectedQuizId(quizId);
    };

    // Handle new quiz button click
    const handleNewQuizClick = () => {
        navigate('/quizzes/create');
    };

    // Handle edit button click
    const handleEditClick = (quizId: number) => {
        navigate(`/quizzes/${quizId}/edit`);
    };

    // Handle delete button click
    const handleDeleteClick = async (quizId: number) => {
        if (!accessToken) {
            return;
        }

        // Confirm deletion
        const confirmDelete = window.confirm(t('quizzes.deleteConfirmation'));

        if (!confirmDelete) {
            return;
        }

        try {
            // Verify quiz exists before attempting deletion
            const quiz = await api.get(`/quizzes/${quizId}`, accessToken);

            if (!quiz) {
                alert(t('quizzes.quizNotFound'));
                setQuizListKey(prev => prev + 1);
                setSelectedQuizId(null);
                return;
            }

            // Call API to delete quiz
            await api.delete(`/quizzes/${quizId}`, accessToken);

            // Clear selection and refetch list
            setSelectedQuizId(null);
            setQuizListKey(prev => prev + 1);
        } catch (error: any) {
            console.error('Failed to delete quiz:', error);

            // Check if quiz not found
            if (error.response?.status === 404 || error.message?.includes('not found')) {
                alert(t('quizzes.quizNotFound'));
                setSelectedQuizId(null);
                setQuizListKey(prev => prev + 1);
            } else {
                alert(t('quizzes.deleteFailed'));
            }
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


    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">{t('quizzes.title')}</h1>
                <p className="page-description">
                    {t('quizzes.description')}
                </p>
            </div>

            {/* Filters Bar */}
            <div className="quiz-filters-bar">
                <input
                    type="text"
                    className="quiz-filter-input"
                    placeholder={t('quizzes.searchQuizzes')}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />

                <select
                    className="quiz-filter-select"
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    disabled={filtersLoading}
                >
                    <option value="">{t('quizzes.allSubjects')}</option>
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
                    <option value="">{t('quizzes.allCategories')}</option>
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
                    <option value="">{t('quizzes.allLevels')}</option>
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
                    {t('quizzes.newQuiz')}
                </button>
            </div>

            <div className="quiz-management-layout">
                {/* Left Panel: Quiz List */}
                <QuizListPanel
                    key={quizListKey}
                    selectedQuizId={selectedQuizId}
                    onSelectQuiz={handleSelectQuiz}
                    searchQuery={searchQuery}
                    selectedSubject={selectedSubject}
                    selectedCategory={selectedCategory}
                    selectedLevel={selectedLevel}
                />

                {/* Right Panel: Quiz Details */}
                <QuizDetailsPanel
                    selectedQuizId={selectedQuizId}
                    onEditClick={handleEditClick}
                    onDeleteClick={handleDeleteClick}
                    onStartLearningSession={handleStartLearningSession}
                    onStartTestSession={handleStartTestSession}
                />
            </div>
        </div>
    );
}

export default QuizzesPage;
