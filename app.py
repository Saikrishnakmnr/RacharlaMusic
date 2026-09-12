import streamlit as st
from gtts import gTTS
import io

# Page setup
st.set_page_config(page_title="సులువు తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 తెలుగు AI వాయిస్ & సాంగ్ జనరేటర్")
st.write("మీ తెలుగు లిరిక్స్ ఇవ్వండి, ఆడియో ట్రాక్ సృష్టించి డౌన్లోడ్ చేసుకోండి!")

# Streamlit Form to lock player stability 
with st.form(key="voice_music_form"):
    user_lyrics = st.text_area(
        label="మీ తెలుగు లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
        value="వినాయకా విఘ్నరాజా వేగమే రావయ్యా |\nమమ్మేలుకొని నీ దీవెనలు ఇయ్యవయ్యా ||",
        height=120
    )
    
    st.write("✨ *గమనిక: ఈ వెర్షన్ మీ లిరిక్స్ను స్వచ్ఛమైన తెలుగు వాయిస్ ఆడియోగా మారుస్తుంది.*")
    generate_btn = st.form_submit_button(label="ఆడియోను సృష్టించు (Generate Audio)")

# Processing Block
if generate_btn:
    if not user_lyrics.strip():
        st.warning("✍️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("ఆడియోను కంపోజ్ చేస్తోంది... దయచేసి వేచి ఉండండి..."):
            try:
                # Initialize Google Text-to-Speech engine for Telugu ('te')
                tts = gTTS(text=user_lyrics, lang='te', slow=False)
                
                # Write audio directly into memory bytes
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()
                
                st.success("🎉 మీ కోసం ఆడియో ట్రాక్ సిద్ధమైంది!")
                st.info(f"📝 **సాహిత్యం:**\n\n{user_lyrics}")
                st.divider()
                
                # Persistent audio player (Will not disappear when clicked)
                st.write("🎧 **పాటను ఇక్కడ వినండి (Listen):**")
                st.audio(audio_bytes, format="audio/mp3")
                
                # Native HTML download button (100% free downloading enabled)
                st.download_button(
                    label="📥 ఆడియోను డౌన్లోడ్ చేసుకోండి (Download MP3)",
                    data=audio_bytes,
                    file_name="telugu_ai_vocal.mp3",
                    mime="audio/mp3"
                )
                
            except Exception as e:
                st.error(f"⚠️ లోపం జరిగింది: {str(e)}")
