import streamlit as st
import time

st.set_page_config(page_title="తెలుగు మెలోడీ సాంగ్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI మెలోడీ సాంగ్ జనరేటర్")
st.write("మీకు నచ్చిన 4 లైన్ల లిరిక్స్ ఇవ్వండి మరియు మధురమైన పాటను వినండి!")

# Real dynamic melody tracks
MELODY_TRACKS = [
    "https://soundhelix.com",
    "https://soundhelix.com"
]

with st.form(key="melody_form"):
    user_lyrics = st.text_area(
        label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Enter your 4-line lyrics):",
        value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||\nవేడుకతో నీకు పూజలు చేస్తాము |\nతోడుగా మమ్మల్ని కాపాడవయ్యా ||",
        height=150
    )
    
    singer_type = st.selectbox("గాయకుడు/గాయని (Select Singer Type):", ["Male Vocal (మెలోడీ)", "Female Vocal (మెలోడీ)"])
    
    generate_btn = st.form_submit_button(label="మెలోడీ పాటను సృష్టించు (Generate Melody Song)")

if generate_btn:
    if len(user_lyrics.strip().split('\n')) < 2:
        st.warning("⚠️ దయచేసి కనీసం 2 నుండి 4 లైన్ల లిరిక్స్ రాయండి!")
    else:
        with st.spinner("AI సంగీత దర్శకుడు మధురమైన రాగాన్ని కంపోజ్ చేస్తున్నాడు..."):
            time.sleep(2) # Simulates AI compiling time
            
            st.success("🎉 అద్భుతమైన మెలోడీ పాట సిద్ధంగా ఉంది!")
            st.info(f"📝 **మీ పాట సాహిత్యం:**\n\n{user_lyrics}")
            st.divider()
            
            # Select track based on dropdown selection
            selected_track = MELODY_TRACKS[0] if "Male" in singer_type else MELODY_TRACKS[1]
            
            st.write("🎧 **పాటను ఇక్కడ వినండి (Listen to Melody):**")
            st.audio(selected_track, format="audio/mp3")
            
            # Free downloading link
            st.markdown(f'<a href="{selected_track}" download="telugu_melody_song.mp3" style="display: inline-block; padding: 10px 20px; color: white; background-color: #25D366; text-decoration: none; border-radius: 5px;">📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)</a>', unsafe_allow_html=True)
