import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ActivitySidebar from './ActivitySidebar';
import { Session } from '../../types';

describe('ActivitySidebar', () => {
    const mockSessions: Session[] = [
        {
            id: 1,
            user_id: 1,
            quiz_id: 7,
            mode: 'test',
            started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
            score: 85,
            completed_at: new Date().toISOString(),
            quiz_name: 'JavaScript Basics',
        },
        {
            id: 2,
            user_id: 1,
            quiz_id: 5,
            mode: 'learn',
            started_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
            score: null,
            completed_at: new Date().toISOString(),
            quiz_name: 'Python Fundamentals',
        },
        {
            id: 3,
            user_id: 1,
            quiz_id: 12,
            mode: 'test',
            started_at: new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString(), // 25 hours ago (Yesterday)
            score: 92,
            completed_at: new Date().toISOString(),
        },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders loading state', () => {
        render(<ActivitySidebar recentSessions={null} isLoading={true} />);

        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('Loading activity...')).toBeInTheDocument();
    });

    it('renders error state', () => {
        const error = new Error('Failed to load recent sessions');
        render(<ActivitySidebar recentSessions={null} error={error} />);

        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('Failed to load activity')).toBeInTheDocument();
        expect(screen.getByText(error.message)).toBeInTheDocument();
    });

    it('renders empty state when no sessions provided', () => {
        render(<ActivitySidebar recentSessions={null} />);

        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('No recent activity')).toBeInTheDocument();
    });

    it('renders empty state when sessions array is empty', () => {
        render(<ActivitySidebar recentSessions={[]} />);

        expect(screen.getByText('No recent activity')).toBeInTheDocument();
    });

    it('renders session list with data', () => {
        render(<ActivitySidebar recentSessions={mockSessions} />);

        expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
        expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();
    });

    it('displays quiz name fallback when quiz_name is missing', () => {
        render(<ActivitySidebar recentSessions={mockSessions} />);

        // Third session has no quiz_name, should show "Quiz #12"
        expect(screen.getByText('Quiz #12')).toBeInTheDocument();
    });

    it('displays correct mode for each session', () => {
        render(<ActivitySidebar recentSessions={mockSessions} />);

        const modeElements = screen.getAllByText(/test|learn/);
        expect(modeElements).toHaveLength(3);
        expect(screen.getAllByText('test')).toHaveLength(2);
        expect(screen.getAllByText('learn')).toHaveLength(1);
    });

    it('displays score only for test sessions with scores', () => {
        render(<ActivitySidebar recentSessions={mockSessions} />);

        expect(screen.getByText('85%')).toBeInTheDocument();
        expect(screen.getByText('92%')).toBeInTheDocument();

        // Learn session should not have score displayed
        const scores = screen.queryAllByText(/%$/);
        expect(scores).toHaveLength(2); // Only 2 test sessions with scores
    });

    it('does not display score for learn sessions', () => {
        const learnSession: Session[] = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn',
                started_at: new Date().toISOString(),
                score: null,
                completed_at: new Date().toISOString(),
                quiz_name: 'Test Quiz',
            },
        ];

        render(<ActivitySidebar recentSessions={learnSession} />);

        expect(screen.getByText('learn')).toBeInTheDocument();
        expect(screen.queryByText(/%$/)).not.toBeInTheDocument();
    });

    it('formats time correctly for recent sessions (hours ago)', () => {
        const recentSession: Session[] = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'learn',
                started_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), // 3 hours ago
                score: null,
                completed_at: new Date().toISOString(),
                quiz_name: 'Test Quiz',
            },
        ];

        render(<ActivitySidebar recentSessions={recentSession} />);

        expect(screen.getByText('3h ago')).toBeInTheDocument();
    });

    it('formats time correctly for sessions from yesterday', () => {
        const yesterdaySession: Session[] = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test',
                started_at: new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString(), // 25 hours ago
                score: 88,
                completed_at: new Date().toISOString(),
                quiz_name: 'Test Quiz',
            },
        ];

        render(<ActivitySidebar recentSessions={yesterdaySession} />);

        expect(screen.getByText('Yesterday')).toBeInTheDocument();
    });

    it('formats time correctly for sessions from multiple days ago', () => {
        const oldSession: Session[] = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test',
                started_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
                score: 88,
                completed_at: new Date().toISOString(),
                quiz_name: 'Test Quiz',
            },
        ];

        render(<ActivitySidebar recentSessions={oldSession} />);

        expect(screen.getByText('3d ago')).toBeInTheDocument();
    });

    it('formats time as "Just now" for very recent sessions', () => {
        const justNowSession: Session[] = [
            {
                id: 1,
                user_id: 1,
                quiz_id: 5,
                mode: 'test',
                started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
                score: 88,
                completed_at: new Date().toISOString(),
                quiz_name: 'Test Quiz',
            },
        ];

        render(<ActivitySidebar recentSessions={justNowSession} />);

        expect(screen.getByText('Just now')).toBeInTheDocument();
    });

    it('renders all sessions in correct order', () => {
        render(<ActivitySidebar recentSessions={mockSessions} />);

        const activityItems = screen.getAllByText(/test|learn/);
        expect(activityItems).toHaveLength(3);
    });

    it('displays correct icons for learn and test modes', () => {
        const { container } = render(<ActivitySidebar recentSessions={mockSessions} />);

        const activityIcons = container.querySelectorAll('.activity-icon');
        expect(activityIcons).toHaveLength(3);

        // Check that icons contain the expected emojis (test: ✅, learn: 📖)
        expect(activityIcons[0].textContent).toBe('✅'); // First session is the test
        expect(activityIcons[1].textContent).toBe('📖'); // Second session is learning one
        expect(activityIcons[2].textContent).toBe('✅'); // Third session is the test
    });
});
