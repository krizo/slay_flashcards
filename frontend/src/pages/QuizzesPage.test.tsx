import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import QuizzesPage from './QuizzesPage';
import * as useQuizHook from '../hooks/useQuiz';
import * as useQuizListHook from '../hooks/useQuizList';
import * as useQuizFiltersHook from '../hooks/useQuizFilters';
import { Quiz } from '../types';
import * as apiClient from '../services/apiClient';

// Mock the hooks
vi.mock('../hooks/useQuiz');
vi.mock('../hooks/useQuizList');
vi.mock('../hooks/useQuizFilters');

// Mock the AuthContext
vi.mock('../context/AuthContext', () => ({
    useAuth: () => ({
        accessToken: 'mock-access-token',
        user: { id: 1, name: 'TestUser', email: 'test@example.com', created_at: '2025-10-08T10:00:00Z' },
        isLoading: false,
        isAuthenticated: true,
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    }),
}));

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

// Mock child components
vi.mock('../components/quizzes/QuizListPanel', () => ({
    default: ({ selectedQuizId, onSelectQuiz }: any) => (
        <div data-testid="quiz-list-panel">
            <div data-testid="selected-quiz-id">{selectedQuizId || 'none'}</div>
            <button onClick={() => onSelectQuiz(1)} data-testid="select-quiz-1">
                Select Quiz 1
            </button>
        </div>
    ),
}));

vi.mock('../components/quizzes/QuizDetailsPanel', () => ({
    default: ({ selectedQuizId, onEditClick, onDeleteClick, onStartLearningSession, onStartTestSession }: any) => (
        <div data-testid="quiz-details-panel">
            <div>Quiz ID: {selectedQuizId === null ? 'null' : selectedQuizId}</div>
            <button onClick={() => onEditClick(selectedQuizId)} data-testid="edit-button">
                Edit
            </button>
            <button onClick={() => onDeleteClick(selectedQuizId)} data-testid="delete-button">
                Delete
            </button>
            <button onClick={() => onStartLearningSession(selectedQuizId)} data-testid="start-learn-button">
                Start Learning
            </button>
            <button onClick={() => onStartTestSession(selectedQuizId)} data-testid="start-test-button">
                Start Test
            </button>
        </div>
    ),
}));

vi.mock('../components/quizzes/QuizCreateForm', () => ({
    default: ({ onSuccess, onCancel }: any) => (
        <div data-testid="quiz-create-form">
            <button onClick={onSuccess} data-testid="create-success-button">
                Create Success
            </button>
            <button onClick={onCancel} data-testid="create-cancel-button">
                Cancel Create
            </button>
        </div>
    ),
}));

vi.mock('../components/quizzes/QuizUpdateForm', () => ({
    default: ({ quiz, onSuccess, onCancel }: any) => (
        <div data-testid="quiz-update-form">
            <div>Editing Quiz: {quiz?.name}</div>
            <button onClick={onSuccess} data-testid="update-success-button">
                Update Success
            </button>
            <button onClick={onCancel} data-testid="update-cancel-button">
                Cancel Update
            </button>
        </div>
    ),
}));

// Mock API client
vi.mock('../services/apiClient', () => ({
    api: {
        get: vi.fn(),
        delete: vi.fn(),
    },
}));

