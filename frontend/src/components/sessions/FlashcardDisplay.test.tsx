import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import FlashcardDisplay from './FlashcardDisplay';
import { FlashcardData, SessionFeedback } from '../../types';

describe('FlashcardDisplay', () => {
    const mockFlashcard: FlashcardData = {
        id: 1,
        quiz_id: 1,
        question: {
            title: 'Test Question',
            text: 'What is 2+2?',
            lang: 'en',
            difficulty: 3,
            emoji: '🧮',
            image: null,
            examples: ['1+1=2', '3+1=4'],
        },
        answer: {
            text: '4',
            type: 'integer',
            lang: 'en',
            options: null,
            metadata: {},
        },
    };

    const defaultProps = {
        flashcard: mockFlashcard,
        feedback: null,
        userAnswer: '',
        showAnswer: false,
        totalFlashcards: 10,
        flashcardsCompleted: 5,
        quizName: 'Math Quiz',
        mode: 'learn',
        isSubmitting: false,
        onUserAnswerChange: vi.fn(),
        onSpeak: vi.fn(),
        onSubmitAnswer: vi.fn(),
        onRevealAnswer: vi.fn(),
        onNextFlashcard: vi.fn(),
    };

    describe('Difficulty Stars', () => {
        it('displays 3 filled stars for difficulty 3 (Medium+)', () => {
            const { container } = render(
                <FlashcardDisplay {...defaultProps} />
            );

            const difficultyStars = container.querySelector('.difficulty-stars');
            expect(difficultyStars).toBeInTheDocument();
            expect(difficultyStars?.textContent).toContain('Difficulty:');

            const filledStars = container.querySelectorAll('.star-filled');
            const emptyStars = container.querySelectorAll('.star-empty');

            expect(filledStars).toHaveLength(3);
            expect(emptyStars).toHaveLength(2);
        });

        it('displays 1 filled star for difficulty 1 (Easy)', () => {
            const easyFlashcard = {
                ...mockFlashcard,
                question: { ...mockFlashcard.question, difficulty: 1 },
            };

            const { container } = render(
                <FlashcardDisplay {...defaultProps} flashcard={easyFlashcard} />
            );

            const filledStars = container.querySelectorAll('.star-filled');
            const emptyStars = container.querySelectorAll('.star-empty');

            expect(filledStars).toHaveLength(1);
            expect(emptyStars).toHaveLength(4);
        });

        it('displays 5 filled stars for difficulty 5 (Very Hard)', () => {
            const hardFlashcard = {
                ...mockFlashcard,
                question: { ...mockFlashcard.question, difficulty: 5 },
            };

            const { container } = render(
                <FlashcardDisplay {...defaultProps} flashcard={hardFlashcard} />
            );

            const filledStars = container.querySelectorAll('.star-filled');
            const emptyStars = container.querySelectorAll('.star-empty');

            expect(filledStars).toHaveLength(5);
            expect(emptyStars).toHaveLength(0);
        });

        it('applies correct CSS class for easy difficulty', () => {
            const easyFlashcard = {
                ...mockFlashcard,
                question: { ...mockFlashcard.question, difficulty: 1 },
            };

            const { container } = render(
                <FlashcardDisplay {...defaultProps} flashcard={easyFlashcard} />
            );

            const difficultyStars = container.querySelector('.difficulty-easy');
            expect(difficultyStars).toBeInTheDocument();
        });

        it('applies correct CSS class for hard difficulty', () => {
            const hardFlashcard = {
                ...mockFlashcard,
                question: { ...mockFlashcard.question, difficulty: 4 },
            };

            const { container } = render(
                <FlashcardDisplay {...defaultProps} flashcard={hardFlashcard} />
            );

            const difficultyStars = container.querySelector('.difficulty-hard');
            expect(difficultyStars).toBeInTheDocument();
        });

        it('does not render difficulty stars when difficulty is null', () => {
            const noDifficultyFlashcard = {
                ...mockFlashcard,
                question: { ...mockFlashcard.question, difficulty: null },
            };

            const { container } = render(
                <FlashcardDisplay {...defaultProps} flashcard={noDifficultyFlashcard} />
            );

            const difficultyStars = container.querySelector('.difficulty-stars');
            expect(difficultyStars).not.toBeInTheDocument();
        });

        it('displays "Difficulty:" label', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText('Difficulty:')).toBeInTheDocument();
        });

        it('positions difficulty stars at end of question header row', () => {
            const { container } = render(
                <FlashcardDisplay {...defaultProps} />
            );

            const questionHeader = container.querySelector('.flashcard-question-header');
            const difficultyStars = container.querySelector('.difficulty-stars');

            expect(questionHeader).toContainElement(difficultyStars);
        });
    });

    describe('Question Display', () => {
        it('renders question title and text', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText('Test Question')).toBeInTheDocument();
            expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
        });

        it('renders question emoji', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText('🧮')).toBeInTheDocument();
        });

        it('renders examples when provided', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText('Examples:')).toBeInTheDocument();
            expect(screen.getByText('1+1=2')).toBeInTheDocument();
            expect(screen.getByText('3+1=4')).toBeInTheDocument();
        });

        it('displays speaker button for text-to-speech', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            const speakerButtons = screen.getAllByLabelText(/Read.*aloud/i);
            expect(speakerButtons.length).toBeGreaterThan(0);
        });
    });

    describe('Progress Counter', () => {
        it('displays correct progress counter', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText(/5 \/ 10 cards/)).toBeInTheDocument();
            expect(screen.getByText(/50%/)).toBeInTheDocument();
        });

        it('calculates percentage correctly', () => {
            render(
                <FlashcardDisplay
                    {...defaultProps}
                    flashcardsCompleted={7}
                    totalFlashcards={10}
                />
            );

            expect(screen.getByText(/70%/)).toBeInTheDocument();
        });
    });

    describe('Mode Display', () => {
        it('displays learn mode badge', () => {
            render(<FlashcardDisplay {...defaultProps} mode="learn" />);

            expect(screen.getByText('📚 Learn')).toBeInTheDocument();
        });

        it('displays test mode badge', () => {
            render(<FlashcardDisplay {...defaultProps} mode="test" />);

            expect(screen.getByText('🎯 Test')).toBeInTheDocument();
        });
    });

    describe('Answer Input', () => {
        it('shows answer input before submission', () => {
            const { container } = render(<FlashcardDisplay {...defaultProps} />);

            const answerArea = container.querySelector('.flashcard-answer-area');
            expect(answerArea).toBeInTheDocument();
        });

        it('displays answer hint with format information', () => {
            render(<FlashcardDisplay {...defaultProps} />);

            expect(screen.getByText('Expected format:')).toBeInTheDocument();
        });
    });

    describe('Feedback Display', () => {
        it('displays correct feedback', () => {
            const correctFeedback: SessionFeedback = {
                is_correct: true,
                feedback: 'Correct! Well done!',
                correct_answer: '4',
            };

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    feedback={correctFeedback}
                />
            );

            expect(screen.getByText('Correct! Well done!')).toBeInTheDocument();
        });

        it('displays incorrect feedback', () => {
            const incorrectFeedback: SessionFeedback = {
                is_correct: false,
                feedback: 'Incorrect. The correct answer is 4.',
                correct_answer: '4',
            };

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    feedback={incorrectFeedback}
                />
            );

            expect(screen.getByText('Incorrect. The correct answer is 4.')).toBeInTheDocument();
        });
    });

    describe('Revealed Answer', () => {
        it('displays revealed answer when showAnswer is true', () => {
            render(
                <FlashcardDisplay
                    {...defaultProps}
                    showAnswer={true}
                />
            );

            expect(screen.getByText('Answer:')).toBeInTheDocument();
            expect(screen.getByText('4')).toBeInTheDocument();
        });

        it('includes speaker button for answer', () => {
            render(
                <FlashcardDisplay
                    {...defaultProps}
                    showAnswer={true}
                />
            );

            const speakerButtons = screen.getAllByLabelText(/Read.*aloud/i);
            expect(speakerButtons.length).toBeGreaterThan(1); // One for question, one for answer
        });
    });

    describe('Button Interactions', () => {
        it('calls onSubmitAnswer when Submit Answer is clicked', () => {
            const onSubmitAnswer = vi.fn();

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    userAnswer="4"
                    onSubmitAnswer={onSubmitAnswer}
                />
            );

            const submitButton = screen.getByText(/Check Answer|Submit Answer/);
            fireEvent.click(submitButton);

            expect(onSubmitAnswer).toHaveBeenCalled();
        });

        it('calls onRevealAnswer when Show Answer is clicked', () => {
            const onRevealAnswer = vi.fn();

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    mode="learn"
                    onRevealAnswer={onRevealAnswer}
                />
            );

            const showAnswerButton = screen.getByText('Show Answer');
            fireEvent.click(showAnswerButton);

            expect(onRevealAnswer).toHaveBeenCalled();
        });

        it('calls onNextFlashcard when Next button is clicked', () => {
            const onNextFlashcard = vi.fn();
            const feedback: SessionFeedback = {
                is_correct: true,
                feedback: 'Correct!',
                correct_answer: '4',
            };

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    feedback={feedback}
                    onNextFlashcard={onNextFlashcard}
                />
            );

            const nextButton = screen.getByText(/Next Flashcard/);
            fireEvent.click(nextButton);

            expect(onNextFlashcard).toHaveBeenCalled();
        });

        it('calls onSpeak when speaker button is clicked', () => {
            const onSpeak = vi.fn();

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    onSpeak={onSpeak}
                />
            );

            const speakerButton = screen.getAllByRole('button', { name: /Read.*aloud/i })[0];
            fireEvent.click(speakerButton);

            expect(onSpeak).toHaveBeenCalled();
        });

        it('disables submit button while submitting', () => {
            render(
                <FlashcardDisplay
                    {...defaultProps}
                    userAnswer="4"
                    isSubmitting={true}
                />
            );

            const submitButton = screen.getByText(/Submitting|Checking/);
            expect(submitButton).toBeDisabled();
        });
    });

    describe('Test Mode Behavior', () => {
        it('shows "Don\'t Know" button in test mode', () => {
            render(
                <FlashcardDisplay
                    {...defaultProps}
                    mode="test"
                />
            );

            expect(screen.getByText("Don't Know")).toBeInTheDocument();
        });

        it('submits empty answer when "Don\'t Know" is clicked', () => {
            const onUserAnswerChange = vi.fn();
            const onSubmitAnswer = vi.fn();

            render(
                <FlashcardDisplay
                    {...defaultProps}
                    mode="test"
                    onUserAnswerChange={onUserAnswerChange}
                    onSubmitAnswer={onSubmitAnswer}
                />
            );

            const dontKnowButton = screen.getByText("Don't Know");
            fireEvent.click(dontKnowButton);

            expect(onUserAnswerChange).toHaveBeenCalledWith('');
            expect(onSubmitAnswer).toHaveBeenCalled();
        });
    });
});
