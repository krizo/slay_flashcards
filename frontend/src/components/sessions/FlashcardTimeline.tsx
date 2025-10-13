import { FlashcardData } from '../../types';

interface FlashcardTimelineProps {
    flashcards: FlashcardData[];
    currentIndex: number;
    seenIndices: number[];
    onFlashcardClick?: (index: number) => void;
}

function FlashcardTimeline({
    flashcards,
    currentIndex,
    seenIndices,
    onFlashcardClick
}: FlashcardTimelineProps) {
    return (
        <div className="flashcard-timeline">
            <div className="timeline-content">
                <div className="timeline-progress-badge">
                    In Progress...
                </div>
                {seenIndices.map((index) => {
                    const flashcard = flashcards[index];
                    const isCurrent = index === currentIndex;

                    return (
                        <div
                            key={flashcard.id}
                            className={`timeline-card ${isCurrent ? 'timeline-card--current' : ''}`}
                            onClick={() => onFlashcardClick && onFlashcardClick(index)}
                            role={onFlashcardClick ? 'button' : undefined}
                            tabIndex={onFlashcardClick ? 0 : undefined}
                        >
                            <div className="timeline-card-header">
                                <span className="timeline-card-emoji">
                                    {flashcard.question.emoji}
                                </span>
                                {flashcard.question.difficulty && (
                                    <span className="timeline-card-difficulty">
                                        {'⭐'.repeat(flashcard.question.difficulty)}
                                    </span>
                                )}
                            </div>
                            <div className="timeline-card-title">
                                {flashcard.question.title}
                            </div>
                            {isCurrent && (
                                <div className="timeline-card-badge">Current</div>
                            )}
                        </div>
                    );
                })}

                {/* Show placeholder for upcoming cards */}
                {seenIndices.length < flashcards.length && (
                    <div className="timeline-upcoming">
                        <span className="timeline-upcoming-icon">⏳</span>
                        <span className="timeline-upcoming-text">
                            {flashcards.length - seenIndices.length} more to go
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

export default FlashcardTimeline;
