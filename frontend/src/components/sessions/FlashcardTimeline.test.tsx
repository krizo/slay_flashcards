import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import FlashcardTimeline from './FlashcardTimeline';
import { FlashcardData } from '../../types';

describe('FlashcardTimeline', () => {
    const mockFlashcards: FlashcardData[] = [
        {
            id: 1,
            quiz_id: 1,
            question: {
                title: 'Question 1',
                text: 'What is 2+2?',
                lang: 'en',
                difficulty: 1,
                emoji: '🧮',
                image: null
            },
            answer: {
                text: '4',
                type: 'integer',
                lang: 'en',
                options: null,
                metadata: null
            }
        },
        {
            id: 2,
            quiz_id: 1,
            question: {
                title: 'Question 2',
                text: 'What is the capital of France?',
                lang: 'en',
                difficulty: 2,
                emoji: '🗼',
                image: null
            },
            answer: {
                text: 'Paris',
                type: 'short_text',
                lang: 'en',
                options: null,
                metadata: null
            }
        },
        {
            id: 3,
            quiz_id: 1,
            question: {
                title: 'Question 3',
                text: 'What is 10 * 5?',
                lang: 'en',
                difficulty: 3,
                emoji: '✖️',
                image: null
            },
            answer: {
                text: '50',
                type: 'integer',
                lang: 'en',
                options: null,
                metadata: null
            }
        }
    ];

    it('renders timeline with progress badge showing "In Progress..."', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        expect(screen.getByText('In Progress...')).toBeInTheDocument();
    });

    it('displays only seen flashcards', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        expect(screen.getByText('Question 1')).toBeInTheDocument();
        expect(screen.getByText('Question 2')).toBeInTheDocument();
        expect(screen.queryByText('Question 3')).not.toBeInTheDocument();
    });

    it('marks current flashcard with "Current" badge', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        expect(screen.getByText('Current')).toBeInTheDocument();
    });

    it('applies current class to current flashcard', () => {
        const { container } = render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        const currentCards = container.querySelectorAll('.timeline-card--current');
        expect(currentCards).toHaveLength(1);
    });

    it('displays emoji for each flashcard', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        expect(screen.getByText('🧮')).toBeInTheDocument();
        expect(screen.getByText('🗼')).toBeInTheDocument();
    });

    it('displays difficulty stars correctly', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        expect(screen.getByText('⭐')).toBeInTheDocument(); // 1 star for difficulty 1
        expect(screen.getByText('⭐⭐')).toBeInTheDocument(); // 2 stars for difficulty 2
    });

    it('displays flashcard titles', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        expect(screen.getByText('Question 1')).toBeInTheDocument();
    });

    it('shows upcoming cards placeholder when not all cards are seen', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        expect(screen.getByText('⏳')).toBeInTheDocument();
        expect(screen.getByText('2 more to go')).toBeInTheDocument();
    });

    it('does not show upcoming placeholder when all cards are seen', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={2}
                seenIndices={[0, 1, 2]}
            />
        );

        expect(screen.queryByText('⏳')).not.toBeInTheDocument();
        expect(screen.queryByText(/more to go/)).not.toBeInTheDocument();
    });

    it('calls onFlashcardClick when flashcard is clicked', () => {
        const mockOnClick = vi.fn();

        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
                onFlashcardClick={mockOnClick}
            />
        );

        const firstCard = screen.getByText('Question 1').closest('.timeline-card');
        fireEvent.click(firstCard!);

        expect(mockOnClick).toHaveBeenCalledWith(0);
    });

    it('makes flashcard clickable when onFlashcardClick is provided', () => {
        const mockOnClick = vi.fn();

        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
                onFlashcardClick={mockOnClick}
            />
        );

        const card = screen.getByText('Question 1').closest('.timeline-card');
        expect(card).toHaveAttribute('role', 'button');
        expect(card).toHaveAttribute('tabindex', '0');
    });

    it('does not make flashcard clickable when onFlashcardClick is not provided', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        const card = screen.getByText('Question 1').closest('.timeline-card');
        expect(card).not.toHaveAttribute('role');
        expect(card).not.toHaveAttribute('tabindex');
    });

    it('applies correct CSS classes', () => {
        const { container } = render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        expect(container.querySelector('.flashcard-timeline')).toBeInTheDocument();
        expect(container.querySelector('.timeline-content')).toBeInTheDocument();
        expect(container.querySelector('.timeline-progress-badge')).toBeInTheDocument();
        expect(container.querySelector('.timeline-card')).toBeInTheDocument();
        expect(container.querySelector('.timeline-card-header')).toBeInTheDocument();
        expect(container.querySelector('.timeline-card-emoji')).toBeInTheDocument();
        expect(container.querySelector('.timeline-card-difficulty')).toBeInTheDocument();
        expect(container.querySelector('.timeline-card-title')).toBeInTheDocument();
    });

    it('renders multiple seen flashcards in order', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={2}
                seenIndices={[0, 1, 2]}
            />
        );

        const titles = screen.getAllByText(/Question \d/);
        expect(titles).toHaveLength(3);
        expect(titles[0]).toHaveTextContent('Question 1');
        expect(titles[1]).toHaveTextContent('Question 2');
        expect(titles[2]).toHaveTextContent('Question 3');
    });

    it('handles empty flashcards array', () => {
        render(
            <FlashcardTimeline
                flashcards={[]}
                currentIndex={0}
                seenIndices={[]}
            />
        );

        expect(screen.getByText('In Progress...')).toBeInTheDocument();
        expect(screen.queryByText(/Question/)).not.toBeInTheDocument();
    });

    it('renders without emoji when question emoji is null', () => {
        const flashcardsWithoutEmoji: FlashcardData[] = [
            {
                ...mockFlashcards[0],
                question: {
                    ...mockFlashcards[0].question,
                    emoji: null
                }
            }
        ];

        const { container } = render(
            <FlashcardTimeline
                flashcards={flashcardsWithoutEmoji}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        const emojiSpan = container.querySelector('.timeline-card-emoji');
        expect(emojiSpan).toBeInTheDocument();
        expect(emojiSpan?.textContent).toBe('');
    });

    it('displays correct count in upcoming message', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={0}
                seenIndices={[0]}
            />
        );

        expect(screen.getByText('2 more to go')).toBeInTheDocument();
    });

    it('displays singular "1 more to go" when one card remains', () => {
        render(
            <FlashcardTimeline
                flashcards={mockFlashcards}
                currentIndex={1}
                seenIndices={[0, 1]}
            />
        );

        expect(screen.getByText('1 more to go')).toBeInTheDocument();
    });
});
