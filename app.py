
import io
import os
import re
import time
import requests
import streamlit as st

APP_NAME = "RacharlaMusic"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎵",
    layout="wide",
)

# ---------------------------------------------------------------------
# Optional provider tokens
# ---------------------------------------------------------------------
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN", ""))
REPLICATE_TOKEN = st.secrets.get("REPLICATE_API_TOKEN", os.getenv("REPLICATE_API_TOKEN", ""))

ACE_SPACE = "ACE-Step/Ace-Step-v1.5"
MUSICGEN_SPACE = "Surn/UnlimitedMusicGen"
STABLE_AUDIO_SPACE = "stabilityai/stable-audio-3"

LANGUAGES = {
    "Telugu": "te",
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Urdu": "ur",
}

STYLES = {
    "Melody": "beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar, lush strings, soft percussion, expressive natural singing, polished studio mix",
    "Cinematic": "epic Indian cinematic film song, emotional orchestra, lush strings, piano, cinematic percussion, powerful chorus, expressive natural lead vocal",
    "Romantic": "warm romantic Indian film melody, acoustic guitar, piano, soft strings, gentle percussion, intimate expressive natural singing",
    "Devotional": "beautiful Indian devotional melody, warm harmonium and piano, flute, tanpura texture, soft tabla, lush strings, soulful natural lead vocal",
    "Folk": "modern Indian folk film song, acoustic instruments, flute, dholak, hand percussion, catchy melodic hook, energetic natural singing",
    "Motivational": "uplifting Indian cinematic anthem, warm piano, acoustic guitar, big strings, driving percussion, memorable powerful chorus, natural expressive singing",
}

def clean_lyrics(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    return text

def build_prompt(style_text: str, extra: str, language_name: str) -> str:
    parts = [
        style_text,
        f"Indian {language_name} film song",
        "natural human-like lead vocal, musical phrasing, emotional dynamics, no robotic delivery",
    ]
    if extra.strip():
        parts.append(extra.strip())
    return ", ".join(parts)

def looks_like_quota_error(text: str) -> bool:
    t = (text or "").lower()
    return any(x in t for x in [
        "zerogpu quota",
        "exceeded your zerogpu quota",
        "quota",
        "gpu task aborted",
        "out of gpu",
        "no gpu",
        "capacity",
    ])

def audio_bytes_from_value(value):
    """Recursively find a downloadable audio URL/path/file-like value."""
    if value is None:
        return None

    if isinstance(value, bytes):
        return value

    if hasattr(value, "read"):
        try:
            return value.read()
        except Exception:
            pass

    if isinstance(value, dict):
        # Gradio FileData / API dictionaries
        for k in ("url", "path", "file", "name"):
            v = value.get(k)
            if isinstance(v, str):
                b = download_audio(v)
                if b:
                    return b
        for v in value.values():
            b = audio_bytes_from_value(v)
            if b:
                return b
        return None

    if isinstance(value, (list, tuple)):
        for v in value:
            b = audio_bytes_from_value(v)
            if b:
                return b
        return None

    if isinstance(value, str):
        return download_audio(value)

    return None

def download_audio(value):
    if not value:
        return None

    s = str(value)
    if s.startswith("/"):
        # Local paths returned by a remote Space are not directly readable.
        return None

    if s.startswith("http://") or s.startswith("https://"):
        try:
            r = requests.get(s, timeout=90)
            r.raise_for_status()
            ctype = (r.headers.get("content-type") or "").lower()
            if "audio" in ctype or any(x in s.lower() for x in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]):
                return r.content
        except Exception:
            return None

    return None

def get_gradio_client(space):
    from gradio_client import Client
    kwargs = {}
    if HF_TOKEN:
        kwargs["hf_token"] = HF_TOKEN
    return Client(space, **kwargs)

def safe_view_api(client):
    try:
        return client.view_api(return_format="dict")
    except Exception:
        return client.view_api()

