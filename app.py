import os
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

# Keep the providers simple and explicit.
# ACE-Step is attempted first because it supports lyrics and long-form songs.
# MiniMax is a second provider, but its ZeroGPU quota is respected.
PROVIDERS = [
    ("ACE-Step 1.5", "ACE-Step/Ace-Step-v1.5"),
    ("MiniMax Music 3", "Upsampler/minimax-music3"),
]

HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN", "")).strip()

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎵",
    layout="wide",
)


# ---------------------------------------------------------------------
# Original RacharlaMusic visual design
# ---------------------------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

.stApp{
    font-family:Poppins,sans-serif;
    color:#fff;
    background:
    radial-gradient(circle at 8% 4%,rgba(255,30,205,.22),transparent 27%),
    radial-gradient(circle at 94% 8%,rgba(0,220,255,.18),transparent 28%),
    radial-gradient(circle at 55% 90%,rgba(105,62,255,.22),transparent 34%),
    linear-gradient(135deg,#06051a,#10134a 50%,#061c39);
}

.block-container{
    max-width:1280px;
    padding-top:1rem;
}

.hero{
    border-radius:28px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.16);
    box-shadow:
        0 25px 75px rgba(0,0,0,.48),
        0 0 45px rgba(255,35,205,.13);
    margin-bottom:22px;
}

.hero img{
    display:block;
    width:100%;
}

.glass{
    border:1px solid rgba(255,255,255,.14);
    border-radius:24px;
    padding:22px;
    background:
        linear-gradient(
            145deg,
            rgba(25,28,88,.86),
            rgba(6,20,57,.78)
        );
    box-shadow:
        0 20px 55px rgba(0,0,0,.34),
        inset 0 1px rgba(255,255,255,.06);
}

.title{
    font-size:2.5rem;
    font-weight:800;
    background:
        linear-gradient(
            90deg,
            #fff,
            #ff4ed4,
            #7c62ff,
            #20e5ff
        );
    -webkit-background-clip:text;
    color:transparent;
}

.muted{
    color:#bdbcdc;
}

.badge{
    display:inline-block;
    margin:4px;
    padding:6px 11px;
    border-radius:99px;
    background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.1);
    font-size:.78rem;
}

.tip{
    border-left:4px solid #ff35cf;
    border-radius:0 14px 14px 0;
    background:rgba(255,53,207,.07);
    padding:12px 15px;
}

.stButton>button{
    border:0!important;
    border-radius:16px!important;
    color:#fff!important;
    font-weight:800!important;
    background:
        linear-gradient(
            90deg,
            #ff18c9,
            #824eff,
            #00cef4
        )!important;
    box-shadow:
        0 12px 35px rgba(255,24,201,.3)!important;
    min-height:52px!important;
}

.stButton>button:hover{
    transform:translateY(-2px);
    box-shadow:
        0 18px 45px rgba(255,24,201,.42)!important;
}

div[data-testid="stTextArea"] textarea{
    background:rgba(4,8,35,.88)!important;
    color:white!important;
    border-radius:18px!important;
    border:1px solid rgba(160,110,255,.45)!important;
}

div[data-baseweb="select"]>div{
    background:rgba(6,11,44,.9)!important;
    border-radius:14px!important;
}

