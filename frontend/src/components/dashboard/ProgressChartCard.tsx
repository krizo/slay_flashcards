import { useEffect } from 'react';
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
                return 'last week';
            case 'month':
                return 'last month';
            case 'year':
                return 'last year';
            case 'all':
                return 'all time';
        }
    };
    // Loading state
    if (isLoading) {
        return (
            <div className="dashboard-card progress-chart-card">
                <div className="card-header">
                    <h3 className="card-title">Progress Over Time</h3>
                    <p className="card-subtitle">Your average scores over the {getRangeLabel()}</p>
                </div>
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <p>Loading progress data...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="dashboard-card progress-chart-card">
                <div className="card-header">
                    <h3 className="card-title">Progress Over Time</h3>
                    <p className="card-subtitle">Your average scores over the {getRangeLabel()}</p>
                </div>
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <p className="error-message">Failed to load progress data</p>
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
                    <h3 className="card-title">Progress Over Time</h3>
                    <p className="card-subtitle">Your average scores over the {getRangeLabel()}</p>
                </div>
                <div className="empty-state">
                    <span className="empty-icon">📈</span>
                    <p>No progress data available for this period</p>
                    <p className="empty-hint">Complete some test sessions to see your progress</p>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard-card progress-chart-card">
            <div className="card-header">
                <h3 className="card-title">Progress Over Time</h3>
                <p className="card-subtitle">Your average scores over the {getRangeLabel()} ({data?.length || 0} data points)</p>
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
                            formatter={(value: number) => [`${Math.round(value)}%`, 'Avg Score']}
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
