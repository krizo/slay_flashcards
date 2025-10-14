import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ProgressDataPoint } from '../../types';

type TimePeriod = 'week' | 'month' | 'year' | 'all';

interface ProgressChartCardProps {
    data: ProgressDataPoint[] | null;
    isLoading?: boolean;
    error?: Error | null;
    timePeriod: TimePeriod;
}

const ProgressChartCard = ({ data, isLoading, error, timePeriod }: ProgressChartCardProps) => {
    const { t } = useTranslation();

    useEffect(() => {
        console.log(`📈 ProgressChartCard - ${timePeriod}:`, {
            totalPoints: data?.length,
            firstDate: data?.[0]?.date,
            lastDate: data?.[data.length - 1]?.date,
            allDates: data?.map(d => d.date)
        });
    }, [data, timePeriod]);

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
    // Loading state
    if (isLoading) {
        return (
            <div className="dashboard-card progress-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.progressOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.averageScoresOver', { period: getRangeLabel() })}</p>
                </div>
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>{t('dashboard.loadingProgressData')}</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="dashboard-card progress-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.progressOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.averageScoresOver', { period: getRangeLabel() })}</p>
                </div>
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <p className="error-message">{t('dashboard.failedToLoadProgressData')}</p>
                    <p className="error-detail">{error.message}</p>
                </div>
            </div>
        );
    }

    // No data state
    if (!data || data.length === 0) {
        return (
            <div className="dashboard-card progress-chart-card">
                <div className="card-header">
                    <h3 className="card-title">{t('dashboard.charts.progressOverTime')}</h3>
                    <p className="card-subtitle">{t('dashboard.charts.averageScoresOver', { period: getRangeLabel() })}</p>
                </div>
                <div className="empty-state">
                    <span className="empty-icon">📈</span>
                    <p>{t('dashboard.noProgressData')}</p>
                    <p className="empty-hint">{t('dashboard.completeTestSessions')}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-card progress-chart-card">
            <div className="card-header">
                <h3 className="card-title">{t('dashboard.charts.progressOverTime')}</h3>
                <p className="card-subtitle">{t('dashboard.charts.averageScoresOver', { period: getRangeLabel() })} ({t('dashboard.charts.dataPoints', { count: data?.length || 0 })})</p>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                        <XAxis
                            dataKey="date"
                            stroke="#5B6D83"
                            tick={{ fontSize: 11 }}
                            tickFormatter={(value) => {
                                const date = new Date(value);
                                return `${date.getMonth() + 1}/${date.getDate()}`;
                            }}
                        />
                        <YAxis
                            stroke="#5B6D83"
                            tick={{ fontSize: 11 }}
                            domain={[0, 100]}
                            width={35}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#FFFFFF',
                                border: '1px solid #E5E7EB',
                                borderRadius: '8px',
                                padding: '10px',
                                fontSize: '12px'
                            }}
                            labelFormatter={(value) => {
                                const date = new Date(value);
                                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                            }}
                            formatter={(value: number) => [`${Math.round(value)}%`, t('dashboard.charts.avgScore')]}
                        />
                        <Line
                            type="monotone"
                            dataKey="score"
                            stroke="#6A3FFB"
                            strokeWidth={2}
                            dot={{ fill: '#6A3FFB', r: 3 }}
                            activeDot={{ r: 5 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ProgressChartCard;
