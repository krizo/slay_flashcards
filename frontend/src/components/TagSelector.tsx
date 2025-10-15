import React, { useState } from 'react';
import { useTags } from '../hooks/useTags';
import { Tag } from '../types';
import { useTranslation } from 'react-i18next';
import './TagSelector.css';

interface TagSelectorProps {
    selectedTagIds: number[];
    onChange: (tagIds: number[]) => void;
    disabled?: boolean;
    accessToken?: string | null;
}

export const TagSelector: React.FC<TagSelectorProps> = ({ selectedTagIds, onChange, disabled = false, accessToken }) => {
    const { t } = useTranslation();
    const { tags, loading, createTag } = useTags(accessToken);
    const [isCreating, setIsCreating] = useState(false);
    const [newTagName, setNewTagName] = useState('');
    const [newTagColor, setNewTagColor] = useState('#3B82F6'); // Default blue

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
            setNewTagColor('#3B82F6');
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
                        <input
                            type="color"
                            value={newTagColor}
                            onChange={(e) => setNewTagColor(e.target.value)}
                            className="tag-color-input-inline"
                            title={t('quizEditor.tagColor')}
                        />
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
                                setNewTagColor('#3B82F6');
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
