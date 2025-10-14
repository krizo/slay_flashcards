import { useTranslation } from 'react-i18next';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

type TimePeriod = 'week' | 'month' | 'year' | 'all';

interface SessionDataPoint {
    date: string;
    learn: number;
    test: number;
}

interface SessionsChartCardProps {
    data: SessionDataPoint[] | null;
    isLoading?: boolean;
    error?: Error | null;
    timePeriod: TimePeriod;
}

const SessionsChartCard = ({ data, isLoading, error, timePeriod }: SessionsChartCardProps) => {
    const { t } = useTranslation();

    const getRangeLabel = () => {
        switch (timePeriod) {
            case 'week':
                return t('dashboard.timePeriods.lastWeek');
            case 'month':
                return t('dashboard.timePeriods.lastMonth');
            case 'year':
                return t('dashboard.timePeriods.lastYear');
            case 'all':
                return t('dashboard.timePeriods.allTimeLower');
        }
    };
    // Error state - check first to prioritize errors over loading
    if (error) {
        return (
            <div className="dashboard-card sessions-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.sessionsOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.learningAndTestActivity', { period: getRangeLabel() })}</p>
                </div>
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <p className="error-message">{t('dashboard.failedToLoadSessionsData')}</p>
                    <p className="error-detail">{error.message}</p>
                </div>
            </div>
        );
    }

    // Loading state
    if (isLoading) {
        return (
            <div className="dashboard-card sessions-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.sessionsOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.learningAndTestActivity', { period: getRangeLabel() })}</p>
                </div>
                <div className="loading-state">
                    <div className="loading-spinner" role="status"></div>
                    <p>{t('dashboard.loadingSessionsData')}</p>
                </div>
            </div>
        );
    }

    // No data state
    if (!data || data.length === 0) {
        return (
            <div className="dashboard-card sessions-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.sessionsOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.learningAndTestActivity', { period: getRangeLabel() })}</p>
                </div>
                <div className="empty-state">
                    <span className="empty-icon">📊</span>
                    <p>{t('dashboard.noSessionData')}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-card sessions-chart-card">
            <div className="card-header">
                <h3 className="card-title">{t('dashboard.charts.sessionsOverTime')}</h3>
                <p className="card-subtitle">{t('dashboard.charts.learningAndTestActivity', { period: getRangeLabel() })} ({t('dashboard.charts.dataPoints', { count: data?.length || 0 })})</p>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                        <XAxis
                            dataKey="date"
                            stroke="#5B6D83"
                            tick={{ fontSize: 12 }}
                            tickFormatter={(value) => {
                                const date = new Date(value);
                                return `${date.getMonth() + 1}/${date.getDate()}`;
                            }}
                        />
                        <YAxis
                            stroke="#5B6D83"
                            tick={{ fontSize: 12 }}
                            allowDecimals={false}
                            label={{ value: t('dashboard.charts.sessions'), angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#5B6D83' } }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#FFFFFF',
                                border: '1px solid #E5E7EB',
                                borderRadius: '8px',
                                padding: '10px'
                            }}
                            labelFormatter={(value) => {
                                const date = new Date(value);
                                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                            }}
                        />
                        <Legend
                            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
                            iconType="rect"
                        />
                        <Bar
                            dataKey="learn"
                            fill="#34D399"
                            name={t('dashboard.charts.learnSessions')}
                            radius={[4, 4, 0, 0]}
                        />
                        <Bar
                            dataKey="test"
                            fill="#6A3FFB"
                            name={t('dashboard.charts.testSessions')}
                            radius={[4, 4, 0, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default SessionsChartCard;