.footer{
    text-align:center;
    color:#aaa9c9;
    padding:30px 0 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
<div class="glass">
    <div class="title">🎵 RacharlaMusic</div>
    <div class="muted">
        Your lyrics • AI melody • Natural singing • Your song
    </div>
    <div>
        <span class="badge">🇮🇳 Telugu</span>
        <span class="badge">🇬🇧 English</span>
        <span class="badge">🔀 Mixed</span>
        <span class="badge">🎤 Vocals</span>
        <span class="badge">⬇️ Audio</span>
    </div>
</div>
<br>
""",
    unsafe_allow_html=True,
)


STYLES = {
    "Melody": (
        "beautiful Indian melodic film song, memorable hook, warm piano, "
        "acoustic guitar, lush strings, soft percussion, expressive natural "
        "singing, polished studio mix"
    ),
    "Romantic": (
        "romantic Indian film song, intimate natural vocals, piano, acoustic "
        "guitar, lush strings, emotional melody, polished studio production"
    ),
    "Folk": (
        "Telugu folk-inspired song, organic percussion, acoustic instruments, "
        "catchy traditional melody, energetic natural singing"
    ),
    "Mass": (
        "high-energy Telugu commercial song, powerful natural vocals, punchy "
        "drums, bass, rhythmic hooks, cinematic production"
    ),
    "Sad": (
        "emotional Indian ballad, expressive natural vocals, piano, strings, "
        "restrained drums, haunting memorable melody"
    ),
    "Cinematic": (
        "grand Indian cinematic soundtrack, expressive natural vocals, "
        "orchestral strings, piano, percussion, dramatic build"
    ),
    "Lo-fi": (
        "dreamy lo-fi Indian pop, intimate natural vocals, soft drums, "
        "warm keys, mellow bass"
    ),
    "Devotional": (
        "devotional Indian melody, respectful natural vocals, flute, gentle "
        "percussion, uplifting arrangement"
    ),
    "Hip-hop": (
        "Indian melodic hip-hop, natural sung hook, rhythmic vocal delivery, "
        "deep bass, crisp drums, modern production"
    ),
    "Rock": (
        "Indian pop rock, natural expressive vocals, electric guitars, live "
        "drums, bass, strong melodic chorus"
    ),
    "Pop": (
        "modern Indian pop, natural lead vocals, catchy melody, polished "
        "drums, bass, bright synths"
    ),
}

LANG = {
    "Telugu": "te",
    "English": "en",
    "Telugu + English": "te",
}


# ---------------------------------------------------------------------
# Gradio client
# ---------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_client(space_id):
    from gradio_client import Client

    kwargs = {}

    if HF_TOKEN:
        kwargs["hf_token"] = HF_TOKEN

    return Client(space_id, **kwargs)


@st.cache_data(ttl=120, show_spinner=False)
def get_api_info(space_id):
    client = get_client(space_id)

    try:
        return client.view_api(return_format="dict")
    except TypeError:
        return client.view_api()


# ---------------------------------------------------------------------
# API schema helpers
# ---------------------------------------------------------------------

def all_endpoints(info):
    result = []

    if not isinstance(info, dict):
        return result

    for bucket in ("named_endpoints", "unnamed_endpoints"):
        value = info.get(bucket, {})

        if isinstance(value, dict):
            for name, spec in value.items():
                result.append(
                    (
                        str(name),
                        spec if isinstance(spec, dict) else {},
                    )
                )

        elif isinstance(value, list):
            for spec in value:
                if isinstance(spec, dict):
                    name = (
                        spec.get("api_name")
                        or spec.get("name")
                        or "/unnamed"
                    )
                    result.append((str(name), spec))

    return result


def params_of(spec):
    if not isinstance(spec, dict):
        return []

    for key in ("parameters", "inputs"):
        value = spec.get(key)

        if isinstance(value, list):
            return value

    return []


def returns_of(spec):
    if not isinstance(spec, dict):
        return []

    for key in ("returns", "outputs"):
        value = spec.get(key)

        if isinstance(value, list):
            return value

    return []


def p_name(param):
    if not isinstance(param, dict):
        return str(param)

    return str(
        param.get("parameter_name")
        or param.get("name")
        or param.get("label")
        or param.get("component_label")
        or ""
    )


def p_default(param):
    if not isinstance(param, dict):
        return None

    return param.get("default")


def p_optional(param):
    if not isinstance(param, dict):
        return False

    return bool(
        param.get("optional")
        or param.get("nullable")
    )


def choices_of(param):
    if not isinstance(param, dict):
        return []

    for key in ("choices", "enum", "options", "values"):
        value = param.get(key)

        if isinstance(value, dict):
            return list(value.keys())

        if isinstance(value, (list, tuple)):
            return list(value)

    return []


def text_of(obj):
    if isinstance(obj, str):
        return obj.lower()

    if isinstance(obj, dict):
        return " ".join(text_of(v) for v in obj.values())

    if isinstance(obj, (list, tuple)):
        return " ".join(text_of(v) for v in obj)

    return str(obj).lower()


def endpoint_is_generation(name, spec):
    """
    Strictly identify actual music generation endpoints.

    This avoids accidentally selecting initialization,
    model loading, scoring, LRC, metadata, or UI helper endpoints.
    """

    blob = (
        str(name)
        + " "
        + text_of(params_of(spec))
        + " "
        + text_of(returns_of(spec))
    ).lower()

    params_blob = text_of(params_of(spec))
    returns_blob = text_of(returns_of(spec))

    has_lyrics = "lyrics" in params_blob
    has_duration = (
        "audio_duration" in params_blob
        or "duration" in params_blob
    )
    has_caption = (
        "caption" in params_blob
        or "captions" in params_blob
        or "prompt" in params_blob
    )

    has_audio_output = any(
        token in returns_blob
        for token in (
            "audio",
            "file",
            "filepath",
            "filedata",
            "waveform",
        )
    )

    generation_word = any(
        token in str(name).lower()
        for token in (
            "generate",
            "generation",
            "music",
            "infer",
            "predict",
            "create",
        )
    )

    utility_word = any(
        token in str(name).lower()
        for token in (
            "load",
            "init",
            "initialize",
            "refresh",
            "model",
            "checkpoint",
            "clear",
            "stop",
            "score",
            "lrc",
            "metadata",
            "analyze",
            "understand",
        )
    )

    if utility_word:
        return False

    # Strongest possible match.
    if has_lyrics and has_duration and has_caption:
        return True

    if (
        generation_word
        and has_lyrics
        and has_audio_output
    ):
        return True

    return False


def choose_generation_endpoint(info, provider):
    endpoints = all_endpoints(info)

    candidates = []

    for name, spec in endpoints:
        if not endpoint_is_generation(name, spec):
            continue

        blob = (
            str(name)
            + " "
            + text_of(params_of(spec))
            + " "
            + text_of(returns_of(spec))
        ).lower()

        score = 0

        if "generate_music" in str(name).lower():
            score += 100

        if "generate" in str(name).lower():
            score += 30

        if "music" in str(name).lower():
            score += 20

        if "lyrics" in text_of(params_of(spec)):
            score += 30

        if "audio_duration" in text_of(params_of(spec)):
            score += 15

        if "audio" in text_of(returns_of(spec)):
            score += 20

        if provider == "ACE-Step 1.5":
            if "caption" in blob:
                score += 10

        candidates.append(
            (score, name, spec)
        )

    if not candidates:
        raise RuntimeError(
            "No current music-generation API endpoint was exposed by "
            f"{provider}. The provider's public Gradio API has changed "
            "or is temporarily unavailable."
        )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return candidates[0][1], candidates[0][2]


# ---------------------------------------------------------------------
# Safe value construction
# ---------------------------------------------------------------------

def choice_match(choices, *wanted):
    for wanted_value in wanted:
        if wanted_value is None:
            continue

        for choice in choices:
            if str(choice).strip().lower() == str(
                wanted_value
            ).strip().lower():
                return choice

    return None


def numeric_safe(param, preferred):
    """
    Return a legal numeric value according to the live Gradio schema.
    """

    minimum = param.get("minimum")
    maximum = param.get("maximum")
    step = param.get("step")

    try:
        value = float(preferred)

        if minimum is not None:
            value = max(value, float(minimum))

        if maximum is not None:
            value = min(value, float(maximum))

        if step is not None:
            step_value = float(step)

            if step_value > 0:
                base = float(minimum or 0)
                value = (
                    round((value - base) / step_value)
                    * step_value
                    + base
                )

                if minimum is not None:
                    value = max(
                        value,
                        float(minimum),
                    )

                if maximum is not None:
                    value = min(
                        value,
                        float(maximum),
                    )

        # Gradio integer inputs should receive ints.
        if step is not None:
            try:
                if float(step).is_integer():
                    return int(round(value))
            except Exception:
                pass

        return value

    except Exception:
        return preferred


def build_value(
    param,
    *,
    lyrics,
    caption,
    language,
    duration,
    provider,
):
    """
    Build one value from the LIVE provider schema.

    Important:
    We use provider defaults whenever possible.
    We do NOT invent values for unknown ACE-Step fields.
    """

    name = p_name(param).strip().lower()
    choices = choices_of(param)
    default = p_default(param)

    # -------------------------------------------------------------
    # Text inputs
    # -------------------------------------------------------------

    if (
        name in ("lyrics", "lyric", "lrc")
        or "lyrics" in name
    ):
        return lyrics

    if (
        name in (
            "caption",
            "captions",
            "prompt",
            "text_prompt",
            "description",
        )
        or any(
            token in name
            for token in (
                "caption",
                "prompt",
                "description",
            )
        )
    ):
        return caption

    # -------------------------------------------------------------
    # Language
    # -------------------------------------------------------------

    if "vocal_language" in name:
        if choices:
            match = choice_match(
                choices,
                language,
                language.upper(),
                "Telugu" if language == "te" else None,
                "English" if language == "en" else None,
            )

            if match is not None:
                return match

            # Never force a value that the live UI doesn't accept.
            return choices[0]

        return language

    if name in ("language", "lang"):
        if choices:
            return (
                choice_match(
                    choices,
                    language,
                    "English",
                    "Telugu",
                    "en",
                    "te",
                )
                or choices[0]
            )

        return language

    # -------------------------------------------------------------
    # Duration
    # -------------------------------------------------------------

    if "audio_duration" in name:
        return numeric_safe(
            param,
            duration,
        )

    if name in ("duration", "length"):
        return numeric_safe(
            param,
            duration,
        )

    # -------------------------------------------------------------
    # Audio format
    # -------------------------------------------------------------

    if (
        "audio_format" in name
        or name in ("format", "file_type")
    ):
        if choices:
            return (
                choice_match(
                    choices,
                    "mp3",
                    "wav",
                )
                or choices[0]
            )

        return "mp3"

    # -------------------------------------------------------------
    # Task
    # -------------------------------------------------------------

    if "task_type" in name:
        if choices:
            return (
                choice_match(
                    choices,
                    "text2music",
                    "text-to-music",
                )
                or choices[0]
            )

        return "text2music"

    # -------------------------------------------------------------
    # Inference
    # -------------------------------------------------------------

    if (
        "inference_steps" in name
        or "infer_step" in name
        or name == "steps"
    ):
        return numeric_safe(
            param,
            8,
        )

    if "guidance_scale" in name:
        return numeric_safe(
            param,
            7.0,
        )

    # -------------------------------------------------------------
    # Seed
    # -------------------------------------------------------------

    if (
        "random_seed" in name
        or "randomize_seed" in name
        or "use_random_seed" in name
    ):
        return True

    if name == "seed" or name.endswith("_seed"):
        if default is not None:
            return default

        return 0

    # -------------------------------------------------------------
    # Thinking / LM
    # -------------------------------------------------------------

    if (
        name in (
            "thinking",
            "think",
            "think_checkbox",
            "use_thinking",
        )
    ):
        return False

    if "lm_temperature" in name:
        return default if default is not None else 0.85

    if "lm_cfg_scale" in name:
        return default if default is not None else 2.5

    if "lm_top_k" in name:
        return default if default is not None else 0

    if "lm_top_p" in name:
        return default if default is not None else 0.9

    if "lm_negative_prompt" in name:
        return default if default is not None else ""

    # -------------------------------------------------------------
    # Booleans
    # -------------------------------------------------------------

    if "instrumental" in name:
        return False

    if name.startswith("use_"):
        if default is not None:
            return default
        return False

    if name.startswith("enable_"):
        if default is not None:
            return default
        return False

    if name.startswith("auto_"):
        if default is not None:
            return default
        return False

    if "random" in name and "seed" in name:
        return True

    # -------------------------------------------------------------
    # Batch
    # -------------------------------------------------------------

    if "batch_size" in name:
        return numeric_safe(
            param,
            1,
        )

    # -------------------------------------------------------------
    # Optional audio/file inputs
    # -------------------------------------------------------------

    if any(
        token in name
        for token in (
            "reference_audio",
            "refer_audio",
            "src_audio",
            "source_audio",
            "target_audio",
            "audio_input",
        )
    ):
        return None

    # -------------------------------------------------------------
    # Repainting / cover / advanced optional values
    # -------------------------------------------------------------

    if any(
        token in name
        for token in (
            "repainting_start",
            "repainting_end",
            "audio_cover_strength",
        )
    ):
        if default is not None:
            return default

        return None

    if (
        "cfg_interval" in name
        or name in (
            "shift",
            "headroom",
        )
    ):
        if default is not None:
            return default

        return 0.0 if "interval" in name else 1.0

    # -------------------------------------------------------------
    # Choices
    # -------------------------------------------------------------

    if choices:
        if default is not None:
            matched_default = choice_match(
                choices,
                default,
            )

            if matched_default is not None:
                return matched_default

        return choices[0]

    # -------------------------------------------------------------
    # CRITICAL:
    # Use provider defaults before guessing.
    # -------------------------------------------------------------

    if default is not None:
        return default

    # Optional parameters can safely be None.
    if p_optional(param):
        return None

    # -------------------------------------------------------------
    # Schema-aware numeric fallback
    # -------------------------------------------------------------

    schema_text = text_of(param)

    if "bool" in schema_text:
        return False

    if "float" in schema_text:
        return 0.0

    if "number" in schema_text:
        return 0.0

    if "int" in schema_text:
        return 0

    # Unknown required string.
    return ""


# ---------------------------------------------------------------------
# Audio extraction
# ---------------------------------------------------------------------

def detect_audio_format(data):
    if not data:
        return "mp3", "audio/mpeg"

    # WAV / RIFF
    if len(data) >= 12 and data[:4] == b"RIFF":
        return "wav", "audio/wav"

    # FLAC
    if data[:4] == b"fLaC":
        return "flac", "audio/flac"

    # OGG
    if data[:4] == b"OggS":
        return "ogg", "audio/ogg"

    # MP3 frame / ID3
    if data[:3] == b"ID3":
        return "mp3", "audio/mpeg"

    if len(data) >= 2:
        if data[0] == 0xFF and (
            data[1] & 0xE0
        ) == 0xE0:
            return "mp3", "audio/mpeg"

    return "mp3", "audio/mpeg"


def read_audio_file(path):
    try:
        if path and os.path.isfile(path):
            return Path(path).read_bytes()
    except Exception:
        pass

    return None


def download_url(url, mime=""):
    try:
        response = requests.get(
            url,
            timeout=180,
            allow_redirects=True,
        )
        response.raise_for_status()

        data = response.content

        if not data:
            return None

        ctype = (
            response.headers.get(
                "content-type"
            )
            or mime
            or ""
        ).lower()

        lower = url.lower()

        looks_audio = (
            "audio/" in ctype
            or any(
                ext in lower
                for ext in (
                    ".mp3",
                    ".wav",
                    ".flac",
                    ".ogg",
                    ".m4a",
                )
            )
        )

        if looks_audio:
            return data

        # Some Gradio file URLs don't have an audio MIME type.
        fmt, _ = detect_audio_format(data)

        if fmt in (
            "mp3",
            "wav",
            "flac",
            "ogg",
        ):
            return data

    except Exception:
        return None

    return None


def extract_audio(value):
    """
    Recursively extract an actual audio file from Gradio results.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (bytes, bytearray),
    ):
        return bytes(value)

    if isinstance(value, dict):
        if (
            value.get("__type__")
            == "update"
        ):
            return None

        # Direct file-like fields.
        for key in (
            "path",
            "url",
            "file",
            "name",
        ):
            candidate = value.get(key)

            if not isinstance(
                candidate,
                str,
            ):
                continue

            if candidate.startswith(
                ("http://", "https://")
            ):
                data = download_url(candidate)

                if data:
                    return data

            local = read_audio_file(candidate)

            if local:
                return local

        # Recurse through nested output.
        for child in value.values():
            found = extract_audio(child)

            if found:
                return found

        return None

    if isinstance(
        value,
        (list, tuple),
    ):
        for child in value:
            found = extract_audio(child)

            if found:
                return found

        return None

    if isinstance(value, str):
        if value.startswith(
            ("http://", "https://")
        ):
            return download_url(value)

        return read_audio_file(value)

    return None


