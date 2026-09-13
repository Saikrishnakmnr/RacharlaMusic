import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
import requests
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
    '<div style="color: #bdbcdc;">ACE API & Multi-Engine Vocal Song Generator</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Telugu Melodic": "Melodic Telugu film song, emotional lead vocal, acoustic guitar",
    "Telugu Mass": "High energy Telugu commercial track, fast vocal delivery, energetic beats",
    "Telugu Folk": "Traditional Telugu folk style, authentic vocals, rhythmic dholak",
    "English Pop": "Modern English pop track, catchy vocal hooks, smooth beat",
    "Cinematic": "Grand epic soundtrack with vocal chants and dramatic build",
}

# Sidebar Settings
with st.sidebar:
    st.markdown("## 🔑 API Keys")
    ace_api_key = st.text_input("ACE API Key", type="password", value=os.environ.get("ACE_API_KEY", ""))
    gemini_api_key = st.text_input("Gemini API Key (Fallback)", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    st.markdown("---")
    st.markdown("## 🎵 Audio Settings")
    style_choice = st.selectbox("🎼 Song Style", list(STYLES), index=0)
    duration = st.selectbox("⏱️ Target Duration", [30, 60], index=0)

# Main Form
c1, c2 = st.columns([1.3, 0.7], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Lyrics & Concept Script")
    lyrics_input = st.text_area("Write your lyrics or idea", height=200, placeholder="[Verse]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nMy heart beats for you...")
    track_title = st.text_input("🎧 Song Title", value="My Racharla Track")
    
    st.markdown(f'<div class="tip">Generation target set to <b>{duration} seconds</b>.</div>', unsafe_allow_html=True)
    generate_btn = st.button("✨ GENERATE FULL SONG 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Output Player & Script")
    
    if "audio_bytes" in st.session_state:
        st.success(f"Track Generated: **{st.session_state.get('track_title', 'Untitled')}** ({duration}s)")
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
        st.info("Your audio track will appear here after generation.")

    if "script" in st.session_state:
        st.markdown("---")
        st.markdown("**Generated Song Script:**")
        st.code(st.session_state["script"], language="text")

    st.markdown("</div>", unsafe_allow_html=True)

# 1. Primary Engine: ACE API Generation
def generate_ace_song(api_key, prompt, lyrics, duration_secs):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "lyrics": lyrics,
        "duration": duration_secs,
        "audio_format": "mp3"
    }
    
    response = requests.post("https://api.acestep.io/v1/generate", json=payload, headers=headers, timeout=15)
    if response.status_code == 200:
        res_data = response.json()
        audio_url = res_data.get("audio_url")
        if audio_url:
            audio_res = requests.get(audio_url, timeout=30)
            if audio_res.status_code == 200:
                return audio_res.content
    raise Exception(f"ACE API failed (HTTP {response.status_code})")

# 2. Secondary Engine: Gemini REST Audio Fallback
def generate_gemini_audio(api_key, prompt_style, lyrics):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt_text = f"Sing and compose a musical song in this style: {prompt_style}. Lyrics:\n{lyrics}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseMimeType": "audio/mp3"
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        data = response.json()
        try:
            import base64
            audio_b64 = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            return base64.b64decode(audio_b64)
        except Exception:
            pass
    raise Exception(f"Gemini API audio response invalid (HTTP {response.status_code})")

# 3. Final Backup: Standard TTS Fallback
def generate_fallback_tts(text, duration_secs):
    clean_text = re.sub(r'[^\w\s\u0c00-\u0c7f]', '', text)
    lang_code = 'te' if any('\u0c00' <= char <= '\u0c7f' for char in clean_text) else 'en'
    vocal_text = clean_text[:160] if duration_secs == 30 else clean_text[:320]
    
    encoded_text = urllib.parse.quote(vocal_text.strip(), encoding='utf-8')
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={lang_code}&client=tw-ob"
    
    req = urllib.request.Request(tts_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read()

# Fallback Orchestrator
def generate_song_with_fallbacks(ace_key, gemini_key, prompt, lyrics, duration_secs, style):
    # Try ACE API
    if ace_key.strip():
        try:
            return generate_ace_song(ace_key, prompt, lyrics, duration_secs)
        except Exception:
            pass
            
    # Try Gemini Audio Fallback
    if gemini_key.strip():
        try:
            return generate_gemini_audio(gemini_key, style, lyrics)
        except Exception:
            pass

    # Final TTS Fallback
    return generate_fallback_tts(lyrics, duration_secs)

# Process Generation
if generate_btn:
    if not ace_api_key.strip() and not gemini_api_key.strip():
        st.error("Please enter at least an ACE API Key or Gemini API Key in the sidebar.")
        st.stop()
        
    if not lyrics_input.strip():
        st.warning("Please enter lyrics or a song concept.")
        st.stop()

    status = st.empty()
    status.info(f"Generating {duration}-second song track (~25 seconds)...")

    full_prompt = f"{style_choice} style. {STYLES[style_choice]}. Title: {track_title}"
    formatted_script = f"[Verse 1]\n{lyrics_input}\n\n[Chorus]\n{track_title}\n\n[Outro]\nFade out..."

    try:
        audio_data = generate_song_with_fallbacks(
            ace_api_key.strip(),
            gemini_api_key.strip(),
            full_prompt,
            lyrics_input,
            duration,
            STYLES[style_choice]
        )
        
        if audio_data and len(audio_data) > 500:
            st.session_state["audio_bytes"] = audio_data
            st.session_state["script"] = formatted_script
            st.session_state["track_title"] = track_title.strip() or "Racharla Track"
            status.success("Song generated successfully!")
            st.rerun()
        else:
            status.error("Failed to generate audio output.")
    except Exception as e:
        status.error(f"Generation error: {e}")
