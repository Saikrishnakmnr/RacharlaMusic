def local_free_lyrics(theme: str, language: str, style: str) -> str:
    return f"""[Verse 1]
Walking through the glowing night in {theme}
Every shadow whispers your name softly
Rhythm of the heartbeats echoing deep
Promises we swore we never would break

[Chorus]
Oh, let the music flow through the night
Guiding every step under neon light
Nothing can stop us when the melody plays
Forever in this moment, through all our days
"""

def normalize_sections(text: str) -> str:
    return text.strip()
