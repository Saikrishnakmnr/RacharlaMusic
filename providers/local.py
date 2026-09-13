import math
import struct
import io
import random
from .base import BaseMusicProvider

class LocalFallbackProvider(BaseMusicProvider):
    def generate(self, lyrics: str, style_prompt: str, seed: int, duration_sec: float = 30.0) -> tuple[bytes, str]:
        sample_rate = 22050
        num_samples = int(sample_rate * duration_sec)
        
        # 1. Unique seed & variation based on lyrics content so every song is different
        lyrics_hash = sum(ord(c) for c in lyrics) if lyrics else 0
        combined_seed = seed + lyrics_hash
        random.seed(combined_seed)
        
        # Scale presets based on style prompt
        if "Sad" in style_prompt or "Melodic" in style_prompt:
            scale = [0, 2, 3, 5, 7, 8, 10] # Minor/Emotional
        else:
            scale = [0, 2, 4, 5, 7, 9, 11] # Major/Upbeat
            
        buffer = io.BytesIO()
        import wave
        
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            frames = bytearray()
            variation = (combined_seed % 7) * 4.0
            
            for i in range(num_samples):
                t = i / sample_rate
                
                # Song Structure Progression (Intro -> Verse -> Chorus -> Outro)
                progress = t / duration_sec
                section_factor = 0.5 + 0.5 * math.sin(progress * math.pi * 4)
                
                beat = t * 2.2
                sub_beat = beat % 1.0
                
                # Kick Drum (Punchier in chorus sections)
                kick = 0.0
                if sub_beat < 0.2:
                    kick_env = math.exp(-sub_beat * 12.0)
                    kick = math.sin(2 * math.pi * (100 + variation - sub_beat * 300) * t) * kick_env * (0.4 + 0.2 * section_factor)
                
                # Hi-Hat
                hihat_sub = (t * 8.0) % 1.0
                hihat = (random.random() * 2 - 1) * math.exp(-hihat_sub * 25.0) * 0.08 if (int(t * 8.0) % 2 == 0) else 0.0
                
                # Bassline
                chord_idx = int(t / 3.0) % 4
                base_notes = [87.31 + variation, 116.54, 130.81, 98.00]
                bass_freq = base_notes[chord_idx % len(base_notes)]
                bass = math.sin(2 * math.pi * bass_freq * t) * 0.25 * (0.8 + 0.2 * math.sin(t * math.pi))
                
                # Lead Melody (Changes per lyric text)
                melody_note_idx = int(t * 3.0 + combined_seed) % len(scale)
                note_freq = bass_freq * (2.0 ** (scale[melody_note_idx] / 12.0))
                lead = math.sin(2 * math.pi * note_freq * t) * 0.18 * math.sin(math.pi * (t * 3.0 % 1.0))
                
                # Vocal-like formant simulation layer (adds singing resonance frequencies)
                vocal_formant = math.sin(2 * math.pi * (note_freq * 2.0) * t + math.sin(t * 2.0)) * 0.08 * section_factor
                
                mixed = max(-1.0, min(1.0, kick + hihat + bass + lead + vocal_formant))
                frames.extend(struct.pack('<h', int(mixed * 32767)))
                
            wav_file.writeframes(frames)
            
        return buffer.getvalue(), "RacharlaMusic Dynamic Synthesizer"
