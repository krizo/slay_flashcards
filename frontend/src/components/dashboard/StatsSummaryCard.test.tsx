import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StatsSummaryCard from './StatsSummaryCard';
import { UserStats, Session } from '../../types';

// Helper function to render with user event
const renderWithUser = (component: React.ReactElement) => {
    return {
        user: userEvent.setup(),
        ...render(component),
    };
};

describe('StatsSummaryCard', () => {
    const mockStats: UserStats = {
        total_sessions: 58,
        learn_sessions: 41,
        test_sessions: 17,
        average_score: 82.88,
        best_score: 97,
        study_streak: 15,
        favorite_subjects: [],
        sessions_this_week: 29,
        sessions_this_month: 58,
        unique_quizzes: 12,
    };

    const mockSessions: Session[] = [
        {
            id: 1,
            user_id: 1,
            quiz_id: 7,
            mode: 'test',
            started_at: '2025-10-08T08:38:52Z',
            score: 75,
            completed_at: '2025-10-08T09:00:52Z',
            quiz_name: 'JavaScript Basics',
        },
        {
            id: 2,
            user_id: 1,
            quiz_id: 5,
            mode: 'learn',
            started_at: '2025-10-07T10:20:00Z',
            score: null,
            completed_at: '2025-10-07T10:45:00Z',
            quiz_name: 'Python Fundamentals',
        },
    ];

    it('renders loading state', () => {
        render(<StatsSummaryCard stats={null} isLoading={true} />);

        expect(screen.getByText('Loading statistics...')).toBeInTheDocument();
    });

    it('renders error state', () => {
        const error = new Error('API connection failed');
        render(<StatsSummaryCard stats={null} error={error} />);

        expect(screen.getByText('Failed to load statistics')).toBeInTheDocument();
        expect(screen.getByText('API connection failed')).toBeInTheDocument();
    });

    it('renders empty state when no stats provided', () => {
        render(<StatsSummaryCard stats={null} />);

        expect(screen.getByText('No statistics available')).toBeInTheDocument();
    });

    it('renders user statistics correctly', () => {
        render(<StatsSummaryCard stats={mockStats} userName="Emila" recentSessions={mockSessions} />);

        // Check welcome message
        expect(screen.getByText('Welcome back, Emila! 👋')).toBeInTheDocument();

        // Check stats values (using getAllByText for duplicates)
        const totalSessionsElements = screen.getAllByText('58');
        expect(totalSessionsElements.length).toBeGreaterThanOrEqual(1); // Total sessions (and recent activity)

        expect(screen.getByText('83%')).toBeInTheDocument(); // Average score (rounded)

        // "15" appears twice: for Study Streak and Days Active (both same in 'all' mode)
        const fifteenElements = screen.getAllByText('15');
        expect(fifteenElements.length).toBe(2);

        expect(screen.getByText('97%')).toBeInTheDocument(); // Best score
        expect(screen.getByText('41')).toBeInTheDocument(); // Learn sessions
        expect(screen.getByText('17')).toBeInTheDocument(); // Test sessions
        expect(screen.getByText('12')).toBeInTheDocument(); // Unique quizzes

        // Check calculated stats
        expect(screen.getByText('75%')).toBeInTheDocument(); // Latest score
        expect(screen.getByText('69%')).toBeInTheDocument(); // Min score (estimated: 97 - (97-83)*2 = 69)
        expect(screen.getByText('1.9')).toBeInTheDocument(); // Daily average (58/30)
    });

    it('renders with default user name when not provided', () => {
        render(<StatsSummaryCard stats={mockStats} />);

        expect(screen.getByText('Welcome back, User! 👋')).toBeInTheDocument();
    });

    it('displays — for null average score', () => {
        const statsWithNullAverage = { ...mockStats, average_score: null };
        render(<StatsSummaryCard stats={statsWithNullAverage} recentSessions={mockSessions} />);

        expect(screen.getByText('—%')).toBeInTheDocument();
    });

    it('displays — for null best score', () => {
        const statsWithNullBest = { ...mockStats, best_score: null };
        render(<StatsSummaryCard stats={statsWithNullBest} recentSessions={mockSessions} />);

        // Should have "—%" for best score and min score (which depends on best score)
        const dashElements = screen.getAllByText('—');
        expect(dashElements.length).toBeGreaterThan(0);
    });

    it('renders all stat labels correctly', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

        // Row 1: Session Overview
        expect(screen.getByText('Total Sessions')).toBeInTheDocument();
        expect(screen.getByText('Learn Sessions')).toBeInTheDocument();
        expect(screen.getByText('Test Sessions')).toBeInTheDocument();
        expect(screen.getByText('Unique Quizzes')).toBeInTheDocument();

        // Row 2: Performance Metrics (Latest Score swapped with Study Streak)
        expect(screen.getByText('Average Score')).toBeInTheDocument();
        expect(screen.getByText('Best Score')).toBeInTheDocument();
        expect(screen.getByText('Latest Score')).toBeInTheDocument();
        expect(screen.getByText('Study Streak')).toBeInTheDocument();

        // Row 3: Recent Activity
        expect(screen.getByText('Days Active')).toBeInTheDocument();
        expect(screen.getByText('Min Score')).toBeInTheDocument();
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('Daily Average')).toBeInTheDocument();
    });

    it('renders quick actions section', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
        expect(screen.getByText('Start Learning')).toBeInTheDocument();
        expect(screen.getByText('Take a Test')).toBeInTheDocument();
        expect(screen.getByText('Create Quiz')).toBeInTheDocument();
    });

    it('rounds decimal scores to integers', () => {
        const statsWithDecimals = {
            ...mockStats,
            average_score: 85.67,
            best_score: 92.34,
        };
        render(<StatsSummaryCard stats={statsWithDecimals} recentSessions={mockSessions} />);

        // Should round 85.67 to 86
        expect(screen.getByText('86%')).toBeInTheDocument();
        // Should round 92.34 to 92
        expect(screen.getByText('92%')).toBeInTheDocument();
    });

    it('displays — for latest score when no recent sessions', () => {
        render(<StatsSummaryCard stats={mockStats} recentSessions={null} />);

        // Should show — for latest score
        const latestScoreValue = screen.getAllByText('—');
        expect(latestScoreValue.length).toBeGreaterThan(0);
    });

    it('displays — for latest score when no test sessions available', () => {
        const learnOnlySessions: Session[] = [
            {
                id: 2,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn',
                started_at: '2025-10-07T10:20:00Z',
                score: null,
                completed_at: '2025-10-07T10:45:00Z',
                quiz_name: 'Python Fundamentals',
            },
        ];
        render(<StatsSummaryCard stats={mockStats} recentSessions={learnOnlySessions} />);

        // Should show — for latest score since there are no test sessions
        const latestScoreValue = screen.getAllByText('—');
        expect(latestScoreValue.length).toBeGreaterThan(0);
    });

    describe('Time Period Filter', () => {
        it('renders all time period filter buttons', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            expect(screen.getByText('Week')).toBeInTheDocument();
            expect(screen.getByText('Month')).toBeInTheDocument();
            expect(screen.getByText('Year')).toBeInTheDocument();
            expect(screen.getByText('All Time')).toBeInTheDocument();
        });

        it('defaults to "All Time" period', () => {
            render(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            const allTimeButton = screen.getByText('All Time');
            expect(allTimeButton).toHaveClass('active');
        });

        it('changes active button when clicked', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            const weekButton = screen.getByText('Week');
            const allTimeButton = screen.getByText('All Time');

            // Initially All Time is active
            expect(allTimeButton).toHaveClass('active');
            expect(weekButton).not.toHaveClass('active');

            // Click Week button
            await user.click(weekButton);

            // Now Week is active
            expect(weekButton).toHaveClass('active');
            expect(allTimeButton).not.toHaveClass('active');
        });

        it('updates Days Active subtitle when period changes', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            // Initially shows "all time"
            expect(screen.getByText('all time')).toBeInTheDocument();

            // Click Week button
            await user.click(screen.getByText('Week'));
            expect(screen.getByText('last week')).toBeInTheDocument();

            // Click Month button
            await user.click(screen.getByText('Month'));
            expect(screen.getByText('last month')).toBeInTheDocument();

            // Click Year button
            await user.click(screen.getByText('Year'));
            expect(screen.getByText('last year')).toBeInTheDocument();
        });

        it('calculates Days Active correctly for week period', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            // Click Week button
            await user.click(screen.getByText('Week'));

            // Should show min(sessions_this_week, 7) = min(29, 7) = 7
            const daysActiveElements = screen.getAllByText('7');
            expect(daysActiveElements.length).toBeGreaterThanOrEqual(1);
        });

        it('calculates Days Active correctly for month period', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            // Click Month button
            await user.click(screen.getByText('Month'));

            // Should show min(sessions_this_month, 30) = min(58, 30) = 30
            expect(screen.getByText('30')).toBeInTheDocument();
        });

        it('calculates Days Active correctly for year and all time periods', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            // Year should show study_streak
            await user.click(screen.getByText('Year'));
            const yearElements = screen.getAllByText('15');
            expect(yearElements.length).toBe(2); // Study Streak and Days Active both show 15

            // All Time should also show study_streak
            await user.click(screen.getByText('All Time'));
            const allTimeElements = screen.getAllByText('15');
            expect(allTimeElements.length).toBe(2);
        });

        it('handles week period with fewer sessions than days', async () => {
            const statsWithFewSessions = {
                ...mockStats,
                sessions_this_week: 3,
            };
            const { user } = renderWithUser(
                <StatsSummaryCard stats={statsWithFewSessions} recentSessions={mockSessions} />
            );

            await user.click(screen.getByText('Week'));

            // Should show min(3, 7) = 3
            expect(screen.getByText('3')).toBeInTheDocument();
        });

        it('handles month period with fewer sessions than days', async () => {
            const statsWithFewSessions = {
                ...mockStats,
                sessions_this_month: 15,
            };
            const { user } = renderWithUser(
                <StatsSummaryCard stats={statsWithFewSessions} recentSessions={mockSessions} />
            );

            await user.click(screen.getByText('Month'));

            // Should show min(15, 30) = 15
            const fifteenElements = screen.getAllByText('15');
            expect(fifteenElements.length).toBeGreaterThanOrEqual(1);
        });

        it('switches between all time periods correctly', async () => {
            const { user } = renderWithUser(<StatsSummaryCard stats={mockStats} recentSessions={mockSessions} />);

            // Click through all periods
            await user.click(screen.getByText('Week'));
            expect(screen.getByText('Week')).toHaveClass('active');

            await user.click(screen.getByText('Month'));
            expect(screen.getByText('Month')).toHaveClass('active');
            expect(screen.getByText('Week')).not.toHaveClass('active');

            await user.click(screen.getByText('Year'));
            expect(screen.getByText('Year')).toHaveClass('active');
            expect(screen.getByText('Month')).not.toHaveClass('active');

            await user.click(screen.getByText('All Time'));
            expect(screen.getByText('All Time')).toHaveClass('active');
            expect(screen.getByText('Year')).not.toHaveClass('active');
        });
    });
});
