from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationResult:
    ok: bool
    audio_bytes: Optional[bytes] = None
    mime: str = "audio/wav"
    extension: str = "wav"
    message: str = ""
    provider: str = ""


class BaseMusicProvider:
    name = "Base Music Provider"

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
        raise NotImplementedError
