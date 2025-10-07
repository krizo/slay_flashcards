import { useState } from 'react';
import FlashcardComponent from './components/FlashcardComponent';
import { FlashcardData } from './types';

/**
 * Example quiz session with multiple flashcards
 */
const quizFlashcards: FlashcardData[] = [
  {
    id: 1,
    quiz_id: 4,
    question: {
      title: 'What is React?',
      text: 'Explain what React is and its main purpose in web development.',
      lang: 'en',
      difficulty: 3,
      emoji: '⚛️',
      image: null,
    },
    answer: {
      text: 'React is a JavaScript library for building user interfaces, particularly single-page applications where you need a fast, interactive user experience. It uses a component-based architecture that makes it easy to build and maintain complex UIs.',
      lang: 'en',
      type: 'text',
      options: null,
      metadata: null,
    },
  },
  {
    id: 2,
    quiz_id: 4,
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
      type: 'text',
      options: null,
      metadata: null,
    },
  },
  {
    id: 3,
    quiz_id: 4,
    question: {
      title: 'TypeScript Benefits',
      text: 'Name two key benefits of using TypeScript over JavaScript.',
      lang: 'en',
      difficulty: 2,
      emoji: '📘',
      image: null,
    },
    answer: {
      text: 'Type safety and better IDE support with autocomplete and error detection during development.',
      lang: 'en',
      type: 'text',
      options: null,
      metadata: null,
    },
  },
  {
    id: 4,
    quiz_id: 4,
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
      metadata: { tolerance: 0 },
    },
  },
];

function App() {
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState<number>(0);

  // Handle moving to next flashcard
  const handleNextFlashcard = () => {
    setCurrentFlashcardIndex((prevIndex) => {
      // Cycle back to start when reaching the end
      return (prevIndex + 1) % quizFlashcards.length;
    });
  };

  // Get current flashcard
  const currentFlashcard = quizFlashcards[currentFlashcardIndex];

  return (
    <div className="App">
      <FlashcardComponent
        flashcardData={currentFlashcard}
        mode="learn"
        onNextFlashcard={handleNextFlashcard}
      />
    </div>
  );
}

export default App;
