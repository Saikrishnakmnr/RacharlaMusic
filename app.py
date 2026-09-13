import os
import time
import requests
from pathlib import Path
import streamlit as st

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

# Sidebar Controls (Restored Duration Option)
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
    
    st.markdown(f'<div class="tip">Target length set to <b>{duration} seconds</b>.</div>', unsafe_allow_html=True)
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

# Directly query public Gradio Space API via HTTP requests
def generate_gradio_direct(prompt_text, song_duration):
    # Submit job request to public space node
    submit_url = "https://facebook-musicgen.hf.space/call/predict"
    payload = {
        "data": [
            prompt_text,
            "facebook/musicgen-small",
            "Mel",
            song_duration
        ]
    }
    
    res = requests.post(submit_url, json=payload, timeout=30)
    if res.status_code != 200:
        return None
        
    event_id = res.json().get("event_id")
    if not event_id:
        return None
        
    # Poll event stream for completed file URL
    status_url = f"https://facebook-musicgen.hf.space/call/predict/{event_id}"
    for _ in range(40):
        time.sleep(2)
        poll_res = requests.get(status_url, timeout=30)
        if "event: complete" in poll_res.text:
            lines = poll_res.text.split("\n")
            for line in lines:
                if line.startswith("data:"):
                    import json
                    data_json = json.loads(line.replace("data: ", ""))
                    file_info = data_json[0]
                    file_url = file_info.get("url") if isinstance(file_info, dict) else None
                    if file_url:
                        audio_res = requests.get(file_url, timeout=30)
                        if audio_res.status_code == 200:
                            return audio_res.content
    return None

# Process Generation
if generate:
    if not lyrics.strip():
        st.warning("Please enter your lyrics or concept prompt.")
        st.stop()
        
    prompt = f"{style} style. {STYLES[style]}. Lyrics concept: {lyrics[:200]}"
    
    status = st.empty()
    status.info(f"Generating {duration}-second track via cloud backend... Please wait (~45 seconds)...")
    
    audio_bytes = None
    try:
        audio_bytes = generate_gradio_direct(prompt, duration)
    except Exception as e:
        audio_bytes = None

    if audio_bytes and len(audio_bytes) > 2000:
        st.session_state["audio_bytes"] = audio_bytes
        st.session_state["track_title"] = title.strip() or "Racharla Song"
        status.success("Generation completed successfully!")
        st.rerun()
    else:
        status.error("Public queue busy. Please wait 10 seconds and click Generate again.")
