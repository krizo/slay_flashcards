import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/apiClient';
import { useAuth } from '../context/AuthContext';
import {
    SessionMode,
    FlashcardData,
    SessionCreateResponse,
    SessionFeedback,
    TestResult,
    TestSubmitRequest,
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
    testResults: TestResult | null;
    setUserAnswer: (answer: string) => void;
    submitAnswer: () => Promise<void>;
    revealAnswer: () => void;
    goToNextFlashcard: () => void;
    goToFlashcard: (index: number) => void;
    endSession: () => Promise<void>;
    submitTestSession: () => Promise<void>;
}

export function useSession(quizId: number | null, mode: SessionMode): UseSessionReturn {
    const navigate = useNavigate();
    const { accessToken, user } = useAuth();

    const [currentMode, setCurrentMode] = useState<SessionMode>(mode);
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
    const [testResults, setTestResults] = useState<TestResult | null>(null);
    const [testAnswers, setTestAnswers] = useState<Map<number, string>>(new Map());
    const [testStartTime, setTestStartTime] = useState<number | null>(null);

    // Detect mode change and reset immediately
    if (mode !== currentMode) {
        setCurrentMode(mode);
        setIsSessionStarted(false);
        setIsSessionCompleted(false);
        setTestResults(null);
        setFlashcards([]);
        setCurrentFlashcardIndex(0);
        setFlashcardsCompleted(0);
        setSeenIndices([0]);
        setFeedback(null);
        setUserAnswer('');
        setShowAnswer(false);
        setTestAnswers(new Map());
        setTestStartTime(null);
        setIsLoading(true);
        setError(null);
    }

    // Get current flashcard
    const currentFlashcard = flashcards[currentFlashcardIndex] || null;
    const totalFlashcards = flashcards.length;

    // Initialize session
    useEffect(() => {
        if (!quizId || !accessToken || !user) return;

        // Reset session state when mode or quiz changes
        setIsSessionStarted(false);
        setIsSessionCompleted(false);
        setTestResults(null);
        setFlashcards([]);
        setCurrentFlashcardIndex(0);
        setFlashcardsCompleted(0);
        setSeenIndices([0]);
        setFeedback(null);
        setUserAnswer('');
        setShowAnswer(false);
        setTestAnswers(new Map());
        setTestStartTime(null);
        setIsLoading(true); // Set loading immediately
        setError(null);

        const initializeSession = async () => {
            try {

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

                // Start timer for test mode
                if (mode === 'test') {
                    setTestStartTime(Date.now());
                }

                setIsLoading(false);
            } catch (err) {
                setError(err as Error);
                setIsLoading(false);
            }
        };

        initializeSession();
    }, [quizId, mode, accessToken, user]);

    // Submit answer (for learn mode) or store answer (for test mode)
    const submitAnswer = async () => {
        if (!sessionId || !currentFlashcard || !accessToken) return;

        try {
            setIsSubmitting(true);

            // Both modes: check answer and provide immediate feedback
            const correctAnswer = currentFlashcard.answer.text.trim().toLowerCase();
            const submittedAnswer = userAnswer.trim().toLowerCase();
            const isCorrect = correctAnswer === submittedAnswer;

            // Set feedback based on comparison
            setFeedback({
                is_correct: isCorrect,
                correct_answer: currentFlashcard.answer.text,
                feedback: isCorrect
                    ? 'Correct! Well done!'
                    : 'Incorrect. Click "Show Answer" to see the correct answer.',
            });

            if (mode === 'test') {
                // In test mode, store the answer for final submission
                setTestAnswers((prev) => new Map(prev).set(currentFlashcard.id, userAnswer));
                setIsSubmitting(false);
            } else {
                // Learn mode: track progress on backend
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
            }
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
        // Check if we're on the last flashcard
        if (currentFlashcardIndex + 1 >= flashcards.length) {
            // In test mode, automatically submit the test when reaching the end
            if (mode === 'test') {
                submitTestSession();
            } else {
                // In learn mode, mark session as completed
                setFlashcardsCompleted((prev) => prev + 1);
                setIsSessionCompleted(true);
            }
        } else {
            // Move to next flashcard
            setFlashcardsCompleted((prev) => prev + 1);
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

    // Submit test session and get results
    const submitTestSession = async () => {
        if (!sessionId || !accessToken) return;

        try {
            setIsSubmitting(true);

            // Calculate test duration in seconds
            const duration = testStartTime ? Math.floor((Date.now() - testStartTime) / 1000) : undefined;

            // Prepare answers array
            const answers = Array.from(testAnswers.entries()).map(([flashcard_id, user_answer]) => ({
                flashcard_id,
                user_answer,
                time_taken: 0, // Not tracking individual card time
            }));

            const requestData: TestSubmitRequest = {
                session_id: sessionId,
                answers,
                duration,
            };

            // Submit all answers to backend
            const results = await api.post<TestResult>(
                '/sessions/test/submit',
                requestData,
                accessToken
            );

            // Add duration to results if not provided by backend
            if (results && !results.duration && duration) {
                results.duration = duration;
            }

            setTestResults(results);
            setIsSessionCompleted(true);
            setIsSubmitting(false);
        } catch (err) {
            console.error('Failed to submit test session:', err);
            setError(err as Error);
            setIsSubmitting(false);
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
        testResults,
        setUserAnswer,
        submitAnswer,
        revealAnswer,
        goToNextFlashcard,
        goToFlashcard,
        endSession,
        submitTestSession,
    };
}
