import { useState } from 'react';
import StatsSummaryCard from '../components/dashboard/StatsSummaryCard';
import ProgressChartCard from '../components/dashboard/ProgressChartCard';
import SessionsChartCard from '../components/dashboard/SessionsChartCard';
import ActivitySidebar from '../components/dashboard/ActivitySidebar';
import { useCurrentUser, useUserStats, useRecentSessions, useProgressData, useSessionsData } from '../hooks/useDashboardData';

function DashboardPage() {
    // Fetch current user and dashboard data using custom hooks
    const { data: user } = useCurrentUser();
    const userId = user?.id;

    // State for date range selection
    const [progressDays, setProgressDays] = useState<number>(30);
    const [sessionsDays, setSessionsDays] = useState<number>(7);

    // Only fetch dashboard data if we have a valid user ID
    // Pass 0 to prevent API calls when userId is undefined
    const { data: stats, isLoading: statsLoading, error: statsError } = useUserStats(userId ?? 0);
    const { data: sessions, isLoading: sessionsLoading, error: sessionsError } = useRecentSessions(userId ?? 0, 5);
    const { data: progress, isLoading: progressLoading, error: progressError } = useProgressData(userId ?? 0, progressDays);
    const { data: sessionsData, isLoading: sessionsDataLoading, error: sessionsDataError } = useSessionsData(userId ?? 0, sessionsDays);

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
                    />
                    <ProgressChartCard
                        data={progress}
                        isLoading={progressLoading}
                        error={progressError}
                        onDateRangeChange={setProgressDays}
                    />
                    <SessionsChartCard
                        data={sessionsData}
                        isLoading={sessionsDataLoading}
                        error={sessionsDataError}
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
