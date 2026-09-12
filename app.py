import streamlit as st
import random

# App setup
st.set_page_config(page_title="తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు సాంగ్స్ జనరేటర్")
st.write("మీకు కావలసిన శైలిని ఎంచుకోండి, లిరిక్స్ మరియు పాటను వినండి!")

# Pure Telugu Songs Database (Lyrics + Royalty-free Audio sample links)
# Note: Replace URL links with your own audio files or hosted Telugu mp3 tracks.
songs_db = {
    "భక్తి పాటలు (Devotional)": {
        "lyrics": "వినాయకా విఘ్నరాజా వేగమే రావయ్యా |\nమమ్మేలుకొని నీ దీవెనలు ఇయ్యవయ్యా ||",
        "audio_url": "https://soundhelix.com"  
    },
    "ప్రేమ పాటలు (Romantic)": {
        "lyrics": "నువ్వు నాతో ఉంటే చాలు గుండెల్లో ఏదో అలజడి |\nనీ నీడగా సాగడమే నా ప్రాణానికి ఊపిరి ||",
        "audio_url": "https://soundhelix.com"
    },
    "ఉత్సాహ భరిత పాటలు (Mass/Energetic)": {
        "lyrics": "దరుве బద్దలయ్యేలా అడుగులేయరా తమ్ముడా |\nమన దెబ్బకి లోకమంతా అదిరిపోవాలిరా ||",
        "audio_url": "https://soundhelix.com"
    }
}

# User Interface
genre = st.selectbox("పాట శైలిని ఎంచుకోండి (Select Genre):", list(songs_db.keys()))

if st.button("పాటను ప్లే చేయి (Generate & Play Song)"):
    selected_track = songs_db[genre]
    
    # 1. Show Telugu Lyrics
    st.success("✨ మీ కోసం సిద్ధంగా ఉన్న లిరిక్స్:")
    st.subheader(selected_track["lyrics"])
    
    st.divider()
    
    # 2. Show Audio Music Player
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen to Song):**")
    st.audio(selected_track["audio_url"], format="audio/mp3")
    
