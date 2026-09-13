import io
import json
import time
import html
import re
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st

# ============================================================
# RacharlaMusic - Streamlit AI Song Generator
# ============================================================

APP_NAME = "RacharlaMusic"
POWERED_BY = "RacharlaGPT.in"

# Public ACE-Step 1.5 Space API.
# No API key is required by this app.
# The public service can have queue/quota/cold-start limits.
ACE_BASE = "https://ace-step-ace-step-v1-5.hf.space"
GENERATE_URL = f"{ACE_BASE}/v1/music/generate"

ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(
    page_title="RacharlaMusic — AI Song Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# CSS / Visual design
# ---------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
    --bg1:#07051c;
    --bg2:#11104a;
    --card:rgba(14,18,65,.78);
    --line:rgba(255,255,255,.15);
    --pink:#ff28c8;
    --purple:#7a4dff;
    --cyan:#00d9ff;
    --gold:#ffbf3f;
    --text:#f7f8ff;
    --muted:#b8b8d9;
}

html, body, [class*="css"] {
    font-family:'Poppins',sans-serif;
}

.stApp {
    background:
      radial-gradient(circle at 10% 5%, rgba(255,42,200,.20), transparent 28%),
      radial-gradient(circle at 90% 10%, rgba(0,217,255,.17), transparent 30%),
      radial-gradient(circle at 50% 80%, rgba(122,77,255,.20), transparent 35%),
      linear-gradient(135deg,var(--bg1),var(--bg2) 52%,#071a38);
    color:var(--text);
}

.block-container {
    max-width:1280px;
    padding-top:1.2rem;
    padding-bottom:3rem;
}

section[data-testid="stSidebar"] {
    background:
      linear-gradient(180deg,rgba(20,8,62,.98),rgba(3,17,50,.98));
    border-right:1px solid rgba(255,255,255,.10);
}

.hero {
    position:relative;
    overflow:hidden;
    border-radius:30px;
    border:1px solid rgba(255,255,255,.16);
    box-shadow:0 25px 70px rgba(0,0,0,.45), 0 0 45px rgba(255,40,200,.14);
    margin-bottom:24px;
    background:#090b2a;
}
.hero img {
    width:100%;
    display:block;
    border-radius:30px;
}
.hero-glow {
    position:absolute;
    inset:auto -15% -80px -15%;
    height:150px;
    background:radial-gradient(ellipse,rgba(255,35,206,.42),transparent 65%);
    pointer-events:none;
}

.brand-card {
    border:1px solid rgba(255,255,255,.13);
    border-radius:24px;
    padding:20px;
    background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.025));
    box-shadow:0 18px 50px rgba(0,0,0,.28);
    backdrop-filter:blur(12px);
    margin-bottom:18px;
}

.title-gradient {
    font-size:2.4rem;
    line-height:1.05;
    font-weight:800;
    background:linear-gradient(90deg,#fff,#ff5bd6,#7c67ff,#29e9ff);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
}

.subtitle {
    color:var(--muted);
    margin-top:8px;
    font-size:.98rem;
}

.section-title {
    font-size:1.25rem;
    font-weight:800;
    margin:6px 0 12px;
}

.glass {
    border:1px solid var(--line);
    border-radius:24px;
    padding:22px;
    background:linear-gradient(145deg,rgba(26,28,88,.86),rgba(8,20,58,.76));
    box-shadow:0 18px 50px rgba(0,0,0,.34), inset 0 1px rgba(255,255,255,.06);
    backdrop-filter:blur(14px);
}

.badge-row {
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    margin:8px 0 14px;
}
.badge {
    padding:6px 11px;
    border-radius:999px;
    background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.10);
    color:#eee;
    font-size:.78rem;
}

div[data-testid="stTextArea"] textarea {
    background:rgba(4,8,35,.82)!important;
    color:#fff!important;
    border:1px solid rgba(160,110,255,.45)!important;
    border-radius:18px!important;
    box-shadow:0 0 0 1px rgba(255,40,200,.08), 0 12px 30px rgba(0,0,0,.25)!important;
}

div[data-baseweb="select"] > div {
    background:rgba(6,11,44,.86)!important;
    border:1px solid rgba(255,255,255,.14)!important;
    border-radius:14px!important;
}

