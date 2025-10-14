import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';

interface AuthContextType {
    user: User | null;
    accessToken: string | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (username: string, password: string) => Promise<void>;
    register: (username: string, password: string, email: string, language?: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'auth_token';

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [user, setUser] = useState<User | null>(null);
    const [accessToken, setAccessToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // Fetch user details from the API
    const fetchUser = async (token: string): Promise<User | null> => {
        try {
            const response = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                console.error('Failed to fetch user: API returned', response.status);
                return null;
            }

            const data = await response.json();
            return data.data; // Extract from ApiResponse format
        } catch (error) {
            console.error('Failed to fetch user:', error);
            return null;
        }
    };

    // Initialize auth state from localStorage on mount
    useEffect(() => {
        const initializeAuth = async () => {
            setIsLoading(true);

            // Try to get token from localStorage
            const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);

            if (storedToken) {
                // Validate token by fetching user
                const userData = await fetchUser(storedToken);

                if (userData) {
                    setAccessToken(storedToken);
                    setUser(userData);
                } else {
                    // Invalid token, clear it
                    localStorage.removeItem(TOKEN_STORAGE_KEY);
                }
            }

            setIsLoading(false);
        };

        initializeAuth();
    }, []);

    // Login method - calls /auth/login API
    const login = async (username: string, password: string): Promise<void> => {
        setIsLoading(true);

        try {
            // Call login API
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));

                // Handle different error formats
                let errorMessage = 'Login failed';

                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Pydantic validation errors (422)
                    errorMessage = errorData.detail
                        .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
                        .join(', ');
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }

                throw new Error(errorMessage);
            }

            const data = await response.json();
            const token = data.data.access_token;

            // Fetch user details with the new token
            const userData = await fetchUser(token);

            if (userData) {
                // Store token in localStorage
                localStorage.setItem(TOKEN_STORAGE_KEY, token);

                // Update state
                setAccessToken(token);
                setUser(userData);
            } else {
                throw new Error('Failed to fetch user information');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Register method - calls /auth/register API
    const register = async (username: string, password: string, email: string, language: string = 'pl'): Promise<void> => {
        setIsLoading(true);

        try {
            // Call register API
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, email, language }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));

                // Handle different error formats
                let errorMessage = 'Registration failed';

                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    // Pydantic validation errors (422)
                    errorMessage = errorData.detail
                        .map((err: any) => `${err.loc.join('.')}: ${err.msg}`)
                        .join(', ');
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }

                throw new Error(errorMessage);
            }

            const data = await response.json();
            const token = data.data.access_token;

            // Fetch user details with the new token
            const userData = await fetchUser(token);

            if (userData) {
                // Store token in localStorage
                localStorage.setItem(TOKEN_STORAGE_KEY, token);

                // Update state
                setAccessToken(token);
                setUser(userData);
            } else {
                throw new Error('Failed to fetch user information');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Logout method
    const logout = async (): Promise<void> => {
        try {
            // Call logout API endpoint (optional - client-side logout is most critical)
            if (accessToken) {
                await fetch('/api/v1/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    },
                }).catch((err) => {
                    // Ignore server-side logout errors, client-side cleanup is sufficient
                    console.warn('Server logout failed (continuing with client logout):', err);
                });
            }
        } catch (error) {
            // Ignore errors, we'll clear client state regardless
            console.warn('Logout API call failed:', error);
        } finally {
            // Always clear client-side state, even if server call fails
            localStorage.removeItem(TOKEN_STORAGE_KEY);
            setAccessToken(null);
            setUser(null);
        }
    };

    const isAuthenticated = !!user && !!accessToken;

    const value: AuthContextType = {
        user,
        accessToken,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the AuthContext
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);

    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }

    return context;
};
