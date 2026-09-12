import streamlit as st
import google.generativeai as genai

# Page setup
st.set_page_config(page_title="సులువు తెలుగు సాంగ్స్ జనరేటర్", page_icon="🎵")
st.title("🎵 సులువు తెలుగు AI సాంగ్ జనరేటర్")
st.write("కేవలం మీ లిరిక్స్ ఇవ్వండి, గూగుల్ AI తో నిజమైన పాటను సృష్టించండి!")

# 1. API Key Input (Get a free key from Google AI Studio)
api_key = st.sidebar.text_input("గూగుల్ API కీ ఎంటర్ చేయండి (Google API Key):", type="password")

with st.form(key="easy_music_form"):
    user_lyrics = st.text_area(
        label="మీ తెలుగు లిరిక్స్ ఇక్కడ రాయండి (Telugu Lyrics):",
        value="వినాయకా విఘ్నరాజా వేగమే రావయ్యా |\nమమ్మేలుకొని నీ దీవెనలు ఇయ్యవయ్యా ||",
        height=120
    )
    
    music_style = st.selectbox(
        "సంగీతం శైలి (Music Style):",
        ["Melodic Carnatic Devotional", "Fast Folk Beats", "Slow Acoustic Melody"]
    )
    
    generate_btn = st.form_submit_button(label="పాటను సృష్టించు (Generate & Play)")

# Processing Block
if generate_btn:
    if not api_key:
        st.error("🔑 దయచేసి సైడ్‌బార్‌లో మీ గూగుల్ API కీని ఎంటర్ చేయండి!")
    elif not user_lyrics.strip():
        st.warning("✍️ దయచేసి లిరిక్స్ టైప్ చేయండి!")
    else:
        with st.spinner("AI నిజమైన పాటను కంపోజ్ చేస్తోంది... దయచేసి వేచి ఉండండి..."):
            try:
                # Configure the official Gemini library
                genai.configure(api_key=api_key)
                
                # Combine parameters into a structured prompt
                structured_prompt = f"""
                Generate a full song with male or female vocals in Telugu using these exact lyrics:
                {user_lyrics}
                
                Music Style: {music_style}
                """
                
                # Call Google's official music generation model
                # Note: Lyria/Music capabilities are embedded in the latest generative models
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Request audio generation response
                response = model.generate_content(
                    structured_prompt,
                    generation_config={"response_mime_type": "audio/mp3"}
                )
                
                # Retrieve the raw song data bytes from the model response
                audio_bytes = response.candidates[0].content.parts[0].inline_data.data
                
                st.success("🎉 మీ కోసం నిజమైన పాట సిద్ధమైంది!")
                st.info(f"📝 **సాహిత్యం:**\n\n{user_lyrics}")
                st.divider()
                
                # Persistent audio player (Will not disappear when clicked)
                st.write("🎧 **పాటను ఇక్కడ వినండి (Listen):**")
                st.audio(audio_bytes, format="audio/mp3")
                
                # Native HTML download button (100% free downloading enabled)
                st.download_button(
                    label="📥 పాటను డౌన్లోడ్ చేసుకోండి (Download MP3)",
                    data=audio_bytes,
                    file_name="telugu_ai_song.mp3",
                    mime="audio/mp3"
                )
                
            except Exception as e:
                st.error(f"⚠️ లోపం జరిగింది: {str(e)}")