# ---------------------------------------------------------------------
# ACE-Step
# ---------------------------------------------------------------------

def generate_ace_gradio(
    lyrics,
    caption,
    language,
    duration,
):
    """
    Current ACE-Step integration.

    IMPORTANT:
    Do not use the old /v1/music/generate HTTP fallback here.

    The current public ACE-Step Space is a Gradio 6 application.
    We inspect its live API schema and call the actual generation endpoint.
    """

    client = get_client(
        "ACE-Step/Ace-Step-v1.5"
    )

    info = get_api_info(
        "ACE-Step/Ace-Step-v1.5"
    )

    endpoint, spec = choose_generation_endpoint(
        info,
        "ACE-Step 1.5",
    )

    params = params_of(spec)

    if not params:
        raise RuntimeError(
            "ACE-Step exposed a generation endpoint "
            "but returned no input schema."
        )

    values = []

    for param in params:
        values.append(
            build_value(
                param,
                lyrics=lyrics,
                caption=caption,
                language=language,
                duration=duration,
                provider="ACE-Step 1.5",
            )
        )

    # First try strict positional order.
    try:
        result = client.predict(
            *values,
            api_name=endpoint,
        )

        audio = extract_audio(result)

        if audio:
            return audio

    except Exception as positional_error:
        positional_message = str(
            positional_error
        )

        # Try named parameters as a compatibility path.
        kwargs = {}

        for param, value in zip(
            params,
            values,
        ):
            name = p_name(param)

            if name:
                kwargs[name] = value

        if kwargs:
            try:
                result = client.predict(
                    api_name=endpoint,
                    **kwargs,
                )

                audio = extract_audio(result)

                if audio:
                    return audio

            except Exception as named_error:
                raise RuntimeError(
                    "ACE-Step generation endpoint was found, "
                    "but its live parameter schema rejected the "
                    "request.\n\n"
                    f"Positional call: "
                    f"{positional_message[:900]}\n\n"
                    f"Named call: "
                    f"{str(named_error)[:900]}"
                )

        raise RuntimeError(
            "ACE-Step generation call failed:\n"
            f"{positional_message[:1200]}"
        )

    raise RuntimeError(
        "ACE-Step completed the API call but returned "
        "no downloadable audio."
    )


