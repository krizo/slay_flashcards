import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import {
    SessionMode,
    FlashcardData,
    SessionCreateResponse,
    SessionFeedback,
} from '../types';

interface UseSessionReturn {
    sessionId: number | null;
    currentFlashcard: FlashcardData | null;
    flashcardsCompleted: number;
    totalFlashcards: number;
    feedback: SessionFeedback | null;
    userAnswer: string;
    showAnswer: boolean;
    isLoading: boolean;
    isSubmitting: boolean;
    error: Error | null;
    isSessionStarted: boolean;
    isSessionCompleted: boolean;
    allFlashcards: FlashcardData[];
    currentFlashcardIndex: number;
    seenIndices: number[];
    setUserAnswer: (answer: string) => void;
    submitAnswer: () => Promise<void>;
    revealAnswer: () => void;
    goToNextFlashcard: () => void;
    goToFlashcard: (index: number) => void;
    endSession: () => Promise<void>;
}

export function useSession(quizId: number | null, mode: SessionMode): UseSessionReturn {
    const navigate = useNavigate();
    const { accessToken, user } = useAuth();

    const [sessionId, setSessionId] = useState<number | null>(null);
    const [flashcards, setFlashcards] = useState<FlashcardData[]>([]);
    const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
    const [flashcardsCompleted, setFlashcardsCompleted] = useState(0);
    const [seenIndices, setSeenIndices] = useState<number[]>([0]); // Start with first card as seen
    const [feedback, setFeedback] = useState<SessionFeedback | null>(null);
    const [userAnswer, setUserAnswer] = useState('');
    const [showAnswer, setShowAnswer] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [isSessionStarted, setIsSessionStarted] = useState(false);
    const [isSessionCompleted, setIsSessionCompleted] = useState(false);

    // Get current flashcard
    const currentFlashcard = flashcards[currentFlashcardIndex] || null;
    const totalFlashcards = flashcards.length;

    // Initialize session
    useEffect(() => {
        if (!quizId || !accessToken || !user || isSessionStarted) return;

        const initializeSession = async () => {
            try {
                setIsLoading(true);
                setError(null);

                // Create session
                const session = await api.post<SessionCreateResponse>(
                    '/sessions/',
                    { user_id: user.id, quiz_id: quizId, mode },
                    accessToken
                );

                setSessionId(session.id);

                // Fetch all flashcards for the quiz
                interface ApiFlashcard {
                    id: number;
                    quiz_id: number;
                    question_title: string;
                    question_text: string;
                    question_lang: string | null;
                    question_difficulty: number;
                    question_emoji: string | null;
                    question_image: string | null;
                    answer_text: string;
                    answer_lang: string | null;
                    answer_type: string;
                    answer_options: any[] | null;
                    answer_metadata: any | null;
                }

                const apiFlashcards = await api.get<ApiFlashcard[]>(
                    `/flashcards/`,
                    accessToken,
                    { quiz_id: quizId }
                );

                // Transform API flashcards to frontend format
                const transformedFlashcards: FlashcardData[] = apiFlashcards.map(card => ({
                    id: card.id,
                    quiz_id: card.quiz_id,
                    question: {
                        title: card.question_title,
                        text: card.question_text,
                        lang: card.question_lang,
                        difficulty: card.question_difficulty,
                        emoji: card.question_emoji || '📝',
                        image: card.question_image,
                    },
                    answer: {
                        text: card.answer_text,
                        lang: card.answer_lang,
                        type: card.answer_type as any,
                        options: card.answer_options,
                        metadata: card.answer_metadata,
                    },
                }));

                // Shuffle flashcards for variety
                const shuffled = [...transformedFlashcards].sort(() => Math.random() - 0.5);
                setFlashcards(shuffled);
                setIsSessionStarted(true);
                setIsLoading(false);
            } catch (err) {
                setError(err as Error);
                setIsLoading(false);
            }
        };

        initializeSession();
    }, [quizId, mode, accessToken, user, isSessionStarted]);

    // Submit answer (for learn mode)
    const submitAnswer = async () => {
        if (!sessionId || !currentFlashcard || !accessToken) return;

        try {
            setIsSubmitting(true);

            // Simple answer checking on frontend
            const correctAnswer = currentFlashcard.answer.text.trim().toLowerCase();
            const submittedAnswer = userAnswer.trim().toLowerCase();
            const isCorrect = correctAnswer === submittedAnswer;

            // Set feedback based on comparison
            setFeedback({
                is_correct: isCorrect,
                correct_answer: currentFlashcard.answer.text,
                feedback: isCorrect
                    ? 'Correct! Well done!'
                    : 'Not quite right. Keep practicing!',
            });

            // Track progress on backend
            await api.put(
                `/sessions/learning/${sessionId}/progress`,
                {
                    progress: [{
                        flashcard_id: currentFlashcard.id,
                        reviewed: true,
                        confidence: isCorrect ? 5 : 3,
                    }]
                },
                accessToken
            );

            setIsSubmitting(false);
        } catch (err) {
            // Even if backend tracking fails, show feedback
            console.error('Failed to track progress:', err);
            setIsSubmitting(false);
        }
    };

    // Reveal answer (without submitting)
    const revealAnswer = () => {
        setShowAnswer(true);
    };

    // Go to next flashcard
    const goToNextFlashcard = () => {
        setFlashcardsCompleted((prev) => prev + 1);

        // Check if there are more flashcards
        if (currentFlashcardIndex + 1 >= flashcards.length) {
            setIsSessionCompleted(true);
        } else {
            // Move to next flashcard
            const nextIndex = currentFlashcardIndex + 1;
            setCurrentFlashcardIndex(nextIndex);
            // Add next index to seen indices if not already there
            setSeenIndices((prev) => prev.includes(nextIndex) ? prev : [...prev, nextIndex]);
            setUserAnswer('');
            setShowAnswer(false);
            setFeedback(null);
        }
    };

    // Go to specific flashcard (for timeline navigation)
    const goToFlashcard = (index: number) => {
        if (index >= 0 && index < flashcards.length && seenIndices.includes(index)) {
            setCurrentFlashcardIndex(index);
            setUserAnswer('');
            setShowAnswer(false);
            setFeedback(null);
        }
    };

    // End session
    const endSession = async () => {
        if (sessionId && accessToken) {
            try {
                // Mark session as completed using the new complete endpoint
                await api.post(
                    `/sessions/${sessionId}/complete`,
                    {},
                    accessToken
                );
            } catch (err) {
                console.error('Failed to complete session:', err);
            }
        }

        // Navigate back to quizzes
        navigate('/quizzes');
    };

    return {
        sessionId,
        currentFlashcard,
        flashcardsCompleted,
        totalFlashcards,
        feedback,
        userAnswer,
        showAnswer,
        isLoading,
        isSubmitting,
        error,
        isSessionStarted,
        isSessionCompleted,
        allFlashcards: flashcards,
        currentFlashcardIndex,
        seenIndices,
        setUserAnswer,
        submitAnswer,
        revealAnswer,
        goToNextFlashcard,
        goToFlashcard,
        endSession,
    };
}
