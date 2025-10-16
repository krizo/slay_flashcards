import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { QuizStatus } from '../../types';
import { TagSelector } from '../TagSelector';
import { ComboBox } from '../ComboBox';
import { IconPicker } from '../IconPicker';
import { QuizIcon } from '../QuizIcon';
import { useQuizFilters } from '../../hooks/useQuizFilters';
import { useTags } from '../../hooks/useTags';
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
    onSubmit?: () => void;
    onCancel?: () => void;
    isValid?: boolean;
    error?: string | null;
}

export const QuizMetadataForm: React.FC<QuizMetadataFormProps> = ({
    data,
    onChange,
    disabled = false,
    showValidation = false,
    accessToken,
    onSubmit,
    onCancel,
    isValid = true,
    error = null,
}) => {
    const { t } = useTranslation();
    const { subjects, categories, levels } = useQuizFilters();
    const { tags } = useTags(accessToken);

    // Multi-step form state
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 4;

    // Emoji picker state
    const [showEmojiPicker, setShowEmojiPicker] = useState(false);

    // Get selected tags for display
    const selectedTags = tags.filter(tag => data.tag_ids.includes(tag.id));

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

    const handleIconSelect = (iconName: string) => {
        onChange({
            ...data,
            image: iconName,
        });
        setShowEmojiPicker(false);
    };

    const handleRemoveIcon = () => {
        onChange({
            ...data,
            image: '',
        });
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
            case 4:
                return true;
            default:
                return false;
        }
    };

    const getStepTitle = (step: number): string => {
        switch (step) {
            case 1:
                return t('quizMetadata.stepBasics');
            case 2:
                return t('quizMetadata.stepClassification');
            case 3:
                return t('quizMetadata.stepPersonalization');
            case 4:
                return t('quizMetadata.stepFinalization');
            default:
                return '';
        }
    };

    return (
        <div className="quiz-metadata-form">
            {/* Progress Indicator */}
            <div className="form-progress">
                {[1, 2, 3, 4].map((step, index) => (
                    <React.Fragment key={step}>
                        <div className="progress-step">
                            <div className={`progress-circle ${currentStep === step ? 'active' : ''} ${currentStep > step ? 'completed' : ''}`}>
                                {currentStep > step ? '✓' : step}
                            </div>
                            <span className={`progress-label ${currentStep === step ? 'active' : ''} ${currentStep > step ? 'completed' : ''}`}>
                                {getStepTitle(step)}
                            </span>
                        </div>
                        {index < 3 && (
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
                    <h2 className="form-hero-title">{t('quizMetadata.heroTitleCreate')}</h2>
                    <p className="form-hero-subtitle">{t('quizMetadata.heroSubtitleBasics')}</p>
                </div>

                {/* Name and Description side by side */}
                <div className="form-row">
                    {/* Name */}
                    <div className="form-group">
                        <label htmlFor="name" className="form-label-with-icon-large required">
                            <span className="label-icon-large">📌</span>
                            <span>{t('quizMetadata.nameLabel')}</span>
                        </label>
                        <p className="form-hint-caring">{t('quizMetadata.nameHint')}</p>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            className={`form-input form-input-large ${showValidation && !isNameValid ? 'invalid' : ''}`}
                            value={data.name}
                            onChange={handleInputChange}
                            placeholder={t('quizMetadata.namePlaceholder')}
                            disabled={disabled}
                            required
                        />
                        {showValidation && !isNameValid && (
                            <span className="form-error">{t('quizMetadata.nameRequired')}</span>
                        )}
                    </div>

                    {/* Description */}
                    <div className="form-group">
                        <label htmlFor="description" className="form-label-with-icon-large">
                            <span className="label-icon-large">📋</span>
                            <span>{t('quizMetadata.descriptionLabel')}</span>
                        </label>
                        <p className="form-hint-caring">{t('quizMetadata.descriptionHint')}</p>
                        <textarea
                            id="description"
                            name="description"
                            className="form-input form-textarea form-input-large"
                            value={data.description || ''}
                            onChange={handleInputChange}
                            placeholder={t('quizMetadata.descriptionPlaceholder')}
                            rows={4}
                            disabled={disabled}
                        />
                    </div>
                </div>
            </div>
            )}

            {currentStep === 2 && (
            <div className="form-section-container">
                {/* Hero Section */}
                <div className="form-hero">
                    <div className="form-hero-icon">🏷️</div>
                    <h2 className="form-hero-title">{t('quizMetadata.stepClassification')}</h2>
                    <p className="form-hero-subtitle">{t('quizMetadata.heroSubtitleClassification')}</p>
                </div>

            {/* Subject, Category & Level - Three in a row */}
            <div className="form-row-three">
                <div className="form-group">
                    <label htmlFor="subject" className="form-label-classification required">
                        <span className="classification-icon">📚</span> {t('quizEditor.subject')}
                    </label>
                    <ComboBox
                        value={data.subject}
                        onChange={(value) => onChange({ ...data, subject: value })}
                        options={subjects || []}
                        placeholder={t('quizEditor.subjectPlaceholder')}
                        disabled={disabled}
                        required={true}
                        className={`combobox-classification ${showValidation && !isSubjectValid ? 'invalid' : ''}`}
                        addNewLabel={t('quizMetadata.addNewLabel')}
                        fieldLabel={t('quizMetadata.fieldLabelSubject')}
                    />
                    {showValidation && !isSubjectValid && (
                        <span className="form-error">{t('quizEditor.subjectRequired')}</span>
                    )}
                </div>

                <div className="form-group">
                    <label htmlFor="category" className="form-label-classification">
                        <span className="classification-icon">📂</span> {t('quizEditor.category')}
                    </label>
                    <ComboBox
                        value={data.category || ''}
                        onChange={(value) => onChange({ ...data, category: value })}
                        options={categories || []}
                        placeholder={t('quizEditor.categoryPlaceholder')}
                        disabled={disabled}
                        className="combobox-classification"
                        addNewLabel={t('quizMetadata.addNewLabel')}
                        fieldLabel={t('quizMetadata.fieldLabelCategory')}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="level" className="form-label-classification">
                        <span className="classification-icon">📊</span> {t('quizEditor.level')}
                    </label>
                    <ComboBox
                        value={data.level || ''}
                        onChange={(value) => onChange({ ...data, level: value })}
                        options={levels || []}
                        placeholder={t('quizEditor.levelPlaceholder')}
                        disabled={disabled}
                        className="combobox-classification"
                        addNewLabel={t('quizMetadata.addNewLabel')}
                        fieldLabel={t('quizMetadata.fieldLabelLevel')}
                    />
                </div>
            </div>
            </div>
            )}

            {currentStep === 3 && (
            <div className="form-section-container">
                {/* Hero Section */}
                <div className="form-hero">
                    <div className="form-hero-icon">🎨</div>
                    <h2 className="form-hero-title">{t('quizMetadata.stepPersonalization')}</h2>
                    <p className="form-hero-subtitle">{t('quizMetadata.heroSubtitlePersonalization')}</p>
                </div>

            {/* Tags and Icon - side by side */}
            <div className="form-row-three">
                {/* Tags */}
                <div className="form-group">
                    <label className="form-label">{t('quizMetadata.tagsLabel')}</label>
                    <p className="form-hint">{t('quizMetadata.tagsHint')}</p>
                    <TagSelector
                        selectedTagIds={data.tag_ids}
                        onChange={handleTagsChange}
                        disabled={disabled}
                        accessToken={accessToken}
                    />
                </div>

                {/* Icon Picker */}
                <div className="form-group">
                    <label className="form-label">{t('quizMetadata.iconLabel')}</label>
                    <p className="form-hint">{t('quizMetadata.iconHint')}</p>

                    {data.image ? (
                        <div className="icon-preview-container">
                            <div className="icon-preview">
                                <QuizIcon iconName={data.image} size={48} />
                            </div>
                            <button
                                type="button"
                                className="nav-button nav-button-secondary icon-remove-button"
                                onClick={handleRemoveIcon}
                                disabled={disabled}
                            >
                                {t('quizMetadata.iconRemove')}
                            </button>
                        </div>
                    ) : (
                        <div className="icon-picker-container">
                            {!showEmojiPicker ? (
                                <button
                                    type="button"
                                    className="nav-button nav-button-next icon-picker-button"
                                    onClick={() => setShowEmojiPicker(true)}
                                    disabled={disabled}
                                >
                                    {t('quizMetadata.iconChoose')}
                                </button>
                            ) : (
                                <IconPicker
                                    onSelect={handleIconSelect}
                                    onClose={() => setShowEmojiPicker(false)}
                                />
                            )}
                        </div>
                    )}
                </div>

                {/* Favourite checkbox */}
                <div className="form-group">
                    <label className="checkbox-label-inline checkbox-label-large">
                        <input
                            type="checkbox"
                            name="favourite"
                            checked={data.favourite}
                            onChange={handleInputChange}
                            disabled={disabled}
                        />
                        <span>{t('quizMetadata.favouriteLabel')}</span>
                    </label>
                    <p className="form-hint">{t('quizMetadata.favouriteHint')}</p>
                </div>
            </div>
            </div>
            )}

            {currentStep === 4 && (
            <div className="form-section-container">
                {/* Hero Section */}
                <div className="form-hero">
                    <div className="form-hero-icon">✅</div>
                    <h2 className="form-hero-title">{t('quizMetadata.stepFinalization')}</h2>
                    <p className="form-hero-subtitle">{t('quizMetadata.heroSubtitleFinalization')}</p>
                </div>

                {/* Quiz Summary */}
                <div className="quiz-summary">
                    <h3 className="summary-title">
                        <span style={{ fontSize: '28px', lineHeight: 1 }}>
                            {data.image || '📋'}
                        </span>
                        <span>{t('quizMetadata.summaryTitle')}</span>
                    </h3>
                    <div className="summary-content">
                        {/* Section 1: Nazwa i Opis */}
                        <div className="summary-section">
                            <h4 className="summary-section-title">{t('quizMetadata.summaryBasicInfo')}</h4>
                            <div className="summary-section-items">
                                <div className="summary-item">
                                    <span className="summary-label">{t('quizMetadata.summaryName')}</span>
                                    <span className="summary-value">{data.name || t('quizMetadata.summaryEmpty')}</span>
                                </div>
                                {data.description && (
                                    <div className="summary-item summary-item-full">
                                        <span className="summary-label">{t('quizMetadata.summaryDescription')}</span>
                                        <span className="summary-value summary-description">{data.description}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Section 2: Kategoryzacja */}
                        <div className="summary-section">
                            <h4 className="summary-section-title">{t('quizMetadata.summaryCategorization')}</h4>
                            <div className="summary-section-items">
                                <div className="summary-item">
                                    <span className="summary-label">{t('quizMetadata.summarySubject')}</span>
                                    <span className="summary-value">{data.subject || t('quizMetadata.summaryEmpty')}</span>
                                </div>
                                {data.category && (
                                    <div className="summary-item">
                                        <span className="summary-label">{t('quizMetadata.summaryCategory')}</span>
                                        <span className="summary-value">{data.category}</span>
                                    </div>
                                )}
                                {data.level && (
                                    <div className="summary-item">
                                        <span className="summary-label">{t('quizMetadata.summaryLevel')}</span>
                                        <span className="summary-value">{data.level}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Section 3: Personalizacja */}
                        {(data.tag_ids.length > 0 || true) && (
                            <div className="summary-section">
                                <h4 className="summary-section-title">{t('quizMetadata.summaryPersonalization')}</h4>
                                <div className="summary-section-items">
                                    {selectedTags.length > 0 && (
                                        <div className="summary-item">
                                            <span className="summary-label">{t('quizMetadata.summaryTags')}</span>
                                            <span className="summary-value">{selectedTags.map(tag => tag.name).join(', ')}</span>
                                        </div>
                                    )}
                                    <div className="summary-item">
                                        <span className="summary-label">{t('quizMetadata.summaryFavourite')}</span>
                                        <span className="summary-value">
                                            {data.favourite ? t('quizMetadata.summaryFavouriteYes') : t('quizMetadata.summaryFavouriteNo')}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {error ? (
                    <div className="info-box info-box-error">
                        <strong>Error:</strong> {error}
                    </div>
                ) : (
                    <div className="info-box info-box-success">
                        <strong>{t('quizMetadata.infoReady')}</strong> {t('quizMetadata.infoReadyMessage')}
                    </div>
                )}
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
                        {t('quizMetadata.navBack')}
                    </button>
                )}
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '12px' }}>
                    {onCancel && (
                        <button
                            type="button"
                            className="nav-button nav-button-secondary"
                            onClick={onCancel}
                            disabled={disabled}
                        >
                            {t('quizMetadata.navCancel')}
                        </button>
                    )}
                    {currentStep < totalSteps ? (
                        <button
                            type="button"
                            className="nav-button nav-button-next"
                            onClick={handleNext}
                            disabled={disabled || !isStepValid(currentStep)}
                        >
                            {t('quizMetadata.navNext')}
                        </button>
                    ) : (
                        <button
                            type="button"
                            className="nav-button nav-button-submit"
                            onClick={onSubmit}
                            disabled={disabled || !isValid}
                        >
                            {t('quizMetadata.navDone')}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
