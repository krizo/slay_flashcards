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
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
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
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('🎉')).toBeInTheDocument();
    });

    it('displays all answered questions in breakdown', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
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
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const correctCards = container.querySelectorAll('.timeline-card--correct');
        expect(correctCards).toHaveLength(2);
    });

    it('displays incorrect answers with X mark', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const incorrectCards = container.querySelectorAll('.timeline-card--incorrect');
        expect(incorrectCards).toHaveLength(1);
    });

    it('shows correct answer for incorrect responses', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('London')).toBeInTheDocument();
        expect(screen.getByText('Paris')).toBeInTheDocument();
    });

    it('shows "Review Mistakes" button when there are incorrect answers', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Review Mistakes')).toBeInTheDocument();
    });

    it('does not show "Review Mistakes" button for perfect score', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.queryByText('Review Mistakes')).not.toBeInTheDocument();
    });

    it('always shows "Go to Quizzes" button', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Go to Quizzes')).toBeInTheDocument();
    });

    it('calls onReviewMistakes when "Review Mistakes" button is clicked', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const reviewButton = screen.getByText('Review Mistakes');
        fireEvent.click(reviewButton);

        expect(mockOnReviewMistakes).toHaveBeenCalledTimes(1);
    });

    it('calls onGoToQuizzes when "Go to Quizzes" button is clicked', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
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
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const timelineCards = container.querySelectorAll('.timeline-card');
        expect(timelineCards).toHaveLength(3);
    });

    it('applies correct styling classes to correct answers', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const correctItems = container.querySelectorAll('.timeline-card--correct');
        expect(correctItems).toHaveLength(2);
    });

    it('applies incorrect styling classes to incorrect answers', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        const { container } = render(
            <TestResultsPage
                testResults={mockTestResultsMixed}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        const incorrectItems = container.querySelectorAll('.timeline-card--incorrect');
        expect(incorrectItems).toHaveLength(1);
    });

    it('handles empty user answer', () => {
        const mockOnReviewMistakes = vi.fn();
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

        render(
            <TestResultsPage
                testResults={testResultsWithEmpty}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('(no answer)')).toBeInTheDocument();
    });

    it('always shows "Retry Test" button', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Retry Test')).toBeInTheDocument();
    });

    it('always shows "Learn Mode" button', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
                onGoToQuizzes={mockOnGoToQuizzes}
                onRetry={mockOnRetry}
                onLearn={mockOnLearn}
            />
        );

        expect(screen.getByText('Learn Mode')).toBeInTheDocument();
    });

    it('calls onRetry when "Retry Test" button is clicked', () => {
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
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
        const mockOnReviewMistakes = vi.fn();
        const mockOnGoToQuizzes = vi.fn();
        const mockOnRetry = vi.fn();
        const mockOnLearn = vi.fn();

        render(
            <TestResultsPage
                testResults={mockTestResultsPerfect}
                onReviewMistakes={mockOnReviewMistakes}
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
