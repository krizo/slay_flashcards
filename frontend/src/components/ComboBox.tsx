import React, { useState, useRef, useEffect } from 'react';
import './ComboBox.css';

interface ComboBoxProps {
    value: string;
    onChange: (value: string) => void;
    options: string[];
    placeholder?: string;
    disabled?: boolean;
    className?: string;
    required?: boolean;
    addNewLabel?: string;
}

export const ComboBox: React.FC<ComboBoxProps> = ({
    value,
    onChange,
    options,
    placeholder = '',
    disabled = false,
    className = '',
    required = false,
    addNewLabel = '+ Add new...',
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const wrapperRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                setSearchTerm('');
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Filter options based on search term
    const filteredOptions = options.filter(option =>
        option.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setSearchTerm(newValue);
        onChange(newValue);
        setIsOpen(true);
    };

    const handleOptionSelect = (option: string) => {
        onChange(option);
        setSearchTerm('');
        setIsOpen(false);
    };

    const handleAddNew = () => {
        setSearchTerm('');
        setIsOpen(false);
        if (inputRef.current) {
            inputRef.current.focus();
        }
    };

    const handleInputClick = () => {
        if (!disabled) {
            setIsOpen(!isOpen);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Escape') {
            setIsOpen(false);
            setSearchTerm('');
        }
    };

    return (
        <div ref={wrapperRef} className={`combobox ${className}`}>
            <div className="combobox-input-wrapper">
                <input
                    ref={inputRef}
                    type="text"
                    className="form-input combobox-input"
                    value={searchTerm || value}
                    onChange={handleInputChange}
                    onClick={handleInputClick}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                    disabled={disabled}
                    required={required}
                />
                <button
                    type="button"
                    className="combobox-toggle"
                    onClick={() => !disabled && setIsOpen(!isOpen)}
                    disabled={disabled}
                    aria-label="Toggle dropdown"
                >
                    <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
                        <path
                            d="M1 1L6 6L11 1"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    </svg>
                </button>
            </div>

            {isOpen && !disabled && (
                <div className="combobox-dropdown">
                    <button
                        type="button"
                        className="combobox-option combobox-add-new"
                        onClick={handleAddNew}
                    >
                        {addNewLabel}
                    </button>
                    {filteredOptions.length > 0 && (
                        <div className="combobox-divider" />
                    )}
                    {filteredOptions.map((option, index) => (
                        <button
                            key={index}
                            type="button"
                            className={`combobox-option ${value === option ? 'selected' : ''}`}
                            onClick={() => handleOptionSelect(option)}
                        >
                            {option}
                        </button>
                    ))}
                    {filteredOptions.length === 0 && searchTerm && (
                        <div className="combobox-no-results">
                            No matching options
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