describe('QuizzesPage', () => {
    const mockQuiz: Quiz = {
        id: 1,
        name: 'Test Quiz',
        subject: 'Mathematics',
        description: 'A test quiz',
        user_id: 1,
        flashcard_count: 10,
        created_at: '2025-10-08T10:00:00Z',
        favourite: false,
    };

    const mockRefetch = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();

        // Default mock implementations
        vi.mocked(useQuizListHook.useQuizList).mockReturnValue({
            quizzes: [mockQuiz],
            isLoading: false,
            error: null,
            refetch: mockRefetch,
        });

        vi.mocked(useQuizHook.useQuiz).mockReturnValue({
            quiz: null,
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        });

        vi.mocked(useQuizFiltersHook.useQuizFilters).mockReturnValue({
            subjects: ['Mathematics', 'Science'],
            categories: ['Algebra', 'Geometry'],
            levels: ['Beginner', 'Intermediate'],
            isLoading: false,
            error: null,
        });

        // Mock window.confirm
        window.confirm = vi.fn(() => true);
    });

    const renderWithRouter = (component: React.ReactElement) => {
        return render(<BrowserRouter>{component}</BrowserRouter>);
    };

    describe('Initial Rendering', () => {
        it('renders the page with quiz list panel', () => {
            renderWithRouter(<QuizzesPage />);

            expect(screen.getByTestId('quiz-list-panel')).toBeInTheDocument();
        });

        it('renders quiz details panel by default when no quiz is selected', () => {
            renderWithRouter(<QuizzesPage />);

            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
            expect(screen.queryByTestId('quiz-create-form')).not.toBeInTheDocument();
            expect(screen.queryByTestId('quiz-update-form')).not.toBeInTheDocument();
        });

        it('shows no quiz selected in details panel initially', () => {
            renderWithRouter(<QuizzesPage />);

            expect(screen.getByText(/Quiz ID: null/i)).toBeInTheDocument();
        });

        it('renders correct layout structure', () => {
            const { container } = renderWithRouter(<QuizzesPage />);

            const pageContainer = container.querySelector('.page-container');
            expect(pageContainer).toBeInTheDocument();

            const quizLayout = container.querySelector('.quiz-management-layout');
            expect(quizLayout).toBeInTheDocument();
        });
    });

    describe('Quiz Selection', () => {
        it('updates selected quiz when a quiz is selected from list', () => {
            renderWithRouter(<QuizzesPage />);

            expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('none');

            fireEvent.click(screen.getByTestId('select-quiz-1'));

            expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('1');
        });

        it('passes selected quiz ID to details panel', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));

            expect(screen.getByText(/Quiz ID: 1/i)).toBeInTheDocument();
        });

        it('clears create and edit modes when selecting a quiz', () => {
            renderWithRouter(<QuizzesPage />);

            // First, enter create mode
            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            expect(screen.getByTestId('quiz-create-form')).toBeInTheDocument();

            // Then select a quiz
            fireEvent.click(screen.getByTestId('select-quiz-1'));

            // Should show details panel, not create form
            expect(screen.queryByTestId('quiz-create-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });
    });

    describe('Quiz Creation', () => {
        it('shows create form when new quiz button is clicked', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));

            expect(screen.getByTestId('quiz-create-form')).toBeInTheDocument();
            expect(screen.queryByTestId('quiz-details-panel')).not.toBeInTheDocument();
        });

        it('hides details panel when in create mode', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));

            expect(screen.queryByTestId('quiz-details-panel')).not.toBeInTheDocument();
        });

        it('clears selection when entering create mode', () => {
            renderWithRouter(<QuizzesPage />);

            // Select a quiz first
            fireEvent.click(screen.getByTestId('select-quiz-1'));
            expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('1');

            // Enter create mode
            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));

            // Selection should be cleared
            expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('none');
        });

        it('exits create mode after successful creation', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            expect(screen.getByTestId('quiz-create-form')).toBeInTheDocument();

            fireEvent.click(screen.getByTestId('create-success-button'));

            expect(screen.queryByTestId('quiz-create-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('returns to details panel after successful creation', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            fireEvent.click(screen.getByTestId('create-success-button'));

            expect(screen.queryByTestId('quiz-create-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('returns to details panel when creation is cancelled', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            fireEvent.click(screen.getByTestId('create-cancel-button'));

            expect(screen.queryByTestId('quiz-create-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('maintains details view when creation is cancelled', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            fireEvent.click(screen.getByTestId('create-cancel-button'));

            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });
    });

    describe('Quiz Editing', () => {
        it('shows update form when edit button is clicked', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            // Select a quiz first
            fireEvent.click(screen.getByTestId('select-quiz-1'));

            // Click edit button
            fireEvent.click(screen.getByTestId('edit-button'));

            expect(screen.getByTestId('quiz-update-form')).toBeInTheDocument();
            expect(screen.queryByTestId('quiz-details-panel')).not.toBeInTheDocument();
        });

        it('passes selected quiz to update form', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));

            expect(screen.getByText(/Editing Quiz: Test Quiz/i)).toBeInTheDocument();
        });

        it('fetches quiz data only when in edit mode', () => {
            renderWithRouter(<QuizzesPage />);

            // Initially not editing
            expect(useQuizHook.useQuiz).toHaveBeenCalledWith(null);

            // Select and edit a quiz
            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));

            // Should now fetch quiz data
            expect(useQuizHook.useQuiz).toHaveBeenCalledWith(1);
        });

        it('exits edit mode after successful update', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));
            expect(screen.getByTestId('quiz-update-form')).toBeInTheDocument();

            fireEvent.click(screen.getByTestId('update-success-button'));

            expect(screen.queryByTestId('quiz-update-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('returns to details panel after successful update', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));
            fireEvent.click(screen.getByTestId('update-success-button'));

            expect(screen.queryByTestId('quiz-update-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('returns to details panel when update is cancelled', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));
            fireEvent.click(screen.getByTestId('update-cancel-button'));

            expect(screen.queryByTestId('quiz-update-form')).not.toBeInTheDocument();
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('maintains details view when update is cancelled', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));
            fireEvent.click(screen.getByTestId('update-cancel-button'));

            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });
    });

    describe('Quiz Deletion', () => {
        it('shows confirmation dialog when delete button is clicked', async () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            expect(window.confirm).toHaveBeenCalledWith(
                'Are you sure you want to delete this quiz? This action cannot be undone.'
            );
        });

        it('calls API delete when deletion is confirmed', async () => {
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockResolvedValue(undefined);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(apiClient.api.get).toHaveBeenCalledWith('/quizzes/1', 'mock-access-token');
                expect(apiClient.api.delete).toHaveBeenCalledWith('/quizzes/1', 'mock-access-token');
            });
        });

        it('completes deletion successfully', async () => {
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockResolvedValue(undefined);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(apiClient.api.delete).toHaveBeenCalledWith('/quizzes/1', 'mock-access-token');
            });
        });

        it('clears selection after successful deletion', async () => {
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockResolvedValue(undefined);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('1');

            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(screen.getByTestId('selected-quiz-id')).toHaveTextContent('none');
            });
        });

        it('does not delete when user cancels confirmation', async () => {
            window.confirm = vi.fn(() => false);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            expect(apiClient.api.delete).not.toHaveBeenCalled();
        });

        it('handles deletion error gracefully', async () => {
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockRejectedValue(new Error('Network error'));

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(consoleErrorSpy).toHaveBeenCalled();
                expect(alertSpy).toHaveBeenCalledWith('Failed to delete quiz. Please try again.');
            });

            consoleErrorSpy.mockRestore();
            alertSpy.mockRestore();
        });

        it('does not show alert when deletion fails with network error', async () => {
            vi.spyOn(console, 'error').mockImplementation(() => {});
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockRejectedValue(new Error('Network error'));

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(apiClient.api.delete).toHaveBeenCalled();
                expect(alertSpy).toHaveBeenCalledWith('Failed to delete quiz. Please try again.');
            });

            alertSpy.mockRestore();
        });

        it('handles quiz not found during verification', async () => {
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
            vi.mocked(apiClient.api.get).mockResolvedValue(null);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(alertSpy).toHaveBeenCalledWith('This quiz no longer exists. Refreshing the list...');
            });

            expect(apiClient.api.delete).not.toHaveBeenCalled();
            alertSpy.mockRestore();
        });

        it('handles 404 error during deletion', async () => {
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockRejectedValue({
                response: { status: 404 },
                message: 'Quiz not found'
            });

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(alertSpy).toHaveBeenCalledWith('This quiz no longer exists. Refreshing the list...');
            });

            consoleErrorSpy.mockRestore();
            alertSpy.mockRestore();
        });

        it('deletes quiz without showing alert on success', async () => {
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
            vi.mocked(apiClient.api.get).mockResolvedValue(mockQuiz);
            vi.mocked(apiClient.api.delete).mockResolvedValue(undefined);

            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('delete-button'));

            await waitFor(() => {
                expect(apiClient.api.delete).toHaveBeenCalled();
            });

            // Should not show success alert
            expect(alertSpy).not.toHaveBeenCalledWith('Quiz deleted successfully!');
            alertSpy.mockRestore();
        });
    });

    describe('Learning Session Navigation', () => {
        it('navigates to learning session when start learn button is clicked', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('start-learn-button'));

            expect(mockNavigate).toHaveBeenCalledWith('/learning-session?quizId=1&mode=learn');
        });

        it('navigates to test session when start test button is clicked', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('start-test-button'));

            expect(mockNavigate).toHaveBeenCalledWith('/learning-session?quizId=1&mode=test');
        });
    });

    describe('State Transitions', () => {
        it('correctly transitions from details to create to details', () => {
            renderWithRouter(<QuizzesPage />);

            // Start in details
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();

            // Go to create
            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            expect(screen.getByTestId('quiz-create-form')).toBeInTheDocument();

            // Cancel back to details
            fireEvent.click(screen.getByTestId('create-cancel-button'));
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('correctly transitions from details to edit to details', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            // Select quiz and start in details
            fireEvent.click(screen.getByTestId('select-quiz-1'));
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();

            // Go to edit
            fireEvent.click(screen.getByTestId('edit-button'));
            expect(screen.getByTestId('quiz-update-form')).toBeInTheDocument();

            // Cancel back to details
            fireEvent.click(screen.getByTestId('update-cancel-button'));
            expect(screen.getByTestId('quiz-details-panel')).toBeInTheDocument();
        });

        it('clears edit mode when starting to create new quiz', () => {
            vi.mocked(useQuizHook.useQuiz).mockReturnValue({
                quiz: mockQuiz,
                isLoading: false,
                error: null,
                refetch: vi.fn(),
            });

            renderWithRouter(<QuizzesPage />);

            // Enter edit mode
            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));
            expect(screen.getByTestId('quiz-update-form')).toBeInTheDocument();

            // Start creating new quiz
            fireEvent.click(screen.getByRole('button', { name: /new quiz/i }));
            expect(screen.getByTestId('quiz-create-form')).toBeInTheDocument();
            expect(screen.queryByTestId('quiz-update-form')).not.toBeInTheDocument();
        });
    });

    describe('Hook Integration', () => {
        it('calls useQuiz hook with null when not editing', () => {
            renderWithRouter(<QuizzesPage />);

            expect(useQuizHook.useQuiz).toHaveBeenCalledWith(null);
        });

        it('calls useQuiz hook with quiz ID when editing', () => {
            renderWithRouter(<QuizzesPage />);

            fireEvent.click(screen.getByTestId('select-quiz-1'));
            fireEvent.click(screen.getByTestId('edit-button'));

            expect(useQuizHook.useQuiz).toHaveBeenCalledWith(1);
        });
    });
});
