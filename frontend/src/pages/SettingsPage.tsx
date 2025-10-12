import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/apiClient';
import { UserStats } from '../types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRightFromBracket, faFileImport } from '@fortawesome/free-solid-svg-icons';
import './SettingsPage.css';

const SettingsPage = () => {
    const { user, accessToken, logout } = useAuth();

    // User profile state
    const [userName, setUserName] = useState(user?.name || '');
    const [userEmail, setUserEmail] = useState(user?.email || '');
    const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
    const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // Password change state
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // JSON import state
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isImporting, setIsImporting] = useState(false);
    const [importMessage, setImportMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    // User stats state
    const [userStats, setUserStats] = useState<UserStats | null>(null);
    const [totalQuizzes, setTotalQuizzes] = useState<number>(0);
    const [isLoadingStats, setIsLoadingStats] = useState(true);

    // Fetch user statistics
    useEffect(() => {
        const fetchStats = async () => {
            if (!user || !accessToken) return;

            setIsLoadingStats(true);
            try {
                // Fetch user stats
                const stats = await api.get<UserStats>(`/users/${user.id}/statistics`, accessToken);
                setUserStats(stats);

                // Fetch total quizzes
                const quizzes = await api.get<any[]>('/quizzes/', accessToken);
                setTotalQuizzes(quizzes.length);
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            } finally {
                setIsLoadingStats(false);
            }
        };

        fetchStats();
    }, [user, accessToken]);

    // Handle profile update
    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!user || !accessToken) return;

        setIsUpdatingProfile(true);
        setProfileMessage(null);

        try {
            const updateData: any = {};

            if (userName && userName !== user.name) {
                updateData.name = userName;
            }

            if (userEmail && userEmail !== user.email) {
                updateData.email = userEmail;
            }

            if (Object.keys(updateData).length === 0) {
                setProfileMessage({ type: 'error', text: 'No changes to save' });
                setIsUpdatingProfile(false);
                return;
            }

            await api.put(`/users/${user.id}`, updateData, accessToken);

            setProfileMessage({ type: 'success', text: 'Profile updated successfully! Please log in again for changes to take effect.' });
        } catch (error) {
            setProfileMessage({
                type: 'error',
                text: error instanceof Error ? error.message : 'Failed to update profile'
            });
        } finally {
            setIsUpdatingProfile(false);
        }
    };

    // Handle password change
    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!user || !accessToken) return;

        setIsChangingPassword(true);
        setPasswordMessage(null);

        // Validation
        if (!currentPassword || !newPassword || !confirmPassword) {
            setPasswordMessage({ type: 'error', text: 'All password fields are required' });
            setIsChangingPassword(false);
            return;
        }

        if (newPassword.length < 6) {
            setPasswordMessage({ type: 'error', text: 'New password must be at least 6 characters long' });
            setIsChangingPassword(false);
            return;
        }

        if (newPassword !== confirmPassword) {
            setPasswordMessage({ type: 'error', text: 'New passwords do not match' });
            setIsChangingPassword(false);
            return;
        }

        try {
            await api.put('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            }, accessToken);

            setPasswordMessage({ type: 'success', text: 'Password changed successfully!' });
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (error) {
            setPasswordMessage({
                type: 'error',
                text: error instanceof Error ? error.message : 'Failed to change password'
            });
        } finally {
            setIsChangingPassword(false);
        }
    };

    // Handle file selection
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (!file.name.endsWith('.json')) {
                setImportMessage({ type: 'error', text: 'Please select a JSON file' });
                return;
            }
            setSelectedFile(file);
            setImportMessage(null);
        }
    };

    // Handle drag and drop
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            if (!file.name.endsWith('.json')) {
                setImportMessage({ type: 'error', text: 'Please select a JSON file' });
                return;
            }
            setSelectedFile(file);
            setImportMessage(null);
        }
    };

    // Handle quiz import
    const handleImportQuiz = async () => {
        if (!selectedFile || !accessToken) return;

        setIsImporting(true);
        setImportMessage(null);

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await fetch('/api/v1/quizzes/import-file', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to import quiz');
            }

            const result = await response.json();

            if (result.success) {
                setImportMessage({
                    type: 'success',
                    text: `Successfully imported quiz "${result.data.name}" with ${result.data.flashcard_count} flashcards!`
                });
                setSelectedFile(null);

                // Refresh stats
                const quizzes = await api.get<any[]>('/quizzes/', accessToken);
                setTotalQuizzes(quizzes.length);
            }
        } catch (error) {
            setImportMessage({
                type: 'error',
                text: error instanceof Error ? error.message : 'Failed to import quiz'
            });
        } finally {
            setIsImporting(false);
        }
    };

    // Handle logout
    const handleLogout = async () => {
        await logout();
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Settings</h1>
                <p className="page-description">
                    Manage your profile, import quiz data, and view your statistics
                </p>
            </div>

            <div className="settings-layout-three">
                {/* Left Column - User Profile */}
                <div className="settings-profile-col">
                    <div className="settings-section">
                        <h2 className="settings-section-title">User Profile</h2>
                        <form onSubmit={handleUpdateProfile} className="settings-form">
                            <div className="form-group">
                                <label htmlFor="user-name">Name</label>
                                <input
                                    id="user-name"
                                    type="text"
                                    value={userName}
                                    onChange={(e) => setUserName(e.target.value)}
                                    className="form-input"
                                    placeholder="Your name"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="user-email">Email</label>
                                <input
                                    id="user-email"
                                    type="email"
                                    value={userEmail}
                                    onChange={(e) => setUserEmail(e.target.value)}
                                    className="form-input"
                                    placeholder="your.email@example.com"
                                />
                            </div>

                            {profileMessage && (
                                <div className={`message message-${profileMessage.type}`}>
                                    {profileMessage.text}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={isUpdatingProfile}
                            >
                                {isUpdatingProfile ? 'Updating...' : 'Update Profile'}
                            </button>
                        </form>
                    </div>

                    <div className="settings-section">
                        <h2 className="settings-section-title">Change Password</h2>
                        <form onSubmit={handleChangePassword} className="settings-form">
                            <div className="form-group">
                                <label htmlFor="current-password">Current Password</label>
                                <input
                                    id="current-password"
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="form-input"
                                    placeholder="Current password"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="new-password">New Password</label>
                                <input
                                    id="new-password"
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="form-input"
                                    placeholder="Min 6 characters"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="confirm-password">Confirm Password</label>
                                <input
                                    id="confirm-password"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="form-input"
                                    placeholder="Re-enter password"
                                />
                            </div>

                            {passwordMessage && (
                                <div className={`message message-${passwordMessage.type}`}>
                                    {passwordMessage.text}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={isChangingPassword}
                            >
                                {isChangingPassword ? 'Changing...' : 'Change Password'}
                            </button>
                        </form>
                    </div>

                    <button onClick={handleLogout} className="btn-logout-profile">
                        <FontAwesomeIcon icon={faRightFromBracket} className="logout-icon" />
                        Log Out
                    </button>
                </div>

                {/* Middle Column - Import */}
                <div className="settings-import-col">
                    <div className="settings-section">
                        <h2 className="settings-section-title">Import Quiz from JSON</h2>
                        <p className="settings-section-description">
                            Upload or drag & drop a JSON file containing quiz data
                        </p>

                        <div
                            className={`upload-area ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => document.getElementById('quiz-file-input')?.click()}
                        >
                            <input
                                id="quiz-file-input"
                                type="file"
                                accept=".json"
                                onChange={handleFileSelect}
                                className="file-input"
                            />
                            <div className="upload-icon">📁</div>
                            <div className="upload-text">
                                {selectedFile ? (
                                    <>
                                        <div className="selected-file-name">{selectedFile.name}</div>
                                        <div className="upload-hint">Click to choose different file</div>
                                    </>
                                ) : (
                                    <>
                                        <div>Drop JSON file here or click to browse</div>
                                        <div className="upload-hint">Accepted format: .json</div>
                                    </>
                                )}
                            </div>
                        </div>

                        <div className="import-button-wrapper">
                            <button
                                onClick={handleImportQuiz}
                                className="btn-import"
                                disabled={!selectedFile || isImporting}
                                title={!selectedFile ? 'Please select a JSON file first' : 'Import the selected quiz file'}
                            >
                                {isImporting ? (
                                    <>⏳ Importing...</>
                                ) : (
                                    <>
                                        <FontAwesomeIcon icon={faFileImport} />
                                        Import
                                    </>
                                )}
                            </button>
                        </div>

                        {importMessage && (
                            <div className={`message message-${importMessage.type}`}>
                                {importMessage.text}
                            </div>
                        )}

                        <div className="import-help">
                            <h3>JSON Format Example:</h3>
                            <pre className="code-block">
{`{
  "quiz": {
    "name": "Python Basics",
    "subject": "Programming",
    "category": "Technical",
    "level": "Beginner"
  },
  "flashcards": [
    {
      "question": {
        "title": "Data Types",
        "text": "What is a list in Python?",
        "difficulty": 1,
        "emoji": "📋"
      },
      "answer": {
        "text": "A mutable ordered collection",
        "type": "text"
      }
    },
    {
      "question": {
        "title": "Range Question",
        "text": "Rate Python's popularity (1-10)",
        "difficulty": 1,
        "emoji": "⭐"
      },
      "answer": {
        "text": "8",
        "type": "range",
        "metadata": {
          "min": 1,
          "max": 10,
          "step": 1
        }
      }
    },
    {
      "question": {
        "title": "Multiple Choice",
        "text": "Which is a Python web framework?",
        "difficulty": 2,
        "emoji": "🌐"
      },
      "answer": {
        "text": "Django",
        "type": "choice",
        "options": ["Django", "React", "Angular", "Vue"],
        "metadata": {
          "correct_index": 0,
          "randomize": true
        }
      }
    }
  ]
}`}
                            </pre>
                        </div>
                    </div>
                </div>

                {/* Right Column - User Stats */}
                <div className="settings-stats-col">
                    <div className="settings-section stats-section">
                        <div className="account-header-simple">
                            <div className="user-avatar-simple">
                                {user?.name?.charAt(0).toUpperCase() || 'U'}
                            </div>
                            <div className="user-info-simple">
                                <h3 className="user-name-simple">{user?.name}</h3>
                                <p className="user-email-simple">{user?.email || 'No email set'}</p>
                            </div>
                        </div>

                        <div className="stats-grid-simple">
                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">📚</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">{isLoadingStats ? '...' : totalQuizzes}</div>
                                    <div className="stat-label-simple">Quizzes</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">🎯</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.total_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">Sessions</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">📖</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.learn_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">Learn</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">✅</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.test_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">Tests</div>
                                </div>
                            </div>

                            <div className="stat-card-simple highlight">
                                <div className="stat-icon-simple">⭐</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.best_score?.toFixed(0) || 'N/A'}
                                        {userStats?.best_score ? '%' : ''}
                                    </div>
                                    <div className="stat-label-simple">Best</div>
                                </div>
                            </div>

                            <div className="stat-card-simple highlight">
                                <div className="stat-icon-simple">📊</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.average_score?.toFixed(0) || 'N/A'}
                                        {userStats?.average_score ? '%' : ''}
                                    </div>
                                    <div className="stat-label-simple">Average</div>
                                </div>
                            </div>
                        </div>

                        <div className="account-details-simple">
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">User ID</span>
                                <span className="detail-value-simple">#{user?.id}</span>
                            </div>
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">Member Since</span>
                                <span className="detail-value-simple">
                                    {user?.created_at
                                        ? new Date(user.created_at).toLocaleDateString('en-US', {
                                            month: 'short',
                                            day: 'numeric',
                                            year: 'numeric'
                                        })
                                        : 'N/A'}
                                </span>
                            </div>
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">Study Streak</span>
                                <span className="detail-value-simple">
                                    {isLoadingStats ? '...' : `${userStats?.study_streak || 0} days 🔥`}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
