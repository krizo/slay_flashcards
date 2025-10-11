import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SessionHeader from './SessionHeader';

describe('SessionHeader', () => {
    const mockOnCloseSession = vi.fn();
    const quizName = 'Test Quiz Name';

    beforeEach(() => {
        mockOnCloseSession.mockClear();
    });

    it('renders quiz name without "Quiz:" prefix', () => {
        render(
            <SessionHeader
                quizName={quizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(screen.getByText(quizName)).toBeInTheDocument();
        expect(screen.queryByText(/Quiz:/)).not.toBeInTheDocument();
    });

    it('renders books icon when no image is provided', () => {
        render(
            <SessionHeader
                quizName={quizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        const icon = screen.getByText('📚');
        expect(icon).toBeInTheDocument();
        expect(icon).toHaveClass('session-quiz-icon');
    });

    it('renders books icon when image is null', () => {
        render(
            <SessionHeader
                quizName={quizName}
                quizImage={null}
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(screen.getByText('📚')).toBeInTheDocument();
    });

    it('renders books icon when image does not have valid data:image prefix', () => {
        render(
            <SessionHeader
                quizName={quizName}
                quizImage="8J+Suw=="
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(screen.getByText('📚')).toBeInTheDocument();
        expect(screen.queryByRole('img')).not.toBeInTheDocument();
    });

    it('renders quiz image when valid base64 image is provided', () => {
        const validImage = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

        render(
            <SessionHeader
                quizName={quizName}
                quizImage={validImage}
                onCloseSession={mockOnCloseSession}
            />
        );

        const image = screen.getByRole('img', { name: quizName });
        expect(image).toBeInTheDocument();
        expect(image).toHaveAttribute('src', validImage);
        expect(image).toHaveClass('session-quiz-image');
        expect(screen.queryByText('📚')).not.toBeInTheDocument();
    });

    it('renders close button', () => {
        render(
            <SessionHeader
                quizName={quizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        const closeButton = screen.getByRole('button', { name: /close session/i });
        expect(closeButton).toBeInTheDocument();
        expect(closeButton).toHaveTextContent('✕');
    });

    it('calls onCloseSession when close button is clicked', () => {
        render(
            <SessionHeader
                quizName={quizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        const closeButton = screen.getByRole('button', { name: /close session/i });
        fireEvent.click(closeButton);

        expect(mockOnCloseSession).toHaveBeenCalledTimes(1);
    });

    it('applies correct CSS classes to wrapper elements', () => {
        const { container } = render(
            <SessionHeader
                quizName={quizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(container.querySelector('.session-header')).toBeInTheDocument();
        expect(container.querySelector('.session-title-wrapper')).toBeInTheDocument();
        expect(container.querySelector('.session-title')).toBeInTheDocument();
        expect(container.querySelector('.session-close-button')).toBeInTheDocument();
    });

    it('handles long quiz names', () => {
        const longQuizName = 'This is a very long quiz name that should still be displayed correctly without breaking the layout';

        render(
            <SessionHeader
                quizName={longQuizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(screen.getByText(longQuizName)).toBeInTheDocument();
    });

    it('handles special characters in quiz name', () => {
        const specialQuizName = 'Quiz: C++ & Algorithms (2024) — Level 1 "Advanced"';

        render(
            <SessionHeader
                quizName={specialQuizName}
                onCloseSession={mockOnCloseSession}
            />
        );

        expect(screen.getByText(specialQuizName)).toBeInTheDocument();
    });
});
