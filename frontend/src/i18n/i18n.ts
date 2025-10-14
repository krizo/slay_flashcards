import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from './locales/en.json';
import plTranslations from './locales/pl.json';

const resources = {
    en: {
        translation: enTranslations
    },
    pl: {
        translation: plTranslations
    }
};

i18n
    .use(LanguageDetector) // Detect user language from browser
    .use(initReactI18next) // Pass i18n instance to react-i18next
    .init({
        resources,
        fallbackLng: 'pl', // Fallback language if translation not found
        debug: false, // Set to true for development debugging

        interpolation: {
            escapeValue: false // React already escapes values
        },

        // Language detection options
        detection: {
            order: ['localStorage', 'navigator'], // Check localStorage first, then browser language
            caches: ['localStorage'], // Cache selected language in localStorage
            lookupLocalStorage: 'i18nextLng'
        }
    });

export default i18n;
