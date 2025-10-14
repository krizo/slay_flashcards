import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SettingsPage from './SettingsPage';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/apiClient';

// Mock the auth context
vi.mock('../context/AuthContext', () => ({
    useAuth: vi.fn()
}));

// Mock the API client
vi.mock('../services/apiClient', () => ({
    api: {
        get: vi.fn(),
        put: vi.fn(),
        post: vi.fn()
    }
}));

// Mock FontAwesome
vi.mock('@fortawesome/react-fontawesome', () => ({
    FontAwesomeIcon: ({ icon }: any) => <span data-testid="fa-icon">{icon.iconName}</span>
}));

describe('SettingsPage', () => {
    const mockUser = {
        id: 1,
        name: 'Test User',
        email: 'test@example.com',
        created_at: '2025-01-01T00:00:00Z'
    };

    const mockUserStats = {
        total_sessions: 100,
        learn_sessions: 60,
        test_sessions: 40,
        average_score: 85.5,
        best_score: 95.0,
        study_streak: 7,
        favorite_subjects: [{ Python: 30 }, { JavaScript: 25 }],
        sessions_this_week: 10,
        sessions_this_month: 45,
        unique_quizzes: 15
    };

    const mockLogout = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
        (useAuth as any).mockReturnValue({
            user: mockUser,
            accessToken: 'test-token',
            logout: mockLogout
        });
        (api.get as any).mockResolvedValue([]);
    });

    it('renders the settings page with three columns', () => {
        render(<SettingsPage />);

        expect(screen.getByText('Settings')).toBeInTheDocument();
        expect(screen.getByText('User Profile')).toBeInTheDocument();
        expect(screen.getByText('Import Quiz from JSON')).toBeInTheDocument();
    });

    it('displays user information in the stats column', async () => {
        (api.get as any).mockImplementation((url: string) => {
            if (url.includes('/statistics')) {
                return Promise.resolve(mockUserStats);
            }
            return Promise.resolve([]);
        });

        render(<SettingsPage />);

        await waitFor(() => {
            expect(screen.getByText('Test User')).toBeInTheDocument();
            expect(screen.getByText('test@example.com')).toBeInTheDocument();
        });
    });

    it('displays user statistics when loaded', async () => {
        (api.get as any).mockImplementation((url: string) => {
            if (url.includes('/statistics')) {
                return Promise.resolve(mockUserStats);
            }
            if (url === '/quizzes/') {
                return Promise.resolve([{ id: 1 }, { id: 2 }, { id: 3 }]);
            }
            return Promise.resolve([]);
        });

        render(<SettingsPage />);

        await waitFor(() => {
            expect(screen.getByText('100')).toBeInTheDocument(); // total sessions
            expect(screen.getByText('60')).toBeInTheDocument(); // learn sessions
            expect(screen.getByText('40')).toBeInTheDocument(); // test sessions
            expect(screen.getByText('95%')).toBeInTheDocument(); // best score
            expect(screen.getByText('86%')).toBeInTheDocument(); // average score (rounded)
        });
    });

    it('updates user profile when form is submitted', async () => {
        (api.put as any).mockResolvedValue({ success: true });

        render(<SettingsPage />);

        const nameInput = screen.getByLabelText('Name');
        const emailInput = screen.getByLabelText('Email');

        fireEvent.change(nameInput, { target: { value: 'Updated Name' } });
        fireEvent.change(emailInput, { target: { value: 'updated@example.com' } });

        const updateButton = screen.getByRole('button', { name: /update profile/i });
        fireEvent.click(updateButton);

        await waitFor(() => {
            expect(api.put).toHaveBeenCalledWith(
                '/users/1',
                { name: 'Updated Name', email: 'updated@example.com' },
                'test-token'
            );
        });

        await waitFor(() => {
            expect(screen.getByText(/profile updated successfully/i)).toBeInTheDocument();
        });
    });

    it('validates password change form', async () => {
        render(<SettingsPage />);

        const currentPasswordInput = screen.getByLabelText('Current Password');
        const newPasswordInput = screen.getByLabelText('New Password');
        const confirmPasswordInput = screen.getByLabelText('Confirm Password');

        fireEvent.change(currentPasswordInput, { target: { value: 'old123' } });
        fireEvent.change(newPasswordInput, { target: { value: '12345' } }); // Too short
        fireEvent.change(confirmPasswordInput, { target: { value: '12345' } });

        const changePasswordButton = screen.getByRole('button', { name: /change password/i });
        fireEvent.click(changePasswordButton);

        await waitFor(() => {
            expect(screen.getByText(/must be at least 6 characters/i)).toBeInTheDocument();
        });
    });

    it('validates password confirmation match', async () => {
        render(<SettingsPage />);

        const currentPasswordInput = screen.getByLabelText('Current Password');
        const newPasswordInput = screen.getByLabelText('New Password');
        const confirmPasswordInput = screen.getByLabelText('Confirm Password');

        fireEvent.change(currentPasswordInput, { target: { value: 'old123' } });
        fireEvent.change(newPasswordInput, { target: { value: 'newpassword123' } });
        fireEvent.change(confirmPasswordInput, { target: { value: 'differentpassword' } });

        const changePasswordButton = screen.getByRole('button', { name: /change password/i });
        fireEvent.click(changePasswordButton);

        await waitFor(() => {
            expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
        });
    });

    it('handles file selection for import', () => {
        render(<SettingsPage />);

        const file = new File(['{"quiz": {}}'], 'test.json', { type: 'application/json' });
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

        fireEvent.change(fileInput, { target: { files: [file] } });

        expect(screen.getByText('test.json')).toBeInTheDocument();
    });

    it('validates JSON file type for import', () => {
        render(<SettingsPage />);

        const file = new File(['content'], 'test.txt', { type: 'text/plain' });
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

        fireEvent.change(fileInput, { target: { files: [file] } });

        expect(screen.getByText(/please select a json file/i)).toBeInTheDocument();
    });

    it('enables import button when file is selected', () => {
        render(<SettingsPage />);

        const importButton = screen.getByRole('button', { name: /import/i });
        expect(importButton).toBeDisabled();

        const file = new File(['{"quiz": {}}'], 'test.json', { type: 'application/json' });
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

        fireEvent.change(fileInput, { target: { files: [file] } });

        expect(importButton).not.toBeDisabled();
    });

    it('handles quiz import successfully', async () => {
        globalThis.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                data: {
                    name: 'Imported Quiz',
                    flashcard_count: 10
                }
            })
        }) as any;

        render(<SettingsPage />);

        const file = new File(['{"quiz": {}}'], 'test.json', { type: 'application/json' });
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

        fireEvent.change(fileInput, { target: { files: [file] } });

        const importButton = screen.getByRole('button', { name: /import/i });
        fireEvent.click(importButton);

        await waitFor(() => {
            expect(screen.getByText(/successfully imported quiz/i)).toBeInTheDocument();
        });
    });

    it('handles drag and drop file upload', () => {
        render(<SettingsPage />);

        const uploadArea = document.querySelector('.upload-area') as HTMLElement;
        const file = new File(['{"quiz": {}}'], 'test.json', { type: 'application/json' });

        const dropEvent = {
            preventDefault: vi.fn(),
            dataTransfer: {
                files: [file]
            }
        };

        fireEvent.drop(uploadArea, dropEvent);

        expect(screen.getByText('test.json')).toBeInTheDocument();
    });

    it('shows dragging state on drag over', () => {
        render(<SettingsPage />);

        const uploadArea = document.querySelector('.upload-area') as HTMLElement;

        fireEvent.dragOver(uploadArea, { preventDefault: vi.fn() });

        expect(uploadArea).toHaveClass('dragging');
    });

    it('calls logout when logout button is clicked', () => {
        render(<SettingsPage />);

        const logoutButton = screen.getByRole('button', { name: /log out/i });
        fireEvent.click(logoutButton);

        expect(mockLogout).toHaveBeenCalled();
    });

    it('displays user avatar with first letter of name', () => {
        render(<SettingsPage />);

        const avatar = screen.getByText('T'); // First letter of "Test User"
        expect(avatar).toBeInTheDocument();
    });

    it('shows loading state while fetching statistics', () => {
        (api.get as any).mockImplementation(() => new Promise(() => {})); // Never resolves

        render(<SettingsPage />);

        expect(screen.getAllByText('...').length).toBeGreaterThan(0);
    });

    it('handles API error when fetching statistics', async () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        (api.get as any).mockRejectedValue(new Error('API Error'));

        render(<SettingsPage />);

        await waitFor(() => {
            expect(consoleErrorSpy).toHaveBeenCalled();
        });

        consoleErrorSpy.mockRestore();
    });

    it('displays user ID and member since date', async () => {
        render(<SettingsPage />);

        await waitFor(() => {
            expect(screen.getByText('#1')).toBeInTheDocument();
            expect(screen.getByText('Jan 1, 2025')).toBeInTheDocument();
        });
    });

    it('shows study streak in stats', async () => {
        (api.get as any).mockImplementation((url: string) => {
            if (url.includes('/statistics')) {
                return Promise.resolve(mockUserStats);
            }
            return Promise.resolve([]);
        });

        render(<SettingsPage />);

        await waitFor(() => {
            expect(screen.getByText(/7 days/i)).toBeInTheDocument();
        });
    });

    it('disables profile update when no changes are made', async () => {
        render(<SettingsPage />);

        const updateButton = screen.getByRole('button', { name: /update profile/i });
        fireEvent.click(updateButton);

        // Wait for the UI to settle after form submission
        await waitFor(() => {
            expect(screen.queryByText(/profile updated successfully/i)).not.toBeInTheDocument();
        });

        // Verify that no API call was made when there are no changes
        expect(api.put).not.toHaveBeenCalled();
    });
});
