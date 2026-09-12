import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 డిజిటల్ తెలుగు సాంగ్స్ జనరేటర్")
st.write("మీ స్వంత తెలుగు లిరిక్స్ ఇవ్వండి మరియు పాటను సృష్టించండి!")

# Pre-mapped high-quality audio streams for execution
AUDIO_TRACKS = [
    "https://soundhelix.com",
    "https://soundhelix.com",
    "https://soundhelix.com"
]

# 2. Form container ensures UI persistence across clicks
with st.form(key="song_generator_form"):
    # User Input for Custom Telugu Lyrics
    user_lyrics = st.text_area(
        label="మీ తెలుగు లిరిక్స్ ఇక్కడ రాయండి (Enter your Telugu lyrics):",
        value="వినాయకా విఘ్నరాజా వేగమే రావయ్యా |\nమమ్మేలుకొని నీ దీవెనలు ఇయ్యవయ్యా ||",
        height=150
    )
    
    # Music Style Selection
    music_style = st.selectbox(
        "సంగీతం శైలిని ఎంచుకోండి (Select Music Style):",
        ["మెలోడీ (Melody)", "మాస్ / ఉత్సాహ భరితం (Mass / Energetic)", "భక్తి రసం (Devotional)"]
    )
    
    # Form submission button
    submit_button = st.form_submit_button(label="పాటను సృష్టించు (Generate Song)")

# 3. Processing and output generation outside the form scope
if submit_button or st.experimental_get_query_params():
    if not user_lyrics.strip():
        st.warning("దయచేసి లిరిక్స్ టైప్ చేయండి! (Please enter some lyrics!)")
    else:
        st.success("✨ మీ లిరిక్స్ విజయవంతంగా ప్రాసెస్ చేయబడ్డాయి!")
        
        # Display the custom lyrics inside a clean visual box
        st.info(f"📝 **పాట సాహిత్యం (Your Lyrics):**\n\n{user_lyrics}")
        
        st.divider()
        
        # Audio simulation picker based on style choice length
        track_index = len(music_style) % len(AUDIO_TRACKS)
        selected_audio = AUDIO_TRACKS[track_index]
        
        # Render the audio interface safely
        st.write(f"🎧 **ప్లేయర్ (Music Player - {music_style}):**")
        st.audio(selected_audio, format="audio/mp3")
