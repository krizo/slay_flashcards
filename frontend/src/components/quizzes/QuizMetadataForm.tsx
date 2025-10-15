import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { QuizStatus } from '../../types';
import { TagSelector } from '../TagSelector';
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

    return (
        <div className="quiz-metadata-form">
            {/* Name */}
            <div className="form-group">
                <label htmlFor="name" className="form-label required">
                    {t('quizEditor.name')}
                </label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    className={`form-input ${showValidation && !isNameValid ? 'invalid' : ''}`}
                    value={data.name}
                    onChange={handleInputChange}
                    placeholder={t('quizEditor.namePlaceholder')}
                    disabled={disabled}
                    required
                />
                {showValidation && !isNameValid && (
                    <span className="form-error">{t('quizEditor.nameRequired')}</span>
                )}
            </div>

            {/* Subject */}
            <div className="form-group">
                <label htmlFor="subject" className="form-label required">
                    {t('quizEditor.subject')}
                </label>
                <input
                    type="text"
                    id="subject"
                    name="subject"
                    className={`form-input ${showValidation && !isSubjectValid ? 'invalid' : ''}`}
                    value={data.subject}
                    onChange={handleInputChange}
                    placeholder={t('quizEditor.subjectPlaceholder')}
                    disabled={disabled}
                    required
                />
                {showValidation && !isSubjectValid && (
                    <span className="form-error">{t('quizEditor.subjectRequired')}</span>
                )}
            </div>

            {/* Category & Level - Side by side */}
            <div className="form-row">
                <div className="form-group">
                    <label htmlFor="category" className="form-label">
                        {t('quizEditor.category')}
                    </label>
                    <input
                        type="text"
                        id="category"
                        name="category"
                        className="form-input"
                        value={data.category || ''}
                        onChange={handleInputChange}
                        placeholder={t('quizEditor.categoryPlaceholder')}
                        disabled={disabled}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="level" className="form-label">
                        {t('quizEditor.level')}
                    </label>
                    <input
                        type="text"
                        id="level"
                        name="level"
                        className="form-input"
                        value={data.level || ''}
                        onChange={handleInputChange}
                        placeholder={t('quizEditor.levelPlaceholder')}
                        disabled={disabled}
                    />
                </div>
            </div>

            {/* Description */}
            <div className="form-group">
                <label htmlFor="description" className="form-label">
                    {t('quizEditor.description')}
                </label>
                <textarea
                    id="description"
                    name="description"
                    className="form-input form-textarea"
                    value={data.description || ''}
                    onChange={handleInputChange}
                    placeholder={t('quizEditor.descriptionPlaceholder')}
                    rows={4}
                    disabled={disabled}
                />
            </div>

            {/* Tags */}
            <div className="form-group">
                <label className="form-label">{t('quizEditor.tags')}</label>
                <p className="form-hint">{t('quizEditor.selectTags')}</p>
                <TagSelector
                    selectedTagIds={data.tag_ids}
                    onChange={handleTagsChange}
                    disabled={disabled}
                    accessToken={accessToken}
                />
            </div>

            {/* Image Upload */}
            <div className="form-group">
                <label className="form-label">{t('quizEditor.imageUpload')}</label>
                <p className="form-hint">{t('quizEditor.imageDescription')}</p>

                {data.image ? (
                    <div className="image-preview-container">
                        <img
                            src={getImagePreviewUrl() || ''}
                            alt="Quiz preview"
                            className="image-preview"
                        />
                        <button
                            type="button"
                            className="image-remove-button"
                            onClick={handleRemoveImage}
                            disabled={disabled}
                        >
                            {t('quizEditor.removeImage')}
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
                            {t('quizEditor.uploadImage')}
                        </label>
                    </div>
                )}

                {imageError && (
                    <span className="form-error">{imageError}</span>
                )}
            </div>

            {/* Status & Flags */}
            <div className="form-section">
                <h3 className="form-section-title">{t('quizEditor.statusSection')}</h3>

                {/* Status Selector */}
                <div className="form-group">
                    <label htmlFor="status" className="form-label">
                        {t('quizEditor.status')}
                    </label>
                    <select
                        id="status"
                        name="status"
                        className="form-input form-select"
                        value={data.status}
                        onChange={handleInputChange}
                        disabled={disabled}
                    >
                        <option value="draft">{t('quizEditor.draft')}</option>
                        <option value="published">{t('quizEditor.published')}</option>
                        <option value="archived">{t('quizEditor.archived')}</option>
                    </select>
                </div>

                {/* Checkboxes */}
                <div className="form-checkboxes">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="is_draft"
                            checked={data.is_draft}
                            onChange={handleInputChange}
                            disabled={disabled}
                        />
                        <span className="checkbox-text">
                            {t('quizEditor.isDraft')}
                            <span className="checkbox-hint">{t('quizEditor.draftDescription')}</span>
                        </span>
                    </label>

                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="favourite"
                            checked={data.favourite}
                            onChange={handleInputChange}
                            disabled={disabled}
                        />
                        <span className="checkbox-text">
                            {t('quizEditor.markAsFavourite')}
                        </span>
                    </label>
                </div>
            </div>
        </div>
    );
};
