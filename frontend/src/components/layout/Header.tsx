import { Link, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faGear, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../../context/AuthContext';

function Header() {
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
                    <span className="loading-shimmer">Loading...</span>
                ) : (
                    <>
                        <div className="header-user-name">
                            <div className="header-user-icon">
                                <FontAwesomeIcon icon={faUser} size="sm" />
                            </div>
                            <span>{user?.name || 'User'}</span>
                        </div>

                        <Link to="/settings" className="header-icon-button" title="Settings">
                            <FontAwesomeIcon icon={faGear} size="lg" />
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="header-icon-button"
                            title="Logout"
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
