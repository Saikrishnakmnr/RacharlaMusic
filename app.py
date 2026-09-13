import os
import io
import time
from pathlib import Path
import streamlit as st
from gtts import gTTS
from google import genai

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎵",
    layout="wide",
)

# Visual Styling & UI Theme
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

# UI Poster Banner Restoration
if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div style="color: #bdbcdc;">Gemini AI Vocal Song & Script Generator</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Telugu Romantic": "Melodic Telugu song, emotional lead vocal, acoustic guitar, soft melody",
    "Telugu Mass": "High energy Telugu commercial track, fast vocal rhythm, energetic folk drums",
    "Telugu Folk": "Traditional Telugu folk rhythm, authentic vocal style, dholak",
    "English Pop": "Modern English pop track, upbeat vocal performance, catchy beat",
    "Cinematic": "Epic soundtrack with vocal chants and dramatic build",
}

# Sidebar Settings
with st.sidebar:
    st.markdown("## 🔑 API Configuration")
    api_key = st.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    st.markdown("---")
    st.markdown("## 🎵 Audio Settings")
    style_choice = st.selectbox("🎼 Song Style", list(STYLES), index=0)
    duration = st.selectbox("⏱️ Target Duration", [30, 60], index=0)

# Main Form Setup
c1, c2 = st.columns([1.3, 0.7], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Song Concept & Lyrics")
    lyrics_input = st.text_area("Write your lyrics or idea", height=200, placeholder="[Verse]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nMy heart beats for you...")
    track_title = st.text_input("🎧 Track Title", value="My Racharla Song")
    
    st.markdown(f'<div class="tip">Target audio length configured to <b>{duration} seconds</b>.</div>', unsafe_allow_html=True)
    generate_btn = st.button("✨ GENERATE SONG & SCRIPT 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Output Player & Script")
    
    if "audio_bytes" in st.session_state:
        st.success(f"Track Ready: **{st.session_state.get('track_title', 'Untitled')}** ({duration}s)")
        st.audio(st.session_state["audio_bytes"], format="audio/mp3")
        st.download_button(
            label="⬇️ Download Track (MP3)",
            data=st.session_state["audio_bytes"],
            file_name=f"{st.session_state.get('track_title', 'track')}.mp3",
            mime="audio/mp3",
            use_container_width=True
        )
    else:
        st.info("Your generated audio track will appear here.")
        
    if "script" in st.session_state:
        st.markdown("---")
        st.markdown("**Generated Song Script:**")
        st.code(st.session_state["script"], language="text")
        
    st.markdown("</div>", unsafe_allow_html=True)

# Execution Logic
if generate_btn:
    if not api_key.strip():
        st.error("Please enter your Gemini API Key in the sidebar.")
        st.stop()
        
    if not lyrics_input.strip():
        st.warning("Please enter your song concept or lyrics.")
        st.stop()

    status = st.empty()
    status.info(f"Generating script & {duration}-second audio track via Gemini API...")

    try:
        # 1. Connect to Gemini API using google-genai
        client = genai.Client(api_key=api_key.strip())
        
        # 2. Generate structured lyrics script
        prompt_content = f"""
        Act as a professional music composer. Generate a complete song script based on:
        Title: {track_title}
        Style: {style_choice} ({STYLES[style_choice]})
        Length Target: {duration} seconds
        Input Lyrics/Idea: {lyrics_input}

        Include clear sections like [Intro], [Verse], [Chorus], and [Outro].
        """
        
        script_res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_content
        )
        formatted_script = script_res.text if script_res and script_res.text else lyrics_input

        # 3. Process vocal output audio
        lang_code = 'te' if any('\u0c00' <= char <= '\u0c7f' for char in lyrics_input) else 'en'
        vocal_text = lyrics_input[:160] if duration == 30 else lyrics_input[:320]
        
        tts = gTTS(text=vocal_text, lang=lang_code, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        # 4. Save results to Session State
        st.session_state["audio_bytes"] = audio_fp.read()
        st.session_state["script"] = formatted_script
        st.session_state["track_title"] = track_title.strip() or "Racharla Track"
        
        status.success("Song script & audio generated successfully!")
        st.rerun()

    except Exception as e:
        status.error(f"Generation error: {e}")
