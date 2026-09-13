
import io
import os
import re
import time
from pathlib import Path

import streamlit as st

APP_NAME = "RacharlaMusic"
SPACE_ID = "ACE-Step/Ace-Step-v1.5"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(page_title="RacharlaMusic", page_icon="🎵", layout="wide")

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

st.markdown('<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
            '<div class="muted">Your lyrics • AI melody • Natural singing • Your song</div>'
            '<div><span class="badge">🇮🇳 Telugu</span><span class="badge">🇬🇧 English</span>'
            '<span class="badge">🔀 Mixed</span><span class="badge">🎤 Vocals</span>'
            '<span class="badge">⬇️ MP3</span></div></div><br>', unsafe_allow_html=True)

STYLES = {
"Melody":"beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar, lush strings, soft percussion, expressive natural singing, polished studio mix",
"Romantic":"romantic Indian film song, intimate natural vocals, piano, acoustic guitar, lush strings, emotional melody, polished studio production",
"Folk":"Telugu folk-inspired song, organic percussion, acoustic instruments, catchy traditional melody, energetic natural singing",
"Mass":"high-energy Telugu commercial song, powerful natural vocals, punchy drums, bass, rhythmic hooks, cinematic production",
"Sad":"emotional Indian ballad, expressive natural vocals, piano, strings, restrained drums, haunting memorable melody",
"Cinematic":"grand Indian cinematic soundtrack, expressive natural vocals, orchestral strings, piano, percussion, dramatic build",
"Lo-fi":"dreamy lo-fi Indian pop, intimate natural vocals, soft drums, warm keys, mellow bass",
"Devotional":"devotional Indian melody, respectful natural vocals, flute, gentle percussion, uplifting arrangement",
"Hip-hop":"Indian melodic hip-hop, natural sung hook, rhythmic vocal delivery, deep bass, crisp drums, modern production",
"Rock":"Indian pop rock, natural expressive vocals, electric guitars, live drums, bass, strong melodic chorus",
"Pop":"modern Indian pop, natural lead vocals, catchy melody, polished drums, bass, bright synths"
}
LANG={"Telugu":"te","English":"en","Telugu + English":"te"}

@st.cache_resource(show_spinner=False)
def get_client():
    try:
        from gradio_client import Client
        return Client(SPACE_ID)
    except Exception as e:
        raise RuntimeError(f"Could not connect to the free music service: {e}")

def safe_view_api(client):
    try:
        info=client.view_api(return_format="dict")
        return info
    except TypeError:
        return client.view_api()
    except Exception as e:
        raise RuntimeError(f"Could not read the music service API: {e}")


def _textify(obj):
    """Turn an API schema object into searchable text."""
    try:
        return str(obj).lower()
    except Exception:
        return ""

def _param_list(spec):
    if not isinstance(spec, dict):
        return []
    for key in ("parameters", "inputs"):
        val = spec.get(key)
        if isinstance(val, list):
            return val
    return []

def _return_list(spec):
    if not isinstance(spec, dict):
        return []
    for key in ("returns", "outputs"):
        val = spec.get(key)
        if isinstance(val, list):
            return val
    return []

def endpoint_candidates(info):
    """Return only plausible *generation* endpoints.

    The ACE-Step Space exposes many Gradio events (load/init/config changes).
    Picking the first endpoint containing 'generate' is unsafe because those
    events can return UI update dictionaries rather than audio.
    """
    eps = []
    if not isinstance(info, dict):
        return eps

    for container_key in ("named_endpoints", "unnamed_endpoints"):
        container = info.get(container_key, {})
        if not isinstance(container, dict):
            continue
        for name, spec in container.items():
            params = _param_list(spec)
            returns = _return_list(spec)
            ptxt = _textify(params)
            rtxt = _textify(returns)
            ntxt = _textify(name)
            alltxt = f"{ntxt} {ptxt} {rtxt}"

            # A real music generation event should accept lyrics/caption and
            # normally duration/audio-related parameters.
            has_text = ("lyrics" in ptxt or "lyric" in ptxt)
            has_prompt = any(x in ptxt for x in ("caption", "prompt", "description", "sample_query"))
            has_duration = "duration" in ptxt
            has_audio_output = any(
                x in rtxt for x in ("audio", "filepath", "filedata", "audio_url")
            )
            bad_event = any(
                x in alltxt for x in (
                    "initialize", "initialise", "load_model", "load model",
                    "change_model", "change model", "checkpoint", "refresh"
                )
            )

            score = 0
            if has_text: score += 40
            if has_prompt: score += 25
            if has_duration: score += 15
            if has_audio_output: score += 40
            if "generate" in ntxt: score += 20
            if "music" in ntxt: score += 10
            if "audio" in ntxt: score += 5
            if bad_event: score -= 60

            if has_text or has_prompt or has_audio_output:
                eps.append((score, name, spec))

    eps.sort(key=lambda x: x[0], reverse=True)
    return eps

