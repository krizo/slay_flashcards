from services.audio_service import GTTSAudioService, SilentAudioService


def test_silent_audio_service_always_succeeds():
    """Test that silent audio service always returns True."""
    service = SilentAudioService()
    assert service.play_text("hello") is True
    assert service.play_text("bonjour", "fr") is True
    assert service.play_text("") is True


def test_gtts_audio_service_creation():
    """Test GTTS audio service can be created."""
    service = GTTSAudioService()
    assert service is not None
    assert not service._pygame_initialized


def test_gtts_audio_service_with_text():
    service = GTTSAudioService()
    # Should not crash with empty text
    result = service.play_text("chien", 'fr')
    # Result might be True or False depending on gTTS behavior, but shouldn't crash
    assert isinstance(result, bool)
