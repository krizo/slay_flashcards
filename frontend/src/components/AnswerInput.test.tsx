import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnswerInput from './AnswerInput';
import { AnswerData } from '../types';

describe('AnswerInput', () => {
  it('renders textarea for text answer type', () => {
    const answer: AnswerData = {
      text: 'Sample answer',
      lang: null,
      type: 'text',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const textarea = screen.getByPlaceholderText('Type your answer here...');
    expect(textarea).toBeInTheDocument();
    expect(textarea.tagName).toBe('TEXTAREA');
  });

  it('renders short text input for short_text answer type', () => {
    const answer: AnswerData = {
      text: 'Sample answer',
      lang: null,
      type: 'short_text',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Type your answer...');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders number input with step=1 for integer answer type', () => {
    const answer: AnswerData = {
      text: '42',
      lang: null,
      type: 'integer',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Enter a whole number...');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
    expect(input).toHaveAttribute('step', '1');
  });

  it('renders number input with step=0.01 for float answer type', () => {
    const answer: AnswerData = {
      text: '3.14',
      lang: null,
      type: 'float',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Enter a number...');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
    expect(input).toHaveAttribute('step', '0.01');
  });

  it('renders range input with min/max in placeholder', () => {
    const answer: AnswerData = {
      text: '37',
      lang: null,
      type: 'range',
      options: null,
      metadata: { min: 36, max: 38 },
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Enter a number (36 - 38)...');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
  });

  it('renders True/False radio buttons for boolean answer type', () => {
    const answer: AnswerData = {
      text: 'true',
      lang: null,
      type: 'boolean',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    expect(screen.getByText('True')).toBeInTheDocument();
    expect(screen.getByText('False')).toBeInTheDocument();

    const radioButtons = document.querySelectorAll('input[type="radio"]');
    expect(radioButtons).toHaveLength(2);
  });

  it('renders radio buttons for choice answer type', () => {
    const answer: AnswerData = {
      text: 'b',
      lang: null,
      type: 'choice',
      options: [
        { value: 'a', label: 'Red' },
        { value: 'b', label: 'Blue' },
        { value: 'c', label: 'Green' },
        { value: 'd', label: 'Yellow' }
      ],
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    expect(screen.getByText('Red')).toBeInTheDocument();
    expect(screen.getByText('Blue')).toBeInTheDocument();
    expect(screen.getByText('Green')).toBeInTheDocument();
    expect(screen.getByText('Yellow')).toBeInTheDocument();

    const radioButtons = document.querySelectorAll('input[type="radio"]');
    expect(radioButtons).toHaveLength(4);
  });

  it('renders checkboxes for multiple_choice answer type', () => {
    const answer: AnswerData = {
      text: 'a,c',
      lang: null,
      type: 'multiple_choice',
      options: [
        { value: 'a', label: 'Python' },
        { value: 'b', label: 'HTML' },
        { value: 'c', label: 'Java' },
        { value: 'd', label: 'CSS' }
      ],
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer={[]} onAnswerChange={mockOnChange} />);

    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('HTML')).toBeInTheDocument();
    expect(screen.getByText('Java')).toBeInTheDocument();
    expect(screen.getByText('CSS')).toBeInTheDocument();

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    expect(checkboxes).toHaveLength(4);
  });

  it('calls onAnswerChange when text input changes', () => {
    const answer: AnswerData = {
      text: 'Sample answer',
      lang: null,
      type: 'short_text',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Type your answer...');
    fireEvent.change(input, { target: { value: 'New answer' } });

    expect(mockOnChange).toHaveBeenCalledWith('New answer');
  });

  it('calls onAnswerChange when radio button is selected', () => {
    const answer: AnswerData = {
      text: 'true',
      lang: null,
      type: 'boolean',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

    const trueRadio = screen.getByLabelText('True');
    fireEvent.click(trueRadio);

    expect(mockOnChange).toHaveBeenCalledWith('true');
  });

  it('handles multiple checkbox selections correctly', () => {
    const answer: AnswerData = {
      text: 'a,c',
      lang: null,
      type: 'multiple_choice',
      options: [
        { value: 'a', label: 'Python' },
        { value: 'b', label: 'HTML' },
        { value: 'c', label: 'Java' },
        { value: 'd', label: 'CSS' }
      ],
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer={[]} onAnswerChange={mockOnChange} />);

    const pythonCheckbox = screen.getByLabelText('Python');
    fireEvent.click(pythonCheckbox);

    // Should be called with array containing selected value
    expect(mockOnChange).toHaveBeenCalledWith(['a']);
  });

  it('deselects checkbox when clicked again', () => {
    const answer: AnswerData = {
      text: 'a,c',
      lang: null,
      type: 'multiple_choice',
      options: [
        { value: 'a', label: 'Python' },
        { value: 'b', label: 'HTML' },
        { value: 'c', label: 'Java' },
        { value: 'd', label: 'CSS' }
      ],
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer={['a']} onAnswerChange={mockOnChange} />);

    const pythonCheckbox = screen.getByLabelText('Python');
    fireEvent.click(pythonCheckbox);

    // Should be called with empty array (Python deselected)
    expect(mockOnChange).toHaveBeenCalledWith([]);
  });

  it('displays user answer in text input', () => {
    const answer: AnswerData = {
      text: 'Sample answer',
      lang: null,
      type: 'short_text',
      options: null,
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="My answer" onAnswerChange={mockOnChange} />);

    const input = screen.getByPlaceholderText('Type your answer...') as HTMLInputElement;
    expect(input.value).toBe('My answer');
  });

  it('checks radio button when userAnswer matches', () => {
    const answer: AnswerData = {
      text: 'b',
      lang: null,
      type: 'choice',
      options: [
        { value: 'a', label: 'Red' },
        { value: 'b', label: 'Blue' },
        { value: 'c', label: 'Green' },
        { value: 'd', label: 'Yellow' }
      ],
      metadata: null,
    };

    const mockOnChange = vi.fn();
    render(<AnswerInput answer={answer} userAnswer="b" onAnswerChange={mockOnChange} />);

    const blueRadio = screen.getByLabelText('Blue') as HTMLInputElement;
    expect(blueRadio.checked).toBe(true);
  });

  // Tests for flexible option formats (value/label objects)
  describe('Flexible Option Formats', () => {
    it('renders choice with value/label objects', () => {
      const answer: AnswerData = {
        text: 'Au',
        lang: null,
        type: 'choice',
        options: [
          { value: 'Au', label: 'Au (Gold)' },
          { value: 'Ag', label: 'Ag (Silver)' },
          { value: 'Fe', label: 'Fe (Iron)' },
          { value: 'Cu', label: 'Cu (Copper)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

      // Should display labels
      expect(screen.getByText('Au (Gold)')).toBeInTheDocument();
      expect(screen.getByText('Ag (Silver)')).toBeInTheDocument();
      expect(screen.getByText('Fe (Iron)')).toBeInTheDocument();
      expect(screen.getByText('Cu (Copper)')).toBeInTheDocument();

      const radioButtons = document.querySelectorAll('input[type="radio"]');
      expect(radioButtons).toHaveLength(4);
    });

    it('uses value when submitting choice with value/label objects', () => {
      const answer: AnswerData = {
        text: 'Au',
        lang: null,
        type: 'choice',
        options: [
          { value: 'Au', label: 'Au (Gold)' },
          { value: 'Ag', label: 'Ag (Silver)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer="" onAnswerChange={mockOnChange} />);

      const goldRadio = screen.getByLabelText('Au (Gold)');
      fireEvent.click(goldRadio);

      // Should call with value, not label
      expect(mockOnChange).toHaveBeenCalledWith('Au');
    });

    it('renders multiple_choice with value/label objects', () => {
      const answer: AnswerData = {
        text: 'He,Ne,Ar',
        lang: null,
        type: 'multiple_choice',
        options: [
          { value: 'He', label: 'Helium (He)' },
          { value: 'Ne', label: 'Neon (Ne)' },
          { value: 'O', label: 'Oxygen (O)' },
          { value: 'Ar', label: 'Argon (Ar)' },
          { value: 'N', label: 'Nitrogen (N)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer={[]} onAnswerChange={mockOnChange} />);

      // Should display labels
      expect(screen.getByText('Helium (He)')).toBeInTheDocument();
      expect(screen.getByText('Neon (Ne)')).toBeInTheDocument();
      expect(screen.getByText('Oxygen (O)')).toBeInTheDocument();
      expect(screen.getByText('Argon (Ar)')).toBeInTheDocument();
      expect(screen.getByText('Nitrogen (N)')).toBeInTheDocument();

      const checkboxes = document.querySelectorAll('input[type="checkbox"]');
      expect(checkboxes).toHaveLength(5);
    });

    it('uses values when submitting multiple_choice with value/label objects', () => {
      const answer: AnswerData = {
        text: 'He,Ne',
        lang: null,
        type: 'multiple_choice',
        options: [
          { value: 'He', label: 'Helium (He)' },
          { value: 'Ne', label: 'Neon (Ne)' },
          { value: 'O', label: 'Oxygen (O)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer={[]} onAnswerChange={mockOnChange} />);

      const heliumCheckbox = screen.getByLabelText('Helium (He)');
      fireEvent.click(heliumCheckbox);

      // Should be called with array containing value 'He', not label
      expect(mockOnChange).toHaveBeenCalledWith(['He']);
    });

    it('correctly checks radio with value/label when userAnswer matches value', () => {
      const answer: AnswerData = {
        text: 'Ag',
        lang: null,
        type: 'choice',
        options: [
          { value: 'Au', label: 'Au (Gold)' },
          { value: 'Ag', label: 'Ag (Silver)' },
          { value: 'Fe', label: 'Fe (Iron)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer="Ag" onAnswerChange={mockOnChange} />);

      const silverRadio = screen.getByLabelText('Ag (Silver)') as HTMLInputElement;
      expect(silverRadio.checked).toBe(true);
    });

    it('correctly checks checkboxes with value/label when userAnswer includes values', () => {
      const answer: AnswerData = {
        text: 'He,Ar',
        lang: null,
        type: 'multiple_choice',
        options: [
          { value: 'He', label: 'Helium (He)' },
          { value: 'Ne', label: 'Neon (Ne)' },
          { value: 'Ar', label: 'Argon (Ar)' }
        ],
        metadata: null,
      };

      const mockOnChange = vi.fn();
      render(<AnswerInput answer={answer} userAnswer={['He', 'Ar']} onAnswerChange={mockOnChange} />);

      const heliumCheckbox = screen.getByLabelText('Helium (He)') as HTMLInputElement;
      const neonCheckbox = screen.getByLabelText('Neon (Ne)') as HTMLInputElement;
      const argonCheckbox = screen.getByLabelText('Argon (Ar)') as HTMLInputElement;

      expect(heliumCheckbox.checked).toBe(true);
      expect(neonCheckbox.checked).toBe(false);
      expect(argonCheckbox.checked).toBe(true);
    });
  });
});
