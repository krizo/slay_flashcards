import { createContext, useContext, useState, ReactNode } from 'react';

interface UnsavedChangesContextType {
    hasUnsavedWork: boolean;
    setHasUnsavedWork: (value: boolean) => void;
    requestConfirmation: (action: () => void) => void;
    showConfirmModal: boolean;
    pendingAction: (() => void) | null;
    handleConfirm: () => void;
    handleCancel: () => void;
}

const UnsavedChangesContext = createContext<UnsavedChangesContextType | undefined>(undefined);

export function UnsavedChangesProvider({ children }: { children: ReactNode }) {
    const [hasUnsavedWork, setHasUnsavedWork] = useState(false);
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [pendingAction, setPendingAction] = useState<(() => void) | null>(null);

    const requestConfirmation = (action: () => void) => {
        if (hasUnsavedWork) {
            setPendingAction(() => action);
            setShowConfirmModal(true);
        } else {
            action();
        }
    };

    const handleConfirm = () => {
        setShowConfirmModal(false);
        setHasUnsavedWork(false);
        if (pendingAction) {
            pendingAction();
            setPendingAction(null);
        }
    };

    const handleCancel = () => {
        setShowConfirmModal(false);
        setPendingAction(null);
    };

    return (
        <UnsavedChangesContext.Provider
            value={{
                hasUnsavedWork,
                setHasUnsavedWork,
                requestConfirmation,
                showConfirmModal,
                pendingAction,
                handleConfirm,
                handleCancel,
            }}
        >
            {children}
        </UnsavedChangesContext.Provider>
    );
}

export function useUnsavedChanges() {
    const context = useContext(UnsavedChangesContext);
    if (context === undefined) {
        throw new Error('useUnsavedChanges must be used within a UnsavedChangesProvider');
    }
    return context;
}
