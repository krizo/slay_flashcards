import React, { createContext, useContext, useState, ReactNode } from 'react';

interface PageHeaderContextValue {
    pageTitle: string | null;
    pageSubtitle: string | null;
    setPageHeader: (title: string | null, subtitle: string | null) => void;
}

const PageHeaderContext = createContext<PageHeaderContextValue | undefined>(undefined);

export const PageHeaderProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [pageTitle, setPageTitle] = useState<string | null>(null);
    const [pageSubtitle, setPageSubtitle] = useState<string | null>(null);

    const setPageHeader = (title: string | null, subtitle: string | null) => {
        setPageTitle(title);
        setPageSubtitle(subtitle);
    };

    return (
        <PageHeaderContext.Provider value={{ pageTitle, pageSubtitle, setPageHeader }}>
            {children}
        </PageHeaderContext.Provider>
    );
};

export const usePageHeader = () => {
    const context = useContext(PageHeaderContext);
    if (!context) {
        throw new Error('usePageHeader must be used within PageHeaderProvider');
    }
    return context;
};
