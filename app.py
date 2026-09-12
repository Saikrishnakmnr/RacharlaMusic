import streamlit as st
import time

# 1. App Setup
st.set_page_config(page_title="తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI మెలోడీ సాంగ్ జనరేటర్")
st.write("మీ 4 లైన్ల లిరిక్స్ ఇవ్వండి మరియు పాటను వినండి!")

# High-quality audio sample streams
MELODY_TRACKS = {
    "Male Vocal (మెలోడీ)": "https://soundhelix.com",
    "Female Vocal (మెలోడీ)": "https://soundhelix.com"
}

# 2. CRITICAL FIX: Initialize Session State variables if they don't exist
if "song_generated" not in st.session_state:
    st.session_state.song_generated = False
if "saved_lyrics" not in st.session_state:
    st.session_state.saved_lyrics = ""
if "saved_track" not in st.session_state:
    st.session_state.saved_track = ""

# 3. User Input Form
with st.form(key="music_generation_form"):
    user_lyrics = st.text_area(
        label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Enter your 4-line lyrics):",
        value="చిరు నవ్వులొలికే ఓ చిన్నારી గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||\nవేడుకతో నీకు పూజలు చేస్తాము |\nతోడుగా మమ్మల్ని కాపాడవయ్యా ||",
        height=130
    )
    
    singer_type = st.selectbox("గాయకుడు/గాయని (Select Voice Style):", list(MELODY_TRACKS.keys()))
    
    submit_btn = st.form_submit_button(label="మెలోడీ పాటను సృష్టించు (Generate Song)")

# 4. Action Block: Save data only when the Form Button is pressed
if submit_btn:
    if not user_lyrics.strip():
        st.warning("⚠️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("AI మధురమైన రాగాన్ని కంపోజ్ చేస్తున్నాడు..."):
            time.sleep(1.5) # Simulates backend compilation delay
            
            # Lock everything into the app memory (Session State)
            st.session_state.song_generated = True
            st.session_state.saved_lyrics = user_lyrics
            st.session_state.saved_track = MELODY_TRACKS[singer_type]

st.divider()

# 5. PERMANENT DISPLAY BLOCK: Runs independently of form button state
if st.session_state.song_generated:
    st.success("🎉 అద్భుతమైన మెలోడీ పాట సిద్ధంగా ఉంది!")
    
    # Show lyrics inside a stable block
    st.info(f"📝 **మీ పాట సాహిత్యం:**\n\n{st.session_state.saved_lyrics}")
    
    # Audio component remains completely stable when clicked
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen to Melody):**")
    st.audio(st.session_state.saved_track, format="audio/mp3")
    
    # Clean reset option to clear screen layout safely
    if st.button("🔄 కొత్త పాటను సృష్టించు (Create New Song)"):
        st.session_state.song_generated = False
        st.rerun()
