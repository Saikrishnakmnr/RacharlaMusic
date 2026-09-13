class BaseMusicProvider:
    def generate(self, lyrics: str, style_prompt: str, seed: int) -> tuple[bytes, str]:
        raise NotImplementedError
