import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faGear, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';

function Header() {
    const { t } = useTranslation();
    const { user, isLoading, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            logout();
            navigate('/login');
        } catch (error) {
            console.error('Logout failed:', error);
            // Still navigate to login even if server logout fails
            navigate('/login');
        }
    };

    return (
        <header className="app-header">
            <div className="header-user-info">
                {isLoading ? (
                    <span className="loading-shimmer">{t('common.loading')}</span>
                ) : (
                    <>
                        <div className="header-user-name">
                            <div className="header-user-icon">
                                <FontAwesomeIcon icon={faUser} size="sm" />
                            </div>
                            <span>{user?.name || t('common.user')}</span>
                        </div>

                        <Link to="/settings" className="header-icon-button" title={t('header.settings')}>
                            <FontAwesomeIcon icon={faGear} size="lg" />
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="header-icon-button"
                            title={t('header.logout')}
                            type="button"
                        >
                            <FontAwesomeIcon icon={faRightFromBracket} size="lg" />
                        </button>
                    </>
                )}
            </div>
        </header>
    );
}

export default Header;
