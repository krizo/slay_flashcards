import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Quiz, FlashcardData, Tag } from '../types';
import apiClient from '../services/apiClient';
import './QuizSummaryPage.css';

function QuizSummaryPage() {
    const { t } = useTranslation();
    const { quizId } = useParams<{ quizId: string }>();
    const navigate = useNavigate();

    const [quiz, setQuiz] = useState<Quiz | null>(null);
    const [flashcards, setFlashcards] = useState<FlashcardData[]>([]);
    const [tags, setTags] = useState<Tag[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isPublishing, setIsPublishing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load quiz, flashcards, and tags
    useEffect(() => {
        const loadData = async () => {
            if (!quizId) return;

            setIsLoading(true);
            setError(null);

            try {
                // Load quiz
                const quizResponse = await apiClient.get<{ data: Quiz }>(`/quizzes/${quizId}`);
                setQuiz(quizResponse.data.data);

                // Load flashcards
                const flashcardsResponse = await apiClient.get<{ data: FlashcardData[] }>(
                    `/quizzes/${quizId}/flashcards`
                );
                setFlashcards(flashcardsResponse.data.data || []);

                // Load tags if quiz has tag_ids
                if (quizResponse.data.data.tag_ids && quizResponse.data.data.tag_ids.length > 0) {
                    const tagsResponse = await apiClient.get<{ data: Tag[] }>('/tags/');
                    const allTags = tagsResponse.data.data || [];
                    const quizTags = allTags.filter(tag =>
                        quizResponse.data.data.tag_ids?.includes(tag.id)
                    );
                    setTags(quizTags);
                }
            } catch (err: any) {
                console.error('Failed to load quiz data:', err);
                setError(err.message || 'Failed to load quiz data');
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, [quizId]);

    // Publish quiz
    const handlePublish = async () => {
        if (!quiz) return;

        setIsPublishing(true);
        setError(null);

        try {
            await apiClient.put(`/quizzes/${quiz.id}`, {
                is_draft: false,
                status: 'published',
            });

            // Navigate to quizzes list
            navigate('/quizzes');
        } catch (err: any) {
            console.error('Failed to publish quiz:', err);
            setError(err.message || 'Failed to publish quiz');
            setIsPublishing(false);
        }
    };

    // Continue editing
    const handleEdit = () => {
        if (!quiz) return;
        navigate(`/quizzes/${quiz.id}/edit`);
    };

    // Go back to quizzes
    const handleBackToQuizzes = () => {
        navigate('/quizzes');
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="quiz-summary-page">
                <div className="summary-loading">
                    <div className="loading-spinner"></div>
                    <p>{t('common.loading')}</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !quiz) {
        return (
            <div className="quiz-summary-page">
                <div className="summary-error">
                    <span className="error-icon">⚠️</span>
                    <h2>{t('common.error')}</h2>
                    <p>{error || 'Quiz not found'}</p>
                    <button
                        className="action-button action-button--primary"
                        onClick={handleBackToQuizzes}
                    >
                        {t('createQuiz.backToQuizzes')}
                    </button>
                </div>
            </div>
        );
    }

    const getStatusBadgeClass = () => {
        switch (quiz.status) {
            case 'published':
                return 'status-badge status-badge--published';
            case 'archived':
                return 'status-badge status-badge--archived';
            default:
                return 'status-badge status-badge--draft';
        }
    };

    const canPublish = flashcards.length > 0 && quiz.is_draft;

    return (
        <div className="quiz-summary-page">
            <div className="summary-container">
                {/* Header */}
                <div className="summary-header">
                    <div>
                        <h1>{t('quizSummary.title')}</h1>
                        <p className="summary-subtitle">{t('quizSummary.subtitle')}</p>
                    </div>
                    <div className={getStatusBadgeClass()}>
                        {t(`quizEditor.${quiz.status || 'draft'}`)}
                    </div>
                </div>

                {/* Quiz Details */}
                <div className="summary-section">
                    <h2 className="section-title">{t('quizSummary.quizDetails')}</h2>

                    <div className="quiz-details-grid">
                        {quiz.image && (
                            <div className="quiz-image-preview">
                                <img
                                    src={`data:image/png;base64,${quiz.image}`}
                                    alt={quiz.name}
                                />
                            </div>
                        )}

                        <div className="quiz-info">
                            <div className="info-row">
                                <span className="info-label">{t('quizEditor.name')}:</span>
                                <span className="info-value">{quiz.name}</span>
                            </div>

                            <div className="info-row">
                                <span className="info-label">{t('quizEditor.subject')}:</span>
                                <span className="info-value">{quiz.subject}</span>
                            </div>

                            {quiz.category && (
                                <div className="info-row">
                                    <span className="info-label">{t('quizEditor.category')}:</span>
                                    <span className="info-value">{quiz.category}</span>
                                </div>
                            )}

                            {quiz.level && (
                                <div className="info-row">
                                    <span className="info-label">{t('quizEditor.level')}:</span>
                                    <span className="info-value">{quiz.level}</span>
                                </div>
                            )}

                            {quiz.description && (
                                <div className="info-row">
                                    <span className="info-label">{t('quizEditor.description')}:</span>
                                    <span className="info-value">{quiz.description}</span>
                                </div>
                            )}

                            {tags.length > 0 && (
                                <div className="info-row">
                                    <span className="info-label">{t('quizEditor.tags')}:</span>
                                    <div className="tags-list">
                                        {tags.map(tag => (
                                            <span
                                                key={tag.id}
                                                className="tag-badge"
                                                style={{
                                                    backgroundColor: tag.color || '#3B82F6',
                                                    color: 'white',
                                                }}
                                            >
                                                {tag.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Flashcards List */}
                <div className="summary-section">
                    <h2 className="section-title">
                        {t('quizSummary.flashcards')} ({flashcards.length})
                    </h2>

                    {flashcards.length === 0 ? (
                        <div className="empty-state">
                            <p>{t('quizSummary.noFlashcards')}</p>
                        </div>
                    ) : (
                        <div className="flashcards-list">
                            {flashcards.map((flashcard, index) => (
                                <div key={flashcard.id} className="flashcard-summary-item">
                                    <div className="flashcard-number">{index + 1}</div>
                                    <div className="flashcard-content">
                                        <div className="flashcard-question">
                                            <span className="flashcard-emoji">{flashcard.question.emoji}</span>
                                            <div>
                                                <div className="flashcard-title">
                                                    {flashcard.question.title}
                                                </div>
                                                <div className="flashcard-text">
                                                    {flashcard.question.text}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flashcard-answer">
                                            <span className="answer-type-badge">
                                                {flashcard.answer.type}
                                            </span>
                                            <span className="answer-text">
                                                {flashcard.answer.text}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="summary-actions">
                    <button
                        className="action-button action-button--secondary"
                        onClick={handleBackToQuizzes}
                        disabled={isPublishing}
                    >
                        {t('createQuiz.backToQuizzes')}
                    </button>

                    <div className="summary-actions-right">
                        <button
                            className="action-button action-button--outline"
                            onClick={handleEdit}
                            disabled={isPublishing}
                        >
                            {t('quizSummary.continueEditing')}
                        </button>

                        {canPublish && (
                            <button
                                className="action-button action-button--primary"
                                onClick={handlePublish}
                                disabled={isPublishing || flashcards.length === 0}
                            >
                                {isPublishing ? t('quizSummary.publishing') : t('quizSummary.publish')}
                            </button>
                        )}

                        {!canPublish && !quiz.is_draft && (
                            <button
                                className="action-button action-button--primary"
                                onClick={handleBackToQuizzes}
                            >
                                {t('common.close')}
                            </button>
                        )}
                    </div>
                </div>

                {error && (
                    <div className="error-message">{error}</div>
                )}
            </div>
        </div>
    );
}

export default QuizSummaryPage;
