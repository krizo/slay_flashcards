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

    describe('Statistics Metrics', () => {
        it('displays "Your Best" metric with percentage when value provided', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    yourBest={95.5}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('96%')).toBeInTheDocument(); // Rounded
            expect(screen.getByText('Your Best')).toBeInTheDocument();
        });

        it('displays "—" for "Your Best" when null', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    yourBest={null}
                    onCloseSession={mockOnCloseSession}
                />
            );

            const metrics = screen.getAllByText('—');
            expect(metrics.length).toBeGreaterThan(0);
        });

        it('displays "Your Avg" metric with percentage when value provided', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    yourAverage={82.3}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('82%')).toBeInTheDocument(); // Rounded
            expect(screen.getByText('Your Avg')).toBeInTheDocument();
        });

        it('displays "—" for "Your Avg" when null', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    yourAverage={null}
                    onCloseSession={mockOnCloseSession}
                />
            );

            const metrics = screen.getAllByText('—');
            expect(metrics.length).toBeGreaterThan(0);
        });

        it('displays "Test Sessions" count when value provided', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    testSessions={15}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('15')).toBeInTheDocument();
            expect(screen.getByText('Test Sessions')).toBeInTheDocument();
        });

        it('displays "—" for "Test Sessions" when zero', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    testSessions={0}
                    onCloseSession={mockOnCloseSession}
                />
            );

            const metrics = screen.getAllByText('—');
            expect(metrics.length).toBeGreaterThan(0);
        });

        it('displays all metrics with proper icons', () => {
            const { container } = render(
                <SessionHeader
                    quizName={quizName}
                    yourBest={95}
                    yourAverage={85}
                    testSessions={10}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('⭐')).toBeInTheDocument(); // Your Best icon
            expect(screen.getByText('📊')).toBeInTheDocument(); // Your Avg icon
            expect(screen.getByText('🎯')).toBeInTheDocument(); // Test Sessions icon
            expect(screen.getByText('🕒')).toBeInTheDocument(); // Last Session icon
        });
    });

    describe('Last Session Time Formatting', () => {
        const now = new Date('2025-10-11T12:00:00.000Z');

        beforeEach(() => {
            vi.useFakeTimers();
            vi.setSystemTime(now);
        });

        afterEach(() => {
            vi.useRealTimers();
        });

        it('displays "First time!" when no lastSessionDate provided', () => {
            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={null}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('First time!')).toBeInTheDocument();
        });

        it('displays "Just now" for sessions less than 30 seconds ago', () => {
            const recentDate = new Date(now.getTime() - 20 * 1000).toISOString(); // 20 seconds ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={recentDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('Just now')).toBeInTheDocument();
        });

        it('displays seconds for sessions less than 1 minute ago', () => {
            const recentDate = new Date(now.getTime() - 45 * 1000).toISOString(); // 45 seconds ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={recentDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('45 sec ago')).toBeInTheDocument();
        });

        it('displays minutes for sessions less than 1 hour ago', () => {
            const recentDate = new Date(now.getTime() - 30 * 60 * 1000).toISOString(); // 30 minutes ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={recentDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('30 min ago')).toBeInTheDocument();
        });

        it('displays hours for sessions less than 24 hours ago', () => {
            const recentDate = new Date(now.getTime() - 5 * 60 * 60 * 1000).toISOString(); // 5 hours ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={recentDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('5h ago')).toBeInTheDocument();
        });

        it('displays "Yesterday" for sessions exactly 1 day ago', () => {
            const yesterdayDate = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={yesterdayDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('Yesterday')).toBeInTheDocument();
        });

        it('displays days for sessions less than 7 days ago', () => {
            const daysAgoDate = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(); // 3 days ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={daysAgoDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('3 days ago')).toBeInTheDocument();
        });

        it('displays weeks for sessions less than 30 days ago', () => {
            const weeksAgoDate = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000).toISOString(); // 14 days ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={weeksAgoDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            expect(screen.getByText('2 weeks ago')).toBeInTheDocument();
        });

        it('displays formatted date for sessions older than 30 days', () => {
            const oldDate = new Date('2025-08-15T12:00:00.000Z').toISOString(); // About 2 months ago

            render(
                <SessionHeader
                    quizName={quizName}
                    lastSessionDate={oldDate}
                    onCloseSession={mockOnCloseSession}
                />
            );

            // Should display a formatted date like "8/15/2025"
            const dateElement = screen.getByText(/\d+\/\d+\/\d+/);
            expect(dateElement).toBeInTheDocument();
        });
    });
});
