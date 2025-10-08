import { Routes, Route, NavLink } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import QuizzesPage from './pages/QuizzesPage';
import LearningSessionPage from './pages/LearningSessionPage';
import SettingsPage from './pages/SettingsPage';

function App() {
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
            </aside>

            {/* Main Content Area */}
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<DashboardPage />} />
                    <Route path="/quizzes" element={<QuizzesPage />} />
                    <Route path="/learning-session" element={<LearningSessionPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                </Routes>
            </main>
        </div>
    );
}

export default App;
