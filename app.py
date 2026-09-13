import os
import requests
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
    '<div style="color: #bdbcdc;">Free AI Audio Generator</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melody, warm piano, acoustic guitar, expressive music",
    "Romantic": "romantic Telugu film song, intimate acoustic guitar, soft strings",
    "Folk": "Telugu folk style, traditional drums, energetic rhythm",
    "Mass": "high energy commercial soundtrack, heavy bass, punchy drums",
    "Cinematic": "grand orchestral score, epic strings, dramatic build",
}

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🎵 Audio Settings")
    style = st.selectbox("🎼 Music Style", list(STYLES), index=0)

# Main Form
c1, c2 = st.columns([1.35, 0.75], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Song Details")
    lyrics = st.text_area("Lyrics / Song Concept", height=180, placeholder="[Verse]\nWrite your lyrics or music idea here...")
    title = st.text_input("🎧 Track Title", placeholder="Racharla Track")
    
    st.markdown('<div class="tip">Generating audio clip via keyless serverless API.</div>', unsafe_allow_html=True)
    generate = st.button("✨ GENERATE SONG 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Player & Download")
    
    if "audio_bytes" in st.session_state:
        st.success(f"Generated Track: **{st.session_state.get('track_title', 'Untitled')}**")
        st.audio(st.session_state["audio_bytes"], format="audio/flac")
        st.download_button(
            label="⬇️ Download Audio Track",
            data=st.session_state["audio_bytes"],
            file_name=f"{st.session_state.get('track_title', 'track')}.flac",
            mime="audio/flac",
            use_container_width=True
        )
    else:
        st.info("Your audio will appear here when generation completes.")
    st.markdown("</div>", unsafe_allow_html=True)

# Helper function for Serverless API call
def fetch_serverless_audio(prompt_text):
    url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    payload = {"inputs": prompt_text[:300]}
    
    # 60s timeout to allow cold starts
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200 and len(response.content) > 2000:
        return response.content
    return None

# Process Generation
if generate:
    if not lyrics.strip():
        st.warning("Please enter your lyrics or concept prompt.")
        st.stop()
        
    prompt = f"{style} style. {STYLES[style]}. Concept: {lyrics[:200]}"
    
    status = st.empty()
    status.info("Generating music track via serverless backend... Please wait (30–60 secs)...")
    
    audio_bytes = None
    
    # Provider 1: Direct Serverless Inference Call (No Token, Standard Endpoint)
    try:
        audio_bytes = fetch_serverless_audio(prompt)
    except Exception:
        audio_bytes = None
        
    # Provider 2: Alternative Public Gradio Client
    if not audio_bytes:
        try:
            status.info("Primary serverless route busy. Trying secondary backup space...")
            client = Client("facebook/MusicGen")
            # Try positional parameters instead of rigid api_name schema
            result = client.predict(prompt, "facebook/musicgen-small", "Mel", 30)
            audio_path = result[1] if isinstance(result, (list, tuple)) else result
            if audio_path and os.path.exists(str(audio_path)):
                audio_bytes = Path(audio_path).read_bytes()
        except Exception:
            audio_bytes = None

    # Render Result
    if audio_bytes and len(audio_bytes) > 2000:
        st.session_state["audio_bytes"] = audio_bytes
        st.session_state["track_title"] = title.strip() or "Racharla Song"
        status.success("Generation completed successfully!")
        st.rerun()
    else:
        status.error("The free public servers are currently overloaded. Please wait 15 seconds and click Generate again.")
