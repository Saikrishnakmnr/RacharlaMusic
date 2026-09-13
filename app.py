import base64
import hashlib
import re
import streamlit as st
import streamlit.components.v1 as components

from lyrics.local import generate as generate_lyrics
from providers.local import LocalFallbackProvider

st.set_page_config(page_title="RacharlaMusic", page_icon="🎵", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 10% 10%, rgba(255,0,220,.12), transparent 30%), radial-gradient(circle at 90% 10%, rgba(0,180,255,.12), transparent 32%), linear-gradient(135deg,#07051b,#11165a 55%,#04253c); color:#fff; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#12154f,#11134c); border-right:1px solid rgba(255,255,255,.08); }
.block-container { max-width: 1150px; padding-top: 1.5rem; }
.glass { background: rgba(8,10,35,.48); border:1px solid rgba(255,255,255,.12); border-radius:20px; padding:22px; box-shadow:0 12px 50px rgba(0,0,0,.25); }
.hero { border-radius:22px; padding:18px; background:linear-gradient(100deg,rgba(255,20,200,.13),rgba(0,210,255,.13)); border:1px solid rgba(255,255,255,.12); }
.title { font-size:2.8rem; font-weight:800; background:linear-gradient(90deg,#ff2ccf,#9a62ff,#00dfff); -webkit-background-clip:text; color:transparent; margin:0; }
.hint { border-left:3px solid #00e5ff; padding:10px 14px; background:rgba(0,220,255,.06); border-radius:10px; }
div.stButton > button { border-radius:14px; min-height:48px; font-weight:800; background:linear-gradient(90deg,#ff19c8,#8050ff,#00cfe9); color:white; border:0; }
.download button { border:1px solid rgba(255,255,255,.2); }
.small { color:#aaaecb; font-size:.88rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language = st.selectbox("🌐 Lyrics", ["Telugu", "English", "Telugu + English"])
    vocal = st.selectbox("🎤 Vocal", ["Natural lead", "Female", "Male", "Duet"])
    styles = ["Melody", "Romantic", "Folk", "Mass", "Sad", "Cinematic", "Lo-fi", "Devotional", "Hip-hop", "Rock", "Pop"]
    style = st.selectbox("🎼 Style", styles)
    length_min = st.slider("⏱️ Length", 1, 6, 2, 1, format="%d min")
    st.markdown("---")
    st.info("🆓 **Zero External Dependencies**\n\nNo Hugging Face Spaces, no ZeroGPU quota, no API key, and no payment system.\n\nThe local mode creates a real musical backing/demo track on CPU.")

# Hero
st.markdown('<div class="hero"><div class="title">RacharlaMusic</div><div class="small">Free Telugu • English • Mixed music maker</div></div>', unsafe_allow_html=True)

if (st.session_state.get("language") != language or st.session_state.get("length_min") != length_min or st.session_state.get("style") != style):
    # Do not erase lyrics, but invalidate a previously generated result when core settings change.
    st.session_state.pop("audio", None)
st.session_state["language"] = language
st.session_state["length_min"] = length_min
st.session_state["style"] = style

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### ✍️ Lyrics")
    lyrics = st.text_area("Lyrics", value=st.session_state.get("draft_lyrics", ""), height=300, label_visibility="collapsed", placeholder="Paste your Telugu / English / mixed lyrics here...")
    if st.button("✨ GENERATE FREE LYRICS", use_container_width=True):
        lyrics = generate_lyrics("My Racharla Song", language, style)
        st.session_state["draft_lyrics"] = lyrics
        st.rerun()

with col2:
    st.markdown("### 🎧 Song details")
    title = st.text_input("🎧 Song title", value=st.session_state.get("title_input", "My Racharla Song"))
    direction = st.text_input("🎹 Extra music direction", value="flute intro, warm piano, big cinematic chorus")
    st.markdown('<div class="hint">💡 <b>Better structure:</b> use [Verse], [Pre-Chorus], [Chorus], [Bridge] labels. The local engine uses each lyric line to build a different melodic phrase.</div>', unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.caption(f"{style} • {vocal} • {length_min} minute(s) • exact target: {length_min*60} seconds")
    st.audio(b"", format="audio/wav") if False else None

st.markdown("<br>", unsafe_allow_html=True)
generate = st.button("✨ GENERATE MY SONG 🎵", use_container_width=True)

if generate:
    if not lyrics.strip():
        st.warning("Please paste lyrics or use GENERATE FREE LYRICS first.")
        st.stop()
    st.session_state["draft_lyrics"] = lyrics
    st.session_state["title_input"] = title
    seed_text = f"{title}|{lyrics}|{style}|{vocal}|{direction}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:12], 16)
    seconds = length_min * 60
    status = st.empty()
    status.info(f"🎼 Generating an exact {seconds}-second track with lyric-specific variation...")
    result = LocalFallbackProvider().generate(
        lyrics=lyrics, style_prompt=style, seed=seed, duration_sec=seconds,
        vocal=vocal, title=title or "RacharlaMusic Song", language=language,
    )
    if result.ok:
        st.session_state["audio"] = result.audio_bytes
        st.session_state["duration_seconds"] = seconds
        st.session_state["provider"] = result.provider
        st.session_state["generated_title"] = title.strip() or "RacharlaMusic Song"
        status.success(f"🎉 Song generated successfully — {seconds} seconds.")
    else:
        status.error(result.message)

if "audio" in st.session_state:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.caption(f"Generated by **{st.session_state.get('provider', 'Local Synthesizer')}** • exact duration: **{st.session_state.get('duration_seconds', 0)} seconds**")
    st.audio(st.session_state["audio"], format="audio/wav")

    fname = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.get("generated_title", "RacharlaMusic_Song")).strip("_") or "RacharlaMusic_Song"
    st.download_button("⬇️ DOWNLOAD AUDIO (WAV)", data=st.session_state["audio"], file_name=f"{fname}.wav", mime="audio/wav", use_container_width=True)

    st.markdown("### 🎤 Vocal Singing Companion")
    st.caption("Browser speech can read your lyrics in Telugu/English, but it is not a natural AI singing voice and is not embedded in the downloadable WAV.")
    raw = st.session_state.get("draft_lyrics", lyrics if 'lyrics' in locals() else "")
    safe = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    lang_code = "te-IN" if "Telugu" in st.session_state.get("language", "Telugu") else "en-US"
    html = f"""
    <div style='padding:14px;border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(255,255,255,.04)'>
      <button onclick='startV()' style='padding:11px 18px;border:0;border-radius:10px;background:linear-gradient(90deg,#ff18c9,#824eff,#00cef4);color:white;font-weight:700'>▶️ Start Vocal Companion</button>
      <button onclick='stopV()' style='padding:11px 18px;border:0;border-radius:10px;margin-left:8px;background:rgba(255,255,255,.12);color:white;font-weight:700'>⏹️ Stop</button>
      <span id='s' style='margin-left:10px;color:#00dfff'></span>
    </div>
    <script>
    let u=null;
    function startV(){{
      speechSynthesis.cancel();
      const text=decodeURIComponent(escape(atob('{safe}')));
      u=new SpeechSynthesisUtterance(text); u.lang='{lang_code}'; u.rate=0.82; u.pitch=1.0;
      u.onstart=()=>document.getElementById('s').textContent='🎤 Lyrics speaking...';
      u.onend=()=>document.getElementById('s').textContent='✓ Finished';
      speechSynthesis.speak(u);
    }}
    function stopV(){{speechSynthesis.cancel();document.getElementById('s').textContent='Stopped';}}
    </script>
    """
    components.html(html, height=100)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center;padding:28px;color:#a6a2e8'>🎵 RacharlaMusic • 100% Independent • No External GPU Bottlenecks<br><small>Powered by RacharlaGPT.in</small></div>", unsafe_allow_html=True)
