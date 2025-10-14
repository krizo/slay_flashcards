import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

function RegisterPage() {
    const { t, i18n } = useTranslation();
    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [confirmPassword, setConfirmPassword] = useState<string>('');
    const [language, setLanguage] = useState<string>('pl');
    const [error, setError] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newLanguage = e.target.value;
        setLanguage(newLanguage);
        i18n.changeLanguage(newLanguage);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        if (username.length < 3) {
            setError(t('auth.usernameTooShort'));
            return;
        }

        if (password.length < 8) {
            setError(t('auth.passwordTooShort'));
            return;
        }

        if (password !== confirmPassword) {
            setError(t('auth.passwordsDoNotMatch'));
            return;
        }

        if (!email.includes('@')) {
            setError(t('auth.invalidEmail'));
            return;
        }

        setIsLoading(true);

        try {
            await register(username, password, email, language);
            // Redirect to dashboard on successful registration
            navigate('/');
        } catch (err) {
            setError(err instanceof Error ? err.message : t('auth.failedToRegister'));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-card">
                    <h1 className="login-title">{t('auth.appName')}</h1>
                    <p className="login-subtitle">{t('auth.createAccountSubtitle')}</p>

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group" style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <label htmlFor="language" className="form-label" style={{ marginBottom: 0, fontSize: '14px' }}>
                                {t('auth.languageLabel')}:
                            </label>
                            <select
                                id="language"
                                value={language}
                                onChange={handleLanguageChange}
                                className="form-input"
                                style={{
                                    width: 'auto',
                                    minWidth: '90px',
                                    maxWidth: '100px',
                                    padding: '6px 10px',
                                    fontSize: '14px'
                                }}
                            >
                                <option value="pl">🇵🇱 PL</option>
                                <option value="en">🇬🇧 EN</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="username" className="form-label">
                                {t('auth.username')}
                            </label>
                            <input
                                type="text"
                                id="username"
                                className="form-input"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder={t('auth.chooseUsername')}
                                required
                                disabled={isLoading}
                                autoComplete="username"
                                minLength={3}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="email" className="form-label">
                                {t('auth.email')}
                            </label>
                            <input
                                type="email"
                                id="email"
                                className="form-input"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder={t('auth.enterEmail')}
                                required
                                disabled={isLoading}
                                autoComplete="email"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password" className="form-label">
                                {t('auth.password')}
                            </label>
                            <input
                                type="password"
                                id="password"
                                className="form-input"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder={t('auth.choosePassword')}
                                required
                                disabled={isLoading}
                                autoComplete="new-password"
                                minLength={8}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="confirmPassword" className="form-label">
                                {t('auth.confirmPassword')}
                            </label>
                            <input
                                type="password"
                                id="confirmPassword"
                                className="form-input"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder={t('auth.confirmYourPassword')}
                                required
                                disabled={isLoading}
                                autoComplete="new-password"
                                minLength={8}
                            />
                        </div>

                        {error && (
                            <div className="error-message">
                                <span className="error-icon">⚠️</span>
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            className="login-button"
                            disabled={
                                isLoading ||
                                !username.trim() ||
                                !email.trim() ||
                                !password.trim() ||
                                !confirmPassword.trim()
                            }
                        >
                            {isLoading ? t('auth.creatingAccount') : t('auth.createAccount')}
                        </button>
                    </form>

                    <div className="login-footer">
                        <p className="login-demo-note">
                            {t('auth.alreadyHaveAccount')}{' '}
                            <Link to="/login" className="login-link">
                                {t('auth.signInHere')}
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
