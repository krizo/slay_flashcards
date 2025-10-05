import os
import tempfile
from abc import ABC, abstractmethod

import pygame  # pylint: disable=import-error
from gtts import gTTS  # pylint: disable=import-error


class AudioServiceInterface(ABC):
    """Abstract interface for audio services."""

    @abstractmethod
    def play_text(self, text: str, lang: str = "en") -> bool:
        """Play text as speech. Returns True if successful."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if audio service is available."""


class GTTSAudioService(AudioServiceInterface):
    """Google Text-to-Speech audio service implementation."""

    def __init__(self):
        self._pygame_initialized = False

    def _init_pygame(self) -> None:
        """Initialize pygame mixer if not already done."""
        if not self._pygame_initialized:
            pygame.mixer.init()
            self._pygame_initialized = True

    def is_available(self) -> bool:
        """Check if GTTS and pygame are available."""
        try:
            # Test if we can create a TTS object
            gTTS(text="test", lang="en", slow=False)
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def play_text(self, text: str, lang: str = "en") -> bool:
        """Play text using Google TTS and pygame."""
        try:
            self._init_pygame()

            # Create TTS
            tts = gTTS(text=text, lang=lang, slow=False)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)

                # Play audio
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

                # Clean up
                os.unlink(tmp_file.name)
                return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Audio playback failed: {e}")
            return False
        finally:
            if self._pygame_initialized:
                pygame.mixer.quit()
                self._pygame_initialized = False

    def __del__(self):
        """Cleanup pygame on destruction."""
        if hasattr(self, "_pygame_initialized") and self._pygame_initialized:
            pygame.mixer.quit()


class SilentAudioService(AudioServiceInterface):
    """Silent audio service for when audio is disabled."""

    def is_available(self) -> bool:
        """Silent service is always available."""
        return True

    def play_text(self, text: str, lang: str = "en") -> bool:
        """No-op implementation."""
        return True
