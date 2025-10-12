import { expect } from 'vitest';
import * as matchers from '@testing-library/jest-dom/matchers';
import '@testing-library/jest-dom';


// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Mock ResizeObserver for Recharts tests
global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
};