def choose_endpoint(info):
    eps = endpoint_candidates(info)
    if not eps:
        raise RuntimeError(
            "Could not find the ACE-Step music generation endpoint. "
            "The Hugging Face Space API may have changed."
        )

    # Prefer an endpoint that both consumes lyrics/prompt and returns audio.
    for score, name, spec in eps:
        ptxt = _textify(_param_list(spec))
        rtxt = _textify(_return_list(spec))
        if ("lyric" in ptxt or "caption" in ptxt or "prompt" in ptxt) and \
           any(x in rtxt for x in ("audio", "filepath", "filedata")):
            return name, spec

    return eps[0][1], eps[0][2]

def spec_params(spec):
    return _param_list(spec)

def _choice_values(p):
    choices = p.get("choices") or p.get("enum") or p.get("options")
    if isinstance(choices, dict):
        choices = list(choices.keys())
    if isinstance(choices, (list, tuple)):
        # Gradio sometimes returns [["value","label"], ...]
        out = []
        for c in choices:
            if isinstance(c, (list, tuple)) and c:
                out.append(c[0])
            else:
                out.append(c)
        return out
    return []

def make_value(p, lyrics, caption, language, duration, audio_format):
    name = str(
        p.get("parameter_name")
        or p.get("name")
        or p.get("label")
        or p.get("component_label")
        or ""
    ).lower().strip()

    default = p.get("default", None)
    choices = _choice_values(p)

    # Text inputs first.
    if "lyrics" in name or name == "lyric":
        return lyrics
    if any(x in name for x in ("caption", "prompt", "description", "sample_query", "query")):
        return caption

    if "duration" in name:
        return float(duration)
    if "vocal_language" in name or name == "language" or name.endswith("_language"):
        return language
    if "audio_format" in name:
        return audio_format
    if name in ("thinking", "think", "use_llm_thinking"):
        return True
    if "instrumental" in name:
        return False
    if "inference_steps" in name or name in ("steps", "num_inference_steps"):
        return 8
    if name in ("seed", "seeds"):
        return -1
    if "batch_size" in name:
        return 1
    if name in ("bpm",):
        return None
    if name in ("key_scale", "keyscale"):
        return ""
    if name in ("time_signature", "timesignature"):
        return ""
    if name in ("task_type", "task"):
        return "text2music" if not choices or "text2music" in choices else choices[0]

    # IMPORTANT: do not assume every parameter containing "model" is the main
    # DiT model. The Space has multiple model-related controls.
    if "model" in name:
        preferred = "acestep-v15-turbo"
        if preferred in choices:
            return preferred
        if "xl" in name:
            for c in choices:
                if "xl" in str(c).lower() and "turbo" in str(c).lower():
                    return c
        if choices:
            return choices[0]
        if default is not None:
            return default

    if "use_format" in name:
        return True
    if name == "format":
        return audio_format if "audio" in name else (choices[0] if choices else True)
    if "lm_temperature" in name:
        return 0.85
    if "lm_cfg_scale" in name:
        return 2.0
    if "lm_top_k" in name:
        return 0
    if "lm_top_p" in name:
        return 0.9
    if "lm_repetition_penalty" in name:
        return 1.0
    if "lm_negative_prompt" in name:
        return ""
    if "use_cot" in name or "constrained_decoding" in name or "use_constrained_decoding" in name:
        return True
    if name == "guidance_scale":
        return 7.0
    if name == "shift":
        return 3.0
    if name == "infer_method":
        return "ode"
    if name in ("random_seed", "use_random_seed"):
        return True
    if name == "timesteps":
        return ""
    if "audio_cover_strength" in name:
        return 1.0
    if "repainting_start" in name:
        return 0.0
    if "repainting_end" in name:
        return -1.0
    if "track_name" in name:
        return None
    if "complete_track" in name:
        return []

    # For any dropdown/radio we don't explicitly understand, NEVER send an
    # empty string if the API provides legal choices.
    if choices:
        if default in choices:
            return default
        return choices[0]

    if default is not None:
        return default

    typ = p.get("type", {})
    if isinstance(typ, dict):
        t = str(typ.get("type", "")).lower()
        if "bool" in t:
            return False
        if "number" in t or "integer" in t:
            return 0

    # Last-resort value for optional text fields.
    return ""

def call_generation(client, lyrics, caption, language, duration):
    info = safe_view_api(client)
    endpoint, spec = choose_endpoint(info)
    params = spec_params(spec)

    if not params:
        raise RuntimeError(f"Generation endpoint {endpoint!r} exposes no input parameters.")

    values = [make_value(p, lyrics, caption, language, duration, "mp3") for p in params]

    # Use positional arguments because this is the most compatible path across
    # Gradio Client versions.
    result = client.predict(*values, api_name=endpoint)
    return result, endpoint, spec

