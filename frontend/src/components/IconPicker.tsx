import React from 'react';
import data from '@emoji-mart/data';
import Picker from '@emoji-mart/react';
import './IconPicker.css';

interface IconPickerProps {
    onSelect: (emoji: string) => void;
    onClose: () => void;
}

export const IconPicker: React.FC<IconPickerProps> = ({ onSelect, onClose }) => {
    const handleEmojiSelect = (emoji: any) => {
        onSelect(emoji.native);
    };

    // Custom categories with educational emoji
    const customCategories = [
        {
            id: 'history',
            name: 'Historia',
            emojis: [
                '🏛️', '📜', '⚔️', '👑', '🗿', '🏺', '⚱️',
                '🏰', '🛡️', '📯', '🏹', '⛪', '🕌', '🗝️'
            ]
        },
        {
            id: 'science',
            name: 'Nauki ścisłe',
            emojis: [
                '🔬', '⚗️', '🧪', '🧬', '💉', '🦠', '⚛️',
                '🔭', '🧲', '💊', '🩺', '🧫', '🌡️', '💡'
            ]
        },
        {
            id: 'math',
            name: 'Matematyka',
            emojis: [
                '📐', '📏', '📊', '📈', '📉', '🔢', '➕',
                '➖', '✖️', '➗', '🧮', '💯', '∞', '∑'
            ]
        },
        {
            id: 'geography',
            name: 'Geografia',
            emojis: [
                '🌍', '🌎', '🌏', '🗺️', '⛰️', '🌋', '🏔️',
                '🗻', '🏜️', '🏝️', '🌊', '💧', '🌦️', '🧭'
            ]
        },
        {
            id: 'languages',
            name: 'Języki',
            emojis: [
                '📚', '📖', '📝', '✏️', '✍️', '📕', '📗',
                '📘', '📙', '📓', '📔', '📒', '🖊️', '🖋️'
            ]
        },
        {
            id: 'art',
            name: 'Sztuka',
            emojis: [
                '🎨', '🖼️', '🎭', '🎪', '🎬', '🎤', '🎧',
                '🎵', '🎶', '🎸', '🎹', '🎺', '🎻', '🥁'
            ]
        },
        {
            id: 'sport',
            name: 'Sport',
            emojis: [
                '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉',
                '🥇', '🥈', '🥉', '🏆', '🏅', '🎯', '⛳'
            ]
        },
        {
            id: 'nature',
            name: 'Przyroda',
            emojis: [
                '🌱', '🌿', '🍀', '🌳', '🌲', '🌴', '🌵',
                '🦋', '🐝', '🐞', '🌺', '🌻', '🌸', '🌷'
            ]
        },
        {
            id: 'tech',
            name: 'Technologia',
            emojis: [
                '💻', '🖥️', '⌨️', '🖱️', '🖨️', '📱', '🔋',
                '💾', '💿', '📡', '🔌', '🤖', '🚀', '🛸'
            ]
        },
        {
            id: 'general',
            name: 'Ogólne',
            emojis: [
                '🎓', '📌', '⭐', '✨', '💎', '🔥', '⚡',
                '🌟', '💫', '✅', '❓', '❗', '💭', '🔔'
            ]
        }
    ];

    return (
        <div className="icon-picker">
            <div className="icon-picker-header">
                <h3>Wybierz ikonę</h3>
                <button type="button" className="icon-picker-close" onClick={onClose}>✕</button>
            </div>

            <Picker
                data={data}
                onEmojiSelect={handleEmojiSelect}
                locale="pl"
                theme="light"
                previewPosition="none"
                skinTonePosition="none"
                categories={[
                    'history', 'science', 'math', 'geography', 'languages',
                    'art', 'sport', 'nature', 'tech', 'general'
                ]}
                custom={customCategories}
            />
        </div>
    );
};
