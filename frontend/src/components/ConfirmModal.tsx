import { useTranslation } from 'react-i18next';
import { useUnsavedChanges } from '../contexts/UnsavedChangesContext';
import './ConfirmModal.css';

function ConfirmModal() {
    const { t } = useTranslation();
    const { showConfirmModal, handleConfirm, handleCancel } = useUnsavedChanges();

    if (!showConfirmModal) return null;

    return (
        <div className="confirm-modal-overlay" onClick={handleCancel}>
            <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
                <div className="confirm-modal-icon">⚠️</div>
                <h3 className="confirm-modal-title">{t('createQuiz.unsavedChangesTitle')}</h3>
                <p className="confirm-modal-message">
                    {t('createQuiz.unsavedChangesMessage')}
                </p>
                <div className="confirm-modal-actions">
                    <button
                        type="button"
                        className="confirm-modal-button confirm-modal-cancel"
                        onClick={handleCancel}
                    >
                        {t('createQuiz.cancelLeave')}
                    </button>
                    <button
                        type="button"
                        className="confirm-modal-button confirm-modal-confirm"
                        onClick={handleConfirm}
                    >
                        {t('createQuiz.confirmLeave')}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmModal;
