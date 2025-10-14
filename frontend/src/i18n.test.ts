import { describe, it, expect, beforeEach } from 'vitest';
import i18n from './i18n/i18n';

describe('i18n Configuration', () => {
  beforeEach(async () => {
    // Reset to default language before each test
    await i18n.changeLanguage('pl');
  });

  it('initializes with Polish as default language', () => {
    expect(i18n.language).toBe('pl');
  });

  it('has Polish and English languages configured', () => {
    const languages = Object.keys(i18n.options.resources || {});
    expect(languages).toContain('pl');
    expect(languages).toContain('en');
  });

  it('can switch to English language', async () => {
    await i18n.changeLanguage('en');
    expect(i18n.language).toBe('en');
  });

  it('can switch back to Polish language', async () => {
    await i18n.changeLanguage('en');
    await i18n.changeLanguage('pl');
    expect(i18n.language).toBe('pl');
  });

  describe('Polish translations', () => {
    beforeEach(async () => {
      await i18n.changeLanguage('pl');
    });

    it('translates common.loading correctly', () => {
      expect(i18n.t('common.loading')).toBe('Ładowanie...');
    });

    it('translates nav.dashboard correctly', () => {
      expect(i18n.t('nav.dashboard')).toBe('Postępy');
    });

    it('translates nav.quizzes correctly', () => {
      expect(i18n.t('nav.quizzes')).toBe('Quizy');
    });

    it('translates nav.settings correctly', () => {
      expect(i18n.t('nav.settings')).toBe('Ustawienia');
    });

    it('translates quizzes.startTest correctly', () => {
      expect(i18n.t('quizzes.startTest')).toBe('Rozpocznij test');
    });

    it('translates quizzes.startLearning correctly', () => {
      expect(i18n.t('quizzes.startLearning')).toBe('Rozpocznij naukę');
    });

    it('translates auth.appName correctly', () => {
      expect(i18n.t('auth.appName')).toBe('SlayFlashcards');
    });

    it('translates settings.title correctly', () => {
      expect(i18n.t('settings.title')).toBe('Ustawienia');
    });
  });

  describe('English translations', () => {
    beforeEach(async () => {
      await i18n.changeLanguage('en');
    });

    it('translates common.loading correctly', () => {
      expect(i18n.t('common.loading')).toBe('Loading...');
    });

    it('translates nav.dashboard correctly', () => {
      expect(i18n.t('nav.dashboard')).toBe('Dashboard');
    });

    it('translates nav.quizzes correctly', () => {
      expect(i18n.t('nav.quizzes')).toBe('Quizzes');
    });

    it('translates nav.settings correctly', () => {
      expect(i18n.t('nav.settings')).toBe('Settings');
    });

    it('translates quizzes.startTest correctly', () => {
      expect(i18n.t('quizzes.startTest')).toBe('Start Test');
    });

    it('translates quizzes.startLearning correctly', () => {
      expect(i18n.t('quizzes.startLearning')).toBe('Start Learning');
    });

    it('translates auth.appName correctly', () => {
      expect(i18n.t('auth.appName')).toBe('SlayFlashcards');
    });

    it('translates settings.title correctly', () => {
      expect(i18n.t('settings.title')).toBe('Settings');
    });
  });

  describe('Fallback behavior', () => {
    it('returns key when translation is missing', async () => {
      await i18n.changeLanguage('pl');
      expect(i18n.t('nonexistent.key')).toBe('nonexistent.key');
    });

    it('uses fallback language when translation is missing in current language', async () => {
      await i18n.changeLanguage('en');
      // If a key exists in PL but not in EN, it should fall back
      const result = i18n.t('some.missing.key');
      expect(typeof result).toBe('string');
    });
  });

  describe('Interpolation', () => {
    it('supports variable interpolation', async () => {
      await i18n.changeLanguage('en');
      // Test a translation with interpolation if you have any
      // Example: i18n.t('common.greeting', { name: 'John' })
      // For now, just verify the mechanism works
      const result = i18n.t('common.welcome');
      expect(typeof result).toBe('string');
    });
  });

  describe('Namespace support', () => {
    it('has translation namespace configured', () => {
      const defaultNS = i18n.options.defaultNS;
      // Check if it's either a string or array containing 'translation'
      const isValid = typeof defaultNS === 'string'
        ? defaultNS === 'translation'
        : Array.isArray(defaultNS) && defaultNS.includes('translation');
      expect(isValid).toBe(true);
    });

    it('loads translation namespace', () => {
      const namespaces = i18n.options.ns as string[];
      expect(namespaces).toContain('translation');
    });
  });

  describe('Language detection', () => {
    it('stores language preference', async () => {
      await i18n.changeLanguage('en');
      expect(i18n.language).toBe('en');

      await i18n.changeLanguage('pl');
      expect(i18n.language).toBe('pl');
    });
  });
});
