from .base import BaseMusicProvider, GenerationResult
from audio.wav import synthesize_song

import hashlib


class LocalFallbackProvider(BaseMusicProvider):

    name = "RacharlaMusic Local Music Engine"

    def generate(
        self,
        lyrics: str,
        style_prompt: str,
        seed: int,
        duration_sec: float = 30.0,
        vocal: str = "Natural lead",
        title: str = "RacharlaMusic Song",
        language: str = "Telugu",
        direction: str = "",
    ) -> GenerationResult:

        try:

            if not lyrics.strip():
                return GenerationResult(
                    ok=False,
                    message="Lyrics are empty.",
                    provider=self.name,
                )

            duration_sec = max(
                1.0,
                float(duration_sec),
            )

            song_data = (
                f"{title}|"
                f"{lyrics}|"
                f"{style_prompt}|"
                f"{vocal}|"
                f"{language}|"
                f"{direction}|"
                f"{seed}"
            )

            digest = hashlib.sha256(
                song_data.encode("utf-8")
            ).hexdigest()

            final_seed = int(
                digest[:16],
                16,
            )

            audio = synthesize_song(
                lyrics=lyrics,
                style=style_prompt,
                vocal=vocal,
                duration_seconds=duration_sec,
                seed=final_seed,
            )

            return GenerationResult(
                ok=True,
                audio_bytes=audio,
                mime="audio/wav",
                extension="wav",
                message=(
                    f"Generated {int(duration_sec)} "
                    "seconds of music."
                ),
                provider=self.name,
            )

        except Exception as exc:

            return GenerationResult(
                ok=False,
                message=f"Generation failed: {exc}",
                provider=self.name,
            )
