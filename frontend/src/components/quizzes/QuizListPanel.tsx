import { useState, useEffect } from 'react';
import { useQuizList } from '../../hooks/useQuizList';

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
    // Debounce search query
    const [debouncedQuery, setDebouncedQuery] = useState<string>('');

    // Debounce search input
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedQuery(searchQuery);
        }, 500);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Fetch quizzes with filters
    const { quizzes, isLoading, error } = useQuizList({
        nameContains: debouncedQuery || undefined,
        subject: selectedSubject || undefined,
        category: selectedCategory || undefined,
        level: selectedLevel || undefined,
    });

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
                                        <div className="quiz-list-item-header">
                                            <h3 className="quiz-list-item-name">{quiz.name}</h3>
                                            <span className="quiz-list-item-badge">{quiz.subject}</span>
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
