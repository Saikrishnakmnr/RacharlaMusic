import io
import math
import random
import wave
from array import array


SAMPLE_RATE = 16000


STYLE_SETTINGS = {
    "Melody": {
        "bpm": 92,
        "root": 261.63,
        "brightness": 0.75,
        "drums": 0.45,
    },
    "Romantic": {
        "bpm": 76,
        "root": 220.00,
        "brightness": 0.62,
        "drums": 0.20,
    },
    "Folk": {
        "bpm": 104,
        "root": 196.00,
        "brightness": 0.80,
        "drums": 0.65,
    },
    "Mass": {
        "bpm": 112,
        "root": 146.83,
        "brightness": 0.85,
        "drums": 0.90,
    },
    "Sad": {
        "bpm": 70,
        "root": 220.00,
        "brightness": 0.48,
        "drums": 0.15,
    },
    "Cinematic": {
        "bpm": 82,
        "root": 174.61,
        "brightness": 0.72,
        "drums": 0.35,
    },
    "Lo-fi": {
        "bpm": 78,
        "root": 196.00,
        "brightness": 0.45,
        "drums": 0.25,
    },
    "Devotional": {
        "bpm": 72,
        "root": 261.63,
        "brightness": 0.65,
        "drums": 0.18,
    },
    "Hip-hop": {
        "bpm": 88,
        "root": 130.81,
        "brightness": 0.65,
        "drums": 0.95,
    },
    "Rock": {
        "bpm": 116,
        "root": 164.81,
        "brightness": 0.88,
        "drums": 0.95,
    },
    "Pop": {
        "bpm": 108,
        "root": 246.94,
        "brightness": 0.78,
        "drums": 0.72,
    },
}


MAJOR_INTERVALS = [
    0,
    2,
    4,
    5,
    7,
    9,
    11,
]

MINOR_INTERVALS = [
    0,
    2,
    3,
    5,
    7,
    8,
    10,
]


def midi_to_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def hz_from_root(root, semitone):
    return root * (2.0 ** (semitone / 12.0))


def smooth_envelope(position, length, attack=0.04, release=0.08):
    if length <= 0:
        return 0.0

    t = position / length

    if t < attack:
        return t / attack

    if t > 1.0 - release:
        return max(
            0.0,
            (1.0 - t) / release,
        )

    return 1.0


def add_voice(
    samples,
    start,
    length,
    frequency,
    amplitude,
    waveform="sine",
):
    end = min(
        len(samples),
        start + length,
    )

    if end <= start:
        return

    phase = 0.0

    for i in range(start, end):

        local = i - start

        env = smooth_envelope(
            local,
            length,
            attack=0.08,
            release=0.14,
        )

        phase = (
            2.0
            * math.pi
            * frequency
            * local
            / SAMPLE_RATE
        )

        if waveform == "soft":

            value = (
                0.72 * math.sin(phase)
                + 0.20 * math.sin(phase * 2.0)
                + 0.08 * math.sin(phase * 3.0)
            )

        elif waveform == "warm":

            value = (
                0.58 * math.sin(phase)
                + 0.27 * math.sin(phase * 2.0)
                + 0.10 * math.sin(phase * 3.0)
                + 0.05 * math.sin(phase * 4.0)
            )

        else:

            value = math.sin(phase)

        samples[i] += (
            value
            * amplitude
            * env
        )


def add_bass(
    samples,
    start,
    length,
    frequency,
    amplitude,
):
    end = min(
        len(samples),
        start + length,
    )

    for i in range(start, end):

        local = i - start

        env = smooth_envelope(
            local,
            length,
            attack=0.02,
            release=0.18,
        )

        phase = (
            2.0
            * math.pi
            * frequency
            * local
            / SAMPLE_RATE
        )

        value = (
            0.78 * math.sin(phase)
            + 0.18 * math.sin(phase * 2.0)
            + 0.04 * math.sin(phase * 3.0)
        )

        samples[i] += (
            value
            * amplitude
            * env
        )


def add_kick(
    samples,
    start,
    amplitude,
):
    length = int(
        SAMPLE_RATE * 0.20
    )

    end = min(
        len(samples),
        start + length,
    )

    for i in range(start, end):

        local = i - start

        t = local / SAMPLE_RATE

        env = math.exp(
            -18.0 * t
        )

        frequency = (
            125.0
            - 75.0 * min(
                1.0,
                t * 5.0,
            )
        )

        phase = (
            2.0
            * math.pi
            * frequency
            * t
        )

        samples[i] += (
            math.sin(phase)
            * env
            * amplitude
        )


