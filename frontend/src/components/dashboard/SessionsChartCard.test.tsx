import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SessionsChartCard from './SessionsChartCard';

describe('SessionsChartCard', () => {
    const mockSessionsData = [
        { date: '2025-10-04', learn: 2, test: 1 },
        { date: '2025-10-05', learn: 1, test: 0 },
        { date: '2025-10-06', learn: 3, test: 2 },
        { date: '2025-10-07', learn: 0, test: 1 },
        { date: '2025-10-08', learn: 2, test: 0 },
        { date: '2025-10-09', learn: 1, test: 1 },
        { date: '2025-10-10', learn: 2, test: 3 },
    ];

    describe('Loading State', () => {
        it('should render loading state when isLoading is true', () => {
            render(<SessionsChartCard data={null} isLoading={true} timePeriod="week" />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText(/Your learning and test activity over the last week/)).toBeInTheDocument();
            expect(screen.getByText('Loading sessions data...')).toBeInTheDocument();
            expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument(); // loading spinner
        });

        it('should show loading spinner in loading state', () => {
            const { container } = render(<SessionsChartCard data={null} isLoading={true} timePeriod="week" />);
            const spinner = container.querySelector('.loading-spinner');
            expect(spinner).toBeInTheDocument();
        });
    });

    describe('Error State', () => {
        it('should render error state when error is provided', () => {
            const mockError = new Error('Network error');
            render(<SessionsChartCard timePeriod="week" data={null} error={mockError} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText('Failed to load sessions data')).toBeInTheDocument();
            expect(screen.getByText('Network error')).toBeInTheDocument();
        });

        it('should display error icon in error state', () => {
            const mockError = new Error('API failed');
            render(<SessionsChartCard timePeriod="week" data={null} error={mockError} />);

            expect(screen.getByText('⚠️')).toBeInTheDocument();
        });

        it('should show card header in error state', () => {
            const mockError = new Error('Failed');
            render(<SessionsChartCard timePeriod="week" data={null} error={mockError} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText('Your learning and test activity over the last week')).toBeInTheDocument();
        });
    });

    describe('Empty State', () => {
        it('should render empty state when data is null', () => {
            render(<SessionsChartCard timePeriod="week" data={null} isLoading={false} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText('No session data available')).toBeInTheDocument();
        });

        it('should render empty state when data is empty array', () => {
            render(<SessionsChartCard timePeriod="week" data={[]} isLoading={false} />);

            expect(screen.getByText('No session data available')).toBeInTheDocument();
            expect(screen.getByText('📊')).toBeInTheDocument();
        });

        it('should show card header in empty state', () => {
            render(<SessionsChartCard timePeriod="week" data={[]} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText('Your learning and test activity over the last week')).toBeInTheDocument();
        });
    });

    describe('Data State', () => {
        it('should render chart when data is provided', () => {
            render(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.getByText('Your learning and test activity over the last week (7 data points)')).toBeInTheDocument();

            // Chart should be rendered (ResponsiveContainer creates the chart)
            const chartContainer = screen.getByText('Sessions Over Time').closest('.dashboard-card');
            expect(chartContainer).toBeInTheDocument();
        });

        it('should display card header with data', () => {
            render(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);

            const title = screen.getByText('Sessions Over Time');
            const subtitle = screen.getByText('Your learning and test activity over the last week (7 data points)');

            expect(title).toBeInTheDocument();
            expect(subtitle).toBeInTheDocument();
            expect(title.className).toContain('card-title');
            expect(subtitle.className).toContain('card-subtitle');
        });

        it('should render with proper dashboard card structure', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);

            const dashboardCard = container.querySelector('.dashboard-card.sessions-chart-card');
            expect(dashboardCard).toBeInTheDocument();

            const cardHeader = container.querySelector('.card-header');
            expect(cardHeader).toBeInTheDocument();

            const chartContainer = container.querySelector('.chart-container');
            expect(chartContainer).toBeInTheDocument();
        });

        it('should not show loading, error, or empty states when data is present', () => {
            render(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);

            expect(screen.queryByText('Loading sessions data...')).not.toBeInTheDocument();
            expect(screen.queryByText('Failed to load sessions data')).not.toBeInTheDocument();
            expect(screen.queryByText('No session data available')).not.toBeInTheDocument();
        });
    });

    describe('Component Structure', () => {
        it('should have consistent card structure across all states', () => {
            const { rerender, container } = render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} />);

            let card = container.querySelector('.dashboard-card.sessions-chart-card');
            expect(card).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={null} error={new Error('Test')} />);
            card = container.querySelector('.dashboard-card.sessions-chart-card');
            expect(card).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={[]} />);
            card = container.querySelector('.dashboard-card.sessions-chart-card');
            expect(card).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);
            card = container.querySelector('.dashboard-card.sessions-chart-card');
            expect(card).toBeInTheDocument();
        });

        it('should always show card header', () => {
            const { rerender } = render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} />);
            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={null} error={new Error('Test')} />);
            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={[]} />);
            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();

            rerender(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);
            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
        });
    });

    describe('Props Handling', () => {
        it('should handle undefined props gracefully', () => {
            render(<SessionsChartCard timePeriod="week" data={undefined as any} />);
            expect(screen.getByText('No session data available')).toBeInTheDocument();
        });

        it('should prioritize error over loading state', () => {
            const mockError = new Error('Error');
            render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} error={mockError} />);

            expect(screen.getByText('Failed to load sessions data')).toBeInTheDocument();
            expect(screen.queryByText('Loading sessions data...')).not.toBeInTheDocument();
        });

        it('should prioritize error over data state', () => {
            const mockError = new Error('Error');
            render(<SessionsChartCard timePeriod="week" data={mockSessionsData} error={mockError} />);

            expect(screen.getByText('Failed to load sessions data')).toBeInTheDocument();
        });

        it('should prioritize loading over empty state', () => {
            render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} />);

            expect(screen.getByText('Loading sessions data...')).toBeInTheDocument();
            expect(screen.queryByText('No session data available')).not.toBeInTheDocument();
        });
    });

    describe('Data Visualization', () => {
        it('should handle single day data', () => {
            const singleDayData = [{ date: '2025-10-10', learn: 5, test: 3 }];
            render(<SessionsChartCard timePeriod="week" data={singleDayData} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
            expect(screen.queryByText('No session data available')).not.toBeInTheDocument();
        });

        it('should handle data with zero values', () => {
            const zeroData = [
                { date: '2025-10-10', learn: 0, test: 0 },
                { date: '2025-10-11', learn: 0, test: 0 },
            ];
            render(<SessionsChartCard timePeriod="week" data={zeroData} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
        });

        it('should handle large session counts', () => {
            const largeData = [{ date: '2025-10-10', learn: 100, test: 50 }];
            render(<SessionsChartCard timePeriod="week" data={largeData} />);

            expect(screen.getByText('Sessions Over Time')).toBeInTheDocument();
        });
    });

    describe('CSS Classes', () => {
        it('should apply correct CSS classes to loading state', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} />);

            expect(container.querySelector('.loading-state')).toBeInTheDocument();
            expect(container.querySelector('.loading-spinner')).toBeInTheDocument();
        });

        it('should apply correct CSS classes to error state', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={null} error={new Error('Test')} />);

            expect(container.querySelector('.error-state')).toBeInTheDocument();
            expect(container.querySelector('.error-icon')).toBeInTheDocument();
            expect(container.querySelector('.error-message')).toBeInTheDocument();
            expect(container.querySelector('.error-detail')).toBeInTheDocument();
        });

        it('should apply correct CSS classes to empty state', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={[]} />);

            expect(container.querySelector('.empty-state')).toBeInTheDocument();
            expect(container.querySelector('.empty-icon')).toBeInTheDocument();
        });

        it('should apply correct CSS classes to data state', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={mockSessionsData} />);

            expect(container.querySelector('.chart-container')).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('should have loading spinner with implicit role', () => {
            const { container } = render(<SessionsChartCard timePeriod="week" data={null} isLoading={true} />);
            const loadingState = container.querySelector('.loading-state');
            expect(loadingState).toBeInTheDocument();
        });

        it('should display error messages accessibly', () => {
            const mockError = new Error('Connection failed');
            render(<SessionsChartCard timePeriod="week" data={null} error={mockError} />);

            const errorMessage = screen.getByText('Failed to load sessions data');
            const errorDetail = screen.getByText('Connection failed');

            expect(errorMessage).toBeInTheDocument();
            expect(errorDetail).toBeInTheDocument();
        });
    });
});
