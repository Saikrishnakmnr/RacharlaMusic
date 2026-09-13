import os
import re
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
    '<div style="color: #bdbcdc;">AI Music & Full Vocal Track Generator</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Telugu Melodic": "melodic telugu film song, emotional male vocal, acoustic guitar beat",
    "Telugu Mass": "high energy telugu commercial beat, fast vocals, folk drums, mass beat",
    "Telugu Folk": "traditional telugu folk rhythm, authentic vocals, dholak drum beat",
    "English Pop": "modern synth pop, upbeat melodic vocal hook, EDM beat",
    "Cinematic": "epic soundtrack, orchestra, dramatic build, choral vocals",
}

# Sidebar Settings
with st.sidebar:
    st.markdown("## 🔑 Music API Settings")
    api_key = st.text_input("API Key", type="password", value=os.environ.get("SUNO_API_KEY", os.environ.get("ACE_API_KEY", "")))
    api_endpoint = st.text_input("API Endpoint Base URL", value="https://api.suno.ai/v1")
    
    st.markdown("---")
    st.markdown("## 🎵 Audio Settings")
    style_choice = st.selectbox("🎼 Song Style", list(STYLES), index=0)

# Main Form
c1, c2 = st.columns([1.3, 0.7], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Lyrics & Concept Script")
    lyrics_input = st.text_area("Write your lyrics or idea", height=200, placeholder="[Verse]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nMy heart beats for you...")
    track_title = st.text_input("🎧 Song Title", value="My Racharla Track")
    
    generate_btn = st.button("✨ GENERATE FULL MUSIC & VOCALS 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Output Player & Script")
    
    if "audio_bytes" in st.session_state:
        st.success(f"Track Generated: **{st.session_state.get('track_title', 'Untitled')}**")
        st.audio(st.session_state["audio_bytes"], format="audio/mp3")
        
        clean_file_name = re.sub(r'[^\w\s-]', '', st.session_state.get('track_title', 'track')).strip().replace(' ', '_') or "track"
        st.download_button(
            label="⬇️ Download Track (MP3)",
            data=st.session_state["audio_bytes"],
            file_name=f"{clean_file_name}.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
    else:
        st.info("Your audio track with music and vocals will appear here after generation.")

    if "script" in st.session_state:
        st.markdown("---")
        st.markdown("**Generated Song Script:**")
        st.code(st.session_state["script"], language="text")

    st.markdown("</div>", unsafe_allow_html=True)

# Function to handle real music synthesis polling
def generate_music_track(key, base_url, prompt_style, lyrics, title):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": lyrics,
        "tags": prompt_style,
        "title": title,
        "make_instrumental": False,
        "wait_audio": True
    }
    
    # 1. Trigger Generation Task
    endpoint = f"{base_url.rstrip('/')}/generate"
    response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"API Error ({response.status_code}): {response.text}")
        
    res_data = response.json()
    
    # Handle array or direct object response structures
    task_items = res_data if isinstance(res_data, list) else res_data.get("data", [res_data])
    audio_url = task_items[0].get("audio_url") or task_items[0].get("stream_url")
    
    # 2. Poll status if URL is not immediately returned
    if not audio_url and "id" in task_items[0]:
        task_id = task_items[0]["id"]
        status_url = f"{base_url.rstrip('/')}/tasks/{task_id}"
        
        for _ in range(30):
            time.sleep(3)
            poll_res = requests.get(status_url, headers=headers, timeout=15)
            if poll_res.status_code == 200:
                p_data = poll_res.json()
                if p_data.get("status") == "complete":
                    audio_url = p_data.get("audio_url")
                    break

    if not audio_url:
        raise Exception("Audio generation completed but no direct audio URL was provided by the API.")
        
    # 3. Download MP3 audio stream
    audio_res = requests.get(audio_url, timeout=60)
    if audio_res.status_code == 200:
        return audio_res.content
    else:
        raise Exception("Failed to fetch generated MP3 audio stream.")

# Process Generation
if generate_btn:
    if not api_key.strip():
        st.error("Please enter a valid Music API Key in the sidebar.")
        st.stop()
        
    if not lyrics_input.strip():
        st.warning("Please enter lyrics or a song concept.")
        st.stop()

    status = st.empty()
    status.info("Generating full musical composition with instruments and vocals (~30–45 seconds)...")

    full_style = STYLES[style_choice]
    formatted_script = f"[Style: {style_choice}]\n\n[Verse]\n{lyrics_input}\n\n[Chorus]\n{track_title}"

    try:
        audio_data = generate_music_track(
            api_key.strip(), 
            api_endpoint.strip(), 
            full_style, 
            lyrics_input.strip(), 
            track_title.strip()
        )
        
        st.session_state["audio_bytes"] = audio_data
        st.session_state["script"] = formatted_script
        st.session_state["track_title"] = track_title.strip() or "Racharla Track"
        status.success("Musical track generated successfully!")
        st.rerun()

    except Exception as e:
        status.error(f"Generation error: {e}")
