import {useState} from 'react';
import FlashcardComponent from '../components/FlashcardComponent';
import {FlashcardData} from '../types';

/**
 * Example quiz session with multiple flashcards demonstrating all 8 answer types
 */
const exampleFlashcardData: FlashcardData[] = [
    // 1. text - Free-form text input
    {
        id: 1,
        quiz_id: 8,
        question: {
            title: 'What is React?',
            text: 'Explain what React is and its main purpose in web development.',
            lang: 'en',
            difficulty: 3,
            emoji: '⚛️',
            image: null,
        },
        answer: {
            text: 'React is a JavaScript library for building user interfaces, particularly single-page applications where you need a fast, interactive user experience.',
            lang: 'en',
            type: 'text',
            options: null,
            metadata: null,
        },
    },
    // 2. short_text - Short text input
    {
        id: 2,
        quiz_id: 8,
        question: {
            title: 'French: Dog',
            text: 'How do you say "dog" in French?',
            lang: 'en',
            difficulty: 1,
            emoji: '🐶',
            image: null,
        },
        answer: {
            text: 'chien',
            lang: 'fr',
            type: 'short_text',
            options: null,
            metadata: null,
        },
    },
    // 3. integer - Integer input
    {
        id: 3,
        quiz_id: 8,
        question: {
            title: 'Days in a Week',
            text: 'How many days are in a week?',
            lang: 'en',
            difficulty: 1,
            emoji: '📅',
            image: null,
        },
        answer: {
            text: '7',
            lang: null,
            type: 'integer',
            options: null,
            metadata: {tolerance: 0},
        },
    },
    // 4. float - Floating-point number input
    {
        id: 4,
        quiz_id: 8,
        question: {
            title: 'Value of Pi',
            text: 'What is the value of Pi to 2 decimal places?',
            lang: 'en',
            difficulty: 2,
            emoji: '🥧',
            image: null,
        },
        answer: {
            text: '3.14',
            lang: null,
            type: 'float',
            options: null,
            metadata: {tolerance: 0.01},
        },
    },
    // 5. range - Numeric range input
    {
        id: 5,
        quiz_id: 8,
        question: {
            title: 'Normal Body Temperature',
            text: 'What is a normal human body temperature in degrees Celsius?',
            lang: 'en',
            difficulty: 2,
            emoji: '🌡️',
            image: null,
        },
        answer: {
            text: '37',
            lang: null,
            type: 'range',
            options: null,
            metadata: {min: 36, max: 38},
        },
    },
    // 6. boolean - True/False selection
    {
        id: 6,
        quiz_id: 8,
        question: {
            title: 'TypeScript and JavaScript',
            text: 'Is TypeScript a superset of JavaScript?',
            lang: 'en',
            difficulty: 2,
            emoji: '📘',
            image: null,
        },
        answer: {
            text: 'true',
            lang: null,
            type: 'boolean',
            options: null,
            metadata: null,
        },
    },
    // 7. choice - Single choice from options
    {
        id: 7,
        quiz_id: 8,
        question: {
            title: 'Sky Color',
            text: 'What color is a clear daytime sky?',
            lang: 'en',
            difficulty: 1,
            emoji: '🌤️',
            image: null,
        },
        answer: {
            text: 'Blue',
            lang: null,
            type: 'choice',
            options: ['Red', 'Blue', 'Green', 'Yellow'],
            metadata: null,
        },
    },
    // 8. multiple_choice - Multiple selections from options
    {
        id: 8,
        quiz_id: 8,
        question: {
            title: 'Programming Languages',
            text: 'Which of the following are programming languages?',
            lang: 'en',
            difficulty: 2,
            emoji: '💻',
            image: null,
        },
        answer: {
            text: 'Python, Java',
            lang: null,
            type: 'multiple_choice',
            options: ['Python', 'HTML', 'Java', 'CSS'],
            metadata: null,
        },
    },
];

const QuizzesPage = () => {
    const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState<number>(0);

    // Handle moving to next flashcard
    const handleNextFlashcard = () => {
        setCurrentFlashcardIndex((prevIndex) => {
            // Cycle back to start when reaching the end
            return (prevIndex + 1) % exampleFlashcardData.length;
        });
    };

    // Get current flashcard
    const currentFlashcard = exampleFlashcardData[currentFlashcardIndex];

    return (
        <div className="page-container">
            <div className="page-header">
                <h1 className="page-title">Quizzes Overview</h1>
                <p className="page-description">
                    Practice with flashcards demonstrating all 8 answer types.
                </p>
            </div>

            <div className="page-content">
                <div className="flashcard-wrapper">
                    <FlashcardComponent
                        flashcardData={currentFlashcard}
                        mode="learn"
                        onNextFlashcard={handleNextFlashcard}
                    />
                </div>
            </div>
        </div>
    );
};

export default QuizzesPage;
