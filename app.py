import streamlit as st
import time

# 1. Page Configuration
st.set_page_config(page_title="తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI మెలోడీ సాంగ్ జనరేటర్")
st.write("మీ 4 లైన్ల లిరిక్స్ ఇవ్వండి మరియు పాటను వినండి!")

# Setup music track library
MELODY_TRACKS = {
    "Male Vocal (మెలోడీ)": "https://soundhelix.com",
    "Female Vocal (మెలోడీ)": "https://soundhelix.com"
}

# 2. Setup Persistent State Cache Memory
if "is_generated" not in st.session_state:
    st.session_state.is_generated = False
if "cached_lyrics" not in st.session_state:
    st.session_state.cached_lyrics = ""
if "cached_track" not in st.session_state:
    st.session_state.cached_track = ""

# 3. Input UI
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Enter your 4-line lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నારી గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||\nవేడుకతో నీకు పూజలు చేస్తాము |\nతోడుగా మమ్మల్ని కాపాడవయ్యా ||",
    height=130
)

singer_type = st.selectbox("గాయకుడు/గాయని (Select Voice Style):", list(MELODY_TRACKS.keys()))

# 4. Trigger Execution Action
if st.button("పాటను సృష్టించు (Generate Song)", key="main_gen_btn"):
    if not user_lyrics.strip():
        st.warning("⚠️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("AI మధురమైన రాగాన్ని కంపోజ్ చేస్తున్నాడు..."):
            time.sleep(1.0) # Processing buffer simulation
            st.session_state.is_generated = True
            st.session_state.cached_lyrics = user_lyrics
            st.session_state.cached_track = MELODY_TRACKS[singer_type]

st.divider()

# 5. BUG-FREE PERMANENT DISPLAY OUTSIDE INTERACTION CYCLE
if st.session_state.is_generated:
    st.success("🎉 అద్భుతమైన మెలోడీ పాట సిద్ధంగా ఉంది!")
    st.info(f"📝 **మీ పాట సాహిత్యం:**\n\n{st.session_state.cached_lyrics}")
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen below without any disabling issue):**")
    
    # CRITICAL FIX: Direct HTML injection bypassing Streamlit state re-evaluation loops
    audio_html = f"""
    <div style="background-color: #f1f3f4; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <audio controls style="width: 100%;">
            <source src="{st.session_state.cached_track}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    </div>
    <div style="margin-top: 15px;">
        <a href="{st.session_state.cached_track}" download="telugu_song.mp3" 
           style="display: inline-block; padding: 12px 24px; color: white; background-color: #25D366; 
           text-decoration: none; border-radius: 6px; font-weight: bold; text-align: center;">
           📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)
        </a>
    </div>
    """
    st.components.v1.html(audio_html, height=130)
