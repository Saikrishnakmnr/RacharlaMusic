import streamlit as st
import requests
import base64

# 1. Page Configuration
st.set_page_config(page_title="ఉచిత తెలుగు సాంగ్ జనరేటర్", page_icon="🎵")
st.title("🎵 ఉచిత తెలుగు AI సాంగ్ జనరేటర్")
st.write("డబ్బులు లేదా API కీలు అవసరం లేదు! మీ తెలుగు లిరిక్స్ ఇచ్చి ఆడియోను సృష్టించండి.")

# Initialize persistent memory state variables to lock mobile browser stability
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "saved_voice_data" not in st.session_state:
    st.session_state.saved_voice_data = None
if "saved_lyrics" not in st.session_state:
    st.session_state.saved_lyrics = ""

# 2. User Input Area
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||",
    height=120
)

# 3. Trigger Free Open-Source Generation Pipeline
if st.button("ఉచిత ఆడియోను సృష్టించు (Generate Free Audio)"):
    if not user_lyrics.strip():
        st.warning("✍️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("ఓపెన్-సోర్స్ AI ఆడియోను సిద్ధం చేస్తోంది... దయచేసి వేచి ఉండండి..."):
            try:
                # Direct call to Hugging Face's stable, free open-source Telugu audio model
                API_URL = "https://huggingface.co"
                headers = {"Content-Type": "application/json"}
                payload = {"inputs": user_lyrics}
                
                response = requests.post(API_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    # Store data directly into safe app memory slots to bypass mobile resets
                    st.session_state.audio_ready = True
                    st.session_state.saved_voice_data = audio_bytes
                    st.session_state.saved_lyrics = user_lyrics
                else:
                    st.error("🤖 సర్వర్ బిజీగా ఉంది లేదా రెస్పాన్స్ రాలేదు. దయచేసి మరోసారి బటన్ నొక్కండి.")
            except Exception as e:
                st.error(f"⚠️ లోపం జరిగింది: {str(e)}")

st.divider()

# 4. FIXED DISPLAY BLOCK OUTSIDE INTERACTION CYCLE (Will not vanish on mobile play)
if st.session_state.audio_ready:
    st.success("🎉 మీ తెలుగు ఆడియో ట్రాక్ సిద్ధమైంది!")
    st.info(f"📝 **సాహిత్యం:**\n\n{st.session_state.saved_lyrics}")
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen below without any disabling issue):**")
    
    # Safe base64 HTML5 container preventing refresh bugs on mobile screen layouts
    b64_audio = base64.b64encode(st.session_state.saved_voice_data).decode()
    
    audio_html = f"""
    <div style="background-color: #f1f3f4; padding: 12px; border-radius: 8px;">
        <audio controls style="width: 100%;">
            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
        </audio>
    </div>
    """
    st.components.v1.html(audio_html, height=80)
    
    # Persistent Download Button
    st.download_button(
        label="📥 ఆడియోను డౌన్లోడ్ చేసుకోండి (Download WAV)",
        data=st.session_state.saved_voice_data,
        file_name="telugu_free_vocal.wav",
        mime="audio/wav"
    )
