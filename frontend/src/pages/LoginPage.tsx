import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
    const { t } = useTranslation();
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const buildVersion = import.meta.env.VITE_BUILD_VERSION;
    const buildDate = import.meta.env.VITE_BUILD_DATE;
    const isCI = import.meta.env.VITE_IS_CI === 'true';
    const environment = import.meta.env.VITE_ENVIRONMENT || 'staging';

    const getEnvironmentEmoji = () => {
        if (environment === 'production') return '🚀';
        if (environment === 'staging') return '🧪';
        return '🔧';
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(username, password);
            // Redirect to dashboard on successful login
            navigate('/');
        } catch (err) {
            setError(err instanceof Error ? err.message : t('auth.failedToLogin'));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-card">
                    <h1 className="login-title">{t('auth.appName')}</h1>
                    <p className="login-subtitle">{t('auth.signInSubtitle')}</p>

                    <form onSubmit={handleSubmit} className="login-form">
                        <div className="form-group">
                            <label htmlFor="username" className="form-label">
                                {t('auth.usernameOrEmail')}
                            </label>
                            <input
                                type="text"
                                id="username"
                                className="form-input"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder={t('auth.enterUsername')}
                                required
                                disabled={isLoading}
                                autoComplete="username"
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
                                placeholder={t('auth.enterPassword')}
                                required
                                disabled={isLoading}
                                autoComplete="current-password"
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
                            disabled={isLoading || !username.trim() || !password.trim()}
                        >
                            {isLoading ? t('auth.signingIn') : t('auth.signIn')}
                        </button>
                    </form>

                    <div className="login-footer">
                        <p className="login-demo-note">
                            {t('auth.dontHaveAccount')}{' '}
                            <Link to="/register" className="login-link">
                                {t('auth.createOneHere')}
                            </Link>
                        </p>
                    </div>
                </div>

                <div className="login-version-info">
                    {isCI && buildVersion && buildDate ? (
                        <div className="version-label">
                            {getEnvironmentEmoji()} {environment} : v{buildVersion} : {buildDate}
                        </div>
                    ) : (
                        <div className="version-label">
                            🔧 {t('auth.localEnvironment')}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