def extract_audio(result):
    """Recursively find an actual audio file/URL, ignoring Gradio UI updates."""
    audio_exts = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".webm")

    if isinstance(result, dict):
        # FileData / audio component dictionaries.
        for key in ("path", "url", "audio_url", "name"):
            v = result.get(key)
            if isinstance(v, str):
                if v.startswith("http") or os.path.exists(v) or v.lower().split("?")[0].endswith(audio_exts):
                    return v
        for v in result.values():
            found = extract_audio(v)
            if found:
                return found

    elif isinstance(result, (list, tuple)):
        for v in result:
            found = extract_audio(v)
            if found:
                return found

    elif isinstance(result, str):
        clean = result.split("?")[0].lower()
        if result.startswith("http") or os.path.exists(result) or clean.endswith(audio_exts):
            return result

    return None

with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language=st.selectbox("🌐 Lyrics",list(LANG),index=0)
    vocal=st.selectbox("🎤 Vocal",["Natural lead","Female","Male","Duet"])
    style=st.selectbox("🎼 Style",list(STYLES),index=0)
    duration_label=st.select_slider("⏱️ Length",["1 min","2 min","3 min","4 min","5 min","6 min"],value="4 min")
    duration=int(duration_label.split()[0])*60
    st.markdown("---")
    st.info("No API key is required by this version. Generation uses the public ACE-Step Hugging Face Space. Free ZeroGPU availability can vary.")

c1,c2=st.columns([1.35,.75],gap="large")
with c1:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("### ✍️ Create your song")
    lyrics=st.text_area("Lyrics",height=330,max_chars=8000,placeholder="[Verse 1]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nYou are my light...")
    title=st.text_input("🎧 Song title",placeholder="My Racharla Song")
    extra=st.text_input("🎹 Extra music direction",placeholder="flute intro, warm piano, big cinematic chorus")
    st.markdown('<div class="tip">💡 Better structure: use [Verse], [Pre-Chorus], [Chorus], [Bridge], [Outro].</div>',unsafe_allow_html=True)
    generate=st.button("✨  GENERATE MY SONG  🎵",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.markdown(f"**Language:** {language}<br>**Vocal:** {vocal}<br>**Style:** {style}<br>**Length:** {duration_label}",unsafe_allow_html=True)
    st.markdown(f'<p class="muted">{STYLES[style]}</p>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

if generate:
    if not lyrics.strip():
        st.warning("Please paste your lyrics first.")
        st.stop()

    vocal_text={
        "Natural lead":"natural human-like lead singing, expressive phrasing, clear diction",
        "Female":"natural human-like female lead singing, expressive phrasing, clear diction",
        "Male":"natural human-like male lead singing, expressive phrasing, clear diction",
        "Duet":"natural human-like male and female duet singing, expressive harmonies"
    }[vocal]
    caption=f"{STYLES[style]}, {vocal_text}, {extra}, professional studio mix, strong melodic chorus, no spoken narration"
    status=st.empty()
    try:
        status.info("🔌 Connecting to the free AI music Space...")
        client=get_client()
        status.info("🎼 Sending your lyrics to ACE-Step 1.5...")
        with st.spinner("🎵 Generating your song... this can take time on a free GPU queue."):
            result, endpoint_used, endpoint_spec = call_generation(
                client, lyrics, caption, LANG[language], duration
            )
        status.success("🎉 Generation finished!")

        audio_path=extract_audio(result)
        if audio_path and os.path.exists(audio_path):
            data=Path(audio_path).read_bytes()
        elif audio_path and audio_path.startswith("http"):
            import requests
            rr=requests.get(audio_path,timeout=180)
            rr.raise_for_status()
            data=rr.content
        else:
            st.write(result)
            st.error("The music service returned a result, but no downloadable audio file could be identified.")
            st.stop()

        st.session_state["audio"]=data
        st.session_state["title"]=title.strip() or "RacharlaMusic Song"
    except Exception as e:
        st.error("❌ The free music service could not generate the song.")
        st.code(str(e))
        st.info("This is usually a temporary Hugging Face/ZeroGPU queue or API availability problem—not a problem with your lyrics.")

if "audio" in st.session_state:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.audio(st.session_state["audio"],format="audio/mpeg")
    fname=re.sub(r"[^A-Za-z0-9_-]+","_",st.session_state["title"]).strip("_") or "RacharlaMusic_Song"
    st.download_button("⬇️ DOWNLOAD MP3",st.session_state["audio"],file_name=f"{fname}.mp3",mime="audio/mpeg",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown('<div class="footer">🎵 <b>RacharlaMusic</b> • Create • Sing • Share • Anytime<br>Powered by <b>RacharlaGPT.in</b></div>',unsafe_allow_html=True)
