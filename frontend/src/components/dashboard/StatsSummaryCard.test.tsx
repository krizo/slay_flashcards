import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatsSummaryCard from './StatsSummaryCard';
import { UserStats } from '../../types';

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
        render(<StatsSummaryCard stats={mockStats} userName="Emila" />);

        // Check welcome message
        expect(screen.getByText('Welcome back, Emila! 👋')).toBeInTheDocument();

        // Check stats values
        expect(screen.getByText('58')).toBeInTheDocument(); // Total sessions
        expect(screen.getByText('83%')).toBeInTheDocument(); // Average score (rounded)
        expect(screen.getByText('15')).toBeInTheDocument(); // Study streak
        expect(screen.getByText('97%')).toBeInTheDocument(); // Best score
        expect(screen.getByText('41')).toBeInTheDocument(); // Learn sessions
        expect(screen.getByText('17')).toBeInTheDocument(); // Test sessions
    });

    it('renders with default user name when not provided', () => {
        render(<StatsSummaryCard stats={mockStats} />);

        expect(screen.getByText('Welcome back, User! 👋')).toBeInTheDocument();
    });

    it('displays N/A for null average score', () => {
        const statsWithNullAverage = { ...mockStats, average_score: null };
        render(<StatsSummaryCard stats={statsWithNullAverage} />);

        expect(screen.getByText('N/A%')).toBeInTheDocument();
    });

    it('displays N/A for null best score', () => {
        const statsWithNullBest = { ...mockStats, best_score: null };
        render(<StatsSummaryCard stats={statsWithNullBest} />);

        // Should have one N/A% for best score
        const naElements = screen.getAllByText('N/A%');
        expect(naElements.length).toBeGreaterThan(0);
    });

    it('renders all stat labels correctly', () => {
        render(<StatsSummaryCard stats={mockStats} />);

        expect(screen.getByText('Total Sessions')).toBeInTheDocument();
        expect(screen.getByText('Average Score')).toBeInTheDocument();
        expect(screen.getByText('Day Streak')).toBeInTheDocument();
        expect(screen.getByText('Best Score')).toBeInTheDocument();
        expect(screen.getByText('Learn Sessions')).toBeInTheDocument();
        expect(screen.getByText('Test Sessions')).toBeInTheDocument();
    });

    it('renders quick actions section', () => {
        render(<StatsSummaryCard stats={mockStats} />);

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
        render(<StatsSummaryCard stats={statsWithDecimals} />);

        // Should round 85.67 to 86
        expect(screen.getByText('86%')).toBeInTheDocument();
        // Should round 92.34 to 92
        expect(screen.getByText('92%')).toBeInTheDocument();
    });
});
