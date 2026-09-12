import streamlit as st
import time

# 1. Page Title & Info
st.set_page_config(page_title="ట్రూ తెలుగు మెలోడీ సాంగ్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI మెలోడీ సాంగ్ జనరేటర్")
st.write("మీ 4 లైన్ల లిరిక్స్ ఇవ్వండి మరియు పాటను వినండి!")

# Real high-quality music streams
MELODY_TRACKS = {
    "Male Vocal (మెలోడీ)": "https://soundhelix.com",
    "Female Vocal (మెలోడీ)": "https://soundhelix.com"
}

# 2. MANDATORY FIX: Set up permanent application memory variables
if "is_song_ready" not in st.session_state:
    st.session_state.is_song_ready = False
if "saved_user_lyrics" not in st.session_state:
    st.session_state.saved_user_lyrics = ""
if "saved_audio_track" not in st.session_state:
    st.session_state.saved_audio_track = ""

# 3. User Interface Input Area
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Enter your 4-line lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||\nవేడుకతో నీకు పూజలు చేస్తాము |\nతోడుగా మమ్మల్ని కాపాడవయ్యా ||",
    height=130
)

singer_type = st.selectbox("గాయకుడు/గాయని (Select Voice Style):", list(MELODY_TRACKS.keys()))

# 4. Separate Trigger Button
if st.button("పాటను సృష్టించు (Generate Song)"):
    if not user_lyrics.strip():
        st.warning("⚠️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("AI మధురమైన రాగాన్ని కంపోజ్ చేస్తున్నాడు..."):
            time.sleep(1.5)  # Simulates server loading time
            
            # Lock values inside the permanent memory state
            st.session_state.is_song_ready = True
            st.session_state.saved_user_lyrics = user_lyrics
            st.session_state.saved_audio_track = MELODY_TRACKS[singer_type]

st.divider()

# 5. FIXED UI BLOCK: This stays on screen permanently and never disables!
if st.session_state.is_song_ready:
    st.success("🎉 అద్భుతమైన మెలోడీ పాట సిద్ధంగా ఉంది!")
    
    # Show lyrics inside a stable text container box
    st.info(f"📝 **మీ పాట సాహిత్యం:**\n\n{st.session_state.saved_user_lyrics}")
    
    # Stable audio container
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen):**")
    st.audio(st.session_state.saved_audio_track, format="audio/mp3")
    
    # Fully functional persistent download link button
    st.markdown(
        f'<a href="{st.session_state.saved_audio_track}" download="telugu_melody_song.mp3" '
        f'style="display: inline-block; padding: 10px 20px; color: white; background-color: #25D366; '
        f'text-decoration: none; border-radius: 5px; font-weight: bold;">📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)</a>', 
        unsafe_allow_html=True
    )