# ---------------------------------------------------------------------
# MiniMax Music 3
# ---------------------------------------------------------------------

def generate_minimax(
    lyrics,
    caption,
    duration,
):
    """
    MiniMax Music 3 exposes a plain five-input endpoint:

        generate_music(
            description,
            duration,
            seed,
            instrumental,
            lyrics
        )

    The current Space returns WAV.
    """

    if not HF_TOKEN:
        # Don't claim that a token is always mandatory.
        # It simply makes quota behavior much more reliable.
        token_note = (
            "No HF_TOKEN is configured, so this request uses "
            "the unauthenticated ZeroGPU path."
        )
    else:
        token_note = (
            "Using the configured Hugging Face token."
        )

    client = get_client(
        "Upsampler/minimax-music3"
    )

    info = get_api_info(
        "Upsampler/minimax-music3"
    )

    endpoint = None

    for name, spec in all_endpoints(info):
        blob = (
            str(name)
            + " "
            + text_of(spec)
        ).lower()

        if (
            "generate_music" in str(name).lower()
            and "lyrics" in blob
        ):
            endpoint = name
            break

    if endpoint is None:
        # Exact current endpoint from the provider,
        # but only use it if API discovery did not expose it.
        endpoint = "generate_music"

    endpoint = str(endpoint)

    # Gradio 6 wants the endpoint name without inventing
    # a double slash. Older gradio_client accepts both forms,
    # so normalize only here.
    endpoint = endpoint.lstrip("/")

    safe_duration = max(
        5,
        min(
            int(duration),
            300,
        ),
    )

    result = client.predict(
        caption,
        safe_duration,
        0,
        False,
        lyrics,
        api_name=endpoint,
    )

    audio = extract_audio(result)

    if not audio:
        raise RuntimeError(
            "MiniMax Music 3 returned no downloadable audio."
        )

    return audio, token_note


