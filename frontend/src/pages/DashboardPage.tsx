import StatsSummaryCard from '../components/dashboard/StatsSummaryCard';
import ProgressChartCard from '../components/dashboard/ProgressChartCard';
import ActivitySidebar from '../components/dashboard/ActivitySidebar';
import {
    mockUserStats,
    mockRecentSessions,
    mockProgressData,
    mockTrendingQuizzes,
} from '../data/mockData';

function DashboardPage() {
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
                    <StatsSummaryCard stats={mockUserStats} userName="Learner" />
                    <ProgressChartCard data={mockProgressData} />
                </div>
                <ActivitySidebar
                    recentSessions={mockRecentSessions}
                    trendingQuizzes={mockTrendingQuizzes}
                />
            </div>
        </div>
    );
}

export default DashboardPage;
