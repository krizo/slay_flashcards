import {beforeEach, describe, expect, it, vi} from 'vitest';
import {fireEvent, render, screen} from '@testing-library/react';
import FlashcardComponent from './FlashcardComponent';
import {FlashcardData} from '../types';

// Mock the audio utils
vi.mock('../utils/audioUtils', () => ({
    playAudio: vi.fn(),
    stopAudio: vi.fn(),
    isAudioAvailable: vi.fn(() => true),
}));

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
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        // Question should be visible (appears twice: front and back)
        expect(screen.getAllByText('What is TypeScript?')).toHaveLength(2);
        expect(screen.getByText('Explain what TypeScript is.')).toBeInTheDocument();
        expect(screen.getAllByText('📘')).toHaveLength(2);
        expect(screen.getByText('Show Answer')).toBeInTheDocument();
    });

    it('displays correct difficulty level with active dots', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const container = document.querySelector('.flashcard-container');
        const difficultyDots = container?.querySelectorAll('.flashcard-difficulty .dot');

        // difficulty 3: 3 dots on front + 3 dots on back = 6 total
        expect(difficultyDots).toHaveLength(6);

        // All rendered dots are active (3 on front + 3 on back)
        const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');
        expect(activeDots).toHaveLength(6);
    });

    it('displays quiz progress correctly', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.getAllByText('1 / 10')).toHaveLength(2); // Front and back
    });

    it('flips the card when "Show Answer" button is clicked', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const flashcardContainer = document.querySelector('.flashcard-container');

        // Initially not flipped
        expect(flashcardContainer).not.toHaveClass('flipped');

        // Click "Show Answer" button to flip
        const showAnswerButton = screen.getByText('Show Answer');
        fireEvent.click(showAnswerButton);

        // Should now be flipped
        expect(flashcardContainer).toHaveClass('flipped');
    });

    it('toggles flip state: Show Answer flips to back, clicking back side flips to front', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const flashcardContainer = document.querySelector('.flashcard-container');
        const showAnswerButton = screen.getByText('Show Answer');

        // Click Show Answer to flip to back
        fireEvent.click(showAnswerButton);
        expect(flashcardContainer).toHaveClass('flipped');

        // Click back side to unflip
        const backSide = document.querySelector('.flashcard-back');
        fireEvent.click(backSide!);
        expect(flashcardContainer).not.toHaveClass('flipped');

        // Click Show Answer again to flip again
        fireEvent.click(showAnswerButton);
        expect(flashcardContainer).toHaveClass('flipped');
    });

    it('renders answer content on the back side', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        // Answer text should be in the document (even if hidden by CSS)
        expect(
            screen.getByText('TypeScript is a strongly typed programming language that builds on JavaScript.')
        ).toBeInTheDocument();

        expect(screen.getByText('Answer:')).toBeInTheDocument();
        expect(screen.getByText('Next Flashcard')).toBeInTheDocument();
    });

    it('displays language tag when lang is provided', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const langTags = screen.getAllByText('en');
        expect(langTags.length).toBeGreaterThan(0);
    });

    it('does not display language tag when lang is null', () => {
        mockFlashcardData.question.lang = null;
        mockFlashcardData.answer.lang = null;

        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.queryByText('en')).not.toBeInTheDocument();
    });

    it('renders audio icons when lang is provided', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const audioIcons = document.querySelectorAll('.fa-volume-up');
        expect(audioIcons.length).toBeGreaterThan(0);
    });

    it('defaults to learn mode when no mode is provided', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        // Learn mode shows "Show Answer" button
        expect(screen.getByText('Show Answer')).toBeInTheDocument();
    });

    it('supports test mode', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData} mode="test"/>);

        // Test mode also shows "Show Answer" button (same UI for now)
        expect(screen.getByText('Show Answer')).toBeInTheDocument();
    });

    it('displays answer type information', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.getByText('Answer Type:')).toBeInTheDocument();
        expect(screen.getByText('text')).toBeInTheDocument();
    });

    it('handles different difficulty levels correctly', () => {
        mockFlashcardData.question.difficulty = 5;
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const container = document.querySelector('.flashcard-container');
        const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');

        // 5 active on front + 5 active on back = 10 total
        expect(activeDots).toHaveLength(10);
    });

    it('handles difficulty level 1 correctly', () => {
        mockFlashcardData.question.difficulty = 1;
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const container = document.querySelector('.flashcard-container');
        const activeDots = container?.querySelectorAll('.flashcard-difficulty .dot.active');

        // 1 active on front + 1 active on back = 2 total
        expect(activeDots).toHaveLength(2);
    });

    it('renders "Don\'t Know" button on front side', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.getByText('Don\'t Know')).toBeInTheDocument();
    });

    it('renders "Show Answer" button on front side', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.getByText('Show Answer')).toBeInTheDocument();
    });

    it('renders "Next Flashcard" button on back side', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        expect(screen.getByText('Next Flashcard')).toBeInTheDocument();
    });

    it('calls onNextFlashcard when "Next Flashcard" button is clicked', () => {
        const mockOnNext = vi.fn();
        render(<FlashcardComponent flashcardData={mockFlashcardData} onNextFlashcard={mockOnNext}/>);

        const nextButton = screen.getByText('Next Flashcard');
        fireEvent.click(nextButton);

        expect(mockOnNext).toHaveBeenCalledTimes(1);
    });

    it('calls onNextFlashcard when "Don\'t Know" button is clicked', () => {
        const mockOnNext = vi.fn();
        render(<FlashcardComponent flashcardData={mockFlashcardData} onNextFlashcard={mockOnNext}/>);

        const dontKnowButton = screen.getByText('Don\'t Know');
        fireEvent.click(dontKnowButton);

        expect(mockOnNext).toHaveBeenCalledTimes(1);
    });

    it('resets card to front when "Next Flashcard" button is clicked', () => {
        const mockOnNext = vi.fn();
        render(<FlashcardComponent flashcardData={mockFlashcardData} onNextFlashcard={mockOnNext}/>);

        const flashcardContainer = document.querySelector('.flashcard-container');
        const showAnswerButton = screen.getByText('Show Answer');

        // Flip the card first using Show Answer button
        fireEvent.click(showAnswerButton);
        expect(flashcardContainer).toHaveClass('flipped');

        // Click the Next button
        const nextButton = screen.getByText('Next Flashcard');
        fireEvent.click(nextButton);

        // Card should be reset to front (not flipped)
        expect(flashcardContainer).not.toHaveClass('flipped');
    });

    it('prevents card flip when clicking "Don\'t Know" button', () => {
        const mockOnNext = vi.fn();
        render(<FlashcardComponent flashcardData={mockFlashcardData} onNextFlashcard={mockOnNext}/>);

        const flashcardContainer = document.querySelector('.flashcard-container');

        // Initially not flipped
        expect(flashcardContainer).not.toHaveClass('flipped');

        // Click Don't Know button shouldn't flip the card
        const dontKnowButton = screen.getByText('Don\'t Know');
        fireEvent.click(dontKnowButton);

        expect(flashcardContainer).not.toHaveClass('flipped');
    });

    it('calls playAudio when clicking audio icon on question', async () => {
        const {playAudio} = await import('../utils/audioUtils');
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const audioIcons = document.querySelectorAll('.fa-volume-up');
        const questionAudioIcon = audioIcons[0] as HTMLElement;

        fireEvent.click(questionAudioIcon);

        expect(playAudio).toHaveBeenCalledWith('Explain what TypeScript is.', 'en');
    });

    it('calls playAudio when clicking audio icon on answer', async () => {
        const {playAudio} = await import('../utils/audioUtils');
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const audioIcons = document.querySelectorAll('.fa-volume-up');
        const answerAudioIcon = audioIcons[1] as HTMLElement;

        fireEvent.click(answerAudioIcon);

        expect(playAudio).toHaveBeenCalledWith(
            'TypeScript is a strongly typed programming language that builds on JavaScript.',
            'en'
        );
    });

    it('prevents card flip when clicking audio icon', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const flashcardContainer = document.querySelector('.flashcard-container');
        const audioIcons = document.querySelectorAll('.fa-volume-up');
        const questionAudioIcon = audioIcons[0] as HTMLElement;

        // Click audio icon
        fireEvent.click(questionAudioIcon);

        // Card should not flip
        expect(flashcardContainer).not.toHaveClass('flipped');
    });

    it('applies correct CSS classes for flip animation', () => {
        render(<FlashcardComponent flashcardData={mockFlashcardData}/>);

        const front = document.querySelector('.flashcard-front');
        const back = document.querySelector('.flashcard-back');

        expect(front).toBeInTheDocument();
        expect(back).toBeInTheDocument();
    });
});
