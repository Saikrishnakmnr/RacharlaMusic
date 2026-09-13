def validate_audio(audio_bytes: bytes) -> bool:
    if not audio_bytes or len(audio_bytes) < 44:
        return False
    return audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE'
