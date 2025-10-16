import { Outlet, NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Header from './Header';
import Footer from './Footer';
import ConfirmModal from '../ConfirmModal';

function MainLayout() {
    const { t } = useTranslation();

    return (
        <div className="app-layout">
            {/* Sidebar Navigation */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <h2 className="app-logo">⚡ {t('auth.appName')}</h2>
                </div>
                <nav className="sidebar-nav">
                    <ul className="nav-list">
                        <li className="nav-item">
                            <NavLink to="/" className="nav-link" end>
                                <span className="nav-icon">📊</span>
                                <span className="nav-text">{t('nav.dashboard')}</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/quizzes" className="nav-link">
                                <span className="nav-icon">📚</span>
                                <span className="nav-text">{t('nav.quizzes')}</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/learning-session" className="nav-link">
                                <span className="nav-icon">🎓</span>
                                <span className="nav-text">{t('nav.learningSession')}</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/settings" className="nav-link">
                                <span className="nav-icon">⚙️</span>
                                <span className="nav-text">{t('nav.settings')}</span>
                            </NavLink>
                        </li>
                    </ul>
                </nav>
                <Footer />
            </aside>

            {/* Main Content Area with Header */}
            <div className="main-content-wrapper">
                <Header />
                <main className="main-content">
                    <Outlet />
                </main>
            </div>

            {/* Global confirmation modal */}
            <ConfirmModal />
        </div>
    );
}

export default MainLayout;
