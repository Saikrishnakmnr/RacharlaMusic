import streamlit as st
from google import genai
from gtts import gTTS
import base64
import io

# 1. Page Configuration
st.set_page_config(page_title="జెమిని ఆడియో జనరేటర్", page_icon="🎵")
st.title("🎵 జెమిని ఆడియో సాంగ్ జనరేటర్")
st.write("మీ జెమిని కీ ఉపయోగించి డైరెక్ట్ ఆడియోను సృష్టించండి!")

# 2. Get the Gemini Key from Secrets or Sidebar Drawer
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("గూగుల్ API కీ (Gemini Key):", type="password")

# Initialize persistent memory state variables to block page reset bugs
if "audio_ready" not in st.session_state:
    st.session_state.audio_ready = False
if "saved_voice_data" not in st.session_state:
    st.session_state.saved_voice_data = None
if "saved_lyrics" not in st.session_state:
    st.session_state.saved_lyrics = ""

# 3. User Text Input Layout
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండాలయ్యా ||",
    height=120
)

# 4. Trigger Execution Action
if st.button("ఆడియోను సృష్టించు (Generate Audio)"):
    if not api_key:
        st.error("🔑 దయచేసి సైడ్‌బార్‌లో మీ గూగుల్ జెమిని కీని ఎంటర్ చేయండి!")
    elif not user_lyrics.strip():
        st.warning("✍️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("జెమిని AI మీ లిరిక్స్ ప్రాసెస్ చేస్తోంది..."):
            try:
                # Initialize the modern Google GenAI Client
                client = genai.Client(api_key=api_key)
                
                # Refine the poetry structure for proper vocal delivery rhythm
                prompt_text = f"Format and clean up these Telugu lyrics for a smooth musical cadence. Do not add any English or meta-text, output ONLY the Telugu lyrics: {user_lyrics}"
                
                # FIXED: Targets the mandated production model 'gemini-3.6-flash'
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt_text
                )
                
                # Extract text response from the API output safely
                refined_text = response.text if response.text else user_lyrics
                
                # 5. Build high fidelity audio data array from the processed lyrics stream
                tts = gTTS(text=refined_text, lang='te', slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()
                
                if audio_bytes:
                    st.session_state.audio_ready = True
                    st.session_state.saved_voice_data = audio_bytes
                    st.session_state.saved_lyrics = refined_text
                else:
                    st.error("ఆడియో డేటా దొరకలేదు. దయచేసి మరోసారి ప్రయత్నించండి.")
                    
            except Exception as e:
                st.error(f"⚠️ లోపం జరిగింది: {str(e)}")

st.divider()

# 6. FIXED DISPLAY BLOCK OUTSIDE INTERACTION CYCLE
if st.session_state.audio_ready:
    st.success("🎉 జెమిని ద్వారా మీ ఆడియో ట్రాక్ సిద్ధమైంది!")
    st.info(f"📝 **సాహిత్యం:**\n\n{st.session_state.saved_lyrics}")
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen below without any disabling issue):**")
    
    # Safe HTML5 wrapper rendering to prevent mobile page refreshing bugs completely
    b64_audio = base64.b64encode(st.session_state.saved_voice_data).decode()
    
    audio_html = f"""
    <div style="background-color: #f1f3f4; padding: 12px; border-radius: 8px;">
        <audio controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    </div>
    """
    st.components.v1.html(audio_html, height=80)
    
    # Persistent Download Button
    st.download_button(
        label="📥 ఆడియోను డౌన్లోడ్ చేసుకోండి (Download MP3)",
        data=st.session_state.saved_voice_data,
        file_name="gemini_song.mp3",
        mime="audio/mp3"
    )