def flatten_text(obj):
    if isinstance(obj, str):
        return obj.lower()
    if isinstance(obj, dict):
        return " ".join(flatten_text(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(flatten_text(v) for v in obj)
    return str(obj).lower()

def endpoint_specs(api_info):
    out = []
    if isinstance(api_info, dict):
        for key in ("named_endpoints", "unnamed_endpoints"):
            val = api_info.get(key, {})
            if isinstance(val, dict):
                for name, spec in val.items():
                    out.append((name, spec))
            elif isinstance(val, list):
                for spec in val:
                    if isinstance(spec, dict):
                        out.append((spec.get("api_name") or spec.get("name") or "/unnamed", spec))
    return out

def choose_generation_endpoint(api_info):
    candidates = []
    for name, spec in endpoint_specs(api_info):
        params = spec.get("parameters") or spec.get("inputs") or []
        returns = spec.get("returns") or spec.get("outputs") or []
        ptxt = flatten_text(params)
        rtxt = flatten_text(returns)
        ntxt = flatten_text(name)

        score = 0
        if any(x in ptxt for x in ["lyrics", "caption", "prompt", "simple_query", "text"]):
            score += 7
        if any(x in ptxt for x in ["duration", "audio_duration"]):
            score += 3
        if any(x in rtxt for x in ["audio", "file", "filepath", "path"]):
            score += 7
        if any(x in ntxt for x in ["generate", "music", "predict"]):
            score += 4
        if any(x in ntxt for x in ["load", "init", "model", "refresh", "checkpoint"]):
            score -= 10

        if score > 0:
            candidates.append((score, name, spec))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0] if candidates else None

def choices_for(param):
    if not isinstance(param, dict):
        return []
    for key in ("choices", "enum", "values"):
        v = param.get(key)
        if isinstance(v, list):
            return v
    return []

def param_name(param):
    if isinstance(param, dict):
        return str(param.get("parameter_name") or param.get("name") or param.get("label") or "")
    return str(param)

def make_gradio_value(param, prompt, lyrics, duration, language_code):
    name = param_name(param).lower()
    choices = choices_for(param)

    def pick(*wanted):
        for w in wanted:
            for c in choices:
                if str(c).lower() == str(w).lower():
                    return c
        return choices[0] if choices else None

    if "lyrics" in name:
        return lyrics
    if any(x in name for x in ["caption", "prompt", "simple_query", "description", "text"]):
        return prompt
    if "duration" in name or "length" in name:
        return duration
    if "vocal_language" in name or name in ("language", "lang"):
        return pick(language_code, "te" if language_code == "te" else None, "English", "en")
    if "audio_format" in name or "format" == name:
        return pick("mp3", "wav")
    if "thinking" in name or "think" in name:
        return False
    if "instrumental" in name:
        return False
    if "batch" in name:
        return 1
    if "inference_steps" in name or "steps" in name:
        return 8
    if "seed" in name:
        return -1
    if "guidance" in name or "cfg" in name:
        return 3.5
    if "temperature" in name:
        return 0.85
    if "top_k" in name:
        return 250
    if "top_p" in name:
        return 0.9
    if "model" in name:
        # Main DiT model vs 5Hz/LM selector.
        if any(x in name for x in ["lm", "language", "5hz"]):
            for c in choices:
                if "5hz" in str(c).lower() or "lm" in str(c).lower():
                    return c
        for wanted in ("acestep-v15-turbo", "turbo", "medium", "small"):
            for c in choices:
                if wanted in str(c).lower():
                    return c
        return choices[0] if choices else None
    if "generation_mode" in name or name == "mode":
        return pick("custom", "simple")
    if "task_type" in name:
        return pick("text2music", "text-to-music")
    if "bpm" in name:
        return None
    if "key" in name or "scale" in name:
        return None
    if "time_signature" in name or "timesignature" in name:
        return None
    if choices:
        # Never send an invalid blank choice to a Gradio dropdown.
        return choices[0]

    # Reasonable primitive defaults based on schema hints.
    t = flatten_text(param)
    if "bool" in t:
        return False
    if "int" in t:
        return 0
    if "float" in t:
        return 0.0
    return None

def call_dynamic_gradio(space, prompt, lyrics, duration, language_code):
    client = get_gradio_client(space)
    api = safe_view_api(client)
    selected = choose_generation_endpoint(api)
    if not selected:
        raise RuntimeError(f"No generation endpoint found for {space}")

    _, endpoint, spec = selected
    params = spec.get("parameters") or spec.get("inputs") or []
    values = [
        make_gradio_value(p, prompt, lyrics, duration, language_code)
        for p in params
    ]

    result = client.predict(*values, api_name=endpoint)
    audio = audio_bytes_from_value(result)
    if not audio:
        raise RuntimeError(f"{space}: generation returned no downloadable audio")
    return audio

def call_musicgen(prompt, duration):
    # This Space documents a direct Gradio REST API and internally segments
    # longer MusicGen generations.
    url = "https://huggingface.co/spaces/Surn/UnlimitedMusicGen/api/predict_simple"
    payload = {
        "model": "stereo-small",
        "text": prompt,
        "duration": min(int(duration), 60),
        "temperature": 0.8,
        "cfg_coef": 4.0,
        "seed": -1,
        "overlap": 2,
        "video_orientation": "Landscape",
    }
    r = requests.post(url, json=payload, timeout=180)
    if r.status_code >= 400:
        raise RuntimeError(f"MusicGen HTTP {r.status_code}: {r.text[:500]}")

    data = r.json()
    if isinstance(data, (list, tuple)):
        # documented response: video_url, audio_url, seed
        for item in data:
            b = audio_bytes_from_value(item)
            if b:
                return b
    return audio_bytes_from_value(data)

def call_replicate(prompt, duration):
    if not REPLICATE_TOKEN:
        raise RuntimeError("Replicate fallback is disabled because REPLICATE_API_TOKEN is not configured.")

    # Replicate's MusicGen endpoint is a paid API in general, so it is kept
    # as an optional fourth fallback rather than silently charging anyone.
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_TOKEN}",
        "Content-Type": "application/json",
    }
    version = "671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb"
    payload = {
        "version": version,
        "input": {
            "prompt": prompt,
            "duration": min(int(duration), 30),
            "output_format": "mp3",
        },
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    job = r.json()
    poll_url = job.get("urls", {}).get("get")
    if not poll_url:
        raise RuntimeError("Replicate did not return a polling URL.")

    for _ in range(90):
        p = requests.get(poll_url, headers=headers, timeout=30)
        p.raise_for_status()
        data = p.json()
        if data.get("status") == "succeeded":
            return audio_bytes_from_value(data.get("output"))
        if data.get("status") in ("failed", "canceled"):
            raise RuntimeError(str(data.get("error") or data.get("status")))
        time.sleep(2)

    raise RuntimeError("Replicate generation timed out.")

def try_provider(name, fn, status_box):
    status_box.info(f"🎼 Trying {name}…")
    try:
        audio = fn()
        if audio:
            status_box.success(f"✅ Generated with {name}")
            return audio, None
        raise RuntimeError("No audio returned.")
    except Exception as e:
        msg = str(e)
        if looks_like_quota_error(msg):
            status_box.warning(f"⚠️ {name} is temporarily unavailable because its GPU quota/capacity is exhausted.")
        else:
            status_box.warning(f"⚠️ {name} failed: {msg[:300]}")
        return None, msg

# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.1rem;
}
.sub {
    opacity: .78;
    margin-bottom: 1rem;
}
.card {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 16px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎵 RacharlaMusic</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Telugu • English • Indian film songs • automatic multi-provider fallback</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 1])

