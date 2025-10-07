/**
 * Audio utility functions for Text-to-Speech playback
 * Uses Web Speech API (SpeechSynthesis)
 */

/**
 * Play text using browser's Text-to-Speech
 * @param text - Text to speak
 * @param lang - Language code (e.g., 'en', 'fr', 'es')
 */
export const playAudio = (text: string, lang: string | null): void => {
    if (!text || text.trim() === '') {
        console.warn('playAudio: No text provided');
        return;
    }

    // Check if browser supports Speech Synthesis
    if (!('speechSynthesis' in window)) {
        console.error('Speech Synthesis not supported in this browser');
        alert('Text-to-speech is not supported in your browser');
        return;
    }

    try {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        // Create speech utterance
        const utterance = new SpeechSynthesisUtterance(text);

        // Set language if provided
        if (lang) {
            utterance.lang = lang;
        }

        // Optional: Set voice properties
        utterance.rate = 0.9; // Slightly slower for better comprehension
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Speak the text
        window.speechSynthesis.speak(utterance);
    } catch (error) {
        console.error('Error playing audio:', error);
        alert('Failed to play audio');
    }
};

/**
 * Stop any currently playing audio
 */
export const stopAudio = (): void => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
};

/**
 * Check if audio/TTS is available
 */
export const isAudioAvailable = (): boolean => {
    return 'speechSynthesis' in window;
};
