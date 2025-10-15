import React from 'react';

interface QuizIconProps {
    iconName: string;
    size?: number;
    className?: string;
}

export const QuizIcon: React.FC<QuizIconProps> = ({ iconName, size = 24, className = '' }) => {
    // Emoji are just text, so we display them directly
    return (
        <span
            className={className}
            style={{
                fontSize: `${size}px`,
                lineHeight: 1,
                display: 'inline-block'
            }}
        >
            {iconName || '📚'}
        </span>
    );
};
