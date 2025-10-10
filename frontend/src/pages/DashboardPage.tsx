import { useAuth } from '../context/AuthContext';
import StatsSummaryCard from '../components/dashboard/StatsSummaryCard';
import ProgressChartCard from '../components/dashboard/ProgressChartCard';
import ActivitySidebar from '../components/dashboard/ActivitySidebar';
import { useUserStats, useRecentSessions, useProgressData } from '../hooks/useDashboardData';

function DashboardPage() {
    // Get user from auth context
    const { user } = useAuth();
    const userId = user?.id || 0;

    // Fetch dashboard data using custom hooks
    const { data: stats, isLoading: statsLoading, error: statsError } = useUserStats(userId);
    const { data: sessions, isLoading: sessionsLoading, error: sessionsError } = useRecentSessions(userId, 5);
    const { data: progress, isLoading: progressLoading, error: progressError } = useProgressData(userId, 7);

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
