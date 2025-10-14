import { expect } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';
import '@testing-library/jest-dom';
import i18n from './src/i18n/i18n';


// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Initialize i18n for tests with English as default
// This makes pre-existing tests work while new i18n tests explicitly set their language
i18n.changeLanguage('en');

// Mock ResizeObserver for Recharts tests
global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
};
