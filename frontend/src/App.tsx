import React from 'react';
import FlashcardComponent from './components/FlashcardComponent';
import { FlashcardData } from './types';

/**
 * Example flashcard data for testing the component
 * This matches the FlashcardData interface with realistic sample content
 */
const exampleFlashcardData: FlashcardData = {
  id: 1,
  quiz_id: 10,
  question: {
    title: 'What is React?',
    text: 'Explain what React is and its main purpose in web development and modern software engineering practices.',
    lang: 'en',
    difficulty: 3,
    emoji: '⚛️',
    image: null,
  },
  answer: {
    text: 'React is a JavaScript library for building user interfaces, particularly single-page applications where you need a fast, interactive user experience. It uses a component-based architecture that makes it easy to build and maintain complex UIs. React also features a virtual DOM for efficient rendering, unidirectional data flow for predictable state management, and a rich ecosystem of tools and libraries. Companies like Facebook, Instagram, Netflix, and Airbnb use React in production for millions of users worldwide.',
    lang: 'en',
    type: 'text',
    options: null,
    metadata: null,
  },
};

function App() {
  return (
    <div className="App">
      <FlashcardComponent flashcardData={exampleFlashcardData} />
    </div>
  );
}

export default App;
