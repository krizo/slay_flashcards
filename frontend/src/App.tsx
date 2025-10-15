import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { SessionProvider } from './contexts/SessionContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import QuizzesPage from './pages/QuizzesPage';
import LearningSessionPage from './pages/LearningSessionPage';
import SettingsPage from './pages/SettingsPage';
import CreateQuizPage from './pages/CreateQuizPage';
import EditQuizPage from './pages/EditQuizPage';
import QuizSummaryPage from './pages/QuizSummaryPage';

function App() {
    return (
        <AuthProvider>
            <SessionProvider>
                <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected routes with MainLayout */}
                <Route
                    path="/*"
                    element={
                        <ProtectedRoute>
                            <MainLayout />
                        </ProtectedRoute>
                    }
                >
                    <Route path="" element={<DashboardPage />} />
                    <Route path="quizzes" element={<QuizzesPage />} />
                    <Route path="quizzes/create" element={<CreateQuizPage />} />
                    <Route path="quizzes/:quizId/edit" element={<EditQuizPage />} />
                    <Route path="quizzes/:quizId/summary" element={<QuizSummaryPage />} />
                    <Route path="learning-session" element={<LearningSessionPage />} />
                    <Route path="settings" element={<SettingsPage />} />
                </Route>
            </Routes>
            </SessionProvider>
        </AuthProvider>
    );
}

export default App;