# ---------------------------------------------------------------------
# Provider error classification
# ---------------------------------------------------------------------

def is_quota_error(text):
    text = (
        text or ""
    ).lower()

    return any(
        token in text
        for token in (
            "zerogpu quota",
            "exceeded your zerogpu quota",
            "0s left",
            "quota limit",
            "gpu quota",
            "larger than the maximum allowed",
            "gpu limit",
        )
    )


def is_capacity_error(text):
    text = (
        text or ""
    ).lower()

    return any(
        token in text
        for token in (
            "capacity",
            "queue",
            "no gpu was available",
            "timeout",
            "503",
            "502",
            "504",
            "space is sleeping",
        )
    )


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")

    language = st.selectbox(
        "🌐 Lyrics",
        list(LANG),
        index=0,
    )

    vocal = st.selectbox(
        "🎤 Vocal",
        [
            "Natural lead",
            "Female",
            "Male",
            "Duet",
        ],
    )

    style = st.selectbox(
        "🎼 Style",
        list(STYLES),
        index=0,
    )

    # IMPORTANT:
    # Start at 1 minute for testing.
    # The selector still supports the original 1–6 minutes.
    duration_label = st.select_slider(
        "⏱️ Length",
        [
            "1 min",
            "2 min",
            "3 min",
            "4 min",
            "5 min",
            "6 min",
        ],
        value="1 min",
    )

    duration = (
        int(duration_label.split()[0])
        * 60
    )

    st.markdown("---")

    st.info(
        "RacharlaMusic uses public AI music services. "
        "Generation availability depends on the provider's "
        "current GPU capacity and your Hugging Face quota."
    )


