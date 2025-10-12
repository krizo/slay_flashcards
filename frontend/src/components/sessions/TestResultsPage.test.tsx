import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TestResultsPage from './TestResultsPage';
import { TestResult } from '../../types';

describe('TestResultsPage', () => {
    const mockTestResultsPerfect: TestResult = {
        final_score: 100,
        correct: 3,
        total: 3,
        breakdown: [
            {
                flashcard_id: 1,
                question: 'What is 2+2?',
                user_answer: '4',
                correct_answer: '4',
                evaluation: 'correct',
            },
            {
                flashcard_id: 2,
                question: 'What is the capital of France?',
                user_answer: 'Paris',
                correct_answer: 'Paris',
                evaluation: 'correct',
            },
            {
                flashcard_id: 3,
                question: 'What is 10 * 5?',
                user_answer: '50',
                correct_answer: '50',
                evaluation: 'correct',
            },
        ],
    };

    const mockTestResultsMixed: TestResult = {
        final_score: 66.67,
        correct: 2,
        total: 3,
        breakdown: [
            {
                flashcard_id: 1,
                question: 'What is 2+2?',
                user_answer: '4',
                correct_answer: '4',
                evaluation: 'correct',
            },
            {
                flashcard_id: 2,
                question: 'What is the capital of France?',
                user_answer: 'London',
                correct_answer: 'Paris',
                evaluation: 'incorrect',
            },
            {
                flashcard_id: 3,
                question: 'What is 10 * 5?',
                user_answer: '50',
                correct_answer: '50',
                evaluation: 'correct',
            },
        ],
    };

    it('renders test results with score', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Test Complete!')).toBeInTheDocument();
        expect(screen.getAllByText('100%').length).toBeGreaterThan(0);
        expect(screen.getByText('3 out of 3 correct')).toBeInTheDocument();
    });

    it('displays celebration icon for high score (>= 80%)', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('🎉')).toBeInTheDocument();
    });

    it('displays all answered questions in breakdown', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
        expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
        expect(screen.getByText('What is 10 * 5?')).toBeInTheDocument();
    });

    it('displays correct answers with checkmark', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const correctCards = container.querySelectorAll('.timeline-card--correct');
        expect(correctCards).toHaveLength(2);
    });

    it('displays incorrect answers with X mark', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const incorrectCards = container.querySelectorAll('.timeline-card--incorrect');
        expect(incorrectCards).toHaveLength(1);
    });

    it('shows correct answer for incorrect responses', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        // Click on the incorrect answer card to reveal answers
        const incorrectCard = container.querySelector('.timeline-card--incorrect');
        expect(incorrectCard).toBeInTheDocument();

        if (incorrectCard) {
            fireEvent.click(incorrectCard);
            expect(screen.getByText('London')).toBeInTheDocument();
            expect(screen.getByText('Paris')).toBeInTheDocument();
        }
    });

    it('shows "Show Mistakes Only" filter button when there are incorrect answers', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText(/Show Mistakes Only/)).toBeInTheDocument();
    });

    it('does not show "Show Mistakes Only" filter button for perfect score', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.queryByText(/Show Mistakes Only/)).not.toBeInTheDocument();
    });

    it('always shows "Go to Quizzes" button', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Go to Quizzes')).toBeInTheDocument();
    });

    it('toggles mistakes filter when filter button is clicked', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const filterButton = screen.getByText(/Show Mistakes Only/);
        fireEvent.click(filterButton);

        expect(screen.getByText(/Show All/)).toBeInTheDocument();
    });

    it('calls onGoToQuizzes when "Go to Quizzes" button is clicked', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const goToQuizzesButton = screen.getByText('Go to Quizzes');
        fireEvent.click(goToQuizzesButton);

        expect(mockOnGoToQuizzes).toHaveBeenCalledTimes(1);
    });

    it('displays question number for each item in breakdown', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const timelineCards = container.querySelectorAll('.timeline-card');
        expect(timelineCards).toHaveLength(3);
    });

    it('applies correct styling classes to correct answers', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const correctItems = container.querySelectorAll('.timeline-card--correct');
        expect(correctItems).toHaveLength(2);
    });

    it('applies incorrect styling classes to incorrect answers', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const incorrectItems = container.querySelectorAll('.timeline-card--incorrect');
        expect(incorrectItems).toHaveLength(1);
    });

    it('handles empty user answer', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const testResultsWithEmpty: TestResult = {
            final_score: 0,
            correct: 0,
            total: 1,
            breakdown: [
                {
                    flashcard_id: 1,
                    question: 'What is 2+2?',
                    user_answer: '',
                    correct_answer: '4',
                    evaluation: 'incorrect',
                },
            ],
        };

        const { container } = render(
            <TestResultsPage
                testResults={testResultsWithEmpty}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        // Click on the card to reveal answers
        const card = container.querySelector('.timeline-card');
        expect(card).toBeInTheDocument();

        if (card) {
            fireEvent.click(card);
            expect(screen.getByText('(no answer)')).toBeInTheDocument();
        }
    });

    it('always shows "Retry Test" button', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Retry Test')).toBeInTheDocument();
    });

    it('always shows "Learn Mode" button', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Learn Mode')).toBeInTheDocument();
    });

    it('calls onRetry when "Retry Test" button is clicked', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const retryButton = screen.getByText('Retry Test');
        fireEvent.click(retryButton);

        expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });

    it('calls onLearn when "Learn Mode" button is clicked', () => {
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const learnButton = screen.getByText('Learn Mode');
        fireEvent.click(learnButton);

        expect(mockOnLearn).toHaveBeenCalledTimes(1);
    });
});