def add_snare(
    samples,
    start,
    rng,
    amplitude,
):
    length = int(
        SAMPLE_RATE * 0.16
    )

    end = min(
        len(samples),
        start + length,
    )

    for i in range(start, end):

        local = i - start

        t = local / SAMPLE_RATE

        env = math.exp(
            -24.0 * t
        )

        noise = (
            rng.random() * 2.0
            - 1.0
        )

        body = math.sin(
            2.0
            * math.pi
            * 180.0
            * t
        )

        samples[i] += (
            (
                noise * 0.72
                + body * 0.28
            )
            * env
            * amplitude
        )


def add_hat(
    samples,
    start,
    rng,
    amplitude,
):
    length = int(
        SAMPLE_RATE * 0.055
    )

    end = min(
        len(samples),
        start + length,
    )

    for i in range(start, end):

        local = i - start

        t = local / SAMPLE_RATE

        env = math.exp(
            -70.0 * t
        )

        noise = (
            rng.random() * 2.0
            - 1.0
        )

        samples[i] += (
            noise
            * env
            * amplitude
        )


def clean_lyrics(lyrics):
    lines = []

    for raw in lyrics.splitlines():

        line = raw.strip()

        if not line:
            continue

        # Ignore [Verse], [Chorus], etc.
        if (
            line.startswith("[")
            and line.endswith("]")
        ):
            continue

        lines.append(line)

    return lines


def make_melody_notes(
    lyrics,
    seed,
    scale,
):
    """
    Converts actual lyric content into a deterministic
    but musical note pattern.

    Different lyrics therefore produce different melodies.
    """

    rng = random.Random(seed)

    lines = clean_lyrics(lyrics)

    if not lines:
        lines = [
            "RacharlaMusic melody"
        ]

    notes = []

    for line_index, line in enumerate(lines):

        # Hash the actual line.
        line_value = sum(
            ord(ch)
            for ch in line
        )

        local_seed = (
            seed
            + line_value
            + line_index * 7919
        )

        local_rng = random.Random(
            local_seed
        )

        # Number of notes depends on lyric length.
        count = max(
            4,
            min(
                12,
                len(line) // 7 + 3,
            ),
        )

        phrase = []

        for note_index in range(count):

            # Favor stable scale degrees.
            candidates = [
                0,
                1,
                2,
                3,
                4,
                5,
                6,
            ]

            degree = local_rng.choice(
                candidates
            )

            octave = local_rng.choice(
                [0, 0, 1]
            )

            interval = (
                scale[degree]
                + 12 * octave
            )

            phrase.append(
                interval
            )

        # Make phrase ending more musical.
        phrase[-1] = local_rng.choice(
            [0, 4, 7, 12]
        )

        notes.extend(phrase)

    # Small global variation.
    rng.shuffle(
        notes
    )

    return notes


