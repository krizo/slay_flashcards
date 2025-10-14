import { useTranslation } from 'react-i18next';
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
    const { t } = useTranslation();
    return (
        <div className="flashcard-timeline">
            <div className="timeline-content">
                <div className="timeline-progress-badge">
                    {t('session.timeline.inProgress')}
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
                                <span className="timeline-card-difficulty">
                                    {'⭐'.repeat(flashcard.question.difficulty)}
                                </span>
                            </div>
                            <div className="timeline-card-title">
                                {flashcard.question.title}
                            </div>
                            {isCurrent && (
                                <div className="timeline-card-badge">{t('session.timeline.current')}</div>
                            )}
                        </div>
                    );
                })}

                {/* Show placeholder for upcoming cards */}
                {seenIndices.length < flashcards.length && (
                    <div className="timeline-upcoming">
                        <span className="timeline-upcoming-icon">⏳</span>
                        <span className="timeline-upcoming-text">
                            {t('session.timeline.moreToGo', { count: flashcards.length - seenIndices.length })}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

export default FlashcardTimeline;
