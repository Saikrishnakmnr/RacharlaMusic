from .base import BaseMusicProvider, GenerationResult
from audio.wav import synthesize_song

class LocalFallbackProvider(BaseMusicProvider):
    """Reliable CPU-only fallback. No API key, external GPU, or network call."""
    name = "RacharlaMusic Independent Local Synthesizer"

    def generate(self, lyrics: str, style_prompt: str, seed: int,
                 duration_sec: float = 60.0, vocal: str = "Natural lead",
                 title: str = "RacharlaMusic Song", language: str = "Telugu") -> GenerationResult:
        try:
            audio = synthesize_song(
                lyrics=lyrics or title,
                style=style_prompt,
                seed=seed,
                duration_sec=float(duration_sec),
                vocal=vocal,
            )
            return GenerationResult(True, audio, "audio/wav", "wav",
                                    f"Generated {duration_sec:.0f}s locally on CPU.", self.name)
        except Exception as exc:
            return GenerationResult(False, None, "audio/wav", "wav",
                                    f"Local generation failed: {exc}", self.name)
