export type AnswerType = 'text' | 'integer' | 'float' | 'range' | 'boolean' | 'choice' | 'multiple_choice' | 'short_text';

export type FlashcardMode = 'learn' | 'test';

export interface QuestionData {
    title: string;
    text: string;
    lang?: string | null;
    difficulty: number;
    emoji: string;
    image: string | null;
}

export interface AnswerData {
    text: string;
    lang?: string | null;
    type: AnswerType;
    options: string[] | null;
    metadata: Record<string, any> | null;
}

export interface FlashcardData {
    id: number;
    quiz_id: number;
    question: QuestionData;
    answer: AnswerData;
}
