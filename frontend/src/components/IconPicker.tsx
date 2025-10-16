import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './IconPicker.css';

interface IconPickerProps {
    onSelect: (emoji: string) => void;
    onClose: () => void;
}

interface EmojiCategory {
    nameKey: string;
    emojis: string[];
}

const EMOJI_CATEGORIES: EmojiCategory[] = [
    {
        nameKey: 'iconPicker.categoryHistory',
        emojis: [
            '🏛️', '📜', '⚔️', '👑', '🗿', '🏺', '⚱️',
            '🏰', '🛡️', '📯', '🏹', '⛪', '🕌', '🗝️'
        ]
    },
    {
        nameKey: 'iconPicker.categoryScience',
        emojis: [
            '🔬', '⚗️', '🧪', '🧬', '💉', '🦠', '⚛️',
            '🔭', '🧲', '💊', '🩺', '🧫', '🌡️', '💡'
        ]
    },
    {
        nameKey: 'iconPicker.categoryMath',
        emojis: [
            '📐', '📏', '📊', '📈', '📉', '🔢', '➕',
            '➖', '✖️', '➗', '🧮', '💯', '∞', '∑'
        ]
    },
    {
        nameKey: 'iconPicker.categoryGeography',
        emojis: [
            '🌍', '🌎', '🌏', '🗺️', '⛰️', '🌋', '🏔️',
            '🗻', '🏜️', '🏝️', '🌊', '💧', '🌦️', '🧭'
        ]
    },
    {
        nameKey: 'iconPicker.categoryLanguages',
        emojis: [
            '🇬🇧', '🇵🇱', '🇩🇪', '🇫🇷', '🇪🇸', '🇮🇹',
            '🇷🇺', '🇨🇳', '🇯🇵', '🇺🇦', '🇬🇷', '🇭🇺', '🇳🇱', '🇸🇪'
        ]
    },
    {
        nameKey: 'iconPicker.categoryArt',
        emojis: [
            '🎨', '🖼️', '🎭', '🎪', '🎬', '🎤', '🎧',
            '🎵', '🎶', '🎸', '🎹', '🎺', '🎻', '🥁'
        ]
    },
    {
        nameKey: 'iconPicker.categorySports',
        emojis: [
            '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉',
            '🥇', '🥈', '🥉', '🏆', '🏅', '🎯', '⛳'
        ]
    },
    {
        nameKey: 'iconPicker.categoryNature',
        emojis: [
            '🌱', '🌿', '🍀', '🌳', '🌲', '🌴', '🌵',
            '🦋', '🐝', '🐞', '🌺', '🌻', '🌸', '🌷'
        ]
    },
    {
        nameKey: 'iconPicker.categoryTechnology',
        emojis: [
            '💻', '🖥️', '⌨️', '🖱️', '🖨️', '📱', '🔋',
            '💾', '💿', '📡', '🔌', '🤖', '🚀', '🛸'
        ]
    },
    {
        nameKey: 'iconPicker.categoryGeneral',
        emojis: [
            '🎓', '📌', '⭐', '✨', '💎', '🔥', '⚡',
            '🌟', '💫', '✅', '❓', '❗', '💭', '🔔'
        ]
    }
];

export const IconPicker: React.FC<IconPickerProps> = ({ onSelect, onClose }) => {
    const { t } = useTranslation();
    const [selectedCategory, setSelectedCategory] = useState(0);
    const [customEmoji, setCustomEmoji] = useState('');

    const handleEmojiClick = (emoji: string) => {
        onSelect(emoji);
    };

    const handleCustomEmojiSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (customEmoji.trim()) {
            onSelect(customEmoji.trim());
            setCustomEmoji('');
        }
    };

    const isCustomCategory = selectedCategory === EMOJI_CATEGORIES.length;

    return (
        <div className="icon-picker">
            <div className="icon-picker-header">
                <h3>{t('iconPicker.title')}</h3>
                <button type="button" className="icon-picker-close" onClick={onClose}>✕</button>
            </div>

            <div className="icon-picker-categories">
                {EMOJI_CATEGORIES.map((category, index) => (
                    <button
                        key={index}
                        type="button"
                        className={`category-button ${selectedCategory === index ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(index)}
                    >
                        {t(category.nameKey)}
                    </button>
                ))}
                <button
                    type="button"
                    className={`category-button ${isCustomCategory ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(EMOJI_CATEGORIES.length)}
                >
                    {t('iconPicker.categoryCustom')}
                </button>
            </div>

            {isCustomCategory ? (
                <div className="custom-emoji-input">
                    <form onSubmit={handleCustomEmojiSubmit}>
                        <label htmlFor="custom-emoji" className="custom-emoji-label">
                            {t('iconPicker.customEmojiLabel')}
                        </label>
                        <div className="custom-emoji-controls">
                            <input
                                id="custom-emoji"
                                type="text"
                                className="custom-emoji-field"
                                value={customEmoji}
                                onChange={(e) => setCustomEmoji(e.target.value)}
                                placeholder={t('iconPicker.customEmojiPlaceholder')}
                                autoFocus
                            />
                            <button
                                type="submit"
                                className="custom-emoji-submit"
                                disabled={!customEmoji.trim()}
                            >
                                {t('iconPicker.customEmojiSubmit')}
                            </button>
                        </div>
                        <p className="custom-emoji-hint">
                            {t('iconPicker.customEmojiHint')}
                        </p>
                    </form>
                </div>
            ) : (
                <div className="icon-picker-grid">
                    {EMOJI_CATEGORIES[selectedCategory].emojis.map((emoji) => (
                        <button
                            key={emoji}
                            type="button"
                            className="icon-button"
                            onClick={() => handleEmojiClick(emoji)}
                            title={emoji}
                        >
                            <span style={{ fontSize: '32px' }}>{emoji}</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};
