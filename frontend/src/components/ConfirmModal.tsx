import { useUnsavedChanges } from '../contexts/UnsavedChangesContext';
import './ConfirmModal.css';

function ConfirmModal() {
    const { showConfirmModal, handleConfirm, handleCancel } = useUnsavedChanges();

    if (!showConfirmModal) return null;

    return (
        <div className="confirm-modal-overlay" onClick={handleCancel}>
            <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
                <div className="confirm-modal-icon">⚠️</div>
                <h3 className="confirm-modal-title">Niezapisane zmiany</h3>
                <p className="confirm-modal-message">
                    Masz niezapisane zmiany w formularzu. Czy na pewno chcesz opuścić tę stronę?
                </p>
                <div className="confirm-modal-actions">
                    <button
                        type="button"
                        className="confirm-modal-button confirm-modal-cancel"
                        onClick={handleCancel}
                    >
                        Anuluj
                    </button>
                    <button
                        type="button"
                        className="confirm-modal-button confirm-modal-confirm"
                        onClick={handleConfirm}
                    >
                        Opuść stronę
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmModal;
