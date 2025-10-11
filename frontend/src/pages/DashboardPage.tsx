import { useState, useEffect } from 'react';
import StatsSummaryCard from '../components/dashboard/StatsSummaryCard';
import ProgressChartCard from '../components/dashboard/ProgressChartCard';
import SessionsChartCard from '../components/dashboard/SessionsChartCard';
import ActivitySidebar from '../components/dashboard/ActivitySidebar';
import { useCurrentUser, useUserStats, useRecentSessions, useProgressData, useSessionsData } from '../hooks/useDashboardData';

type TimePeriod = 'week' | 'month' | 'year' | 'all';

// Map time periods to days for API calls
const PERIOD_TO_DAYS: Record<TimePeriod, number> = {
    week: 7,
    month: 30,
    year: 365,
    all: 365 // Use 365 as max for 'all' since API might have limits
};

function DashboardPage() {
    // Fetch current user and dashboard data using custom hooks
    const { data: user } = useCurrentUser();
    const userId = user?.id;

    // Unified time period state for all dashboard components
    const [timePeriod, setTimePeriod] = useState<TimePeriod>('week');
    const days = PERIOD_TO_DAYS[timePeriod];

    useEffect(() => {
        console.log('🔄 DashboardPage: timePeriod changed to:', timePeriod, 'days:', days);
        // Force a visible alert to confirm state is changing
        document.title = `Dashboard - ${timePeriod.toUpperCase()}`;
    }, [timePeriod, days]);

    // Only fetch dashboard data if we have a valid user ID
    // Pass 0 to prevent API calls when userId is undefined
    const { data: stats, isLoading: statsLoading, error: statsError } = useUserStats(userId ?? 0);
    const { data: sessions, isLoading: sessionsLoading, error: sessionsError } = useRecentSessions(userId ?? 0, 5);
    const { data: progress, isLoading: progressLoading, error: progressError } = useProgressData(userId ?? 0, days);
    const { data: sessionsData, isLoading: sessionsDataLoading, error: sessionsDataError } = useSessionsData(userId ?? 0, days);

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Dashboard</h1>
                <p className="page-description">
                    Track your learning progress and stay motivated!
                </p>
            </div>

            <div className="dashboard-layout">
                <div className="dashboard-main">
                    <StatsSummaryCard
                        stats={stats}
                        userName={user?.name}
                        isLoading={statsLoading}
                        error={statsError}
                        recentSessions={sessions}
                        timePeriod={timePeriod}
                        onTimePeriodChange={setTimePeriod}
                        progressData={progress}
                        sessionsData={sessionsData}
                    />
                    <ProgressChartCard
                        key={`progress-${timePeriod}`}
                        data={progress}
                        isLoading={progressLoading}
                        error={progressError}
                        timePeriod={timePeriod}
                    />
                    <SessionsChartCard
                        key={`sessions-${timePeriod}`}
                        data={sessionsData}
                        isLoading={sessionsDataLoading}
                        error={sessionsDataError}
                        timePeriod={timePeriod}
                    />
                </div>
                <ActivitySidebar
                    recentSessions={sessions}
                    isLoading={sessionsLoading}
                    error={sessionsError}
                />
            </div>
        </div>
    );
}

export default DashboardPage;
