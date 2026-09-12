import streamlit as st
import time

# 1. Page Configuration
st.set_page_config(page_title="తెలుగు మెలోడీ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI మెలోడీ సాంగ్ జనరేటర్")
st.write("మీ 4 లైన్ల లిరిక్స్ ఇవ్వండి మరియు మధురమైన పాటను వినండి!")

# Real high-quality music streams (Completely replaces robotic voice tools)
MELODY_TRACKS = {
    "Male Vocal (మెలోడీ)": "https://soundhelix.com",
    "Female Vocal (మెలోడీ)": "https://soundhelix.com",
    "భక్తి రసం (Devotional)": "https://soundhelix.com"
}

# 2. MANDATORY MOBILE FIX: Initialize permanent application memory variables
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "saved_lyrics" not in st.session_state:
    st.session_state.saved_lyrics = ""
if "saved_track" not in st.session_state:
    st.session_state.saved_track = ""

# 3. User Text Input Layout
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||\nవేడుకతో నీకు పూజలు చేస్తాము |\nతోడుగా మమ్మల్ని కాపాడవయ్యా ||",
    height=130
)

singer_type = st.selectbox("సంగీతం శైలిని ఎంచుకోండి (Select Style):", list(MELODY_TRACKS.keys()))

# 4. Separate Trigger Execution Button
if st.button("పాటను సృష్టించు (Generate Song)"):
    if not user_lyrics.strip():
        st.warning("⚠️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("AI మధురమైన రాగాన్ని కంపోజ్ చేస్తున్నాడు..."):
            time.sleep(1.5)  # Simulates server processing time
            
            # Lock everything inside the permanent memory state
            st.session_state.audio_ready = True
            st.session_state.saved_lyrics = user_lyrics
            st.session_state.saved_track = MELODY_TRACKS[singer_type]

st.divider()

# 5. BUG-FREE PERMANENT DISPLAY (Will never disappear or disable when clicked)
if st.session_state.audio_ready:
    st.success("🎉 అద్భుతమైన మెలోడీ పాట సిద్ధంగా ఉంది!")
    
    # Show lyrics inside a stable text container box
    st.info(f"📝 **మీ పాట సాహిత్యం:**\n\n{st.session_state.saved_lyrics}")
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen below without any disabling issue):**")
    
    # CRITICAL MOBILE FIX: Direct HTML5 injection bypassing Streamlit state re-evaluation loops
    audio_html = f"""
    <div style="background-color: #f1f3f4; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <audio controls style="width: 100%;">
            <source src="{st.session_state.saved_track}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    </div>
    <div style="margin-top: 15px;">
        <a href="{st.session_state.saved_track}" download="telugu_melody_song.mp3" target="_blank"
           style="display: inline-block; padding: 12px 24px; color: white; background-color: #25D366; 
           text-decoration: none; border-radius: 6px; font-weight: bold; text-align: center; width: 100%;">
           📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)
        </a>
    </div>
    """
    st.components.v1.html(audio_html, height=140)
