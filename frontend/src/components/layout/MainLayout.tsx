import { Outlet, NavLink } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';

function MainLayout() {
    return (
        <div className="app-layout">
            {/* Sidebar Navigation */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <h2 className="app-logo">⚡ SlayFlashcards</h2>
                </div>
                <nav className="sidebar-nav">
                    <ul className="nav-list">
                        <li className="nav-item">
                            <NavLink to="/" className="nav-link" end>
                                <span className="nav-icon">📊</span>
                                <span className="nav-text">Dashboard</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/quizzes" className="nav-link">
                                <span className="nav-icon">📚</span>
                                <span className="nav-text">Quizzes</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/learning-session" className="nav-link">
                                <span className="nav-icon">🎓</span>
                                <span className="nav-text">Learning Session</span>
                            </NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink to="/settings" className="nav-link">
                                <span className="nav-icon">⚙️</span>
                                <span className="nav-text">Settings</span>
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
        </div>
    );
}

export default MainLayout;
