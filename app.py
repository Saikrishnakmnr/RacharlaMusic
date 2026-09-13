
import os
import re
import time
from pathlib import Path

import requests
import streamlit as st

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

# Public providers. The app tries them in order and automatically skips
# quota/capacity/API failures.
PROVIDERS = [
    ("ACE-Step 1.5", "ACE-Step/Ace-Step-v1.5"),
    ("MiniMax Music 3", "Upsampler/minimax-music3"),
]

HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN", ""))

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎵",
    layout="wide",
)

# ---------------------------------------------------------------------
# Original RacharlaMusic visual design
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp{font-family:Poppins,sans-serif;color:#fff;background:
radial-gradient(circle at 8% 4%,rgba(255,30,205,.22),transparent 27%),
radial-gradient(circle at 94% 8%,rgba(0,220,255,.18),transparent 28%),
radial-gradient(circle at 55% 90%,rgba(105,62,255,.22),transparent 34%),
linear-gradient(135deg,#06051a,#10134a 50%,#061c39);}
.block-container{max-width:1280px;padding-top:1rem}
.hero{border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.16);
box-shadow:0 25px 75px rgba(0,0,0,.48),0 0 45px rgba(255,35,205,.13);margin-bottom:22px}
.hero img{display:block;width:100%}
.glass{border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:22px;
background:linear-gradient(145deg,rgba(25,28,88,.86),rgba(6,20,57,.78));
box-shadow:0 20px 55px rgba(0,0,0,.34),inset 0 1px rgba(255,255,255,.06)}
.title{font-size:2.5rem;font-weight:800;background:linear-gradient(90deg,#fff,#ff4ed4,#7c62ff,#20e5ff);
-webkit-background-clip:text;color:transparent}
.muted{color:#bdbcdc}
.badge{display:inline-block;margin:4px;padding:6px 11px;border-radius:99px;background:rgba(255,255,255,.07);
border:1px solid rgba(255,255,255,.1);font-size:.78rem}
.tip{border-left:4px solid #ff35cf;border-radius:0 14px 14px 0;background:rgba(255,53,207,.07);padding:12px 15px}
.stButton>button{border:0!important;border-radius:16px!important;color:#fff!important;font-weight:800!important;
background:linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important;
box-shadow:0 12px 35px rgba(255,24,201,.3)!important;min-height:52px!important}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 18px 45px rgba(255,24,201,.42)!important}
div[data-testid="stTextArea"] textarea{background:rgba(4,8,35,.88)!important;color:white!important;
border-radius:18px!important;border:1px solid rgba(160,110,255,.45)!important}
div[data-baseweb="select"]>div{background:rgba(6,11,44,.9)!important;border-radius:14px!important}
.footer{text-align:center;color:#aaa9c9;padding:30px 0 8px}
</style>
""", unsafe_allow_html=True)

if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div class="muted">Your lyrics • AI melody • Natural singing • Your song</div>'
    '<div><span class="badge">🇮🇳 Telugu</span><span class="badge">🇬🇧 English</span>'
    '<span class="badge">🔀 Mixed</span><span class="badge">🎤 Vocals</span>'
    '<span class="badge">⬇️ MP3</span></div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar, lush strings, soft percussion, expressive natural singing, polished studio mix",
    "Romantic": "romantic Indian film song, intimate natural vocals, piano, acoustic guitar, lush strings, emotional melody, polished studio production",
    "Folk": "Telugu folk-inspired song, organic percussion, acoustic instruments, catchy traditional melody, energetic natural singing",
    "Mass": "high-energy Telugu commercial song, powerful natural vocals, punchy drums, bass, rhythmic hooks, cinematic production",
    "Sad": "emotional Indian ballad, expressive natural vocals, piano, strings, restrained drums, haunting memorable melody",
    "Cinematic": "grand Indian cinematic soundtrack, expressive natural vocals, orchestral strings, piano, percussion, dramatic build",
    "Lo-fi": "dreamy lo-fi Indian pop, intimate natural vocals, soft drums, warm keys, mellow bass",
    "Devotional": "devotional Indian melody, respectful natural vocals, flute, gentle percussion, uplifting arrangement",
    "Hip-hop": "Indian melodic hip-hop, natural sung hook, rhythmic vocal delivery, deep bass, crisp drums, modern production",
    "Rock": "Indian pop rock, natural expressive vocals, electric guitars, live drums, bass, strong melodic chorus",
    "Pop": "modern Indian pop, natural lead vocals, catchy melody, polished drums, bass, bright synths",
}
LANG = {"Telugu": "te", "English": "en", "Telugu + English": "te"}

# ---------------------------------------------------------------------
# Provider helpers
# ---------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_client(space_id):
    from gradio_client import Client
    kwargs = {}
    if HF_TOKEN:
        kwargs["hf_token"] = HF_TOKEN
    return Client(space_id, **kwargs)

@st.cache_data(ttl=180, show_spinner=False)
def get_api_info(space_id):
    client = get_client(space_id)
    try:
        return client.view_api(return_format="dict")
    except TypeError:
        return client.view_api()

def all_endpoints(info):
    result = []
    if not isinstance(info, dict):
        return result

    for bucket in ("named_endpoints", "unnamed_endpoints"):
        value = info.get(bucket, {})
        if isinstance(value, dict):
            for name, spec in value.items():
                result.append((str(name), spec if isinstance(spec, dict) else {}))
        elif isinstance(value, list):
            for spec in value:
                if isinstance(spec, dict):
                    result.append(
                        (str(spec.get("api_name") or spec.get("name") or "/unnamed"), spec)
                    )
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

def p_name(p):
    if not isinstance(p, dict):
        return str(p)
    return str(
        p.get("parameter_name")
        or p.get("name")
        or p.get("label")
        or p.get("component_label")
        or ""
    )

def choices_of(p):
    if not isinstance(p, dict):
        return []
    for key in ("choices", "enum", "options", "values"):
        value = p.get(key)
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

def endpoint_score(name, spec):
    pn = text_of(params_of(spec))
    rn = text_of(returns_of(spec))
    nn = str(name).lower()
    score = 0

    # Strong generation signals.
    if "lyrics" in pn:
        score += 12
    if any(x in pn for x in ("caption", "prompt", "style", "simple_query", "text_prompt")):
        score += 8
    if any(x in pn for x in ("duration", "length")):
        score += 3
    if any(x in rn for x in ("audio", "file", "filepath", "filedata", "waveform")):
        score += 12
    if any(x in nn for x in ("generate", "generation", "music", "infer", "predict", "create")):
        score += 5

    # Penalize utility endpoints.
    if any(x in nn for x in ("load", "init", "refresh", "model", "checkpoint", "clear", "stop")):
        score -= 15
    if "lyrics" not in pn and "prompt" not in pn and "caption" not in pn and "style" not in pn:
        score -= 4

    return score

def choose_endpoint(info, preferred_terms=()):
    eps = all_endpoints(info)
    scored = []
    for name, spec in eps:
        score = endpoint_score(name, spec)
        blob = (str(name) + " " + text_of(spec)).lower()
        for term in preferred_terms:
            if term.lower() in blob:
                score += 10
        scored.append((score, name, spec))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] <= 0:
        raise RuntimeError("No usable music-generation endpoint was exposed by this provider.")
    return scored[0][1], scored[0][2]

def choose_value(p, *, lyrics, caption, language, duration, provider):
    name = p_name(p).lower()
    choices = choices_of(p)
    default = p.get("default") if isinstance(p, dict) else None

    def pick(*wanted):
        for wanted_value in wanted:
            if wanted_value is None:
                continue
            for c in choices:
                if str(c).lower() == str(wanted_value).lower():
                    return c
        return choices[0] if choices else None

    # ACE-Step.
    if "generation_mode" in name or name in ("mode", "generationmode"):
        for wanted in ("custom", "simple", "text2music"):
            for c in choices:
                if str(c).lower() == wanted.lower():
                    return c
        return choices[0] if choices else "custom"

    if "lyrics" in name or name in ("lrc", "lyric"):
        return lyrics
    if any(x in name for x in ("caption", "sample_query", "description", "desc", "query")):
        return caption
    if "duration" in name or "length" in name:
        return float(duration)
    if "vocal_language" in name:
        return language
    if name in ("language", "lang"):
        return language if language in choices else pick("English", "en")
    if "audio_format" in name or name == "format":
        return pick("mp3", "wav") or "mp3"
    if name in ("thinking", "think", "use_thinking"):
        return False
    if "instrumental" in name:
        return False
    if "task_type" in name:
        return pick("text2music", "text-to-music") or "text2music"
    if "inference_steps" in name or name == "steps":
        return 8
    if "seed" in name:
        return 0
    if "batch_size" in name:
        return 1
    if name == "bpm" or name.endswith("_bpm"):
        return None
    if "key_scale" in name or "keyscale" in name:
        return ""
    if "time_signature" in name or "timesignature" in name:
        return ""
    if "use_format" in name:
        return False
    if "random_seed" in name:
        return True
    if "guidance_scale" in name:
        return 7.0
    if "lm_temperature" in name:
        return 0.85
    if "lm_cfg_scale" in name:
        return 2.5

    # YuE2.
    if provider == "yue2":
        if name == "style":
            return caption
        if "planning_mode" in name:
            return pick("full", "melody", "off") or "full"
        if "render_quality" in name:
            return pick(16, 32) or 16
        if name == "seed":
            return 42

    # DiffRhythm-style endpoints.
    if "current_prompt_type" in name:
        return "text"
    if name == "text_prompt":
        return caption
    if "file_type" in name:
        return pick("mp3", "wav") or "mp3"
    if "randomize_seed" in name:
        return True
    if "cfg_strength" in name:
        return 1.3
    if "odeint_method" in name:
        return pick("euler", "midpoint", "rk4") or "euler"

    # Main model selectors.
    if "model" in name and "path" not in name:
        if choices:
            for wanted in ("acestep-v15-turbo", "small-music", "small", "medium"):
                for c in choices:
                    if wanted.lower() in str(c).lower():
                        return c
            return choices[0]
        return None

    # Generic radio/dropdown.
    if choices:
        if default in choices:
            return default
        return choices[0]

    if default is not None:
        return default

    schema_text = text_of(p)
    if "bool" in schema_text:
        return False
    if "float" in schema_text or "number" in schema_text:
        return 0.0
    if "int" in schema_text:
        return 0
    return ""

def extract_audio(value):
    """Find an actual audio file/URL in Gradio's nested return objects."""
    if value is None:
        return None

    if isinstance(value, (bytes, bytearray)):
        return bytes(value)

    if isinstance(value, dict):
        # Ignore UI update objects.
        if "__type__" in value and value.get("__type__") == "update":
            return None

        mime = str(value.get("mime_type") or value.get("mime") or "").lower()
        candidates = []
        for key in ("path", "url", "file", "name"):
            v = value.get(key)
            if isinstance(v, str):
                candidates.append(v)

        for item in candidates:
            if item.startswith("http://") or item.startswith("https://"):
                data = download_url(item, mime)
                if data:
                    return data
            elif os.path.isfile(item):
                try:
                    return Path(item).read_bytes()
                except Exception:
                    pass

        for child in value.values():
            found = extract_audio(child)
            if found:
                return found
        return None

    if isinstance(value, (list, tuple)):
        for child in value:
            found = extract_audio(child)
            if found:
                return found
        return None

    if isinstance(value, str):
        if os.path.isfile(value):
            try:
                return Path(value).read_bytes()
            except Exception:
                pass
        if value.startswith("http://") or value.startswith("https://"):
            return download_url(value)
    return None

def download_url(url, mime=""):
    try:
        response = requests.get(url, timeout=180)
        response.raise_for_status()
        ctype = (response.headers.get("content-type") or mime or "").lower()
        lower = url.lower()
        if (
            "audio" in ctype
            or any(ext in lower for ext in (".mp3", ".wav", ".flac", ".ogg", ".m4a"))
        ):
            return response.content
    except Exception:
        return None
    return None


def generate_ace_http(lyrics, caption, language, duration):
    """Official ACE-Step async HTTP API fallback."""
    bases = ["https://ace-step-ace-step-v1-5.hf.space"]
    headers = {"Content-Type": "application/json"}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    payload = {
        "caption": caption[:512],
        "lyrics": lyrics[:4096],
        "thinking": False,
        "vocal_language": language,
        "audio_format": "mp3",
        "audio_duration": max(10, min(float(duration), 600)),
        "model": "acestep-v15-turbo",
        "inference_steps": 8,
        "use_format": False,
        "task_type": "text2music",
    }

    last_error = None
    for base in bases:
        try:
            r = requests.post(
                base + "/v1/music/generate",
                json=payload,
                headers=headers,
                timeout=45,
            )
            if r.status_code in (404, 405):
                last_error = f"HTTP {r.status_code}"
                continue
            r.raise_for_status()
            data = r.json()

            job_id = data.get("job_id")
            if not job_id:
                audio = extract_audio(data)
                if audio:
                    return audio
                raise RuntimeError(str(data)[:1000])

            for _ in range(180):
                q = requests.get(
                    base + f"/v1/jobs/{job_id}",
                    headers=headers,
                    timeout=30,
                )
                q.raise_for_status()
                status_data = q.json()
                status = str(status_data.get("status", "")).lower()

                if status == "succeeded":
                    result = status_data.get("result", status_data)
                    audio = extract_audio(result)
                    if audio:
                        return audio

                    paths = []
                    def collect(x):
                        if isinstance(x, dict):
                            for k, v in x.items():
                                if k in ("path", "audio_path", "url") and isinstance(v, str):
                                    paths.append(v)
                                else:
                                    collect(v)
                        elif isinstance(x, (list, tuple)):
                            for v in x:
                                collect(v)

                    collect(result)
                    for p in paths:
                        if p.startswith("http"):
                            audio = download_url(p, "audio/mpeg")
                            if audio:
                                return audio
                        else:
                            u = base + "/v1/audio?path=" + requests.utils.quote(p, safe="")
                            audio = download_url(u, "audio/mpeg")
                            if audio:
                                return audio

                    raise RuntimeError("ACE-Step returned no downloadable audio.")

                if status in ("failed", "error", "cancelled", "canceled"):
                    raise RuntimeError(
                        str(status_data.get("error") or status_data)[:1200]
                    )

                time.sleep(2)

            raise RuntimeError("ACE-Step job timed out.")

        except Exception as exc:
            last_error = str(exc)

    raise RuntimeError(f"ACE-Step HTTP API unavailable: {last_error}")


def generate_minimax_verified(lyrics, caption, duration):
    """
    Verified plain endpoint from Upsampler/minimax-music3:
    generate_music(description, duration, seed, instrumental, lyrics)
    """
    client = get_client("Upsampler/minimax-music3")
    safe_duration = max(5, min(int(duration), 300))

    result = client.predict(
        caption,
        safe_duration,
        0,       # seed: minimum is 0
        False,   # instrumental
        lyrics,
        api_name="generate_music",
    )

    audio = extract_audio(result)
    if not audio:
        raise RuntimeError("MiniMax Music 3 returned no downloadable audio.")
    return audio


def generate_with_gradio(space_id, provider, lyrics, caption, language, duration):
    client = get_client(space_id)
    info = get_api_info(space_id)

    preferred = ()
    if provider == "ACE-Step 1.5":
        preferred = ("generate", "music")
    elif provider == "MiniMax Music 3":
        preferred = ("generate", "music", "stream")
    elif provider == "YuE2-3B":
        preferred = ("generate", "song")
    elif provider == "MusicGen":
        preferred = ("generate", "music", "predict")

    endpoint, spec = choose_endpoint(info, preferred)
    params = params_of(spec)

    # Some providers expose a fixed duration. The UI still keeps the user's
    # requested length; the provider gets its own safe maximum.
    provider_duration = duration
    if provider == "YuE2-3B":
        provider_duration = min(duration, 240)
    elif provider == "MusicGen":
        provider_duration = min(duration, 30)

    values = [
        choose_value(
            p,
            lyrics=lyrics,
            caption=caption,
            language=language,
            duration=provider_duration,
            provider="yue2" if provider == "YuE2-3B" else provider.lower(),
        )
        for p in params
    ]

    try:
        result = client.predict(*values, api_name=endpoint)
    except Exception as first_error:
        # Retry once with parameter-name kwargs when available.
        kwargs = {}
        for p, value in zip(params, values):
            pname = p_name(p)
            if pname:
                kwargs[pname] = value
        if not kwargs:
            raise first_error
        result = client.predict(api_name=endpoint, **kwargs)

    audio = extract_audio(result)
    if not audio:
        raise RuntimeError(
            f"{provider} completed an API call but returned no downloadable audio file."
        )
    return audio

def provider_error_is_temporary(error_text):
    text = (error_text or "").lower()
    return any(
        token in text
        for token in (
            "zerogpu quota",
            "quota",
            "gpu task aborted",
            "capacity",
            "queue",
            "timeout",
            "503",
            "502",
            "504",
            "runtime error",
            "space is sleeping",
        )
    )

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language = st.selectbox("🌐 Lyrics", list(LANG), index=0)
    vocal = st.selectbox("🎤 Vocal", ["Natural lead", "Female", "Male", "Duet"])
    style = st.selectbox("🎼 Style", list(STYLES), index=0)
    duration_label = st.select_slider(
        "⏱️ Length",
        ["1 min", "2 min", "3 min", "4 min", "5 min", "6 min"],
        value="4 min",
    )
    duration = int(duration_label.split()[0]) * 60
    st.markdown("---")
    st.info(
        "RacharlaMusic automatically tries several public music AI providers. "
        "If one provider has no GPU capacity, the next provider is tried."
    )

# ---------------------------------------------------------------------
# Main creator UI
# ---------------------------------------------------------------------
c1, c2 = st.columns([1.35, 0.75], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Create your song")

    lyrics = st.text_area(
        "Lyrics",
        height=330,
        max_chars=8000,
        placeholder="[Verse 1]\nనీ కోసం నా గుండెలో...\n\n[Pre-Chorus]\n...\n\n[Chorus]\nYou are my light...",
    )
    title = st.text_input("🎧 Song title", placeholder="My Racharla Song")
    extra = st.text_input(
        "🎹 Extra music direction",
        value="flute intro, warm piano, big cinematic chorus",
    )

    st.markdown(
        '<div class="tip">💡 Better structure: use [Verse], [Pre-Chorus], '
        '[Chorus], [Bridge], [Outro].</div>',
        unsafe_allow_html=True,
    )
    generate = st.button("✨  GENERATE MY SONG  🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.markdown(
        f"**Language:** {language}<br>"
        f"**Vocal:** {vocal}<br>"
        f"**Style:** {style}<br>"
        f"**Length:** {duration_label}",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="muted">{STYLES[style]}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Generation + automatic fallback
# ---------------------------------------------------------------------
if generate:
    if not lyrics.strip():
        st.warning("Please paste your lyrics first.")
        st.stop()

    vocal_text = {
        "Natural lead": "natural human-like lead singing, expressive phrasing, clear diction",
        "Female": "natural human-like female lead singing, expressive phrasing, clear diction",
        "Male": "natural human-like male lead singing, expressive phrasing, clear diction",
        "Duet": "natural human-like male and female duet singing, expressive harmonies",
    }[vocal]

    caption = (
        f"{STYLES[style]}, {vocal_text}, {extra}, "
        f"professional studio mix, strong melodic chorus, no spoken narration"
    )

    status = st.empty()
    progress = st.progress(0)
    errors = []
    final_audio = None
    used_provider = None

    for index, (provider_name, space_id) in enumerate(PROVIDERS):
        status.info(
            f"🎼 Provider {index + 1}/{len(PROVIDERS)}: "
            f"Trying **{provider_name}**..."
        )

        try:
            with st.spinner(
                f"Generating with {provider_name}. "
                "Public GPU services can take a little time..."
            ):
                if provider_name == "ACE-Step 1.5":
                    try:
                        audio = generate_with_gradio(
                            space_id,
                            provider_name,
                            lyrics,
                            caption,
                            LANG[language],
                            duration,
                        )
                    except Exception as first_error:
                        # If the Gradio UI signature changes, use ACE-Step's
                        # documented HTTP async generation API.
                        if "Value:" in str(first_error) or "not in the list of choices" in str(first_error):
                            audio = generate_ace_http(
                                lyrics, caption, LANG[language], duration
                            )
                        else:
                            raise
                elif provider_name == "MiniMax Music 3":
                    audio = generate_minimax_verified(
                        lyrics, caption, duration
                    )
                else:
                    audio = generate_with_gradio(
                        space_id,
                        provider_name,
                        lyrics,
                        caption,
                        LANG[language],
                        duration,
                    )

            if audio:
                final_audio = audio
                used_provider = provider_name
                progress.progress(100)
                status.success(f"🎉 Song generated with {provider_name}!")
                break

        except Exception as exc:
            message = str(exc)
            errors.append((provider_name, message))

            if provider_error_is_temporary(message):
                status.warning(
                    f"⚠️ {provider_name} is busy/unavailable. "
                    "Automatically trying the next provider..."
                )
            else:
                status.warning(
                    f"⚠️ {provider_name} failed. "
                    "Automatically trying the next provider..."
                )

        progress.progress(int(((index + 1) / len(PROVIDERS)) * 100))

    if final_audio:
        # Store the audio so it remains visible after Streamlit reruns.
        st.session_state["audio"] = final_audio
        st.session_state["title"] = title.strip() or "RacharlaMusic Song"
        st.session_state["provider"] = used_provider
    else:
        status.error("❌ All available generation providers failed.")
        with st.expander("Technical details"):
            for name, message in errors:
                st.write(f"**{name}:**")
                st.code(message[:1500])

        st.info(
            "The important change is that a single provider's ZeroGPU quota "
            "no longer stops the app. Each provider is tried independently."
        )

# ---------------------------------------------------------------------
# Audio preview + download -- intentionally kept in the original UI
# ---------------------------------------------------------------------
if "audio" in st.session_state:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.caption(
        f"Generated by **{st.session_state.get('provider', 'AI music provider')}**"
    )

    # Preview button / player.
    st.audio(st.session_state["audio"], format="audio/mpeg")

    fname = (
        re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            st.session_state.get("title", "RacharlaMusic Song"),
        ).strip("_")
        or "RacharlaMusic_Song"
    )

    st.download_button(
        "⬇️ DOWNLOAD MP3",
        data=st.session_state["audio"],
        file_name=f"{fname}.mp3",
        mime="audio/mpeg",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer">🎵 <b>RacharlaMusic</b> • Create • Sing • Share • Anytime'
    '<br>Powered by <b>RacharlaGPT.in</b></div>',
    unsafe_allow_html=True,
)
