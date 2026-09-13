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

# Visual Styling & Branding
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp { font-family: Poppins, sans-serif; color: #fff; background: linear-gradient(135deg,#06051a,#10134a 50%,#061c39); }
.block-container { max-width: 1280px; padding-top: 1rem; }
.hero { border-radius: 28px; overflow: hidden; border: 1px solid rgba(255,255,255,.16); margin-bottom: 22px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
.hero img { display: block; width: 100%; }
.glass { border: 1px solid rgba(255,255,255,.14); border-radius: 24px; padding: 22px; background: rgba(25,28,88,.86); box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
.title { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg,#fff,#ff4ed4,#7c62ff,#20e5ff); -webkit-background-clip: text; color: transparent; }
.tip { border-left: 4px solid #ff35cf; border-radius: 0 14px 14px 0; background: rgba(255,53,207,.07); padding: 12px 15px; margin: 10px 0; }
.stButton>button { border: 0!important; border-radius: 16px!important; color: #fff!important; font-weight: 800!important; background: linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important; min-height: 52px!important; }
</style>
""", unsafe_allow_html=True)

# Brand Banner Restoration
if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div style="color: #bdbcdc;">Free AI Audio & Vocal Song Generator</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melody with warm piano, expressive vocals and guitar",
    "Telugu Romantic": "romantic Telugu film song, intimate vocal performance, acoustic guitar, soft strings",
    "Telugu Mass": "high energy Telugu commercial track, fast vocal delivery, heavy folk drums, power beat",
    "Telugu Folk": "traditional Telugu folk style, authentic vocals, organic rhythm, dholak",
    "English Pop": "modern English pop track, smooth lead singing style, catchy synth beat",
    "Cinematic": "epic cinematic soundtrack, dramatic orchestration with vocal chants",
}

# Sidebar Controls
with st.sidebar:
    st.markdown("## 🎵 Generation Settings")
    style_choice = st.selectbox("🎼 Song Style", list(STYLES), index=0)
    duration = st.selectbox("⏱️ Target Duration", [30, 60], index=0)

# Main Form
c1, c2 = st.columns([1.3, 0.7], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Song Script & Lyrics")
    lyrics_input = st.text_area("Write your lyrics or idea", height=200, placeholder="[Verse]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nMy heart beats for you...")
    track_title = st.text_input("🎧 Song Title", value="My Racharla Track")
    
    st.markdown(f'<div class="tip">Configured to generate <b>{duration}-second</b> audio track.</div>', unsafe_allow_html=True)
    generate_btn = st.button("✨ GENERATE SONG & SCRIPT 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Output Player & Script")
    
    player_placeholder = st.empty()
    script_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

# Audio Generation Logic via Cloud Endpoints
def fetch_cloud_audio(prompt_text, seconds):
    url = "https://facebook-musicgen.hf.space/call/predict"
    payload = {
        "data": [
            prompt_text,
            "facebook/musicgen-small",
            "Mel",
            seconds
        ]
    }
    
    res = requests.post(url, json=payload, timeout=25)
    if res.status_code == 200:
        event_id = res.json().get("event_id")
        if event_id:
            status_url = f"https://facebook-musicgen.hf.space/call/predict/{event_id}"
            for _ in range(30):
                time.sleep(2)
                poll = requests.get(status_url, timeout=25)
                if "event: complete" in poll.text:
                    for line in poll.text.split("\n"):
                        if line.startswith("data:"):
                            import json
                            data = json.loads(line.replace("data: ", ""))
                            file_info = data[0]
                            file_url = file_info.get("url") if isinstance(file_info, dict) else None
                            if file_url:
                                audio_res = requests.get(file_url, timeout=30)
                                if audio_res.status_code == 200:
                                    return audio_res.content
    return None

# Process Action
if generate_btn:
    if not lyrics_input.strip():
        st.warning("Please enter lyrics or a song concept first.")
        st.stop()

    prompt = f"{style_choice} style. {STYLES[style_choice]}. Lyrics idea: {lyrics_input[:200]}"
    formatted_script = f"[Verse 1]\n{lyrics_input}\n\n[Chorus]\n{track_title} - Harmony\n\n[Outro]\nSoft melody fading out..."
    
    st.session_state["script"] = formatted_script
    st.session_state["track_title"] = track_title.strip() or "Racharla Track"
    
    status = st.empty()
    status.info(f"Generating {duration}-second audio track... Please wait (~35 seconds)...")
    
    audio_bytes = None
    try:
        audio_bytes = fetch_cloud_audio(prompt, duration)
    except Exception:
        audio_bytes = None

    if audio_bytes and len(audio_bytes) > 2000:
        st.session_state["audio_bytes"] = audio_bytes
        status.success("Song generated successfully!")
    else:
        status.warning("Public server busy—retrying audio rendering...")
        # Fallback query attempt
        try:
            fallback_res = requests.post(
                "https://api-inference.huggingface.co/models/facebook/musicgen-small",
                json={"inputs": prompt[:300]},
                timeout=45
            )
            if fallback_res.status_code == 200 and len(fallback_res.content) > 2000:
                st.session_state["audio_bytes"] = fallback_res.content
                status.success("Song generated successfully via backup pipeline!")
            else:
                status.error("Cloud engine busy. Please click Generate once more to complete.")
        except Exception:
            status.error("Cloud engine busy. Please click Generate once more to complete.")
            
    st.rerun()

# Render Session Output
if "audio_bytes" in st.session_state:
    with c2:
        st.success(f"Generated Track: **{st.session_state.get('track_title', 'Untitled')}**")
        st.audio(st.session_state["audio_bytes"], format="audio/wav")
        st.download_button(
            label="⬇️ Download Track (WAV)",
            data=st.session_state["audio_bytes"],
            file_name=f"{st.session_state.get('track_title', 'track')}.wav",
            mime="audio/wav",
            use_container_width=True
        )

if "script" in st.session_state:
    with c2:
        st.markdown("**Generated Song Script:**")
        st.code(st.session_state["script"], language="text")
