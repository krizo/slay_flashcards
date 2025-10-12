import { useState, useEffect } from 'react';
import { useQuizList } from '../../hooks/useQuizList';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar as faStarSolid } from '@fortawesome/free-solid-svg-icons';
import { faStar as faStarRegular } from '@fortawesome/free-regular-svg-icons';
import { api } from '../../services/apiClient';
import { useAuth } from '../../context/AuthContext';

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

interface QuizListPanelProps {
    selectedQuizId: number | null;
    onSelectQuiz: (quizId: number) => void;
    searchQuery: string;
    selectedSubject: string;
    selectedCategory: string;
    selectedLevel: string;
}

/**
 * Left panel component for displaying quiz list
 */
function QuizListPanel({
    selectedQuizId,
    onSelectQuiz,
    searchQuery,
    selectedSubject,
    selectedCategory,
    selectedLevel,
}: QuizListPanelProps) {
    const { accessToken } = useAuth();

    // Debounce search query
    const [debouncedQuery, setDebouncedQuery] = useState<string>('');
    // Local favourite state for optimistic updates
    const [localFavourites, setLocalFavourites] = useState<Record<number, boolean>>({});

    // Debounce search input
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(searchQuery);
        }, 500);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Fetch quizzes with filters
    const { quizzes, isLoading, error, refetch } = useQuizList({
        nameContains: debouncedQuery || undefined,
        subject: selectedSubject || undefined,
        category: selectedCategory || undefined,
        level: selectedLevel || undefined,
    });

    // Handle favourite toggle
    const handleToggleFavourite = async (e: React.MouseEvent, quizId: number, currentFavourite: boolean) => {
        e.stopPropagation(); // Prevent quiz selection when clicking star

        if (!accessToken) return;

        // Optimistic update
        setLocalFavourites(prev => ({ ...prev, [quizId]: !currentFavourite }));

        try {
            await api.patch(`/quizzes/${quizId}/favourite?favourite=${!currentFavourite}`, null, accessToken);
            // Refetch to get updated sort order
            refetch();
        } catch (error) {
            console.error('Failed to toggle favourite:', error);
            // Revert optimistic update on error
            setLocalFavourites(prev => ({ ...prev, [quizId]: currentFavourite }));
        }
    };

    return (
        <div className="quiz-list-panel">
            {/* Quiz List */}
            <div className="quiz-list-container">
                {isLoading ? (
                    <div className="loading-spinner">Loading quizzes...</div>
                ) : error ? (
                    <div className="error-message">
                        Failed to load quizzes: {error.message}
                    </div>
                ) : quizzes && quizzes.length > 0 ? (
                    <ul className="quiz-list">
                        {quizzes.map((quiz) => {
                            // Build category/level subtitle if they exist
                            const subtitleParts = [];
                            if (quiz.category) subtitleParts.push(quiz.category);
                            if (quiz.level) subtitleParts.push(quiz.level);
                            const subtitle = subtitleParts.length > 0 ? subtitleParts.join(' • ') : null;

                            return (
                                <li
                                    key={quiz.id}
                                    className={`quiz-list-item ${
                                        quiz.id === selectedQuizId ? 'quiz-list-item--active' : ''
                                    }`}
                                    onClick={() => onSelectQuiz(quiz.id)}
                                >
                                    <div className="quiz-list-item-icon">
                                        {quiz.image ? decodeImage(quiz.image) : '📚'}
                                    </div>
                                    <div className="quiz-list-item-content">
                                        <div className="quiz-list-item-title-row">
                                            <h3 className="quiz-list-item-name">{quiz.name}</h3>
                                            <span className="quiz-list-item-badge">{quiz.subject}</span>
                                            <button
                                                className={`quiz-favourite-btn ${
                                                    (localFavourites[quiz.id] !== undefined
                                                        ? localFavourites[quiz.id]
                                                        : quiz.favourite)
                                                        ? 'quiz-favourite-btn--active'
                                                        : ''
                                                }`}
                                                onClick={(e) =>
                                                    handleToggleFavourite(
                                                        e,
                                                        quiz.id,
                                                        localFavourites[quiz.id] !== undefined
                                                            ? localFavourites[quiz.id]
                                                            : quiz.favourite
                                                    )
                                                }
                                                title={
                                                    (localFavourites[quiz.id] !== undefined
                                                        ? localFavourites[quiz.id]
                                                        : quiz.favourite)
                                                        ? 'Remove from favourites'
                                                        : 'Add to favourites'
                                                }
                                                aria-label="Toggle favourite"
                                            >
                                                <FontAwesomeIcon
                                                    icon={
                                                        (localFavourites[quiz.id] !== undefined
                                                            ? localFavourites[quiz.id]
                                                            : quiz.favourite)
                                                            ? faStarSolid
                                                            : faStarRegular
                                                    }
                                                />
                                            </button>
                                        </div>
                                        {subtitle && (
                                            <div className="quiz-list-item-subtitle">
                                                {subtitle}
                                            </div>
                                        )}
                                        {quiz.flashcard_count !== undefined && (
                                            <p className="quiz-list-item-meta">
                                                {quiz.flashcard_count} flashcard
                                                {quiz.flashcard_count !== 1 ? 's' : ''}
                                            </p>
                                        )}
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                ) : (
                    <div className="empty-state">
                        <p>No quizzes found</p>
                        <p className="empty-state-hint">
                            {searchQuery || selectedSubject || selectedCategory || selectedLevel
                                ? 'Try adjusting your filters'
                                : 'Create your first quiz to get started'}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default QuizListPanel;
