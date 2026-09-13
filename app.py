import streamlit as st

st.set_page_config(
    page_title="RacharlaMusic Studio",
    page_icon="🎵",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp { font-family: Poppins, sans-serif; color: #fff; background: linear-gradient(135deg,#06051a,#10134a 50%,#061c39); }
.glass { border: 1px solid rgba(255,255,255,.14); border-radius: 24px; padding: 22px; background: rgba(25,28,88,.86); }
.title { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg,#fff,#ff4ed4,#7c62ff,#20e5ff); -webkit-background-clip: text; color: transparent; }
.stButton>button { border: 0!important; border-radius: 16px!important; color: #fff!important; font-weight: 800!important; background: linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important; min-height: 52px!important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic Studio</div>'
    '<div style="color: #bdbcdc;">Generate Full Vocal Song Prompts & Structured Lyrics</div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Telugu Romantic": "Melodic Telugu film song, emotional lead vocals, acoustic guitar, lush strings, 80 BPM",
    "Telugu Mass": "High energy Telugu commercial song, powerful vocals, heavy folk drums, brass section, 128 BPM",
    "English Pop": "Modern English pop ballad, clear smooth lead singing, warm piano, soft synth pads, 100 BPM",
    "Telugu Folk": "Traditional Telugu folk melody, rustic vocals, dholak, rhythm beats",
}

with st.sidebar:
    st.markdown("## 🎼 Track Settings")
    style_choice = st.selectbox("Song Style", list(STYLES))
    genre_tags = STYLES[style_choice]

c1, c2 = st.columns([1.2, 0.8], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Song Concept / Lyrics")
    concept = st.text_area("Enter your topic or lyrics draft", height=180, placeholder="Write a Telugu romantic song about rain and love...")
    title = st.text_input("Song Title", value="My Racharla Song")
    btn = st.button("✨ BUILD SONG PROMPT STUDIO 🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎧 Production Ready Output")
    
    if btn and concept.strip():
        formatted_prompt = f"{genre_tags}, expressive vocals, professional studio recording"
        formatted_lyrics = f"[Verse 1]\n{concept}\n\n[Chorus]\n{title} - my heart beats for you\n\n[Outro]\nSoft melody fading out..."
        
        st.markdown("**Style Prompt (Copy to Suno/Udio):**")
        st.code(formatted_prompt, language="text")
        
        st.markdown("**Structured Lyrics:**")
        st.code(formatted_lyrics, language="text")
        
        st.success("Prompt Ready! Copy these into Suno.com or Udio.com for instant 2-minute vocal generation.")
    else:
        st.info("Enter your song concept and click Generate to prepare production prompts.")
    st.markdown("</div>", unsafe_allow_html=True)
