import streamlit as st

# App setup
st.set_page_config(page_title="తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు సాంగ్స్ జనరేటర్")
st.write("మీకు కావలసిన శైలిని ఎంచుకోండి, లిరిక్స్ మరియు పాటను వినండి!")

# Pure Telugu Songs Database
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
        "lyrics": "దరువే బద్దలయ్యేలా అడుగులేయరా తమ్ముడా |\nమన దెబ్బకి లోకమంతా అదిరిపోవాలిరా ||",
        "audio_url": "https://soundhelix.com"
    }
}

# 1. Initialize session state if it doesn't exist
if "generated_song" not in st.session_state:
    st.session_state.generated_song = None

# User Interface
genre = st.selectbox("పాట శైలిని ఎంచుకోండి (Select Genre):", list(songs_db.keys()))

# 2. When button is clicked, save the selection to session state
if st.button("పాటను ప్లే చేయి (Generate & Play Song)"):
    st.session_state.generated_song = songs_db[genre]

# 3. Always render the song if it exists in session state (prevents disabling)
if st.session_state.generated_song is not None:
    track = st.session_state.generated_song
    
    st.success("✨ మీ కోసం సిద్ధంగా ఉన్న లిరిక్స్:")
    st.subheader(track["lyrics"])
    
    st.divider()
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen to Song):**")
    st.audio(track["audio_url"], format="audio/mp3")
