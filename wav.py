import io
import math
import random
import re
import struct
import wave

SAMPLE_RATE = 22050

STYLE = {
    "Melody":      (104, [261.63, 293.66, 329.63, 392.00, 440.00], 0.70, 0.18),
    "Romantic":    (78,  [220.00, 261.63, 293.66, 329.63, 392.00], 0.56, 0.13),
    "Folk":        (112, [196.00, 220.00, 246.94, 293.66, 329.63], 0.72, 0.22),
    "Mass":        (126, [146.83, 174.61, 196.00, 220.00, 261.63], 0.82, 0.26),
    "Sad":         (72,  [220.00, 246.94, 261.63, 311.13, 349.23], 0.48, 0.10),
    "Cinematic":   (86,  [174.61, 196.00, 220.00, 261.63, 329.63], 0.66, 0.20),
    "Lo-fi":       (82,  [196.00, 220.00, 246.94, 293.66, 329.63], 0.52, 0.11),
    "Devotional":  (68,  [261.63, 293.66, 329.63, 392.00, 440.00], 0.50, 0.10),
    "Hip-hop":     (92,  [130.81, 146.83, 164.81, 196.00, 220.00], 0.76, 0.24),
    "Rock":        (118, [164.81, 196.00, 220.00, 246.94, 293.66], 0.78, 0.30),
    "Pop":         (108, [246.94, 277.18, 329.63, 369.99, 440.00], 0.68, 0.19),
}


def _clean_lines(lyrics):
    out = []
    for raw in str(lyrics).splitlines():
        s = re.sub(r"\[[^\]]+\]", "", raw).strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out or ["RacharlaMusic"]


def _char_value(text):
    # Works for Telugu, English and mixed Unicode text.
    return sum((ord(c) * (i + 1)) for i, c in enumerate(text))


def _sections(lines, count):
    # Every lyric line gets its own evolving melodic phrase. This is the key fix
    # for the previous "same music for every lyrics" behaviour.
    values = []
    for i in range(count):
        line = lines[i % len(lines)]
        values.append((_char_value(line) + i * 7919) & 0x7fffffff)
    return values


def synthesize_song(lyrics, style, seed, duration_sec=60.0, vocal="Natural lead"):
    duration_sec = max(10.0, min(360.0, float(duration_sec)))
    bpm, scale, lead_gain, drum_gain = STYLE.get(style, STYLE["Melody"])
    rng = random.Random(int(seed))
    lines = _clean_lines(lyrics)

    # Use a lower internal render rate for long tracks, keeping CPU/memory safe
    # on Streamlit Community Cloud while preserving browser-playable quality.
    sr = SAMPLE_RATE
    total = int(sr * duration_sec)
    beat_sec = 60.0 / bpm
    phrase_beats = 8
    phrase_sec = beat_sec * phrase_beats
    phrase_count = max(1, math.ceil(duration_sec / phrase_sec))
    phrase_seeds = _sections(lines, phrase_count)

    # Pre-plan note sequences per phrase; no random calls inside every sample.
    phrases = []
    for p in range(phrase_count):
        r = random.Random(seed + phrase_seeds[p])
        notes = []
        for step in range(16):
            idx = (r.randrange(len(scale)) + step + (phrase_seeds[p] % 3)) % len(scale)
            octv = 1.0 if (step % 8 not in (3, 7) and style not in ("Mass", "Rock")) else 0.5
            notes.append(scale[idx] * octv)
        phrases.append(notes)

    # A compact chord progression, transposed by the lyric-derived phrase seed.
    chord_roots = [0, 2, 4, 1]
    frames = bytearray(total * 2)

    # Block rendering avoids huge Python object allocations.
    block = 4096
    for start in range(0, total, block):
        end = min(total, start + block)
        for i in range(start, end):
            t = i / sr
            beat = t / beat_sec
            phrase = min(phrase_count - 1, int(t / phrase_sec))
            local_beat = beat % phrase_beats
            step = int(local_beat * 2.0) % 16
            pseed = phrase_seeds[phrase]

            # Slowly changing accompaniment.
            chord_idx = (int(beat / 2.0) + (pseed % 4)) % 4
            root = scale[chord_roots[chord_idx] % len(scale)] * 0.5
            bass = math.sin(2 * math.pi * root * t) * 0.20
            fifth = math.sin(2 * math.pi * root * 1.5 * t) * 0.055

            # Lyric-specific lead phrase.
            semitone = phrases[phrase][step]
            base = scale[0]
            note = base * (2.0 ** (semitone / 12.0))
            local = (local_beat * 2.0) % 1.0
            env = math.sin(math.pi * max(0.0, min(1.0, local))) ** 0.8
            vibrato = 1.0 + 0.0035 * math.sin(2 * math.pi * 5.2 * t)
            lead = math.sin(2 * math.pi * note * vibrato * t) * lead_gain * 0.42 * env
            lead += math.sin(2 * math.pi * note * 2.0 * t) * lead_gain * 0.07 * env

            # Style-dependent rhythm.
            frac = beat % 1.0
            kick = 0.0
            snare = 0.0
            hat = 0.0
            if frac < 0.12:
                e = math.exp(-frac * 28.0)
                kick = math.sin(2 * math.pi * (82.0 - 42.0 * frac) * t) * drum_gain * 0.60 * e
            if 0.48 < frac < 0.62:
                e = math.exp(-(frac - 0.48) * 35.0)
                snare = math.sin(2 * math.pi * 1800.0 * t) * drum_gain * 0.07 * e
            if style in ("Hip-hop", "Pop", "Rock", "Mass", "Folk", "Lo-fi"):
                hp = (t * bpm / 60.0 * 2.0) % 1.0
                if hp < 0.08:
                    hat = math.sin(2 * math.pi * 6200.0 * t) * 0.025 * drum_gain * math.exp(-hp * 35.0)

            # Tiny deterministic ambience changes between lyric phrases.
            air = math.sin(2 * math.pi * (0.18 + (pseed % 17) * 0.01) * t) * 0.012
            x = bass + fifth + lead + kick + snare + hat + air

            # Fade only at song boundaries.
            fade_in = min(1.0, t / 0.7)
            fade_out = min(1.0, (duration_sec - t) / 1.0)
            x *= max(0.0, min(fade_in, fade_out))
            x = max(-0.96, min(0.96, x))
            struct.pack_into("<h", frames, i * 2, int(x * 32767))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(frames)
    return buf.getvalue()
