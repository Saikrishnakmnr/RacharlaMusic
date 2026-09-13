import streamlit as st
import requests
import time

# 1. App Configuration
st.set_page_config(page_title="Racharla Free Music", page_icon="🎵")
st.title("🎵 Racharla Unofficial Suno AI Generator")
st.write("సంపూర్ణ ఉచితం! ఎటువంటి పేమెంట్స్ లేకుండా మీ స్వంత తెలుగు లిరిక్స్ ద్వారా పాటను సృష్టించండి.")

# Initialize persistent memory cache for stable mobile rendering
if "suno_audio_ready" not in st.session_state:
    st.session_state.suno_audio_ready = False
if "suno_song_url" not in st.session_state:
    st.session_state.suno_song_url = ""
if "suno_lyrics" not in st.session_state:
    st.session_state.suno_lyrics = ""

# 2. Input UI Layout
user_lyrics = st.text_area(
    label="మీ 4 లైన్ల లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
    value="చిరు నవ్వులొలికే ఓ చిన్నారి గణపతి |\nమా గుండెల్లో కొలువై ఉండาลัย్యా ||",
    height=120
)

music_style = st.text_input(
    label="సంగీతం శైలి (Music Style Tags):",
    value="beautiful melodic telugu pop male vocals"
)

# 3. Trigger Unofficial Free Generation Pipeline
if st.button("ఉచిత పాటను సృష్టించు (Generate Free Song)"):
    if not user_lyrics.strip():
        st.warning("✍️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("ఉచిత Suno AI ఇంజిన్ పాటను కంపోజ్ చేస్తోంది... (దీనికి 1-2 నిమిషాలు పట్టవచ్చు)..."):
            try:
                # Payload mapped directly to unofficial custom generation schemas
                payload = {
                    "prompt": user_lyrics,
                    "tags": music_style,
                    "title": "Racharla Track",
                    "make_instrumental": False,
                    "wait_audio": False
                }
                
                # Connecting to a public, free-tier unofficial cloud proxy deployment
                # This instance automatically injects dynamic rotation cookies
                response = requests.post("https://vercel.app", json=payload, timeout=15)
                
                if response.status_code == 200:
                    clips = response.json()
                    
                    # Unofficial wrappers return a list containing two version items
                    if isinstance(clips, list) and len(clips) > 0:
                        # Grab the target object reference data
                        task_id = clips[0].get("id")
                        
                        # 4. Polling Loop to trace cloud file compilation progress
                        song_url = None
                        for _ in range(30):
                            time.sleep(4)
                            status_res = requests.get(f"https://vercel.app{task_id}", timeout=10)
                            
                            if status_res.status_code == 200:
                                status_data = status_res.json()
                                if isinstance(status_data, list) and len(status_data) > 0:
                                    current_clip = status_data[0]
                                    if current_clip.get("status") == "streaming" or current_clip.get("audio_url"):
                                        song_url = current_clip.get("audio_url")
                                        break
                                    elif current_clip.get("status") == "failed":
                                        st.error("AI కంపోజిషన్ ఫెయిల్ అయింది. దయచేసి మరోసారి ప్రయత్నించండి.")
                                        break
                        
                        if song_url:
                            st.session_state.suno_audio_ready = True
                            st.session_state.suno_song_url = song_url
                            st.session_state.suno_lyrics = user_lyrics
                        else:
                            st.error("⏳ సర్వర్ సమయం ముగిసింది. దయచేసి మళ్ళీ ప్రయత్నించండి.")
                    else:
                        st.error("సర్వర్ నుండి తప్పుడు రెస్పాన్స్ వచ్చింది. దయచేసి రీఫ్రెష్ చేయండి.")
                else:
                    st.error(f"🤖 ఉచిత సర్వర్ బిజీగా ఉంది (Status: {response.status_code}). దయచేసి మరోసారి నొక్కండి.")
                    
            except Exception as e:
                st.error(f"⚠️ కనెక్షన్ సర్వర్ లోపం: {str(e)}")

st.divider()

# 5. MOBILE LOCK BLOCK: Permanent layout element that completely bypasses refreshing bugs
if st.session_state.suno_audio_ready:
    st.success("🎉 అద్భుతం! మీ ఉచిత సాంగ్ సిద్ధంగా ఉంది!")
    st.info(f"📝 **సాహిత్యం:**\n\n{st.session_state.suno_lyrics}")
    
    st.write("🎧 **పాటను ఇక్కడ వినండి (Listen below without freezing):**")
    
    # Sandboxed block isolates media playback from primary page state
    audio_html = f"""
    <div style="background-color: #f1f3f4; padding: 12px; border-radius: 8px;">
        <audio controls style="width: 100%;">
            <source src="{st.session_state.suno_song_url}" type="audio/mp3">
        </audio>
    </div>
    <div style="margin-top: 15px;">
        <a href="{st.session_state.suno_song_url}" download="racharla_free_song.mp3" target="_blank"
           style="display: inline-block; padding: 12px 20px; color: white; background-color: #25D366; 
           text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; width: 100%;">
           📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)
        </a>
    </div>
    """
    st.components.v1.html(audio_html, height=140)
