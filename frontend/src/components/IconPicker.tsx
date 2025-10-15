import React, { useState } from 'react';
import './IconPicker.css';

interface IconPickerProps {
    onSelect: (emoji: string) => void;
    onClose: () => void;
}

interface EmojiCategory {
    name: string;
    emojis: string[];
}

const EMOJI_CATEGORIES: EmojiCategory[] = [
    {
        name: '📜 Historia',
        emojis: [
            '🏛️', '📜', '⚔️', '👑', '🗿', '🏺', '⚱️',
            '🏰', '🛡️', '📯', '🏹', '⛪', '🕌', '🗝️'
        ]
    },
    {
        name: '🔬 Nauki ścisłe',
        emojis: [
            '🔬', '⚗️', '🧪', '🧬', '💉', '🦠', '⚛️',
            '🔭', '🧲', '💊', '🩺', '🧫', '🌡️', '💡'
        ]
    },
    {
        name: '📐 Matematyka',
        emojis: [
            '📐', '📏', '📊', '📈', '📉', '🔢', '➕',
            '➖', '✖️', '➗', '🧮', '💯', '∞', '∑'
        ]
    },
    {
        name: '🌍 Geografia',
        emojis: [
            '🌍', '🌎', '🌏', '🗺️', '⛰️', '🌋', '🏔️',
            '🗻', '🏜️', '🏝️', '🌊', '💧', '🌦️', '🧭'
        ]
    },
    {
        name: '🌐 Języki',
        emojis: [
            '🇬🇧', '🇵🇱', '🇩🇪', '🇫🇷', '🇪🇸', '🇮🇹',
            '🇷🇺', '🇨🇳', '🇯🇵', '🇺🇦', '🇬🇷', '🇭🇺', '🇳🇱', '🇸🇪'
        ]
    },
    {
        name: '🎨 Sztuka',
        emojis: [
            '🎨', '🖼️', '🎭', '🎪', '🎬', '🎤', '🎧',
            '🎵', '🎶', '🎸', '🎹', '🎺', '🎻', '🥁'
        ]
    },
    {
        name: '⚽ Sport',
        emojis: [
            '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉',
            '🥇', '🥈', '🥉', '🏆', '🏅', '🎯', '⛳'
        ]
    },
    {
        name: '🌱 Przyroda',
        emojis: [
            '🌱', '🌿', '🍀', '🌳', '🌲', '🌴', '🌵',
            '🦋', '🐝', '🐞', '🌺', '🌻', '🌸', '🌷'
        ]
    },
    {
        name: '💻 Technologia',
        emojis: [
            '💻', '🖥️', '⌨️', '🖱️', '🖨️', '📱', '🔋',
            '💾', '💿', '📡', '🔌', '🤖', '🚀', '🛸'
        ]
    },
    {
        name: '🎓 Ogólne',
        emojis: [
            '🎓', '📌', '⭐', '✨', '💎', '🔥', '⚡',
            '🌟', '💫', '✅', '❓', '❗', '💭', '🔔'
        ]
    }
];

export const IconPicker: React.FC<IconPickerProps> = ({ onSelect, onClose }) => {
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
                <h3>Wybierz ikonę</h3>
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
                        {category.name}
                    </button>
                ))}
                <button
                    type="button"
                    className={`category-button ${isCustomCategory ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(EMOJI_CATEGORIES.length)}
                >
                    ✨ Custom
                </button>
            </div>

            {isCustomCategory ? (
                <div className="custom-emoji-input">
                    <form onSubmit={handleCustomEmojiSubmit}>
                        <label htmlFor="custom-emoji" className="custom-emoji-label">
                            Wklej dowolne emoji:
                        </label>
                        <div className="custom-emoji-controls">
                            <input
                                id="custom-emoji"
                                type="text"
                                className="custom-emoji-field"
                                value={customEmoji}
                                onChange={(e) => setCustomEmoji(e.target.value)}
                                placeholder="🎯 Wklej emoji tutaj..."
                                autoFocus
                            />
                            <button
                                type="submit"
                                className="custom-emoji-submit"
                                disabled={!customEmoji.trim()}
                            >
                                Wybierz
                            </button>
                        </div>
                        <p className="custom-emoji-hint">
                            Możesz wkleić dowolne emoji z klawiatury (Ctrl+Cmd+Space na Mac, Win+. na Windows)
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
