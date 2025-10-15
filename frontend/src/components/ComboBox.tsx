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
    fieldLabel?: string; // e.g., "Kategoria", "Przedmiot", "Poziom"
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
    fieldLabel = 'wartość',
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [modalValue, setModalValue] = useState('');
    const wrapperRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const modalInputRef = useRef<HTMLInputElement>(null);

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
        setIsOpen(false);
        setShowModal(true);
        setModalValue('');
    };

    const handleModalSubmit = () => {
        if (modalValue.trim()) {
            onChange(modalValue.trim());
            setShowModal(false);
            setModalValue('');
            setSearchTerm('');
        }
    };

    const handleModalCancel = () => {
        setShowModal(false);
        setModalValue('');
    };

    const handleModalKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleModalSubmit();
        } else if (e.key === 'Escape') {
            handleModalCancel();
        }
    };

    // Focus modal input when modal opens
    useEffect(() => {
        if (showModal && modalInputRef.current) {
            setTimeout(() => modalInputRef.current?.focus(), 100);
        }
    }, [showModal]);

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

            {/* Modal for adding new value */}
            {showModal && (
                <div className="combobox-modal-overlay" onClick={handleModalCancel}>
                    <div className="combobox-modal" onClick={(e) => e.stopPropagation()}>
                        <h3 className="combobox-modal-title">
                            Nowy{fieldLabel.toLowerCase().endsWith('a') ? 'a' : ''} {fieldLabel.toLowerCase()}
                        </h3>
                        <input
                            ref={modalInputRef}
                            type="text"
                            className="form-input combobox-modal-input"
                            value={modalValue}
                            onChange={(e) => setModalValue(e.target.value)}
                            onKeyDown={handleModalKeyDown}
                            placeholder={`Wpisz ${fieldLabel.toLowerCase()}...`}
                        />
                        <div className="combobox-modal-actions">
                            <button
                                type="button"
                                className="combobox-modal-button combobox-modal-cancel"
                                onClick={handleModalCancel}
                            >
                                Anuluj
                            </button>
                            <button
                                type="button"
                                className="combobox-modal-button combobox-modal-submit"
                                onClick={handleModalSubmit}
                                disabled={!modalValue.trim()}
                            >
                                Dodaj
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