def synthesize_song(
    lyrics,
    style,
    vocal,
    duration_seconds,
    seed,
):
    """
    CPU-only musical backing generator.

    IMPORTANT:
    This is NOT a neural singing model.
    It creates a musical instrumental track.
    """

    duration_seconds = max(
        1.0,
        float(duration_seconds),
    )

    total_samples = int(
        SAMPLE_RATE
        * duration_seconds
    )

    samples = [0.0] * total_samples

    settings = STYLE_SETTINGS.get(
        style,
        STYLE_SETTINGS["Melody"],
    )

    bpm = settings["bpm"]
    root = settings["root"]
    brightness = settings["brightness"]
    drum_level = settings["drums"]

    # Determine major/minor feeling.
    minor_styles = {
        "Sad",
        "Romantic",
        "Lo-fi",
    }

    if style in minor_styles:
        scale = MINOR_INTERVALS
    else:
        scale = MAJOR_INTERVALS

    # Seeded random generator.
    rng = random.Random(
        seed
    )

    # Musical timing.
    beat_seconds = (
        60.0 / bpm
    )

    bar_seconds = (
        beat_seconds * 4.0
    )

    # --------------------------------------------------------
    # Chord progression
    # --------------------------------------------------------

    if style in {
        "Sad",
        "Romantic",
        "Lo-fi",
    }:
        progression = [
            [0, 3, 7],
            [8, 0, 3],
            [5, 0, 3],
            [10, 2, 5],
        ]
    else:
        progression = [
            [0, 4, 7],
            [5, 9, 0],
            [3, 7, 10],
            [4, 7, 11],
        ]

    # --------------------------------------------------------
    # Melody based on actual lyrics
    # --------------------------------------------------------

    melody_notes = make_melody_notes(
        lyrics,
        seed,
        scale,
    )

    melody_index = 0

    # --------------------------------------------------------
    # Chord / section loop
    # --------------------------------------------------------

    bar = 0

    while (
        bar * bar_seconds
        < duration_seconds
    ):

        chord = progression[
            bar % len(progression)
        ]

        chord_start = int(
            bar
            * bar_seconds
            * SAMPLE_RATE
        )

        chord_length = int(
            bar_seconds
            * SAMPLE_RATE
        )

        # Every fourth bar has slightly different intensity.
        section = bar % 8

        if section in {4, 5, 6, 7}:
            chord_amp = 0.075
        else:
            chord_amp = 0.055

        # ----------------------------------------------------
        # Pad/chord
        # ----------------------------------------------------

        for interval in chord:

            freq = hz_from_root(
                root,
                interval,
            )

            add_voice(
                samples,
                chord_start,
                chord_length,
                freq,
                chord_amp,
                waveform="warm",
            )

        # ----------------------------------------------------
        # Bass
        # ----------------------------------------------------

        bass_root = hz_from_root(
            root / 2.0,
            chord[0],
        )

        for beat in range(4):

            start_time = (
                bar * bar_seconds
                + beat * beat_seconds
            )

            if start_time >= duration_seconds:
                break

            start = int(
                start_time
                * SAMPLE_RATE
            )

            length = int(
                beat_seconds
                * 0.90
                * SAMPLE_RATE
            )

            add_bass(
                samples,
                start,
                length,
                bass_root,
                0.10,
            )

        # ----------------------------------------------------
        # Lead melody
        # ----------------------------------------------------

        for beat in range(4):

            start_time = (
                bar * bar_seconds
                + beat * beat_seconds
            )

            if start_time >= duration_seconds:
                break

            note_value = melody_notes[
                melody_index
                % len(melody_notes)
            ]

            melody_index += 1

            # Keep melody in a pleasant register.
            freq = hz_from_root(
                root,
                note_value + 12,
            )

            start = int(
                start_time
                * SAMPLE_RATE
            )

            length = int(
                beat_seconds
                * 0.72
                * SAMPLE_RATE
            )

            lead_amp = (
                0.065
                * brightness
            )

            # Chorus sections are slightly stronger.
            if section >= 4:
                lead_amp *= 1.18

            add_voice(
                samples,
                start,
                length,
                freq,
                lead_amp,
                waveform="soft",
            )

        # ----------------------------------------------------
        # Drums
        # ----------------------------------------------------

        for beat in range(4):

            start_time = (
                bar * bar_seconds
                + beat * beat_seconds
            )

            if start_time >= duration_seconds:
                break

            start = int(
                start_time
                * SAMPLE_RATE
            )

            # Kick.
            if beat in {0, 2}:
                add_kick(
                    samples,
                    start,
                    0.12 * drum_level,
                )

            # Snare.
            if beat in {1, 3}:
                add_snare(
                    samples,
                    start,
                    rng,
                    0.07 * drum_level,
                )

            # 8th-note hats.
            half = int(
                beat_seconds
                * 0.5
                * SAMPLE_RATE
            )

            add_hat(
                samples,
                start,
                rng,
                0.025 * drum_level,
            )

            if (
                start + half
                < total_samples
            ):
                add_hat(
                    samples,
                    start + half,
                    rng,
                    0.018 * drum_level,
                )

        bar += 1

    # --------------------------------------------------------
    # Fade in/out for clean boundaries
    # --------------------------------------------------------

    fade_in_samples = min(
        total_samples,
        int(
            SAMPLE_RATE * 0.8
        ),
    )

    fade_out_samples = min(
        total_samples,
        int(
            SAMPLE_RATE * 1.2
        ),
    )

    for i in range(
        fade_in_samples
    ):
        samples[i] *= (
            i / fade_in_samples
        )

    for i in range(
        fade_out_samples
    ):
        index = (
            total_samples
            - fade_out_samples
            + i
        )

        if 0 <= index < total_samples:
            samples[index] *= (
                1.0
                - i / fade_out_samples
            )

    # --------------------------------------------------------
    # Normalize safely
    # --------------------------------------------------------

    peak = max(
        abs(x)
        for x in samples
    ) if samples else 1.0

    if peak < 0.0001:
        peak = 1.0

    target_peak = 0.82

    multiplier = (
        target_peak / peak
    )

    pcm = array(
        "h"
    )

    for value in samples:

        value *= multiplier

        value = max(
            -1.0,
            min(
                1.0,
                value,
            ),
        )

        pcm.append(
            int(
                value * 32767
            )
        )

    # --------------------------------------------------------
    # WAV output
    # --------------------------------------------------------

    buffer = io.BytesIO()

    with wave.open(
        buffer,
        "wb",
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(
            SAMPLE_RATE
        )

        wav_file.writeframes(
            pcm.tobytes()
        )

    return buffer.getvalue()
