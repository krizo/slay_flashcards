import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/apiClient';
import { UserStats } from '../types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRightFromBracket, faFileImport } from '@fortawesome/free-solid-svg-icons';
import './SettingsPage.css';

const SettingsPage = () => {
    const { t, i18n } = useTranslation();
    const { user, accessToken, logout } = useAuth();

    // User profile state
    const [userName, setUserName] = useState(user?.name || '');
    const [userEmail, setUserEmail] = useState(user?.email || '');
    const [userLanguage, setUserLanguage] = useState(user?.language || 'pl');
    const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
    const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [languageMessage, setLanguageMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

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

    // Load user's language preference on mount
    useEffect(() => {
        if (user?.language) {
            setUserLanguage(user.language);
            i18n.changeLanguage(user.language);
        }
    }, [user, i18n]);

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

            // Language is handled separately by handleLanguageChange

            if (Object.keys(updateData).length === 0) {
                // Silently return - no changes to save
                setIsUpdatingProfile(false);
                return;
            }

            await api.put(`/users/${user.id}`, updateData, accessToken);

            setProfileMessage({ type: 'success', text: t('settings.profileUpdatedSuccess') });

            // Clear message after 3 seconds
            setTimeout(() => setProfileMessage(null), 3000);
        } catch (error) {
            setProfileMessage({
                type: 'error',
                text: error instanceof Error ? error.message : t('settings.failedToUpdateProfile')
            });

            // Clear error message after 5 seconds
            setTimeout(() => setProfileMessage(null), 5000);
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
            setPasswordMessage({ type: 'error', text: t('settings.allPasswordFieldsRequired') });
            setIsChangingPassword(false);
            return;
        }

        if (newPassword.length < 6) {
            setPasswordMessage({ type: 'error', text: t('settings.newPasswordTooShort') });
            setIsChangingPassword(false);
            return;
        }

        if (newPassword !== confirmPassword) {
            setPasswordMessage({ type: 'error', text: t('settings.passwordsDoNotMatch') });
            setIsChangingPassword(false);
            return;
        }

        try {
            await api.put('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            }, accessToken);

            setPasswordMessage({ type: 'success', text: t('settings.passwordChangedSuccess') });
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (error) {
            setPasswordMessage({
                type: 'error',
                text: error instanceof Error ? error.message : t('settings.failedToChangePassword')
            });
        } finally {
            setIsChangingPassword(false);
        }
    };

    // Handle language change - saves immediately
    const handleLanguageChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const languageCode = e.target.value;
        const previousLanguage = userLanguage;

        setUserLanguage(languageCode);
        setLanguageMessage(null);

        if (!user || !accessToken) return;

        try {
            // Change i18n immediately for instant UI feedback
            await i18n.changeLanguage(languageCode);

            // Save to backend
            await api.put(`/users/${user.id}`, { language: languageCode }, accessToken);

            // Show success message
            setLanguageMessage({ type: 'success', text: t('settings.profileUpdatedSuccess') });

            // Clear message after 3 seconds
            setTimeout(() => setLanguageMessage(null), 3000);
        } catch (error) {
            console.error('Failed to update language:', error);
            // Revert on error
            setUserLanguage(previousLanguage);
            await i18n.changeLanguage(previousLanguage);
            setLanguageMessage({ type: 'error', text: t('settings.failedToUpdateProfile') });

            // Clear error message after 5 seconds
            setTimeout(() => setLanguageMessage(null), 5000);
        }
    };

    // Handle file selection
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (!file.name.endsWith('.json')) {
                setImportMessage({ type: 'error', text: t('settings.pleaseSelectJSON') });
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
                setImportMessage({ type: 'error', text: t('settings.pleaseSelectJSON') });
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
                    text: t('settings.importSuccess', {
                        name: result.data.name,
                        count: result.data.flashcard_count
                    })
                });
                setSelectedFile(null);

                // Refresh stats
                const quizzes = await api.get<any[]>('/quizzes/', accessToken);
                setTotalQuizzes(quizzes.length);
            }
        } catch (error) {
            setImportMessage({
                type: 'error',
                text: error instanceof Error ? error.message : t('settings.importFailed')
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
                <h1 className="page-title">{t('settings.title')}</h1>
                <p className="page-description">
                    {t('settings.description')}
                </p>
            </div>

            <div className="settings-layout-three">
                {/* Left Column - User Profile */}
                <div className="settings-profile-col">
                    <div className="settings-section">
                        <h2 className="settings-section-title">{t('settings.userProfile')}</h2>
                        <form onSubmit={handleUpdateProfile} className="settings-form">
                            <div className="form-group">
                                <label htmlFor="user-name">{t('settings.name')}</label>
                                <input
                                    id="user-name"
                                    type="text"
                                    value={userName}
                                    onChange={(e) => setUserName(e.target.value)}
                                    className="form-input"
                                    placeholder={t('settings.yourName')}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="user-email">{t('settings.email')}</label>
                                <input
                                    id="user-email"
                                    type="email"
                                    value={userEmail}
                                    onChange={(e) => setUserEmail(e.target.value)}
                                    className="form-input"
                                    placeholder={t('settings.yourEmail')}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="user-language">{t('settings.language')}</label>
                                <select
                                    id="user-language"
                                    value={userLanguage}
                                    onChange={handleLanguageChange}
                                    className="form-input"
                                >
                                    <option value="pl">🇵🇱 PL</option>
                                    <option value="en">🇬🇧 EN</option>
                                </select>
                            </div>

                            {languageMessage && (
                                <div className={`message message-${languageMessage.type} message-small`}>
                                    {languageMessage.text}
                                </div>
                            )}

                            {profileMessage && (
                                <div className={`message message-${profileMessage.type} message-small`}>
                                    {profileMessage.text}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={isUpdatingProfile}
                            >
                                {isUpdatingProfile ? t('settings.updating') : t('settings.updateProfile')}
                            </button>
                        </form>
                    </div>

                    <div className="settings-section">
                        <h2 className="settings-section-title">{t('settings.changePassword')}</h2>
                        <form onSubmit={handleChangePassword} className="settings-form">
                            <div className="form-group">
                                <label htmlFor="current-password">{t('settings.currentPassword')}</label>
                                <input
                                    id="current-password"
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="form-input"
                                    placeholder={t('settings.currentPasswordPlaceholder')}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="new-password">{t('settings.newPassword')}</label>
                                <input
                                    id="new-password"
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="form-input"
                                    placeholder={t('settings.newPasswordPlaceholder')}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="confirm-password">{t('settings.confirmPassword')}</label>
                                <input
                                    id="confirm-password"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="form-input"
                                    placeholder={t('settings.confirmPasswordPlaceholder')}
                                />
                            </div>

                            {passwordMessage && (
                                <div className={`message message-${passwordMessage.type} message-small`}>
                                    {passwordMessage.text}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={isChangingPassword}
                            >
                                {isChangingPassword ? t('settings.changing') : t('settings.changePassword')}
                            </button>
                        </form>
                    </div>

                    <button onClick={handleLogout} className="btn-logout-profile">
                        <FontAwesomeIcon icon={faRightFromBracket} className="logout-icon" />
                        {t('settings.logOut')}
                    </button>
                </div>

                {/* Middle Column - Import */}
                <div className="settings-import-col">
                    <div className="settings-section">
                        <h2 className="settings-section-title">{t('settings.importQuizFromJSON')}</h2>
                        <p className="settings-section-description">
                            {t('settings.importDescription')}
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
                                        <div className="upload-hint">{t('settings.clickToChooseDifferent')}</div>
                                    </>
                                ) : (
                                    <>
                                        <div>{t('settings.dropFileHere')}</div>
                                        <div className="upload-hint">{t('settings.acceptedFormat')}</div>
                                    </>
                                )}
                            </div>
                        </div>

                        <div className="import-button-wrapper">
                            <button
                                onClick={handleImportQuiz}
                                className="btn-import"
                                disabled={!selectedFile || isImporting}
                                title={!selectedFile ? t('settings.selectFileFirst') : t('settings.importFile')}
                            >
                                {isImporting ? (
                                    <>⏳ {t('settings.importing')}</>
                                ) : (
                                    <>
                                        <FontAwesomeIcon icon={faFileImport} />
                                        {t('settings.import')}
                                    </>
                                )}
                            </button>
                        </div>

                        {importMessage && (
                            <div className={`message message-${importMessage.type} message-small`}>
                                {importMessage.text}
                            </div>
                        )}

                        <div className="import-help">
                            <h3>{t('settings.jsonFormatExample')}</h3>
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
        "text": "a",
        "type": "choice",
        "options": [
          {"value": "a", "label": "Django"},
          {"value": "b", "label": "React"},
          {"value": "c", "label": "Angular"}
        ],
        "metadata": {
          "hint": "Select one option"
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
                                <p className="user-email-simple">{user?.email || t('settings.noEmailSet')}</p>
                            </div>
                        </div>

                        <div className="stats-grid-simple">
                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">📚</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">{isLoadingStats ? '...' : totalQuizzes}</div>
                                    <div className="stat-label-simple">{t('settings.quizzes')}</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">🎯</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.total_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">{t('settings.sessions')}</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">📖</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.learn_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">{t('settings.learn')}</div>
                                </div>
                            </div>

                            <div className="stat-card-simple">
                                <div className="stat-icon-simple">✅</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.test_sessions || 0}
                                    </div>
                                    <div className="stat-label-simple">{t('settings.tests')}</div>
                                </div>
                            </div>

                            <div className="stat-card-simple highlight">
                                <div className="stat-icon-simple">⭐</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.best_score?.toFixed(0) || 'N/A'}
                                        {userStats?.best_score ? '%' : ''}
                                    </div>
                                    <div className="stat-label-simple">{t('settings.best')}</div>
                                </div>
                            </div>

                            <div className="stat-card-simple highlight">
                                <div className="stat-icon-simple">📊</div>
                                <div className="stat-content-simple">
                                    <div className="stat-value-simple">
                                        {isLoadingStats ? '...' : userStats?.average_score?.toFixed(0) || 'N/A'}
                                        {userStats?.average_score ? '%' : ''}
                                    </div>
                                    <div className="stat-label-simple">{t('settings.average')}</div>
                                </div>
                            </div>
                        </div>

                        <div className="account-details-simple">
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">{t('settings.userId')}</span>
                                <span className="detail-value-simple">#{user?.id}</span>
                            </div>
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">{t('settings.memberSince')}</span>
                                <span className="detail-value-simple">
                                    {user?.created_at
                                        ? new Date(user.created_at).toLocaleDateString(i18n.language, {
                                            month: 'short',
                                            day: 'numeric',
                                            year: 'numeric'
                                        })
                                        : 'N/A'}
                                </span>
                            </div>
                            <div className="detail-item-simple">
                                <span className="detail-label-simple">{t('settings.studyStreak')}</span>
                                <span className="detail-value-simple">
                                    {isLoadingStats ? '...' : `${userStats?.study_streak || 0} ${t('settings.days')} 🔥`}
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