# ---------------------------------------------------------------------
# Main creator UI
# ---------------------------------------------------------------------

c1, c2 = st.columns(
    [1.35, 0.75],
    gap="large",
)


with c1:
    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### ✍️ Create your song"
    )

    lyrics = st.text_area(
        "Lyrics",
        height=330,
        max_chars=8000,
        placeholder=(
            "[Verse 1]\n"
            "నీ కోసం నా గుండెలో...\n\n"
            "[Pre-Chorus]\n"
            "...\n\n"
            "[Chorus]\n"
            "You are my light..."
        ),
    )

    title = st.text_input(
        "🎧 Song title",
        placeholder="My Racharla Song",
    )

    extra = st.text_input(
        "🎹 Extra music direction",
        value=(
            "flute intro, warm piano, "
            "big cinematic chorus"
        ),
    )

    st.markdown(
        '<div class="tip">'
        "💡 Better structure: use [Verse], "
        "[Pre-Chorus], [Chorus], [Bridge], [Outro]."
        "</div>",
        unsafe_allow_html=True,
    )

    generate = st.button(
        "✨  GENERATE MY SONG  🎵",
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


with c2:
    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 🎚️ Sound preview"
    )

    st.markdown(
        f"""
        **Language:** {language}<br>
        **Vocal:** {vocal}<br>
        **Style:** {style}<br>
        **Length:** {duration_label}
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p class="muted">{STYLES[style]}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------

if generate:

    if not lyrics.strip():
        st.warning(
            "Please paste your lyrics first."
        )
        st.stop()

    vocal_text = {
        "Natural lead": (
            "natural human-like lead singing, "
            "expressive phrasing, clear diction"
        ),
        "Female": (
            "natural human-like female lead singing, "
            "expressive phrasing, clear diction"
        ),
        "Male": (
            "natural human-like male lead singing, "
            "expressive phrasing, clear diction"
        ),
        "Duet": (
            "natural human-like male and female duet "
            "singing, expressive harmonies"
        ),
    }[vocal]

    caption = (
        f"{STYLES[style]}, "
        f"{vocal_text}, "
        f"{extra}, "
        "professional studio mix, "
        "strong melodic chorus, "
        "no spoken narration"
    )

    status = st.empty()

    progress = st.progress(0)

    errors = []

    final_audio = None
    used_provider = None
    provider_note = ""

    for index, (
        provider_name,
        space_id,
    ) in enumerate(PROVIDERS):

        status.info(
            f"🎼 Provider {index + 1}/"
            f"{len(PROVIDERS)}: "
            f"Trying **{provider_name}**..."
        )

        try:

            with st.spinner(
                f"Generating with {provider_name}..."
            ):

                if provider_name == "ACE-Step 1.5":

                    audio = generate_ace_gradio(
                        lyrics=lyrics,
                        caption=caption,
                        language=LANG[language],
                        duration=duration,
                    )

                elif provider_name == "MiniMax Music 3":

                    audio, provider_note = (
                        generate_minimax(
                            lyrics=lyrics,
                            caption=caption,
                            duration=duration,
                        )
                    )

                else:
                    raise RuntimeError(
                        "Unknown provider."
                    )

            if audio:

                final_audio = audio
                used_provider = provider_name

                progress.progress(100)

                status.success(
                    f"🎉 Song generated with "
                    f"{provider_name}!"
                )

                break

        except Exception as exc:

            message = str(exc)

            errors.append(
                (
                    provider_name,
                    message,
                )
            )

            if is_quota_error(message):

                status.warning(
                    f"⚠️ {provider_name} has no usable "
                    "ZeroGPU quota right now."
                )

            elif is_capacity_error(message):

                status.warning(
                    f"⚠️ {provider_name} is currently "
                    "busy/unavailable."
                )

            else:

                status.warning(
                    f"⚠️ {provider_name} failed. "
                    "Checking the next provider..."
                )

        progress.progress(
            int(
                (
                    (index + 1)
                    / len(PROVIDERS)
                )
                * 100
            )
        )

    # -----------------------------------------------------------------
    # Success
    # -----------------------------------------------------------------

    if final_audio:

        fmt, mime = detect_audio_format(
            final_audio
        )

        st.session_state["audio"] = final_audio
        st.session_state["audio_format"] = fmt
        st.session_state["audio_mime"] = mime
        st.session_state["title"] = (
            title.strip()
            or "RacharlaMusic Song"
        )
        st.session_state["provider"] = (
            used_provider
        )

        if provider_note:
            st.session_state[
                "provider_note"
            ] = provider_note

    # -----------------------------------------------------------------
    # Failure
    # -----------------------------------------------------------------

    else:

        status.error(
            "❌ No generation provider is "
            "available right now."
        )

        # Give a useful diagnosis rather than
        # pretending the fallback system fixed it.

        quota_failures = [
            name
            for name, message in errors
            if is_quota_error(message)
        ]

        if quota_failures:

            st.warning(
                "The current public AI providers are "
                "running through Hugging Face ZeroGPU. "
                "Your request cannot be generated until "
                "a usable ZeroGPU quota is available."
            )

        with st.expander(
            "Technical details"
        ):

            for name, message in errors:

                st.write(
                    f"**{name}:**"
                )

                st.code(
                    message[:2500]
                )

        st.caption(
            "This message is intentionally specific: "
            "a provider quota/capacity problem cannot be "
            "fixed by retrying the same provider repeatedly."
        )


# ---------------------------------------------------------------------
# Audio preview + download
# ---------------------------------------------------------------------

if "audio" in st.session_state:

    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "## 🎉 Your song is ready"
    )

    st.caption(
        "Generated by **"
        f"{st.session_state.get('provider', 'AI music provider')}"
        "**"
    )

    fmt = st.session_state.get(
        "audio_format",
        "mp3",
    )

    mime = st.session_state.get(
        "audio_mime",
        "audio/mpeg",
    )

    # Actual provider format is used.
    st.audio(
        st.session_state["audio"],
        format=mime,
    )

    fname = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        st.session_state.get(
            "title",
            "RacharlaMusic Song",
        ),
    ).strip("_")

    if not fname:
        fname = "RacharlaMusic_Song"

    extension = fmt

    download_label = (
        "⬇️ DOWNLOAD MP3"
        if fmt == "mp3"
        else f"⬇️ DOWNLOAD {fmt.upper()}"
    )

    st.download_button(
        download_label,
        data=st.session_state["audio"],
        file_name=f"{fname}.{extension}",
        mime=mime,
        use_container_width=True,
    )

    if fmt != "mp3":
        st.caption(
            f"The provider returned {fmt.upper()} audio. "
            "The file is intentionally downloaded with the "
            "correct extension instead of falsely labeling "
            "the WAV file as MP3."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        🎵 <b>RacharlaMusic</b> •
        Create • Sing • Share • Anytime
        <br>
        Powered by <b>RacharlaGPT.in</b>
    </div>
    """,
    unsafe_allow_html=True,
)
