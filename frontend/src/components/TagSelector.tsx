import React, { useState } from 'react';
import { useTags } from '../hooks/useTags';
import { useTranslation } from 'react-i18next';
import './TagSelector.css';

interface TagSelectorProps {
    selectedTagIds: number[];
    onChange: (tagIds: number[]) => void;
    disabled?: boolean;
    accessToken?: string | null;
}

// Predefined color palette (8 colors)
const PRESET_COLORS = [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#6B7280', // Gray
];

export const TagSelector: React.FC<TagSelectorProps> = ({ selectedTagIds, onChange, disabled = false, accessToken }) => {
    const { t } = useTranslation();
    const { tags, loading, createTag } = useTags(accessToken);
    const [isCreating, setIsCreating] = useState(false);
    const [newTagName, setNewTagName] = useState('');
    const [newTagColor, setNewTagColor] = useState(PRESET_COLORS[0]); // Default blue

    const handleTagToggle = (tagId: number) => {
        if (disabled) return;

        if (selectedTagIds.includes(tagId)) {
            onChange(selectedTagIds.filter(id => id !== tagId));
        } else {
            onChange([...selectedTagIds, tagId]);
        }
    };

    const handleCreateTag = async () => {
        if (!newTagName.trim()) return;

        const newTag = await createTag({
            name: newTagName.trim(),
            color: newTagColor,
        });

        if (newTag) {
            // Auto-select the newly created tag
            onChange([...selectedTagIds, newTag.id]);
            setNewTagName('');
            setNewTagColor(PRESET_COLORS[0]);
            setIsCreating(false);
        }
    };

    if (loading) {
        return <div className="tag-selector-loading">{t('common.loading')}</div>;
    }

    return (
        <div className="tag-selector">
            <div className="tag-list-inline">
                {tags.map((tag) => (
                    <button
                        key={tag.id}
                        type="button"
                        className={`tag-chip ${selectedTagIds.includes(tag.id) ? 'selected' : ''}`}
                        style={{
                            borderColor: tag.color || '#D1D5DB',
                            backgroundColor: selectedTagIds.includes(tag.id) ? tag.color || '#3B82F6' : 'transparent',
                            color: selectedTagIds.includes(tag.id) ? '#FFFFFF' : '#374151',
                        }}
                        onClick={() => handleTagToggle(tag.id)}
                        disabled={disabled}
                    >
                        {tag.name}
                    </button>
                ))}

                {isCreating && (
                    <>
                        <input
                            type="text"
                            value={newTagName}
                            onChange={(e) => setNewTagName(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleCreateTag()}
                            placeholder={t('quizEditor.tagNamePlaceholder')}
                            maxLength={50}
                            className="tag-name-input-inline"
                            autoFocus
                        />
                        <div className="tag-color-picker">
                            {PRESET_COLORS.map((color) => (
                                <button
                                    key={color}
                                    type="button"
                                    className={`tag-color-button ${newTagColor === color ? 'selected' : ''}`}
                                    style={{ backgroundColor: color }}
                                    onClick={() => setNewTagColor(color)}
                                    title={color}
                                />
                            ))}
                        </div>
                        <button
                            type="button"
                            className="tag-action-button tag-save-button"
                            onClick={handleCreateTag}
                            disabled={!newTagName.trim()}
                        >
                            {t('common.save')}
                        </button>
                        <button
                            type="button"
                            className="tag-action-button tag-cancel-button"
                            onClick={() => {
                                setIsCreating(false);
                                setNewTagName('');
                                setNewTagColor(PRESET_COLORS[0]);
                            }}
                        >
                            {t('common.cancel')}
                        </button>
                    </>
                )}

                {!isCreating && !disabled && (
                    <button
                        type="button"
                        className="tag-create-button-inline"
                        onClick={() => setIsCreating(true)}
                        title={t('quizEditor.createTag')}
                    >
                        +
                    </button>
                )}
            </div>
        </div>
    );
};
