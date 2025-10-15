import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { QuizStatus } from '../../types';
import { TagSelector } from '../TagSelector';
import { ComboBox } from '../ComboBox';
import { useQuizFilters } from '../../hooks/useQuizFilters';
import './QuizMetadataForm.css';

export interface QuizMetadataFormData {
    name: string;
    subject: string;
    category?: string;
    level?: string;
    description?: string;
    tag_ids: number[];
    image?: string | null;
    status: QuizStatus;
    is_draft: boolean;
    favourite: boolean;
}

interface QuizMetadataFormProps {
    data: QuizMetadataFormData;
    onChange: (data: QuizMetadataFormData) => void;
    disabled?: boolean;
    showValidation?: boolean;
    accessToken?: string | null;
}

const MAX_IMAGE_SIZE = 102400; // 100KB in bytes

export const QuizMetadataForm: React.FC<QuizMetadataFormProps> = ({
    data,
    onChange,
    disabled = false,
    showValidation = false,
    accessToken,
}) => {
    const { t } = useTranslation();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [imageError, setImageError] = useState<string | null>(null);
    const { subjects, categories, levels } = useQuizFilters();

    // Multi-step form state
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 3;

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;

        onChange({
            ...data,
            [name]: type === 'checkbox' ? checked : value,
        });
    };

    const handleTagsChange = (tagIds: number[]) => {
        onChange({
            ...data,
            tag_ids: tagIds,
        });
    };

    const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setImageError(null);

        // Validate file type
        if (!file.type.startsWith('image/')) {
            setImageError(t('quizEditor.invalidImageFormat'));
            return;
        }

        // Check file size
        if (file.size > MAX_IMAGE_SIZE) {
            setImageError(t('quizEditor.imageTooLarge'));
            return;
        }

        // Convert to base64
        const reader = new FileReader();
        reader.onload = (event) => {
            const base64String = event.target?.result as string;
            // Remove the data:image/...;base64, prefix
            const base64Data = base64String.split(',')[1];
            onChange({
                ...data,
                image: base64Data,
            });
        };
        reader.onerror = () => {
            setImageError('Failed to read image file');
        };
        reader.readAsDataURL(file);
    };

    const handleRemoveImage = () => {
        onChange({
            ...data,
            image: '',
        });
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
        setImageError(null);
    };

    const getImagePreviewUrl = () => {
        if (!data.image) return null;
        return `data:image/png;base64,${data.image}`;
    };

    const isNameValid = data.name.trim().length > 0;
    const isSubjectValid = data.subject.trim().length > 0;

    // Step navigation
    const handleNext = () => {
        if (currentStep < totalSteps) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    // Validation for each step
    const isStepValid = (step: number): boolean => {
        switch (step) {
            case 1:
                return isNameValid;
            case 2:
                return isSubjectValid;
            case 3:
                return true;
            default:
                return false;
        }
    };

    const getStepTitle = (step: number): string => {
        switch (step) {
            case 1:
                return 'Podstawy';
            case 2:
                return 'Szczegóły';
            case 3:
                return 'Finalizacja';
            default:
                return '';
        }
    };

    return (
        <div className="quiz-metadata-form">
            {/* Progress Indicator */}
            <div className="form-progress">
                {[1, 2, 3].map((step, index) => (
                    <React.Fragment key={step}>
                        <div className="progress-step">
                            <div className={`progress-circle ${currentStep === step ? 'active' : ''} ${currentStep > step ? 'completed' : ''}`}>
                                {currentStep > step ? '✓' : step}
                            </div>
                            <span className={`progress-label ${currentStep === step ? 'active' : ''} ${currentStep > step ? 'completed' : ''}`}>
                                {getStepTitle(step)}
                            </span>
                        </div>
                        {index < 2 && (
                            <div className={`progress-divider ${currentStep > step ? 'completed' : ''}`} />
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Step Content */}
            <div className="form-step">

            {/* ========== STEP 1: PODSTAWOWE INFORMACJE ========== */}
            {currentStep === 1 && (
            <div className="form-section-container">
                {/* Hero Section */}
                <div className="form-hero">
                    <div className="form-hero-icon">✨</div>
                    <h2 className="form-hero-title">Stwórz nowy quiz!</h2>
                    <p className="form-hero-subtitle">Zacznijmy od podstaw - nadaj nazwę i opisz swój quiz</p>
                </div>
                <div className="form-section-header">
                    <span className="form-section-header-icon">📝</span>
                    <h3 className="form-section-header-title">Podstawowe informacje</h3>
                </div>
                <div className="form-section-divider" />

                {/* Name */}
                <div className="form-group">
                    <label htmlFor="name" className="form-label required">
                        Nazwa quizu
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        className={`form-input ${showValidation && !isNameValid ? 'invalid' : ''}`}
                        value={data.name}
                        onChange={handleInputChange}
                        placeholder="np. Matematyka - Równania kwadratowe"
                        disabled={disabled}
                        required
                    />
                    {showValidation && !isNameValid && (
                        <span className="form-error">Nazwa jest wymagana</span>
                    )}
                </div>

                {/* Description */}
                <div className="form-group">
                    <label htmlFor="description" className="form-label">
                        Opis
                    </label>
                    <textarea
                        id="description"
                        name="description"
                        className="form-input form-textarea"
                        value={data.description || ''}
                        onChange={handleInputChange}
                        placeholder="Opisz czego dotyczy ten quiz i co będzie testowane..."
                        rows={3}
                        disabled={disabled}
                    />
                </div>
            </div>
            )}

            {/* ========== STEP 2: KLASYFIKACJA I PERSONALIZACJA ========== */}
            {currentStep === 2 && (
            <>
            {/* ========== KLASYFIKACJA ========== */}
            <div className="form-section-container">
                <div className="form-section-header">
                    <span className="form-section-header-icon">🏷️</span>
                    <h3 className="form-section-header-title">Klasyfikacja</h3>
                </div>
                <div className="form-section-divider" />

                <div className="info-box">
                    Pomaga uporządkować quizy i ułatwia ich wyszukiwanie. Możesz wybrać istniejące wartości lub dodać nowe.
                </div>

            {/* Subject, Category & Level - Three in a row */}
            <div className="form-row-three">
                <div className="form-group">
                    <label htmlFor="subject" className="form-label required">
                        {t('quizEditor.subject')}
                    </label>
                    <ComboBox
                        value={data.subject}
                        onChange={(value) => onChange({ ...data, subject: value })}
                        options={subjects || []}
                        placeholder={t('quizEditor.subjectPlaceholder')}
                        disabled={disabled}
                        required={true}
                        className={showValidation && !isSubjectValid ? 'invalid' : ''}
                        addNewLabel="+ Dodaj nowy..."
                        fieldLabel="Przedmiot"
                    />
                    {showValidation && !isSubjectValid && (
                        <span className="form-error">{t('quizEditor.subjectRequired')}</span>
                    )}
                </div>

                <div className="form-group">
                    <label htmlFor="category" className="form-label">
                        {t('quizEditor.category')}
                    </label>
                    <ComboBox
                        value={data.category || ''}
                        onChange={(value) => onChange({ ...data, category: value })}
                        options={categories || []}
                        placeholder={t('quizEditor.categoryPlaceholder')}
                        disabled={disabled}
                        addNewLabel="+ Dodaj nowy..."
                        fieldLabel="Kategoria"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="level" className="form-label">
                        {t('quizEditor.level')}
                    </label>
                    <ComboBox
                        value={data.level || ''}
                        onChange={(value) => onChange({ ...data, level: value })}
                        options={levels || []}
                        placeholder={t('quizEditor.levelPlaceholder')}
                        disabled={disabled}
                        addNewLabel="+ Dodaj nowy..."
                        fieldLabel="Poziom"
                    />
                </div>
            </div>
            </div>

            {/* ========== PERSONALIZACJA ========== */}
            <div className="form-section-container">
                <div className="form-section-header">
                    <span className="form-section-header-icon">🎨</span>
                    <h3 className="form-section-header-title">Personalizacja</h3>
                </div>
                <div className="form-section-divider" />

            {/* Tags and Icon - side by side */}
            <div className="form-row">
                {/* Tags */}
                <div className="form-group">
                    <label className="form-label">Tagi</label>
                    <p className="form-hint">Dodaj tagi aby łatwiej organizować quizy</p>
                    <TagSelector
                        selectedTagIds={data.tag_ids}
                        onChange={handleTagsChange}
                        disabled={disabled}
                        accessToken={accessToken}
                    />
                </div>

                {/* Icon/Emoji Upload */}
                <div className="form-group">
                    <label className="form-label">Ikona quizu</label>
                    <p className="form-hint">Małe emoji lub ikona (maks. 100KB, ok. 80x80px)</p>

                    {data.image ? (
                        <div className="image-preview-container">
                            <img
                                src={getImagePreviewUrl() || ''}
                                alt="Quiz icon"
                                className="image-preview image-preview-small"
                            />
                            <button
                                type="button"
                                className="image-remove-button"
                                onClick={handleRemoveImage}
                                disabled={disabled}
                            >
                                Usuń
                            </button>
                        </div>
                    ) : (
                        <div className="image-upload-area">
                            <input
                                ref={fileInputRef}
                                type="file"
                                id="image"
                                accept="image/*"
                                onChange={handleImageChange}
                                disabled={disabled}
                                className="image-input"
                            />
                            <label htmlFor="image" className="image-upload-label">
                                Dodaj ikonę
                            </label>
                        </div>
                    )}

                    {imageError && (
                        <span className="form-error">{imageError}</span>
                    )}
                </div>
            </div>
            </div>
            </>
            )}

            {/* ========== STEP 3: USTAWIENIA PUBLIKACJI ========== */}
            {currentStep === 3 && (
            <div className="form-section-container">
                <div className="form-section-header">
                    <span className="form-section-header-icon">⚙️</span>
                    <h3 className="form-section-header-title">Ustawienia publikacji</h3>
                </div>
                <div className="form-section-divider" />

                <div className="info-box info-box-warning">
                    <strong>Szkic</strong> - quiz jest widoczny tylko dla Ciebie<br/>
                    <strong>Opublikowany</strong> - quiz jest dostępny publicznie<br/>
                    <strong>Zarchiwizowany</strong> - quiz jest ukryty, ale zachowany
                </div>

            {/* Status & Flags - compact row */}
            <div className="form-row-status">
                <div className="form-group">
                    <label htmlFor="status" className="form-label">
                        Status
                    </label>
                    <select
                        id="status"
                        name="status"
                        className="form-input form-select"
                        value={data.status}
                        onChange={handleInputChange}
                        disabled={disabled}
                    >
                        <option value="draft">Szkic</option>
                        <option value="published">Opublikowany</option>
                        <option value="archived">Zarchiwizowany</option>
                    </select>
                </div>

                <div className="form-group-checkboxes">
                    <label className="checkbox-label-inline">
                        <input
                            type="checkbox"
                            name="is_draft"
                            checked={data.is_draft}
                            onChange={handleInputChange}
                            disabled={disabled}
                        />
                        <span>Wersja robocza</span>
                    </label>

                    <label className="checkbox-label-inline">
                        <input
                            type="checkbox"
                            name="favourite"
                            checked={data.favourite}
                            onChange={handleInputChange}
                            disabled={disabled}
                        />
                        <span>⭐ Ulubiony</span>
                    </label>
                </div>
            </div>

            <div className="info-box info-box-success">
                <strong>💡 Wskazówka:</strong> Wersja robocza pozwala pracować nad quizem bez publikowania go. Ulubione quizy są łatwiej dostępne na liście.
            </div>
            </div>
            )}

            </div>

            {/* Navigation */}
            <div className="form-navigation">
                {currentStep > 1 && (
                    <button
                        type="button"
                        className="nav-button nav-button-back"
                        onClick={handleBack}
                        disabled={disabled}
                    >
                        ← Wstecz
                    </button>
                )}
                {currentStep < totalSteps ? (
                    <button
                        type="button"
                        className="nav-button nav-button-next"
                        onClick={handleNext}
                        disabled={disabled || !isStepValid(currentStep)}
                        style={{ marginLeft: currentStep === 1 ? 'auto' : '0' }}
                    >
                        Dalej →
                    </button>
                ) : (
                    <button
                        type="button"
                        className="nav-button nav-button-submit"
                        disabled={disabled}
                        style={{ marginLeft: 'auto' }}
                    >
                        Gotowe ✓
                    </button>
                )}
            </div>
        </div>
    );
};
