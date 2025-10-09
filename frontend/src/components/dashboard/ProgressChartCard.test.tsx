import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProgressChartCard from './ProgressChartCard';
import { ProgressDataPoint } from '../../types';

describe('ProgressChartCard', () => {
    const mockProgressData: ProgressDataPoint[] = [
        { date: '2025-10-02', score: 75 },
        { date: '2025-10-03', score: 78 },
        { date: '2025-10-04', score: 80 },
        { date: '2025-10-05', score: 82 },
        { date: '2025-10-06', score: 79 },
        { date: '2025-10-07', score: 85 },
        { date: '2025-10-08', score: 88 },
    ];

    it('renders loading state', () => {
        render(<ProgressChartCard data={null} isLoading={true} />);

        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
        expect(screen.getByText('Loading progress data...')).toBeInTheDocument();
    });

    it('renders error state', () => {
        const error = new Error('Network error occurred');
        render(<ProgressChartCard data={null} error={error} />);

        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
        expect(screen.getByText('Failed to load progress data')).toBeInTheDocument();
        expect(screen.getByText('Network error occurred')).toBeInTheDocument();
    });

    it('renders empty state when no data provided', () => {
        render(<ProgressChartCard data={null} />);

        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
        expect(screen.getByText('No progress data available')).toBeInTheDocument();
    });

    it('renders empty state when data array is empty', () => {
        render(<ProgressChartCard data={[]} />);

        expect(screen.getByText('No progress data available')).toBeInTheDocument();
    });

    it('renders chart with data', () => {
        render(<ProgressChartCard data={mockProgressData} />);

        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
        expect(screen.getByText('Your average scores over the last 7 days')).toBeInTheDocument();

        // Check that chart container is rendered
        const chartContainer = document.querySelector('.chart-container');
        expect(chartContainer).toBeInTheDocument();
    });

    it('displays correct title and subtitle', () => {
        render(<ProgressChartCard data={mockProgressData} />);

        expect(screen.getByText('Progress Over Time')).toBeInTheDocument();
        expect(screen.getByText('Your average scores over the last 7 days')).toBeInTheDocument();
    });

    it('renders chart even with single data point', () => {
        const singleDataPoint: ProgressDataPoint[] = [
            { date: '2025-10-08', score: 88 },
        ];

        render(<ProgressChartCard data={singleDataPoint} />);

        const chartContainer = document.querySelector('.chart-container');
        expect(chartContainer).toBeInTheDocument();
    });

    it('handles data with zero scores', () => {
        const dataWithZeros: ProgressDataPoint[] = [
            { date: '2025-10-08', score: 0 },
            { date: '2025-10-09', score: 50 },
        ];

        render(<ProgressChartCard data={dataWithZeros} />);

        const chartContainer = document.querySelector('.chart-container');
        expect(chartContainer).toBeInTheDocument();
    });
});
