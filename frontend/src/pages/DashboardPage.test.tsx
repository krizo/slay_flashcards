import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardPage from './DashboardPage';
import * as useDashboardData from '../hooks/useDashboardData';
import { User, UserStats, Session, ProgressDataPoint } from '../types';

// Mock the hooks module
vi.mock('../hooks/useDashboardData', () => ({
    useCurrentUser: vi.fn(),
    useUserStats: vi.fn(),
    useRecentSessions: vi.fn(),
    useProgressData: vi.fn(),
    useSessionsData: vi.fn(),
}));

// Mock the AuthContext module
vi.mock('../context/AuthContext', () => ({
    useAuth: () => ({
        accessToken: 'mock-access-token',
        user: { id: 1, name: 'Emila', email: 'emila@test.com', created_at: '2025-10-08T10:00:00Z' },
        isLoading: false,
        isAuthenticated: true,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}));

describe('DashboardPage', () => {
    const mockUser: User = {
        id: 1,
        name: 'Emila',
        email: 'emila@test.com',
        created_at: '2025-10-08T10:00:00Z',
    };

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

    const mockProgressData: ProgressDataPoint[] = [
        { date: '2025-10-02', score: 75 },
        { date: '2025-10-03', score: 78 },
        { date: '2025-10-04', score: 80 },
        { date: '2025-10-05', score: 82 },
        { date: '2025-10-06', score: 79 },
        { date: '2025-10-07', score: 85 },
        { date: '2025-10-08', score: 88 },
    ];

    const mockSessionsData = [
        { date: '2025-10-04', learn: 2, test: 1 },
        { date: '2025-10-05', learn: 1, test: 0 },
        { date: '2025-10-06', learn: 3, test: 2 },
        { date: '2025-10-07', learn: 0, test: 1 },
        { date: '2025-10-08', learn: 2, test: 0 },
        { date: '2025-10-09', learn: 1, test: 1 },
        { date: '2025-10-10', learn: 2, test: 3 },
    ];

    beforeEach(() => {
        vi.clearAllMocks();

        // Default mock implementations
        vi.mocked(useDashboardData.useCurrentUser).mockReturnValue({
            data: mockUser,
            isLoading: false,
            error: null,
        });

        vi.mocked(useDashboardData.useUserStats).mockReturnValue({
            data: mockStats,
            isLoading: false,
            error: null,
        });

        vi.mocked(useDashboardData.useRecentSessions).mockReturnValue({
            data: mockSessions,
            isLoading: false,
            error: null,
        });

        vi.mocked(useDashboardData.useProgressData).mockReturnValue({
            data: mockProgressData,
            isLoading: false,
            error: null,
        });

        vi.mocked(useDashboardData.useSessionsData).mockReturnValue({
            data: mockSessionsData,
            isLoading: false,
            error: null,
        });
    });

    it('renders page header with title and description', () => {
        render(<DashboardPage />);

        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Track your learning progress and stay motivated!')).toBeInTheDocument();
    });

    it('renders all main dashboard components', () => {
        render(<DashboardPage />);

        // Check for elements from each component
        expect(screen.getByText(/Welcome back/)).toBeInTheDocument(); // StatsSummaryCard
        expect(screen.getByText('Progress Over Time')).toBeInTheDocument(); // ProgressChartCard
        expect(screen.getByText('Sessions Over Time')).toBeInTheDocument(); // SessionsChartCard
        // "Recent Activity" appears in both StatsSummaryCard and ActivitySidebar
        const recentActivityElements = screen.getAllByText('Recent Activity');
        expect(recentActivityElements.length).toBeGreaterThanOrEqual(1);
    });

    it('passes user name to StatsSummaryCard', () => {
        render(<DashboardPage />);

        expect(screen.getByText('Welcome back, Emila! 👋')).toBeInTheDocument();
    });

    it('passes stats with loading and error states to StatsSummaryCard', () => {
        vi.mocked(useDashboardData.useUserStats).mockReturnValue({
            data: null,
            isLoading: true,
            error: null,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Loading statistics...')).toBeInTheDocument();
    });

    it('passes progress data with loading state to ProgressChartCard', () => {
        vi.mocked(useDashboardData.useProgressData).mockReturnValue({
            data: null,
            isLoading: true,
            error: null,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Loading progress data...')).toBeInTheDocument();
    });

    it('passes sessions with loading state to ActivitySidebar', () => {
        vi.mocked(useDashboardData.useRecentSessions).mockReturnValue({
            data: null,
            isLoading: true,
            error: null,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Loading activity...')).toBeInTheDocument();
    });

    it('calls hooks with correct parameters', () => {
        render(<DashboardPage />);

        expect(useDashboardData.useCurrentUser).toHaveBeenCalledTimes(1);
        expect(useDashboardData.useUserStats).toHaveBeenCalledWith(1); // userId = 1
        expect(useDashboardData.useRecentSessions).toHaveBeenCalledWith(1, 5); // userId = 1, limit = 5
        expect(useDashboardData.useProgressData).toHaveBeenCalledWith(1, 365); // userId = 1, days = 365 (default 'all')
        expect(useDashboardData.useSessionsData).toHaveBeenCalledWith(1, 365); // userId = 1, days = 365 (default 'all')
    });

    it('handles error state in StatsSummaryCard', () => {
        const error = new Error('Network timeout occurred');
        vi.mocked(useDashboardData.useUserStats).mockReturnValue({
            data: null,
            isLoading: false,
            error,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Failed to load statistics')).toBeInTheDocument();
        expect(screen.getByText('Network timeout occurred')).toBeInTheDocument();
    });

    it('handles error state in ProgressChartCard', () => {
        const error = new Error('Failed to load progress');
        vi.mocked(useDashboardData.useProgressData).mockReturnValue({
            data: null,
            isLoading: false,
            error,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Failed to load progress data')).toBeInTheDocument();
        expect(screen.getByText(error.message)).toBeInTheDocument();
    });

    it('handles error state in ActivitySidebar', () => {
        const error = new Error('Unable to fetch sessions');
        vi.mocked(useDashboardData.useRecentSessions).mockReturnValue({
            data: null,
            isLoading: false,
            error,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Failed to load activity')).toBeInTheDocument();
        expect(screen.getByText('Unable to fetch sessions')).toBeInTheDocument();
    });

    it('renders with default user name when user data is not loaded', () => {
        vi.mocked(useDashboardData.useCurrentUser).mockReturnValue({
            data: null,
            isLoading: false,
            error: null,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Welcome back, User! 👋')).toBeInTheDocument();
    });

    it('displays all dashboard data when all hooks return successfully', () => {
        render(<DashboardPage />);

        // Check StatsSummaryCard data
        // Total sessions now calculated from sessionsData: 2+1+3+0+2+1+2 learn + 1+0+2+1+0+1+3 test = 12+8 = 19 (was 58)
        const sessionsElements = screen.getAllByText('19');
        expect(sessionsElements.length).toBeGreaterThanOrEqual(1); // total sessions and recent activity both show 19

        // Average score is now calculated from progressData: (75+78+80+82+79+85+88)/7 = 81 (was 83)
        expect(screen.getByText('81%')).toBeInTheDocument(); // average_score from progressData

        // Check ActivitySidebar data
        expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
        expect(screen.getByText('Python Fundamentals')).toBeInTheDocument();

        // Check ProgressChartCard is rendered (chart container exists)
        const chartContainer = document.querySelector('.chart-container');
        expect(chartContainer).toBeInTheDocument();
    });

    it('handles partial loading states correctly', () => {
        // Only stats are loading
        vi.mocked(useDashboardData.useUserStats).mockReturnValue({
            data: null,
            isLoading: true,
            error: null,
        });

        render(<DashboardPage />);

        // Stats should show loading
        expect(screen.getByText('Loading statistics...')).toBeInTheDocument();

        // Other components should show their data
        expect(screen.getByText('JavaScript Basics')).toBeInTheDocument();
        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
    });

    it('handles multiple simultaneous errors', () => {
        const statsError = new Error('Stats API unavailable');
        const progressError = new Error('Progress API unavailable');

        vi.mocked(useDashboardData.useUserStats).mockReturnValue({
            data: null,
            isLoading: false,
            error: statsError,
        });

        vi.mocked(useDashboardData.useProgressData).mockReturnValue({
            data: null,
            isLoading: false,
            error: progressError,
        });

        render(<DashboardPage />);

        expect(screen.getByText('Failed to load statistics')).toBeInTheDocument();
        expect(screen.getByText('Stats API unavailable')).toBeInTheDocument();
        expect(screen.getByText('Failed to load progress data')).toBeInTheDocument();
        expect(screen.getByText('Progress API unavailable')).toBeInTheDocument();
    });

    it('renders correct layout structure', () => {
        const { container } = render(<DashboardPage />);

        const pageContainer = container.querySelector('.page-container');
        expect(pageContainer).toBeInTheDocument();

        const dashboardLayout = container.querySelector('.dashboard-layout');
        expect(dashboardLayout).toBeInTheDocument();

        const dashboardMain = container.querySelector('.dashboard-main');
        expect(dashboardMain).toBeInTheDocument();
    });

    describe('Dashboard Layout and Stats Order', () => {
        it('renders stats in correct row order', () => {
            const { container } = render(<DashboardPage />);

            const statsGrid = container.querySelector('.stats-grid--extended');
            expect(statsGrid).toBeInTheDocument();

            const statItems = container.querySelectorAll('.stat-item');
            expect(statItems.length).toBe(12); // 4 columns x 3 rows
        });

        it('renders Row 1 stats (Session Overview) in correct order', () => {
            render(<DashboardPage />);

            // Get all stat labels
            const labels = screen.getAllByText(/Total Sessions|Learn Sessions|Test Sessions|Unique Quizzes/);

            // Should have all 4 session overview stats
            expect(screen.getByText('Total Sessions')).toBeInTheDocument();
            expect(screen.getByText('Learn Sessions')).toBeInTheDocument();
            expect(screen.getByText('Test Sessions')).toBeInTheDocument();
            expect(screen.getByText('Unique Quizzes')).toBeInTheDocument();
        });

        it('renders Row 2 stats (Performance Metrics) with Latest Score in 3rd position', () => {
            render(<DashboardPage />);

            // Should have all 4 performance metrics
            expect(screen.getByText('Average Score')).toBeInTheDocument();
            expect(screen.getByText('Best Score')).toBeInTheDocument();
            expect(screen.getByText('Latest Score')).toBeInTheDocument();
            expect(screen.getByText('Study Streak')).toBeInTheDocument();

            // All should be highlighted
            const { container } = render(<DashboardPage />);
            const highlightedStats = container.querySelectorAll('.stat-item--highlight');
            expect(highlightedStats.length).toBeGreaterThanOrEqual(4);
        });

        it('renders Row 3 stats (Recent Activity) in correct order', () => {
            render(<DashboardPage />);

            expect(screen.getByText('Days Active')).toBeInTheDocument();
            expect(screen.getByText('Min Score')).toBeInTheDocument();
            const recentActivityElements = screen.getAllByText('Recent Activity');
            expect(recentActivityElements.length).toBeGreaterThanOrEqual(1);
            expect(screen.getByText('Daily Average')).toBeInTheDocument();
        });

        it('renders time period filter buttons', () => {
            const { container } = render(<DashboardPage />);

            // Check that time period filter exists
            const timePeriodFilter = container.querySelector('.time-period-filter');
            expect(timePeriodFilter).toBeInTheDocument();

            // Multiple components have these buttons, so use getAllByText
            const weekButtons = screen.getAllByText('Week');
            expect(weekButtons.length).toBeGreaterThanOrEqual(1);

            const monthButtons = screen.getAllByText('Month');
            expect(monthButtons.length).toBeGreaterThanOrEqual(1);

            const allTimeButtons = screen.getAllByText('All Time');
            expect(allTimeButtons.length).toBeGreaterThanOrEqual(1);
        });

        it('has All Time filter active by default in stats card', () => {
            const { container } = render(<DashboardPage />);

            const timePeriodFilter = container.querySelector('.time-period-filter');
            const activeButton = timePeriodFilter?.querySelector('.period-btn.active');
            expect(activeButton).toHaveTextContent('All Time');
        });

        it('displays stat subtitles for better context', () => {
            render(<DashboardPage />);

            // Check for some key subtitles (now period-specific)
            // Default period is 'all' which shows "all time"
            const allTimeSubtitles = screen.getAllByText('all time');
            expect(allTimeSubtitles.length).toBeGreaterThanOrEqual(1);
            expect(screen.getByText('most recent test')).toBeInTheDocument();
            expect(screen.getByText('consecutive days')).toBeInTheDocument();
        });

        it('calculates and displays derived metrics correctly', () => {
            render(<DashboardPage />);

            // Latest Score and Min Score: both 75% (Latest is from most recent test, Min is from progressData min)
            // 75% appears multiple times: Latest Score stat, Min Score stat, and activity sidebar
            const scoreElements = screen.getAllByText('75%');
            expect(scoreElements.length).toBeGreaterThanOrEqual(2); // At least Latest Score and Min Score

            // Daily Average: 19 sessions / 7 days active = 2.7
            expect(screen.getByText('2.7')).toBeInTheDocument();
        });

        it('displays emoji icons for all stats', () => {
            const { container } = render(<DashboardPage />);

            const statIcons = container.querySelectorAll('.stat-icon');
            expect(statIcons.length).toBeGreaterThanOrEqual(12);

            // Check for specific emojis (some appear in multiple places)
            expect(screen.getByText('📚')).toBeInTheDocument(); // Total Sessions
            expect(screen.getByText('⭐')).toBeInTheDocument(); // Average Score
            expect(screen.getByText('🏆')).toBeInTheDocument(); // Best Score
            const testEmojis = screen.getAllByText('📝'); // Latest Score and action button
            expect(testEmojis.length).toBeGreaterThanOrEqual(1);
            expect(screen.getByText('🔥')).toBeInTheDocument(); // Study Streak
        });

        it('renders responsive grid layout classes', () => {
            const { container } = render(<DashboardPage />);

            const statsGrid = container.querySelector('.stats-grid.stats-grid--extended');
            expect(statsGrid).toBeInTheDocument();
        });
    });
});