with left:
    language_name = st.selectbox("Language", list(LANGUAGES.keys()), index=0)
    style_name = st.selectbox("Style", list(STYLES.keys()), index=0)
    duration_min = st.slider("Length", 1, 6, 2, 1)
    title = st.text_input("Song title", placeholder="e.g. Naa Pranam")
    lyrics = st.text_area(
        "Lyrics",
        height=300,
        placeholder="[Verse]\n...\n\n[Pre-Chorus]\n...\n\n[Chorus]\n...",
    )

with right:
    extra = st.text_area(
        "Music direction",
        height=130,
        value="flute intro, warm piano, big cinematic chorus",
    )
    st.markdown("**Suggested structure:** `[Verse] [Pre-Chorus] [Chorus] [Bridge] [Outro]`")

    prompt = build_prompt(STYLES[style_name], extra, language_name)

    st.markdown("### 🎚️ Sound preview")
    st.write(f"**Language:** {language_name}")
    st.write("**Vocal:** Natural lead")
    st.write(f"**Style:** {style_name}")
    st.write(f"**Length:** {duration_min} min")
    st.caption(prompt)

generate = st.button("🎼 Generate song", type="primary", use_container_width=True)

if generate:
    lyrics = clean_lyrics(lyrics)

    if not lyrics:
        st.error("Please enter lyrics first.")
        st.stop()

    if len(lyrics) < 20:
        st.warning("The lyrics are very short. A fuller verse + chorus usually gives a better song.")

    duration_sec = duration_min * 60
    status = st.empty()

    # IMPORTANT:
    # We deliberately try several independent providers. ACE-Step is first
    # because it supports lyrics + vocals. If its shared ZeroGPU quota is gone,
    # the request moves on instead of showing a false 'generation finished'.
    providers = [
        (
            "ACE-Step 1.5",
            lambda: call_dynamic_gradio(
                ACE_SPACE, prompt, lyrics, duration_sec, LANGUAGES[language_name]
            ),
        ),
        (
            "Stable Audio 3",
            lambda: call_dynamic_gradio(
                STABLE_AUDIO_SPACE, prompt, "", min(duration_sec, 60), "en"
            ),
        ),
        (
            "MusicGen fallback",
            lambda: call_musicgen(prompt, duration_sec),
        ),
    ]

    if REPLICATE_TOKEN:
        providers.append(
            (
                "Replicate MusicGen fallback",
                lambda: call_replicate(prompt, duration_sec),
            )
        )

    final_audio = None
    errors = []

    for provider_name, provider_fn in providers:
        audio, err = try_provider(provider_name, provider_fn, status)
        if audio:
            final_audio = audio
            break
        errors.append((provider_name, err))

    if final_audio:
        st.balloons()
        st.success(f"🎉 Song generated successfully — provider: {provider_name}")
        st.audio(final_audio, format="audio/mpeg")
        filename = re.sub(r"[^A-Za-z0-9_-]+", "_", title.strip() or "racharlamusic_song")
        st.download_button(
            "⬇️ Download song",
            data=final_audio,
            file_name=f"{filename}.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )
    else:
        st.error("❌ All available music providers are currently unavailable.")
        with st.expander("Technical details"):
            for name, err in errors:
                st.write(f"**{name}:** {err}")
        st.info(
            "The app is now configured to fail over automatically. "
            "If every public free provider is out of GPU capacity, there is no "
            "reliable way for a Streamlit CPU server to synthesize a full song by itself."
        )

st.divider()
st.caption(
    "RacharlaMusic uses public AI generation services. Free GPU providers can have "
    "shared capacity limits; the app automatically tries the next provider when one fails."
)
