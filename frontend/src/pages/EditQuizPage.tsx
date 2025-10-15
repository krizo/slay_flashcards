import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { FlashcardEditor, FlashcardEditorData } from '../components/quizzes/FlashcardEditor';
import { Quiz, FlashcardData } from '../types';
import { api as apiClient } from '../services/apiClient';
import './CreateQuizPage.css';

interface FlashcardState extends FlashcardEditorData {
    id?: number;
    isDirty: boolean;
}

function EditQuizPage() {
    const { t } = useTranslation();
    const { quizId } = useParams<{ quizId: string }>();
    const navigate = useNavigate();
    const { accessToken } = useAuth();

    // State management
    const [quiz, setQuiz] = useState<Quiz | null>(null);
    const [flashcards, setFlashcards] = useState<FlashcardState[]>([]);
    const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Load quiz and flashcards
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
                const loadedFlashcards = (flashcardsResponse.data.data || []).map(fc => ({
                    id: fc.id,
                    question: fc.question,
                    answer: fc.answer,
                    isDirty: false,
                }));

                // If no flashcards, add an empty one
                if (loadedFlashcards.length === 0) {
                    setFlashcards([createEmptyFlashcard()]);
                } else {
                    setFlashcards(loadedFlashcards);
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

    // Create empty flashcard
    function createEmptyFlashcard(): FlashcardState {
        return {
            question: {
                title: '',
                text: '',
                lang: null,
                difficulty: null,
                emoji: '📝',
                image: null,
                examples: null,
            },
            answer: {
                text: '',
                lang: null,
                type: 'text',
                options: null,
                metadata: { case_sensitive: false },
            },
            isDirty: false,
        };
    }

    // Validate flashcard
    const isFlashcardValid = (flashcard: FlashcardState) => {
        return (
            flashcard.question.title.trim().length > 0 &&
            flashcard.question.text.trim().length > 0 &&
            flashcard.answer.text.trim().length > 0
        );
    };

    // Save flashcard
    const saveFlashcard = useCallback(async (flashcard: FlashcardState, index: number) => {
        if (!quiz || !accessToken || !isFlashcardValid(flashcard)) return;

        try {
            if (flashcard.id) {
                // Update existing flashcard
                await apiClient.put(`/flashcards/${flashcard.id}`, {
                    question: flashcard.question,
                    answer: flashcard.answer,
                });
            } else {
                // Create new flashcard
                const response = await apiClient.post<{ data: FlashcardData }>('/flashcards/', {
                    quiz_id: quiz.id,
                    question: flashcard.question,
                    answer: flashcard.answer,
                });

                // Update flashcard with ID
                setFlashcards(prev => {
                    const updated = [...prev];
                    updated[index] = {
                        ...updated[index],
                        id: response.data.data.id,
                        isDirty: false,
                    };
                    return updated;
                });
            }
        } catch (err) {
            console.error('Failed to save flashcard:', err);
        }
    }, [quiz, accessToken]);

    // Auto-save current flashcard with debouncing
    useEffect(() => {
        if (!isLoading && flashcards[currentFlashcardIndex]?.isDirty) {
            // Clear existing timeout
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }

            // Set new timeout for auto-save
            saveTimeoutRef.current = setTimeout(() => {
                saveFlashcard(flashcards[currentFlashcardIndex], currentFlashcardIndex);
            }, 2000); // 2 second debounce

            return () => {
                if (saveTimeoutRef.current) {
                    clearTimeout(saveTimeoutRef.current);
                }
            };
        }
    }, [flashcards, currentFlashcardIndex, isLoading, saveFlashcard]);

    // Handle flashcard change
    const handleFlashcardChange = (data: FlashcardEditorData) => {
        setFlashcards(prev => {
            const updated = [...prev];
            updated[currentFlashcardIndex] = {
                ...updated[currentFlashcardIndex],
                ...data,
                isDirty: true,
            };
            return updated;
        });
    };

    // Add new flashcard
    const handleAddFlashcard = () => {
        setFlashcards(prev => [...prev, createEmptyFlashcard()]);
        setCurrentFlashcardIndex(flashcards.length);
    };

    // Navigate to flashcard
    const handleFlashcardClick = (index: number) => {
        // Save current flashcard before switching
        if (flashcards[currentFlashcardIndex]?.isDirty) {
            saveFlashcard(flashcards[currentFlashcardIndex], currentFlashcardIndex);
        }
        setCurrentFlashcardIndex(index);
    };

    // Delete flashcard
    const handleDeleteFlashcard = async (index: number) => {
        const flashcard = flashcards[index];

        // If flashcard has an ID, delete from backend
        if (flashcard.id && quiz) {
            try {
                await apiClient.delete(`/flashcards/${flashcard.id}`);
            } catch (err) {
                console.error('Failed to delete flashcard:', err);
                return;
            }
        }

        // Remove from local state
        setFlashcards(prev => prev.filter((_, i) => i !== index));

        // Adjust current index if needed
        if (currentFlashcardIndex >= flashcards.length - 1) {
            setCurrentFlashcardIndex(Math.max(0, flashcards.length - 2));
        }
    };

    // Navigate to summary
    const handleGoToSummary = () => {
        // Save current flashcard before navigating
        if (flashcards[currentFlashcardIndex]?.isDirty) {
            saveFlashcard(flashcards[currentFlashcardIndex], currentFlashcardIndex);
        }
        navigate(`/quizzes/${quiz?.id}/summary`);
    };

    // Cancel and go back
    const handleCancel = () => {
        navigate('/quizzes');
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="create-quiz-page">
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
            <div className="create-quiz-page">
                <div className="summary-error">
                    <span className="error-icon">⚠️</span>
                    <h2>{t('common.error')}</h2>
                    <p>{error || 'Quiz not found'}</p>
                    <button
                        className="action-button action-button--primary"
                        onClick={handleCancel}
                    >
                        {t('createQuiz.backToQuizzes')}
                    </button>
                </div>
            </div>
        );
    }

    // Main editor
    const currentFlashcard = flashcards[currentFlashcardIndex];

    return (
            <div className="create-quiz-page">
                <div className="create-quiz-content-wrapper">
                    {/* Main editor area */}
                    <div className="flashcard-editor-container">
                        <div className="editor-header">
                            <div>
                                <h2>{quiz?.name}</h2>
                                <p className="editor-subtitle">
                                    {t('createQuiz.flashcardEditorSubtitle', {
                                        current: currentFlashcardIndex + 1,
                                        total: flashcards.length,
                                    })}
                                </p>
                            </div>
                            {isSaving && (
                                <span className="saving-indicator">{t('createQuiz.saving')}</span>
                            )}
                        </div>

                        {currentFlashcard && (
                            <FlashcardEditor
                                data={currentFlashcard}
                                onChange={handleFlashcardChange}
                                disabled={isSaving}
                            />
                        )}

                        <div className="editor-actions">
                            <button
                                type="button"
                                className="action-button action-button--secondary"
                                onClick={handleCancel}
                            >
                                {t('createQuiz.backToQuizzes')}
                            </button>
                            <div className="editor-actions-right">
                                <button
                                    type="button"
                                    className="action-button action-button--outline"
                                    onClick={handleAddFlashcard}
                                >
                                    + {t('createQuiz.addFlashcard')}
                                </button>
                                <button
                                    type="button"
                                    className="action-button action-button--primary"
                                    onClick={handleGoToSummary}
                                    disabled={flashcards.length === 0}
                                >
                                    {t('createQuiz.goToSummary')}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Timeline sidebar */}
                    <div className="flashcard-timeline">
                        <h3 className="timeline-title">{t('createQuiz.flashcards')}</h3>
                        <div className="timeline-items">
                            {flashcards.map((flashcard, index) => (
                                <div
                                    key={index}
                                    className={`timeline-item ${index === currentFlashcardIndex ? 'active' : ''} ${isFlashcardValid(flashcard) ? 'valid' : 'invalid'}`}
                                    onClick={() => handleFlashcardClick(index)}
                                >
                                    <div className="timeline-item-number">{index + 1}</div>
                                    <div className="timeline-item-content">
                                        <div className="timeline-item-title">
                                            {flashcard.question.title || t('createQuiz.untitled')}
                                        </div>
                                        {flashcard.isDirty && (
                                            <span className="timeline-item-badge">{t('createQuiz.unsaved')}</span>
                                        )}
                                    </div>
                                    {flashcards.length > 1 && (
                                        <button
                                            type="button"
                                            className="timeline-item-delete"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteFlashcard(index);
                                            }}
                                        >
                                            ✕
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
}

export default EditQuizPage;
