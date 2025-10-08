import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ProgressDataPoint } from '../../types';

interface ProgressChartCardProps {
    data: ProgressDataPoint[];
}

const ProgressChartCard = ({ data }: ProgressChartCardProps) => {
    return (
        <div className="dashboard-card progress-chart-card">
            <div className="card-header">
                <h3 className="card-title">Progress Over Time</h3>
                <p className="card-subtitle">Your average scores over the last 7 days</p>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
                            domain={[0, 100]}
                            label={{ value: 'Score (%)', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#5B6D83' } }}
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
                            formatter={(value: number) => [`${value}%`, 'Score']}
                        />
                        <Line
                            type="monotone"
                            dataKey="score"
                            stroke="#6A3FFB"
                            strokeWidth={3}
                            dot={{ fill: '#6A3FFB', r: 5 }}
                            activeDot={{ r: 7 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ProgressChartCard;
