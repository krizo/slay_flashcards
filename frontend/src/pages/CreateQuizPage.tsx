import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, UNSAFE_NavigationContext } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { usePageHeader } from '../contexts/PageHeaderContext';
import { useUnsavedChanges } from '../contexts/UnsavedChangesContext';
import { QuizMetadataForm, QuizMetadataFormData } from '../components/quizzes/QuizMetadataForm';
import { FlashcardEditor, FlashcardEditorData } from '../components/quizzes/FlashcardEditor';
import { Quiz, FlashcardData } from '../types';
import { api as apiClient } from '../services/apiClient';
import './CreateQuizPage.css';

type CreationStep = 'metadata' | 'flashcards' | 'summary';

interface FlashcardState extends FlashcardEditorData {
    id?: number;
    isDirty: boolean;
}

function CreateQuizPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { accessToken } = useAuth();
    const { setPageHeader } = usePageHeader();
    const { setHasUnsavedWork, requestConfirmation } = useUnsavedChanges();
    const navigationContext = React.useContext(UNSAFE_NavigationContext);
    const isNavigatingRef = useRef(false);

    // State management
    const [step, setStep] = useState<CreationStep>('metadata');

    // Set page header when on metadata step
    useEffect(() => {
        if (step === 'metadata') {
            setPageHeader(t('createQuiz.title'), t('createQuiz.metadataSubtitle'));
        } else {
            setPageHeader(null, null);
        }
        return () => setPageHeader(null, null);
    }, [step, t, setPageHeader]);
    const [quiz, setQuiz] = useState<Quiz | null>(null);
    const [metadataForm, setMetadataForm] = useState<QuizMetadataFormData>({
        name: '',
        subject: '',
        category: '',
        level: '',
        description: '',
        tag_ids: [],
        image: null,
        status: 'draft',
        is_draft: true,
        favourite: false,
    });
    const [flashcards, setFlashcards] = useState<FlashcardState[]>([]);
    const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showValidation, setShowValidation] = useState(false);

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Check if there's unsaved work
    const hasUnsavedWork = () => {
        if (step === 'metadata') {
            return metadataForm.name.trim().length > 0 || metadataForm.subject.trim().length > 0;
        }
        if (step === 'flashcards') {
            return flashcards.some(f => f.isDirty || isFlashcardValid(f));
        }
        return false;
    };

    // Update context when unsaved work status changes
    useEffect(() => {
        setHasUnsavedWork(hasUnsavedWork());
    }, [metadataForm, flashcards, step, setHasUnsavedWork]);

    // Reset hasUnsavedWork when component unmounts
    useEffect(() => {
        return () => {
            setHasUnsavedWork(false);
        };
    }, [setHasUnsavedWork]);

    // Prevent browser close/refresh
    useEffect(() => {
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (hasUnsavedWork()) {
                e.preventDefault();
                e.returnValue = '';
                return '';
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }, [metadataForm, flashcards, step]);

    // Block navigation within the app
    useEffect(() => {
        if (!navigationContext?.navigator) return;

        const originalPush = navigationContext.navigator.push;
        const originalReplace = navigationContext.navigator.replace;

        navigationContext.navigator.push = (to: any, state?: any, opts?: any) => {
            if (!isNavigatingRef.current && hasUnsavedWork()) {
                requestConfirmation(() => {
                    isNavigatingRef.current = true;
                    originalPush.call(navigationContext.navigator, to, state, opts);
                });
                return;
            }
            originalPush.call(navigationContext.navigator, to, state, opts);
        };

        navigationContext.navigator.replace = (to: any, state?: any, opts?: any) => {
            if (!isNavigatingRef.current && hasUnsavedWork()) {
                requestConfirmation(() => {
                    isNavigatingRef.current = true;
                    originalReplace.call(navigationContext.navigator, to, state, opts);
                });
                return;
            }
            originalReplace.call(navigationContext.navigator, to, state, opts);
        };

        return () => {
            navigationContext.navigator.push = originalPush;
            navigationContext.navigator.replace = originalReplace;
        };
    }, [navigationContext, metadataForm, flashcards, step, requestConfirmation]);

    // Initialize with one empty flashcard
    useEffect(() => {
        if (flashcards.length === 0) {
            setFlashcards([createEmptyFlashcard()]);
        }
    }, []);

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

    // Validate metadata form
    const isMetadataValid = () => {
        return metadataForm.name.trim().length > 0 && metadataForm.subject.trim().length > 0;
    };

    // Validate flashcard
    const isFlashcardValid = (flashcard: FlashcardState) => {
        return (
            flashcard.question.title.trim().length > 0 &&
            flashcard.question.text.trim().length > 0 &&
            flashcard.answer.text.trim().length > 0
        );
    };

    // Handle metadata form submission
    const handleMetadataSubmit = async () => {
        if (!isMetadataValid()) {
            setShowValidation(true);
            return;
        }

        setIsSaving(true);
        setError(null);

        try {
            // Create quiz with metadata
            const response = await apiClient.post<{ data: Quiz }>('/quizzes/', {
                name: metadataForm.name,
                subject: metadataForm.subject,
                category: metadataForm.category || null,
                level: metadataForm.level || null,
                description: metadataForm.description || null,
                tag_ids: metadataForm.tag_ids,
                image: metadataForm.image || null,
                status: metadataForm.status,
                is_draft: metadataForm.is_draft,
                favourite: metadataForm.favourite,
            });

            setQuiz(response.data.data);
            isNavigatingRef.current = true;
            setHasUnsavedWork(false);
            setStep('flashcards');
            setShowValidation(false);
        } catch (err: any) {
            console.error('Failed to create quiz:', err);
            setError(err.message || 'Failed to create quiz');
        } finally {
            setIsSaving(false);
        }
    };

    // Save quiz metadata
    const saveQuizMetadata = useCallback(async () => {
        if (!quiz || !accessToken) return;

        try {
            await apiClient.put(`/quizzes/${quiz.id}`, {
                name: metadataForm.name,
                subject: metadataForm.subject,
                category: metadataForm.category || null,
                level: metadataForm.level || null,
                description: metadataForm.description || null,
                tag_ids: metadataForm.tag_ids,
                image: metadataForm.image || null,
                status: metadataForm.status,
                is_draft: metadataForm.is_draft,
                favourite: metadataForm.favourite,
            });
        } catch (err) {
            console.error('Failed to save quiz metadata:', err);
        }
    }, [quiz, metadataForm, accessToken]);

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
        if (step === 'flashcards' && flashcards[currentFlashcardIndex]?.isDirty) {
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
    }, [flashcards, currentFlashcardIndex, step, saveFlashcard]);

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
        isNavigatingRef.current = true;
        setHasUnsavedWork(false);
        navigate(`/quizzes/${quiz?.id}/summary`);
    };

    // Cancel and go back
    const handleCancel = () => {
        requestConfirmation(() => {
            isNavigatingRef.current = true;
            setHasUnsavedWork(false);
            navigate('/quizzes');
        });
    };

    // Render metadata step
    if (step === 'metadata') {
        return (
            <div className="create-quiz-page">
                <div className="create-quiz-container">
                    <QuizMetadataForm
                        data={metadataForm}
                        onChange={setMetadataForm}
                        disabled={isSaving}
                        showValidation={showValidation}
                        accessToken={accessToken}
                        onSubmit={handleMetadataSubmit}
                        onCancel={handleCancel}
                        isValid={isMetadataValid()}
                    />

                    {error && (
                        <div className="error-message">{error}</div>
                    )}
                </div>
            </div>
        );
    }

    // Render flashcards step
    if (step === 'flashcards') {
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

    return null;
}

export default CreateQuizPage;
