import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FlashcardComponent from './FlashcardComponent';
import { FlashcardData } from '../types';

describe('FlashcardComponent', () => {
  let mockFlashcardData: FlashcardData;

  beforeEach(() => {
    mockFlashcardData = {
      id: 1,
      quiz_id: 10,
      question: {
        title: 'What is TypeScript?',
        text: 'Explain what TypeScript is.',
        lang: 'en',
        difficulty: 3,
        emoji: '📘',
        image: null,
      },
      answer: {
        text: 'TypeScript is a strongly typed programming language that builds on JavaScript.',
        lang: 'en',
        type: 'text',
        options: null,
        metadata: null,
      },
    };
  });

  it('renders the flashcard with question visible initially', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    // Question should be visible (appears twice: front and back)
    expect(screen.getAllByText('What is TypeScript?')).toHaveLength(2);
    expect(screen.getByText('Explain what TypeScript is.')).toBeInTheDocument();
    expect(screen.getAllByText('📘')).toHaveLength(2);
    expect(screen.getByText('Show Answer')).toBeInTheDocument();
  });

  it('displays correct difficulty level with active dots', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const container = document.querySelector('.flashcard-container');
    const difficultyDots = container?.querySelectorAll('.flashcard-difficulty .dot');

    // 5 dots on front + 5 dots on back = 10 total
    expect(difficultyDots).toHaveLength(10);

    // Check that exactly 6 dots are active (3 on front + 3 on back)
    const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');
    expect(activeDots).toHaveLength(6);
  });

  it('displays quiz progress correctly', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    expect(screen.getAllByText('1 / 10')).toHaveLength(2); // Front and back
  });

  it('flips the card when clicked', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const flashcardContainer = document.querySelector('.flashcard-container');

    // Initially not flipped
    expect(flashcardContainer).not.toHaveClass('flipped');

    // Click to flip
    fireEvent.click(flashcardContainer!);

    // Should now be flipped
    expect(flashcardContainer).toHaveClass('flipped');
  });

  it('toggles flip state on multiple clicks', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const flashcardContainer = document.querySelector('.flashcard-container');

    // Click to flip
    fireEvent.click(flashcardContainer!);
    expect(flashcardContainer).toHaveClass('flipped');

    // Click again to unflip
    fireEvent.click(flashcardContainer!);
    expect(flashcardContainer).not.toHaveClass('flipped');

    // Click once more to flip again
    fireEvent.click(flashcardContainer!);
    expect(flashcardContainer).toHaveClass('flipped');
  });

  it('renders answer content on the back side', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    // Answer text should be in the document (even if hidden by CSS)
    expect(
      screen.getByText('TypeScript is a strongly typed programming language that builds on JavaScript.')
    ).toBeInTheDocument();

    expect(screen.getByText('Answer:')).toBeInTheDocument();
    expect(screen.getByText('Next Flashcard')).toBeInTheDocument();
  });

  it('displays language tag when lang is provided', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const langTags = screen.getAllByText('en');
    expect(langTags.length).toBeGreaterThan(0);
  });

  it('does not display language tag when lang is null', () => {
    mockFlashcardData.question.lang = null;
    mockFlashcardData.answer.lang = null;

    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    expect(screen.queryByText('en')).not.toBeInTheDocument();
  });

  it('renders audio icons when lang is provided', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const audioIcons = document.querySelectorAll('.fa-volume-up');
    expect(audioIcons.length).toBeGreaterThan(0);
  });

  it('defaults to learn mode when no mode is provided', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    // Learn mode shows "Show Answer" button
    expect(screen.getByText('Show Answer')).toBeInTheDocument();
  });

  it('supports test mode', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} mode="test" />);

    // Test mode also shows "Show Answer" button (same UI for now)
    expect(screen.getByText('Show Answer')).toBeInTheDocument();
  });

  it('displays answer type information', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    expect(screen.getByText('Answer Type:')).toBeInTheDocument();
    expect(screen.getByText('text')).toBeInTheDocument();
  });

  it('handles different difficulty levels correctly', () => {
    mockFlashcardData.question.difficulty = 5;
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const container = document.querySelector('.flashcard-container');
    const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');

    // 5 active on front + 5 active on back = 10 total
    expect(activeDots).toHaveLength(10);
  });

  it('handles difficulty level 1 correctly', () => {
    mockFlashcardData.question.difficulty = 1;
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const container = document.querySelector('.flashcard-container');
    const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');

    // 1 active on front + 1 active on back = 2 total
    expect(activeDots).toHaveLength(2);
  });

  it('renders both Show Answer and Next Flashcard buttons', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    expect(screen.getByText('Show Answer')).toBeInTheDocument();
    expect(screen.getByText('Next Flashcard')).toBeInTheDocument();
  });

  it('applies correct CSS classes for flip animation', () => {
    render(<FlashcardComponent flashcardData={mockFlashcardData} />);

    const front = document.querySelector('.flashcard-front');
    const back = document.querySelector('.flashcard-back');

    expect(front).toBeInTheDocument();
    expect(back).toBeInTheDocument();
  });
});
