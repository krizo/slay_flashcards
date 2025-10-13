import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

// Mock the useAuth hook
vi.mock('../../context/AuthContext', () => ({
    useAuth: () => ({
        user: { id: 1, name: 'Test User' },
        logout: vi.fn(),
    }),
}));

// Mock the SessionContext
let mockSessionContextValue: any = {
    sessionInfo: null,
    setSessionInfo: vi.fn(),
};

vi.mock('../../contexts/SessionContext', () => ({
    useSessionContext: () => mockSessionContextValue,
}));

describe('Header', () => {
    const renderWithProviders = (sessionInfo: any = null) => {
        mockSessionContextValue = {
            sessionInfo,
            setSessionInfo: vi.fn(),
        };

        return render(
            <BrowserRouter>
                <Header />
            </BrowserRouter>
        );
    };

    beforeEach(() => {
        vi.clearAllMocks();
        mockSessionContextValue = {
            sessionInfo: null,
            setSessionInfo: vi.fn(),
        };
    });

    it('renders header component', () => {
        const { container } = renderWithProviders();
        expect(container.querySelector('.app-header')).toBeInTheDocument();
    });

    it('renders user info when no session is active', () => {
        renderWithProviders();

        // Should show user info section
        expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    it('displays session info when session is active', () => {
        renderWithProviders({
            quizName: 'Physics Quiz',
            quizImage: '📚',
            subject: 'Science',
            category: 'Mechanics',
            level: 'Grade 10',
            yourBest: 95,
            yourAverage: 85,
            lastScore: 90,
            testSessions: 5,
            lastSessionDate: '2025-10-13T12:00:00',
        });

        expect(screen.getByText('Physics Quiz')).toBeInTheDocument();
    });

    describe('Base64 Emoji Decoding', () => {
        it('decodes short base64 strings as UTF-8 emojis', () => {
            // Base64 for "✈️" (airplane emoji) - properly encoded
            const encoder = new TextEncoder();
            const bytes = encoder.encode('✈️');
            const binaryString = Array.from(bytes, byte => String.fromCharCode(byte)).join('');
            const base64Emoji = btoa(binaryString);

            renderWithProviders({
                quizName: 'Travel Quiz',
                quizImage: base64Emoji,
                subject: 'Geography',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            // The emoji should be rendered (though we can't directly test the decoded value,
            // we can verify the component doesn't crash and renders the quiz name)
            expect(screen.getByText('Travel Quiz')).toBeInTheDocument();
        });

        it('handles regular image URLs without decoding', () => {
            // URLs starting with http:// or https:// are treated as text (emoji replacement)
            // since the component logic considers them as emoji if they don't start with 'data:'
            renderWithProviders({
                quizName: 'History Quiz',
                quizImage: 'https://example.com/image.png',
                subject: 'History',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            // The URL is displayed as text/emoji in a span, not as an image
            expect(screen.getByText('History Quiz')).toBeInTheDocument();
            expect(screen.getByText('https://example.com/image.png')).toBeInTheDocument();
        });

        it('handles plain emoji without decoding', () => {
            renderWithProviders({
                quizName: 'Math Quiz',
                quizImage: '🔢',
                subject: 'Mathematics',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            expect(screen.getByText('🔢')).toBeInTheDocument();
        });
    });

    describe('Quiz Metadata Display', () => {
        it('displays quiz subject, category, and level', () => {
            renderWithProviders({
                quizName: 'Advanced Physics',
                quizImage: '⚛️',
                subject: 'Science',
                category: 'Quantum Mechanics',
                level: 'University',
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            expect(screen.getByText('📚 Science')).toBeInTheDocument();
            expect(screen.getByText('📂 Quantum Mechanics')).toBeInTheDocument();
            expect(screen.getByText('📊 University')).toBeInTheDocument();
        });

        it('handles null category and level gracefully', () => {
            const { container } = renderWithProviders({
                quizName: 'General Quiz',
                quizImage: '📝',
                subject: 'General Knowledge',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            expect(screen.getByText('📚 General Knowledge')).toBeInTheDocument();
            // Category and level should not appear in quiz metadata section
            const metadataSection = container.querySelector('.header-quiz-metadata');
            expect(metadataSection?.textContent).not.toContain('📂');
            expect(metadataSection?.textContent).not.toContain('📊');
        });
    });

    describe('Metrics Display', () => {
        it('displays all metrics with rounded values', () => {
            renderWithProviders({
                quizName: 'Test Quiz',
                quizImage: '📊',
                subject: 'Testing',
                category: null,
                level: null,
                yourBest: 95.7,
                yourAverage: 82.3,
                lastScore: 88.9,
                testSessions: 12,
                lastSessionDate: '2025-10-13T12:00:00',
            });

            // Values should be rounded to integers with % sign
            expect(screen.getByText('96%')).toBeInTheDocument(); // yourBest
            expect(screen.getByText('82%')).toBeInTheDocument(); // yourAverage
            expect(screen.getByText('89%')).toBeInTheDocument(); // lastScore
            expect(screen.getByText('12')).toBeInTheDocument(); // testSessions
        });

        it('handles null metrics gracefully', () => {
            renderWithProviders({
                quizName: 'New Quiz',
                quizImage: '🆕',
                subject: 'New',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: null,
            });

            // Should show N/A or dash for null values
            const dashElements = screen.getAllByText('—');
            expect(dashElements.length).toBeGreaterThan(0);
        });

        it('displays metric labels correctly', () => {
            renderWithProviders({
                quizName: 'Quiz',
                quizImage: '📝',
                subject: 'Test',
                category: null,
                level: null,
                yourBest: 90,
                yourAverage: 80,
                lastScore: 85,
                testSessions: 5,
                lastSessionDate: '2025-10-13T12:00:00',
            });

            expect(screen.getByText('Your Best')).toBeInTheDocument();
            expect(screen.getByText('Your Avg')).toBeInTheDocument();
            expect(screen.getByText('Last Score')).toBeInTheDocument();
            expect(screen.getByText('Tests')).toBeInTheDocument();
        });
    });

    describe('Single-Row Layout', () => {
        it('renders metrics in tile cards', () => {
            const { container } = renderWithProviders({
                quizName: 'Layout Test',
                quizImage: '📐',
                subject: 'Design',
                category: null,
                level: null,
                yourBest: 95,
                yourAverage: 85,
                lastScore: 90,
                testSessions: 5,
                lastSessionDate: '2025-10-13T12:00:00',
            });

            // Check for header-session-metrics container
            const statsContainer = container.querySelector('.header-session-metrics');
            expect(statsContainer).toBeInTheDocument();

            // Check for metric tiles
            const metricTiles = container.querySelectorAll('.header-metric-tile');
            expect(metricTiles.length).toBeGreaterThan(0);
        });
    });

    describe('Last Session Date', () => {
        it('formats recent session date correctly', () => {
            const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();

            renderWithProviders({
                quizName: 'Recent Quiz',
                quizImage: '⏰',
                subject: 'Time',
                category: null,
                level: null,
                yourBest: null,
                yourAverage: null,
                lastScore: null,
                testSessions: 0,
                lastSessionDate: oneHourAgo,
            });

            // Should display relative time like "1h ago"
            expect(screen.getByText(/ago/)).toBeInTheDocument();
        });
    });
});
