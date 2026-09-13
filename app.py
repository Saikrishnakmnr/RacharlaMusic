import os
import re
import random
from pathlib import Path
import streamlit as st

from providers.local import LocalFallbackProvider
from audio.validator import validate_audio
from lyrics.generator import local_free_lyrics, normalize_sections

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(page_title=APP_NAME, page_icon="🎵", layout="wide")

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
.stButton>button{border:0!important;border-radius:16px!important;color:#fff!important;font-weight:800!important;
background:linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important;
box-shadow:0 12px 35px rgba(255,24,201,.3)!important;min-height:52px!important}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 18px 45px rgba(255,24,201,.42)!important}
div[data-testid="stTextArea"] textarea{background:rgba(4,8,35,.88)!important;color:white!important;
border-radius:18px!important;border:1px solid rgba(160,110,255,.45)!important}
div[data-baseweb="select"]>div{background:rgba(6,11,44,.9)!important;border-radius:14px!important}
.footer{text-align:center;color:#aaa9c9;padding:30px 0 8px}
.free-note{border:1px solid rgba(0,220,255,.20);background:rgba(0,220,255,.06);padding:10px 14px;border-radius:14px;color:#c9f8ff}
</style>
""", unsafe_allow_html=True)

if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div class="muted">Your lyrics • Independent Synth • Instant generation • 100% Free</div>'
    '<div><span class="badge">🇮🇳 Telugu</span><span class="badge">🇬🇧 English</span>'
    '<span class="badge">🔀 Mixed</span><span class="badge">🎹 Synth Audio</span>'
    '<span class="badge">⬇️ WAV/MP3</span><span class="badge">🆓 No ZeroGPU</span></div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar",
    "Romantic": "romantic Indian film song, intimate lead vocal, piano, acoustic guitar",
    "Folk": "Telugu folk-inspired song, organic percussion, acoustic instruments",
    "Mass": "high-energy Telugu commercial song, powerful rhythm, punchy drums",
    "Sad": "emotional Indian ballad, expressive piano, strings",
    "Cinematic": "grand Indian cinematic soundtrack, orchestral strings",
    "Lo-fi": "dreamy lo-fi Indian pop, soft drums, warm keys",
    "Devotional": "devotional Indian melody, flute, gentle percussion",
    "Hip-hop": "Indian melodic hip-hop, deep bass, crisp drums",
    "Rock": "Indian pop rock, electric guitars, live drums",
    "Pop": "modern Indian pop, catchy melody, bright synths",
}

with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language = st.selectbox("🌐 Lyrics", ["Telugu", "English", "Telugu + English"], index=0)
    vocal = st.selectbox("🎤 Vocal", ["Natural lead", "Female", "Male", "Duet"])
    style = st.selectbox("🎼 Style", list(STYLES), index=0)
    duration_label = st.select_slider("⏱️ Length", ["30 sec", "1 min", "2 min", "3 min"], value="30 sec")
    st.markdown("---")
    st.markdown('<div class="free-note">🆓 <b>Zero External Dependencies</b><br>No Hugging Face Spaces, No ZeroGPU limits, No API keys!</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1.35, 0.75], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Create your song")
    theme_for_lyrics = st.text_input("🧠 Free lyrics idea (optional)", placeholder="A love story under Hyderabad night lights")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        make_lyrics = st.button("📝 GENERATE FREE LYRICS", use_container_width=True)
    with col_b:
        clear_lyrics = st.button("↺ Clear lyrics", use_keyword_argument=True) if hasattr(st.button, "use_keyword_argument") else st.button("↺ Clear lyrics", use_container_width=True)

    if clear_lyrics:
        st.session_state["lyrics_text"] = ""
        st.rerun()

    if make_lyrics:
        if not theme_for_lyrics.strip():
            st.warning("Enter a song idea first.")
        else:
            generated_lyrics = normalize_sections(local_free_lyrics(theme_for_lyrics, language, style))
            st.session_state["lyrics_text"] = generated_lyrics
            st.success("Lyrics ready!")

    lyrics = st.text_area("Lyrics", value=st.session_state.get("lyrics_text", ""), height=330, placeholder="[Verse 1]\n...", key="lyrics_text")
    title = st.text_input("🎧 Song title", placeholder="My Racharla Song")
    extra = st.text_input("🎹 Extra music direction", value="flute intro, warm piano, big cinematic chorus")
    generate = st.button("✨  GENERATE MY SONG  🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.markdown(f"**Language:** {language}<br>**Vocal:** {vocal}<br>**Style:** {style}<br>**Length:** {duration_label}", unsafe_allow_html=True)
    st.markdown(f'<p class="muted">{STYLES[style]}</p>', unsafe_allow_html=True)
    st.markdown("**Provider:** Independent Local Synthesizer (100% Reliable)", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if generate:
    if not lyrics.strip():
        st.warning("Please paste lyrics or generate free lyrics first.")
        st.stop()

    status = st.empty()
    status.info("🎼 Generating song with Independent Local Synthesizer...")
    
    provider = LocalFallbackProvider()
    audio, label = provider.generate(lyrics, style_prompt=STYLES[style], seed=random.randint(1, 100000))
    
    if validate_audio(audio):
        st.session_state["audio"] = bytes(audio)
        st.session_state["title"] = title.strip() or "RacharlaMusic Song"
        st.session_state["provider"] = label
        status.success(f"🎉 Song generated successfully with {label}!")
    else:
        status.error("Generation failed.")

if "audio" in st.session_state and validate_audio(st.session_state["audio"]):
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.caption(f"Generated by **{st.session_state.get('provider', 'Synthesizer')}**")
    st.audio(st.session_state["audio"], format="audio/wav")
    fname = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.get("title", "Song"))
    st.download_button("⬇️ DOWNLOAD AUDIO", data=st.session_state["audio"], file_name=f"{fname}.wav", mime="audio/wav", use_keyword_argument=True) if hasattr(st.download_button, "use_keyword_argument") else st.download_button("⬇️ DOWNLOAD AUDIO", data=st.session_state["audio"], file_name=f"{fname}.wav", mime="audio/wav", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">🎵 <b>RacharlaMusic</b> • 100% Independent • No External GPU Bottlenecks</div>', unsafe_allow_html=True)
