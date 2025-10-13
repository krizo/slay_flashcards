import { createContext, useContext, useState, ReactNode } from 'react';

interface SessionInfo {
    quizName: string;
    quizImage?: string | null;
    subject?: string;
    category?: string | null;
    level?: string | null;
    yourBest?: number | null;
    yourAverage?: number | null;
    lastScore?: number | null;
    testSessions?: number;
    lastSessionDate?: string | null;
    onCloseSession: () => void;
}

interface SessionContextType {
    sessionInfo: SessionInfo | null;
    setSessionInfo: (info: SessionInfo | null) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
    const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);

    return (
        <SessionContext.Provider value={{ sessionInfo, setSessionInfo }}>
            {children}
        </SessionContext.Provider>
    );
}

export function useSessionContext() {
    const context = useContext(SessionContext);
    if (context === undefined) {
        throw new Error('useSessionContext must be used within a SessionProvider');
    }
    return context;
}
