import os
from pathlib import Path
import streamlit as st
from gradio_client import Client

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎵",
    layout="wide",
)

# Visual Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp { font-family: Poppins, sans-serif; color: #fff; background: linear-gradient(135deg,#06051a,#10134a 50%,#061c39); }
.block-container { max-width: 1280px; padding-top: 1rem; }
.hero { border-radius: 28px; overflow: hidden; border: 1px solid rgba(255,255,255,.16); margin-bottom: 22px; }
.hero img { display: block; width: 100%; }
.glass { border: 1px solid rgba(255,255,255,.14); border-radius: 24px; padding: 22px; background: rgba(25,28,88,.86); }
.title { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg,#fff,#ff4ed4,#7c62ff,#20e5ff); -webkit-background-clip: text; color: transparent; }
.tip { border-left: 4px solid #ff35cf; border-radius: 0 14px 14px 0; background: rgba(255,53,207,.07); padding: 12px 15px; margin: 10px 0; }
.stButton>button { border: 0!important; border-radius: 16px!important; color: #fff!important; font-weight: 800!important; background: linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important; min-height: 52px!important; }
</style>
""", unsafe_allow_html=True)

if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div style="color: #bdbcdc;">Free AI Audio Generator (30–60 Second Preview Mode)</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melody, warm piano, acoustic guitar, expressive singing style",
    "Romantic": "romantic Telugu film song, intimate vocals, acoustic guitar, soft strings",
    "Folk": "Telugu folk style, traditional drums, energetic rhythm, catchy melody",
    "Mass": "high energy commercial song, heavy bass, punchy drums, power beat",
    "Cinematic": "grand orchestral score, epic strings, dramatic build",
}

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🎵 Audio Settings")
    style = st.selectbox("🎼 Music Style", list(STYLES), index=0)
    duration = st.selectbox("⏱️ Target Duration", [30, 60], index=0)

# Main Form
c1, c2 = st.columns([1.35, 0.75], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Song Details")
    lyrics = st.text_area("Lyrics / Song Concept", height=180, placeholder="[Verse]\nWrite your lyrics or music idea here...")
    title = st.text_input("🎧 Track Title", placeholder="Racharla Track")
    
    st.markdown(f'<div class="tip">Configured for standard <b>{duration}-second</b> cloud audio generation.</div>', unsafe_allow_html=True)
    generate = st.button("✨ GENERATE SONG 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Player & Download")
    
    if "audio_bytes" in st.session_state:
        st.success(f"Generated Track: **{st.session_state.get('track_title', 'Untitled')}**")
        st.audio(st.session_state["audio_bytes"], format="audio/wav")
        st.download_button(
            label="⬇️ Download Audio Track",
            data=st.session_state["audio_bytes"],
            file_name=f"{st.session_state.get('track_title', 'track')}.wav",
            mime="audio/wav",
            use_container_width=True
        )
    else:
        st.info("Your audio will appear here when generation completes.")
    st.markdown("</div>", unsafe_allow_html=True)

# Verification helper
def is_valid_audio_file(filepath: str) -> bool:
    return bool(filepath and os.path.exists(filepath) and os.path.getsize(filepath) > 1000)

# Process Generation
if generate:
    if not lyrics.strip():
        st.warning("Please enter your lyrics or concept prompt.")
        st.stop()
        
    prompt = f"{style} style. {STYLES[style]}. Lyrics: {lyrics[:250]}"
    
    status = st.empty()
    status.info("Connecting to free music generator... Please wait 30-60 seconds.")
    
    audio_path = None
    
    # Primary API connection
    try:
        client = Client("facebook/MusicGen")
        result = client.predict(
            text=prompt,
            model_name="facebook/musicgen-small",
            decoder="Mel",
            duration=duration,
            api_name="/predict"
        )
        if isinstance(result, (list, tuple)):
            audio_path = result[1] if len(result) > 1 else result[0]
        else:
            audio_path = result
    except Exception as e:
        status.warning("Primary provider busy, trying fallback space...")
        try:
            client = Client("ACE-Step/ACE-Step")
            result = client.predict(
                prompt,
                lyrics,
                duration,
                api_name="/text2music"
            )
            audio_path = result
        except Exception as e2:
            status.error(f"Generation failed across available endpoints: {e2}")

    # Process Audio Result and Verify Output
    if is_valid_audio_file(str(audio_path)):
        st.session_state["audio_bytes"] = Path(audio_path).read_bytes()
        st.session_state["track_title"] = title.strip() or "Racharla Song"
        status.success("Generation completed successfully!")
        st.rerun()
    else:
        status.error("Failed to generate audio file. Please click Generate again.")
