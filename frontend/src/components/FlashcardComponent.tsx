import {useEffect, useRef, useState} from 'react';
import {FlashcardData, FlashcardMode} from '../types';
import {playAudio, stopAudio} from '../utils/audioUtils';
import AnswerInput from './AnswerInput';

interface FlashcardComponentProps {
    flashcardData: FlashcardData;
    mode?: FlashcardMode;
    onNextFlashcard?: () => void;
}

/**
 * FlashcardComponent - Main component for displaying and interacting with flashcards
 *
 * Features:
 * - Displays question on front, answer on back
 * - Flip animation controlled by CSS classes and isFlipped state
 * - Shows difficulty indicators, emoji, and language tags
 * - Supports two modes: 'learn' (interactive learning) and 'test' (quiz with scoring)
 * - Dynamic height based on content
 */
const FlashcardComponent: React.FC<FlashcardComponentProps> = ({
                                                                   flashcardData,
                                                                   onNextFlashcard
                                                               }) => {
    // State to track if card is flipped (false = showing question, true = showing answer)
    const [isFlipped, setIsFlipped] = useState<boolean>(false);
    const [cardHeight, setCardHeight] = useState<number>(350);
    const [userAnswer, setUserAnswer] = useState<string | string[]>('');

    const frontRef = useRef<HTMLDivElement>(null);
    const backRef = useRef<HTMLDivElement>(null);

    // Update card height based on content
    useEffect(() => {
        const updateHeight = () => {
            // Temporarily remove height constraint to measure natural height
            if (frontRef.current && backRef.current) {
                const frontHeight = frontRef.current.scrollHeight;
                const backHeight = backRef.current.scrollHeight;
                const maxHeight = Math.max(frontHeight, backHeight, 350);
                setCardHeight(maxHeight);
            }
        };

        // Small delay to ensure DOM is fully rendered
        setTimeout(updateHeight, 10);

        // Update on window resize
        window.addEventListener('resize', updateHeight);
        return () => window.removeEventListener('resize', updateHeight);
    }, [flashcardData, isFlipped]);

    // Stop audio when flashcard changes
    useEffect(() => {
        return () => {
            stopAudio();
        };
    }, [flashcardData.id]);

    // Toggle flip state when Show Answer button is clicked
    const handleShowAnswerClick = (event: React.MouseEvent) => {
        event.stopPropagation();
        setIsFlipped(true);
    };

    // Flip back to question when clicking on answer side
    const handleBackClick = () => {
        setIsFlipped(false);
    };

    const {question, answer} = flashcardData;

    // Render difficulty dots based on difficulty level (1-5)
    const renderDifficultyDots = () => {
        const dots = [];
        for (let i = 1; i <= 5; i++) {
            dots.push(
                <span
                    key={i}
                    className={`dot ${i <= question.difficulty ? 'active' : ''}`}
                ></span>
            );
        }
        return dots;
    };

    // Handle audio playback for question or answer
    const handleAudioClick = (event: React.MouseEvent, text: string, lang: string | null) => {
        event.stopPropagation(); // Prevent card flip
        playAudio(text, lang);
    };

    // Handle next flashcard button click
    const handleNextClick = (event: React.MouseEvent) => {
        event.stopPropagation(); // Prevent card flip
        if (onNextFlashcard) {
            setIsFlipped(false); // Reset to front side
            setUserAnswer(''); // Clear answer
            onNextFlashcard();
        }
    };

    // Handle "Don't Know" button click
    const handleDontKnowClick = (event: React.MouseEvent) => {
        event.stopPropagation(); // Prevent card flip
        if (onNextFlashcard) {
            setIsFlipped(false); // Reset to front side
            setUserAnswer(''); // Clear answer
            onNextFlashcard();
        }
    };

    // Handle answer change
    const handleAnswerChange = (value: string | string[]) => {
        setUserAnswer(value);
    };


    return (
        <div
            className={`flashcard-container ${isFlipped ? 'flipped' : ''}`}
            style={{height: `${cardHeight}px`}}
        >
            {/* FRONT SIDE - Question */}
            <div className="flashcard-front" ref={frontRef}>
                {/* Header with difficulty and progress */}
                <div className="flashcard-header">
                    <div className="flashcard-difficulty">
                        {renderDifficultyDots()}
                    </div>
                    <span className="flashcard-quiz-progress">
                        {flashcardData.id} / {flashcardData.quiz_id}
                    </span>
                </div>

                {/* Emoji */}
                <div className="flashcard-emoji">{question.emoji}</div>

                {/* Main content - Question */}
                <div className="flashcard-main-content">
                    <h2 className="flashcard-question-title">{question.title}</h2>
                    <div className="flashcard-question-text">
                        <span>{question.text}</span>
                        {question.lang && (
                            <>
                                <i
                                    className="fas fa-volume-up flashcard-audio-icon"
                                    onClick={(e) => handleAudioClick(e, question.text, question.lang ?? null)}
                                ></i>
                                <span className="flashcard-lang-tag">{question.lang}</span>
                            </>
                        )}
                    </div>

                    {/* Answer Input */}
                    <AnswerInput
                        answer={answer}
                        userAnswer={userAnswer}
                        onAnswerChange={handleAnswerChange}
                    />
                </div>

                {/* Action buttons - Front side */}
                <div className="flashcard-button-group">
                    <button
                        className="flashcard-button-secondary"
                        onClick={handleDontKnowClick}
                    >
                        Don't Know
                    </button>
                    <button
                        className="flashcard-button"
                        onClick={handleShowAnswerClick}
                    >
                        Show Answer
                    </button>
                </div>
            </div>

            {/* BACK SIDE - Answer */}
            <div className="flashcard-back" ref={backRef} onClick={handleBackClick}>
                {/* Header with difficulty and progress */}
                <div className="flashcard-header">
                    <div className="flashcard-difficulty">
                        {renderDifficultyDots()}
                    </div>
                    <span className="flashcard-quiz-progress">
                        {flashcardData.id} / {flashcardData.quiz_id}
                    </span>
                </div>

                {/* Emoji */}
                <div className="flashcard-emoji">{question.emoji}</div>

                {/* Main content - Answer */}
                <div className="flashcard-main-content">
                    <h2 className="flashcard-question-title">{question.title}</h2>

                    {/* Answer text box */}
                    <div className="flashcard-answer-text-box">
                        <strong>Answer:</strong>
                        <div className="flashcard-answer-text-display">
                            <span>{answer.text}</span>
                            {answer.lang && (
                                <>
                                    <i
                                        className="fas fa-volume-up flashcard-audio-icon"
                                        onClick={(e) => handleAudioClick(e, answer.text, answer.lang ?? null)}
                                    ></i>
                                    <span className="flashcard-lang-tag">{answer.lang}</span>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Answer type info */}
                    <p className="flashcard-type-info">
                        Answer Type: <strong>{answer.type}</strong>
                    </p>
                </div>

                {/* Action button - Back side */}
                <button
                    className="flashcard-button"
                    onClick={handleNextClick}
                >
                    Next Flashcard
                </button>
            </div>
        </div>
    );
};

export default FlashcardComponent;
