import { useSearchParams } from 'react-router-dom';
import { useSession } from '../hooks/useSession';
import { useQuiz } from '../hooks/useQuiz';
import { useQuizPerformance } from '../hooks/useQuizPerformance';
import { useQuizSessions } from '../hooks/useQuizSessions';
import SessionHeader from '../components/sessions/SessionHeader';
import FlashcardDisplay from '../components/sessions/FlashcardDisplay';
import { SessionMode } from '../types';

function LearningSessionPage() {
    const [searchParams] = useSearchParams();
    const quizId = searchParams.get('quizId');
    const mode = (searchParams.get('mode') as SessionMode) || 'learn';

    const quizIdNumber = quizId ? parseInt(quizId, 10) : null;

    // Get quiz details for header
    const { quiz } = useQuiz(quizIdNumber);

    // Get quiz-specific performance stats for header metrics (all-time data)
    const { performance } = useQuizPerformance(quizIdNumber, 365); // Get full year of data

    // Get recent sessions to find the last session date
    const { sessions } = useQuizSessions(quizIdNumber, 50);

    // Calculate last session date (only include completed sessions)
    // Exclude sessions completed in the last 30 seconds (likely the one we just finished before starting this one)
    const now = new Date();
    const sortedSessions = sessions ? [...sessions]
        .filter(s => {
            if (!s.completed) return false;
            const completedAt = s.completed_at ? new Date(s.completed_at) : new Date(s.started_at);
            const secondsAgo = (now.getTime() - completedAt.getTime()) / 1000;
            return secondsAgo > 30; // Only show sessions completed more than 30 seconds ago
        })
        .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
    : [];
    const lastSessionDate = sortedSessions.length > 0 ? sortedSessions[0].started_at : null;

    // Use session hook for all session logic
    const {
        currentFlashcard,
        flashcardsCompleted,
        totalFlashcards,
        feedback,
        userAnswer,
        showAnswer,
        isLoading,
        isSubmitting,
        error,
        isSessionCompleted,
        setUserAnswer,
        submitAnswer,
        revealAnswer,
        goToNextFlashcard,
        endSession,
    } = useSession(quizIdNumber, mode);

    // Text-to-speech function
    const handleSpeak = (text: string, lang?: string | null) => {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);

            // Map language codes to speech synthesis locale codes
            const langMap: Record<string, string> = {
                'en': 'en-US',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'de': 'de-DE',
                'it': 'it-IT',
                'pt': 'pt-PT',
                'ru': 'ru-RU',
                'ja': 'ja-JP',
                'zh': 'zh-CN',
                'ko': 'ko-KR',
                'ar': 'ar-SA',
                'hi': 'hi-IN',
                'pl': 'pl-PL',
                'nl': 'nl-NL',
                'sv': 'sv-SE',
                'tr': 'tr-TR',
            };

            // Use the provided language or default to en-US
            if (lang && langMap[lang]) {
                utterance.lang = langMap[lang];
            } else if (lang) {
                utterance.lang = lang; // Use as-is if not in map
            } else {
                utterance.lang = 'en-US'; // Default
            }

            window.speechSynthesis.speak(utterance);
        }
    };

    // Show loading state during initialization
    if (isLoading && !currentFlashcard) {
        return (
            <div className="session-page">
                <div className="session-loading-overlay">
                    <div className="loading-spinner"></div>
                    <p>Preparing your learning session...</p>
                </div>
            </div>
        );
    }

    // Show error state
    if (error) {
        return (
            <div className="session-page">
                <div className="session-error-message">
                    <span className="error-icon">⚠️</span>
                    <h2>Session Error</h2>
                    <p>{error.message}</p>
                    <button
                        className="control-button control-button--primary"
                        onClick={endSession}
                    >
                        Return to Quizzes
                    </button>
                </div>
            </div>
        );
    }

    // Show completion state
    if (isSessionCompleted) {
        return (
            <div className="session-page">
                <div className="session-completion-message">
                    <span className="completion-icon">🎉</span>
                    <h2>Session Complete!</h2>
                    <p>
                        You've completed {flashcardsCompleted} of {totalFlashcards}{' '}
                        flashcards.
                    </p>
                    <button
                        className="control-button control-button--primary"
                        onClick={endSession}
                    >
                        Finish Session
                    </button>
                </div>
            </div>
        );
    }

    // Main session view
    return (
        <div className="session-page">
            <SessionHeader
                quizName={quiz?.name || 'Loading...'}
                quizImage={quiz?.image}
                yourBest={performance?.scores.highest ?? null}
                yourAverage={performance?.scores.average ?? null}
                testSessions={performance?.test_sessions ?? 0}
                lastSessionDate={lastSessionDate}
                onCloseSession={endSession}
            />

            <div className="session-content-wrapper">
                <FlashcardDisplay
                    flashcard={currentFlashcard}
                    feedback={feedback}
                    userAnswer={userAnswer}
                    showAnswer={showAnswer}
                    totalFlashcards={totalFlashcards}
                    flashcardsCompleted={flashcardsCompleted}
                    quizName={quiz?.name || 'Loading...'}
                    mode={mode}
                    isSubmitting={isSubmitting}
                    onUserAnswerChange={setUserAnswer}
                    onSpeak={handleSpeak}
                    onSubmitAnswer={submitAnswer}
                    onRevealAnswer={revealAnswer}
                    onNextFlashcard={goToNextFlashcard}
                />
            </div>
        </div>
    );
}

export default LearningSessionPage;
