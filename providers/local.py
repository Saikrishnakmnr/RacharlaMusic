import math
import struct
import io
import random
from .base import BaseMusicProvider

class LocalFallbackProvider(BaseMusicProvider):
    def generate(self, lyrics: str, style_prompt: str, seed: int, duration_sec: float = 30.0) -> tuple[bytes, str]:
        sample_rate = 22050
        num_samples = int(sample_rate * duration_sec)
        
        # Use lyrics content and seed to create unique melody patterns per song
        lyrics_hash = sum(ord(c) for c in lyrics) if lyrics else 0
        combined_seed = seed + lyrics_hash
        random.seed(combined_seed)
        
        scale = [0, 2, 3, 5, 7, 8, 10]
        buffer = io.BytesIO()
        import wave
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                beat = t * 2.0
                sub_beat = beat % 1.0
                
                variation = (combined_seed % 7) * 5.0
                
                kick = 0.0
                if sub_beat < 0.15:
                    kick_env = math.exp(-sub_beat * 15.0)
                    kick = math.sin(2 * math.pi * (110 + variation - sub_beat * 400) * t) * kick_env * 0.5
                
                hihat_sub = (t * 8.0) % 1.0
                hihat = (random.random() * 2 - 1) * math.exp(-hihat_sub * 30.0) * 0.1 if (int(t * 8.0) % 2 == 0) else 0.0
                
                chord_idx = int(t / 2.0) % 4
                base_notes = [98.0 + variation, 130.81, 146.83, 123.47]
                bass_freq = base_notes[chord_idx % len(base_notes)]
                bass = math.sin(2 * math.pi * bass_freq * t) * 0.3 * (1.0 - (t % 0.5))
                
                melody_note_idx = int(t * 4.0 + combined_seed) % len(scale)
                note_freq = bass_freq * (2.0 ** (scale[melody_note_idx] / 12.0))
                lead = math.sin(2 * math.pi * note_freq * t) * 0.2 * math.sin(math.pi * (t * 4.0 % 1.0))
                
                mixed = max(-1.0, min(1.0, kick + hihat + bass + lead))
                frames.extend(struct.pack('<h', int(mixed * 32767)))
                
            wav_file.writeframes(frames)
        return buffer.getvalue(), "RacharlaMusic Dynamic Synthesizer"