.stButton > button {
    border:0!important;
    border-radius:16px!important;
    min-height:52px!important;
    font-weight:800!important;
    font-size:1rem!important;
    color:#fff!important;
    background:linear-gradient(90deg,#ff19c8,#8d4dff,#00cfff)!important;
    box-shadow:0 10px 30px rgba(255,25,200,.28),0 0 28px rgba(0,207,255,.13)!important;
    transition:transform .18s ease, box-shadow .18s ease!important;
}
.stButton > button:hover {
    transform:translateY(-2px) scale(1.01);
    box-shadow:0 16px 42px rgba(255,25,200,.40),0 0 35px rgba(0,207,255,.20)!important;
}

.download-wrap {
    padding-top:8px;
}

.metric {
    text-align:center;
    border-radius:18px;
    padding:15px 10px;
    background:rgba(255,255,255,.055);
    border:1px solid rgba(255,255,255,.09);
}
.metric .big {font-size:1.5rem;font-weight:800;}
.metric .small {font-size:.72rem;color:var(--muted);}

.tip {
    border-left:4px solid #ff3bd4;
    padding:12px 15px;
    background:rgba(255,59,212,.07);
    border-radius:0 14px 14px 0;
    color:#e8e8ff;
    font-size:.86rem;
}

.footer {
    text-align:center;
    color:#aaa9ca;
    padding:28px 0 8px;
    font-size:.82rem;
}
.footer strong {
    color:#ff5bd6;
}

audio {
    width:100%;
    margin-top:10px;
}

@media (max-width: 800px) {
  .title-gradient {font-size:1.75rem;}
  .block-container {padding-left:.75rem;padding-right:.75rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Session state
# ---------------------------
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "song_meta" not in st.session_state:
    st.session_state.song_meta = None

# ---------------------------
# Helpers
# ---------------------------
STYLE_PROMPTS = {
    "Melody": "beautiful Indian melodic pop ballad, memorable melody, warm acoustic piano, lush strings, soft percussion, expressive natural lead singing",
    "Romantic": "romantic Indian film song, warm intimate natural vocals, piano, acoustic guitar, lush strings, emotional melody, polished studio production",
    "Folk": "Telugu folk inspired song, organic percussion, acoustic instruments, catchy traditional melody, energetic natural singing",
    "Mass": "high-energy Telugu commercial mass song, powerful natural vocals, punchy drums, bass, rhythmic hooks, cinematic production",
    "Sad": "emotional Indian sad ballad, expressive natural vocals, piano, strings, restrained drums, haunting memorable melody",
    "Cinematic": "grand Indian cinematic soundtrack, expressive natural vocals, orchestral strings, piano, percussion, dramatic build and polished mix",
    "Lo-fi": "dreamy lo-fi Indian pop, intimate natural vocals, soft drums, warm keys, mellow bass, gentle tape texture",
    "Devotional": "devotional Indian melody, respectful natural vocals, flute, tanpura-like drone, gentle percussion, uplifting spiritual arrangement",
    "Hip-hop": "Indian melodic hip-hop song, natural sung hook, rhythmic vocal delivery, deep bass, crisp drums, modern polished production",
    "Rock": "Indian pop rock song, natural expressive vocals, electric guitars, live drums, bass, strong melodic chorus",
    "Pop": "modern Indian pop song, natural lead vocals, catchy melody, polished drums, bass, bright synths, radio-ready production",
}

VOCAL_PROMPTS = {
    "Female": "female lead vocal, natural human-like singing, expressive phrasing, clear diction",
    "Male": "male lead vocal, natural human-like singing, expressive phrasing, clear diction",
    "Duet": "male and female duet vocals, natural human-like singing, expressive call-and-response, harmonies",
    "Any": "natural human-like lead singing, expressive phrasing, clear diction",
}

LANG_MAP = {
    "Telugu": "te",
    "English": "en",
    "Telugu + English": "te",
}

def clean_lyrics(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    # Preserve user words; add section markers only where helpful.
    if not re.search(r"\[(verse|chorus|bridge|intro|outro)", text, re.I):
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if len(lines) >= 8:
            half = max(4, len(lines)//2)
            text = "[Verse 1]\n" + "\n".join(lines[:half]) + "\n\n[Chorus]\n" + "\n".join(lines[half:])
    return text[:4096]

def submit_generation(caption, lyrics, lang, duration):
    payload = {
        "caption": caption[:512],
        "lyrics": lyrics[:4096],
        "thinking": True,
        "vocal_language": lang,
        "audio_format": "mp3",
        "audio_duration": float(duration),
        "model": "acestep-v15-turbo",
        "inference_steps": 8,
        "use_random_seed": True,
        "batch_size": 1,
        "task_type": "text2music",
    }
    r = requests.post(GENERATE_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if "job_id" not in data:
        raise RuntimeError(f"Generation service returned an unexpected response: {data}")
    return data

def poll_job(job_id, status_box, max_seconds=1500):
    url = f"{ACE_BASE}/v1/jobs/{quote(job_id)}"
    started = time.time()
    last_status = ""
    while time.time() - started < max_seconds:
        r = requests.get(url, timeout=45)
        r.raise_for_status()
        data = r.json()
        status = str(data.get("status", "")).lower()

        if status != last_status:
            last_status = status

        if status == "succeeded":
            status_box.success("🎉 Your song is ready!")
            return data

        if status == "failed":
            raise RuntimeError(data.get("error") or "The music service reported a generation failure.")

        queue = data.get("queue_position")
        eta = data.get("eta_seconds")
        if queue is not None:
            msg = f"🎧 Waiting in the music queue — position {queue}"
        elif eta is not None:
            msg = f"🎼 Generating your song — estimated wait {int(eta)} sec"
        else:
            msg = f"🎵 Generating your song — {status or 'processing'}"
        status_box.info(msg)
        time.sleep(5)

    raise TimeoutError("The free music server took too long. Please try again when the queue is lighter.")

def find_audio_reference(obj):
    """Recursively find an audio URL/path in the API result."""
    if isinstance(obj, dict):
        for key in ("url", "audio_url", "path", "audio_path", "file", "filename"):
            value = obj.get(key)
            if isinstance(value, str) and (".mp3" in value.lower() or ".wav" in value.lower() or ".flac" in value.lower() or key in ("url", "audio_url")):
                return value
        for value in obj.values():
            found = find_audio_reference(value)
            if found:
                return found
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            found = find_audio_reference(value)
            if found:
                return found
    elif isinstance(obj, str):
        if obj.startswith("http://") or obj.startswith("https://") or ".mp3" in obj.lower() or ".wav" in obj.lower():
            return obj
    return None

def download_audio(result):
    ref = find_audio_reference(result.get("result", result))
    if not ref:
        raise RuntimeError(f"Generation succeeded but no audio file was returned. Server response: {result}")

    if ref.startswith("http://") or ref.startswith("https://"):
        audio_url = ref
    else:
        audio_url = f"{ACE_BASE}/v1/audio?path={quote(ref, safe='')}"

    r = requests.get(audio_url, timeout=180)
    r.raise_for_status()
    return r.content

# ---------------------------
# Hero
# ---------------------------
if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown('<div class="hero-glow"></div></div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="brand-card">
  <div class="title-gradient">🎵 RacharlaMusic</div>
  <div class="subtitle">Your lyrics • AI melody • Natural singing • Your song</div>
  <div class="badge-row">
    <span class="badge">🎤 Telugu</span>
    <span class="badge">🌐 English</span>
    <span class="badge">💫 Mixed Lyrics</span>
    <span class="badge">🎼 Melody</span>
    <span class="badge">⬇️ MP3 Download</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    st.caption("Create • Sing • Share")
    st.markdown("---")
    st.markdown("### 🎚️ Song settings")

    language = st.selectbox("🌐 Lyrics language", list(LANG_MAP.keys()), index=0)
    vocal = st.selectbox("🎤 Vocal", list(VOCAL_PROMPTS.keys()), index=0)
    style = st.selectbox("🎼 Music style", list(STYLE_PROMPTS.keys()), index=0)
    duration_label = st.select_slider(
        "⏱️ Song length",
        options=["1 min", "2 min", "3 min", "4 min", "5 min", "6 min"],
        value="4 min",
    )
    duration = int(duration_label.split()[0]) * 60

    st.markdown("---")
    st.markdown("### ✨ Quick styles")
    for s in ["Melody", "Romantic", "Folk", "Mass", "Cinematic", "Devotional"]:
        if st.button(f"🎵 {s}", key=f"style_{s}", use_container_width=True):
            st.session_state.selected_style = s
            st.rerun()

    st.markdown("---")
    st.caption("Powered by open music-generation technology.")
    st.caption("Free hosted generation may have queues or availability limits.")

if "selected_style" in st.session_state and st.session_state.selected_style in STYLE_PROMPTS:
    style = st.session_state.selected_style

# ---------------------------
# Main form
# ---------------------------
left, right = st.columns([1.35, .75], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ Create your song</div>', unsafe_allow_html=True)
    st.caption("Paste your own Telugu, English, or Telugu + English lyrics.")

    lyrics = st.text_area(
        "Lyrics",
        height=330,
        max_chars=4096,
        placeholder="""[Verse 1]
నీ కోసం నా గుండెలో
ఒక చిన్న పాట పాడుతా...

[Chorus]
You are my light,
You are my song...

[Verse 2]
...
""",
        label_visibility="collapsed",
    )

    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("🎧 Song title", placeholder="My Racharla Song")
    with c2:
        energy = st.select_slider("🔥 Energy", options=["Soft", "Balanced", "Powerful"], value="Balanced")

    custom_style = st.text_input(
        "🎹 Optional music direction",
        placeholder="e.g. flute intro, warm piano, big cinematic chorus",
    )

    st.markdown('<div class="tip">💡 Tip: Add <b>[Verse]</b>, <b>[Chorus]</b>, and <b>[Bridge]</b> sections for better song structure.</div>', unsafe_allow_html=True)
    st.write("")

    generate = st.button("✨  GENERATE MY SONG  🎵", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎚️ Your sound</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        st.markdown('<div class="metric"><div class="big">🎤</div><div class="small">VOCAL</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="metric"><div class="big">🎼</div><div class="small">MELODY</div></div>', unsafe_allow_html=True)
    st.write("")
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f'<div class="metric"><div class="big">{duration_label}</div><div class="small">TARGET LENGTH</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="metric"><div class="big">✨</div><div class="small">{html.escape(style.upper())}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown(
        f"""
        <div class="badge-row">
          <span class="badge">🌐 {html.escape(language)}</span>
          <span class="badge">🎙️ {html.escape(vocal)}</span>
          <span class="badge">🎼 {html.escape(style)}</span>
          <span class="badge">⚡ {html.escape(energy)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Generate
# ---------------------------
if generate:
    if not lyrics.strip():
        st.warning("✍️ Please paste your lyrics first.")
        st.stop()

    prepared = clean_lyrics(lyrics)

    energy_map = {
        "Soft": "gentle dynamics, intimate arrangement",
        "Balanced": "balanced dynamics, clear chorus lift",
        "Powerful": "strong dynamics, energetic chorus and punchy drums",
    }

    caption = (
        f"{STYLE_PROMPTS[style]}, {VOCAL_PROMPTS[vocal]}, "
        f"{energy_map[energy]}, polished professional studio mix, "
        "clean vocal mix, strong melody, tasteful harmony, no spoken narration"
    )
    if custom_style.strip():
        caption += f", {custom_style.strip()}"

    status = st.empty()
    progress = st.progress(0)

    try:
        status.info("🚀 Connecting to the free music-generation server...")
        progress.progress(8)

        submitted = submit_generation(
            caption=caption,
            lyrics=prepared,
            lang=LANG_MAP[language],
            duration=duration,
        )
        job_id = submitted["job_id"]
        progress.progress(15)

        result = poll_job(job_id, status, max_seconds=1500)
        progress.progress(85)

        status.info("⬇️ Preparing your MP3 download...")
        audio = download_audio(result)
        progress.progress(100)

        st.session_state.audio_bytes = audio
        st.session_state.song_meta = {
            "title": title.strip() or "RacharlaMusic Song",
            "language": language,
            "vocal": vocal,
            "style": style,
            "duration": duration_label,
            "job_id": job_id,
        }
        status.success("🎉 Song created successfully!")

    except requests.HTTPError as e:
        status.error(f"❌ Music server HTTP error: {e}")
        st.info("The public free server may be busy or temporarily unavailable. Please try again later.")
    except Exception as e:
        status.error(f"❌ Generation failed: {e}")
        st.info("Your lyrics were not changed. Try a shorter test song first if the free server is busy.")

# ---------------------------
# Result
# ---------------------------
if st.session_state.audio_bytes:
    meta = st.session_state.song_meta or {}
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("## 🎉 Your generated song")
    st.markdown(
        f"**{html.escape(meta.get('title','RacharlaMusic Song'))}**  ·  "
        f"{html.escape(meta.get('language',''))} · "
        f"{html.escape(meta.get('style',''))} · "
        f"{html.escape(meta.get('duration',''))}"
    )

    st.audio(st.session_state.audio_bytes, format="audio/mp3")

    filename = re.sub(r"[^A-Za-z0-9_-]+", "_", meta.get("title", "RacharlaMusic_Song")).strip("_") or "RacharlaMusic_Song"
    st.download_button(
        "⬇️  DOWNLOAD MP3",
        data=st.session_state.audio_bytes,
        file_name=f"{filename}.mp3",
        mime="audio/mpeg",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    """
<div class="footer">
  🎵 <strong>RacharlaMusic</strong> · Create • Sing • Share • Anytime<br>
  Powered by <strong>RacharlaGPT.in</strong>
</div>
""",
    unsafe_allow_html=True,
)
