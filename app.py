import os
import re
import base64
from pathlib import Path

import streamlit as st

# Google GenAI SDK
try:
    from google import genai
except ImportError:
    genai = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="RacharlaMusic — AI Song Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "RacharlaMusic"
MODEL_NAME = "lyria-3.5"

POSTER_PATH = Path("assets/racharlamusic_poster.png")


# ============================================================
# NEON / GLASS UI
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(138,43,226,.18), transparent 28%),
        radial-gradient(circle at 90% 15%, rgba(0,229,255,.14), transparent 28%),
        radial-gradient(circle at 50% 100%, rgba(255,0,153,.12), transparent 30%),
        #05060b;
    color: #f7f7ff;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(12, 13, 25, .98),
            rgba(6, 7, 14, .98)
        );
    border-right: 1px solid rgba(0, 229, 255, .15);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.3rem;
}

.hero {
    border: 1px solid rgba(0,229,255,.25);
    background:
        linear-gradient(
            135deg,
            rgba(12,14,28,.90),
            rgba(23,8,34,.82)
        );
    border-radius: 25px;
    padding: 12px;
    box-shadow:
        0 0 30px rgba(0,229,255,.08),
        0 0 70px rgba(255,0,153,.06);
    margin-bottom: 22px;
}

.hero img {
    width: 100%;
    max-height: 360px;
    object-fit: cover;
    border-radius: 18px;
}

.brand {
    text-align: center;
    margin-top: 12px;
}

.brand h1 {
    margin: 0;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(
        90deg,
        #00e5ff,
        #a855f7,
        #ff2ba6
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand p {
    color: #aeb4ca;
    margin-top: 5px;
}

.glass {
    background: rgba(15, 17, 30, .72);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 20px;
    padding: 22px;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.04),
        0 15px 45px rgba(0,0,0,.22);
}

.section-title {
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 8px;
    color: #ffffff;
}

.hint {
    background: rgba(0,229,255,.055);
    border: 1px solid rgba(0,229,255,.16);
    border-radius: 13px;
    padding: 12px 15px;
    color: #b9dce4;
    font-size: .88rem;
    margin: 10px 0 16px 0;
}

.preview-title {
    color: #d9dcf0;
    font-weight: 700;
    margin: 15px 0 8px 0;
}

.footer {
    text-align: center;
    color: #747a91;
    font-size: .82rem;
    padding: 25px 0 10px 0;
}

.small-status {
    text-align: center;
    color: #8e95ae;
    font-size: .82rem;
    margin-top: 8px;
}

div.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(0,229,255,.28);
    background:
        linear-gradient(
            90deg,
            rgba(0,229,255,.16),
            rgba(168,85,247,.18),
            rgba(255,43,166,.16)
        );
    color: white;
    font-weight: 800;
    min-height: 48px;
    transition: all .2s ease;
}

div.stButton > button:hover {
    border-color: rgba(0,229,255,.65);
    box-shadow:
        0 0 18px rgba(0,229,255,.18),
        0 0 28px rgba(255,43,166,.08);
    transform: translateY(-1px);
}

.stTextArea textarea,
.stTextInput input {
    background: rgba(4,5,12,.72) !important;
    color: #f5f6ff !important;
    border-radius: 13px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stSlider {
    color: white;
}

label {
    color: #d9dced !important;
    font-weight: 600 !important;
}

audio {
    width: 100%;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def get_api_key():
    """
    Streamlit secrets first, then environment variables.

    Recommended Streamlit secret:
        GEMINI_API_KEY = "..."
    """

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.getenv("GEMINI_API_KEY", "")

    if not key:
        try:
            key = st.secrets.get("GOOGLE_API_KEY", "")
        except Exception:
            key = ""

    if not key:
        key = os.getenv("GOOGLE_API_KEY", "")

    return str(key).strip()


@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key):
    if genai is None:
        raise RuntimeError(
            "The Google GenAI SDK is not installed. "
            "Add google-genai to requirements.txt."
        )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    return genai.Client(api_key=api_key)


def clean_filename(value):
    value = value.strip()
    value = re.sub(r"[^a-zA-Z0-9_\- ]+", "", value)
    value = re.sub(r"\s+", "_", value)
    return value[:70] or "racharlamusic_song"


def language_instruction(language):
    if language == "Telugu":
        return (
            "The song must be sung primarily in natural Telugu. "
            "Use authentic Telugu pronunciation and natural Telugu phrasing."
        )

    if language == "English":
        return (
            "The song must be sung primarily in natural English "
            "with clear, expressive pronunciation."
        )

    return (
        "Create a natural Telugu + English bilingual song. "
        "Use Telugu and English organically rather than translating every line."
    )


def vocal_instruction(vocal):
    if vocal == "Female":
        return (
            "Use a natural expressive female lead singer with believable "
            "human phrasing, emotion and breath."
        )

    if vocal == "Male":
        return (
            "Use a natural expressive male lead singer with believable "
            "human phrasing, emotion and breath."
        )

    if vocal == "Duet":
        return (
            "Use a natural male and female duet. "
            "Let the voices interact naturally and harmonize in the chorus."
        )

    return (
        "Use a natural expressive lead singer. "
        "The vocal must sound human, emotional and musical."
    )


def style_instruction(style):
    styles = {
        "Melody": (
            "strong memorable melody, flowing vocal lines, "
            "beautiful melodic instrumentation"
        ),
        "Romantic": (
            "warm romantic atmosphere, intimate vocals, "
            "lush chords and emotional melody"
        ),
        "Folk": (
            "Indian folk-inspired rhythm, organic percussion, "
            "acoustic instruments and earthy melodic phrasing"
        ),
        "Mass": (
            "high-energy commercial Indian cinema feel, "
            "powerful rhythm, catchy hook and energetic chorus"
        ),
        "Sad": (
            "emotional melancholic atmosphere, expressive vocals, "
            "minor-key feeling and restrained instrumentation"
        ),
        "Cinematic": (
            "large cinematic arrangement, evolving orchestration, "
            "dramatic dynamics and emotional climax"
        ),
        "Lo-fi": (
            "soft lo-fi textures, mellow drums, warm keys, "
            "relaxed intimate vocal delivery"
        ),
        "Devotional": (
            "devotional atmosphere, soulful melody, "
            "Indian acoustic/percussion elements and reverent vocals"
        ),
        "Hip-hop": (
            "modern hip-hop groove, rhythmic vocal phrasing, "
            "strong bass and a catchy melodic hook"
        ),
        "Rock": (
            "driving drums, electric guitars, powerful chorus "
            "and energetic band arrangement"
        ),
        "Pop": (
            "modern polished pop production, catchy melody, "
            "strong chorus and radio-friendly arrangement"
        ),
    }

    return styles.get(style, styles["Melody"])


def build_music_prompt(
    lyrics,
    title,
    language,
    vocal,
    style,
    duration_minutes,
    extra_direction,
):
    duration_text = (
        f"approximately {duration_minutes} minute"
        if duration_minutes == 1
        else f"approximately {duration_minutes} minutes"
    )

    lyrics_text = lyrics.strip()

    if not lyrics_text:
        lyrics_text = (
            "Write original lyrics that fit the requested language and style."
        )

    if title.strip():
        title_instruction = f'Song title: "{title.strip()}"'
    else:
        title_instruction = "Create a suitable original song title."

    extra = extra_direction.strip()
    if not extra:
        extra = "No additional direction."

    prompt = f"""
Create an original full-length song for RacharlaMusic.

{title_instruction}

TARGET DURATION:
Create a song lasting approximately {duration_text}.
Use the requested duration as a musical target and make the arrangement
feel like a complete song rather than a short loop.

LANGUAGE:
{language_instruction(language)}

VOCAL:
{vocal_instruction(vocal)}

STYLE:
{style_instruction(style)}

MUSICAL QUALITY:
- Create a beautiful original melody.
- Make the melody memorable and emotionally coherent.
- Use natural human-like singing.
- Use realistic vocal phrasing, dynamics and breaths.
- Make the instruments support the vocal melody.
- Include an intro, verses, chorus/hook, and an ending.
- Build the arrangement naturally toward the chorus.
- Avoid sounding like a synthetic demo or simple loop.
- Make the song feel professionally arranged and produced.
- Do not imitate a specific real singer or artist.

STRUCTURE:
Use clear musical sections such as:
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]

CUSTOM LYRICS:
Use the following lyrics as the actual song lyrics.
Do not replace them with unrelated lyrics.

Lyrics:

{lyrics_text}

ADDITIONAL MUSIC DIRECTION:
{extra}

IMPORTANT:
Preserve the meaning and wording of the supplied lyrics as much as
musically possible. Perform them naturally and melodically.
Do not make the result instrumental.
Do not mention these instructions in the song.
"""

    return prompt.strip()


def extract_audio_from_interaction(interaction):
    """
    Current Lyria 3.5 Interactions API exposes generated audio through
    interaction.output_audio.data as base64.

    A defensive fallback also walks through interaction.steps.
    """

    # Preferred documented convenience property.
    try:
        output_audio = interaction.output_audio

        if output_audio is not None:
            data = getattr(output_audio, "data", None)

            if data:
                if isinstance(data, bytes):
                    return data

                if isinstance(data, str):
                    return base64.b64decode(data)

    except Exception:
        pass

    # Defensive fallback for SDK/schema variations.
    try:
        steps = getattr(interaction, "steps", None) or []

        for step in steps:
            if getattr(step, "type", None) != "model_output":
                continue

            content = getattr(step, "content", None) or []

            for block in content:
                if getattr(block, "type", None) != "audio":
                    continue

                data = getattr(block, "data", None)

                if not data:
                    continue

                if isinstance(data, bytes):
                    return data

                if isinstance(data, str):
                    return base64.b64decode(data)

    except Exception:
        pass

    return None


def extract_generated_text(interaction):
    try:
        text = getattr(interaction, "output_text", None)
        if text:
            return str(text)
    except Exception:
        pass

    pieces = []

    try:
        steps = getattr(interaction, "steps", None) or []

        for step in steps:
            if getattr(step, "type", None) != "model_output":
                continue

            content = getattr(step, "content", None) or []

            for block in content:
                if getattr(block, "type", None) == "text":
                    text = getattr(block, "text", None)
                    if text:
                        pieces.append(str(text))

    except Exception:
        pass

    return "\n".join(pieces).strip()


def generate_song(
    lyrics,
    title,
    language,
    vocal,
    style,
    duration_minutes,
    extra_direction,
):
    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to Streamlit Secrets."
        )

    client = get_gemini_client(api_key)

    prompt = build_music_prompt(
        lyrics=lyrics,
        title=title,
        language=language,
        vocal=vocal,
        style=style,
        duration_minutes=duration_minutes,
        extra_direction=extra_direction,
    )

    # Official Google GenAI Interactions API.
    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        response_format={"type": "audio"},
    )

    audio_bytes = extract_audio_from_interaction(interaction)

    if not audio_bytes:
        raise RuntimeError(
            "Lyria 3.5 completed the request but returned no audio data."
        )

    generated_text = extract_generated_text(interaction)

    return audio_bytes, generated_text, prompt


# ============================================================
# HERO
# ============================================================

if POSTER_PATH.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER_PATH), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning(
        "Poster not found: assets/racharlamusic_poster.png"
    )

st.markdown(
    """
<div class="brand">
    <h1>RacharlaMusic</h1>
    <p>AI-powered Telugu • English • Mixed-language song generation</p>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎛️ Song Controls")

    language = st.selectbox(
        "Language",
        [
            "Telugu",
            "English",
            "Telugu + English",
        ],
        index=0,
    )

    vocal = st.selectbox(
        "Vocal",
        [
            "Natural lead",
            "Female",
            "Male",
            "Duet",
        ],
        index=0,
    )

    style = st.selectbox(
        "Style",
        [
            "Melody",
            "Romantic",
            "Folk",
            "Mass",
            "Sad",
            "Cinematic",
            "Lo-fi",
            "Devotional",
            "Hip-hop",
            "Rock",
            "Pop",
        ],
        index=0,
    )

    length = st.slider(
        "Song length",
        min_value=1,
        max_value=6,
        value=1,
        step=1,
        format="%d min",
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="small-status">
        🎵 Powered by Google Lyria 3.5<br>
        🎤 Natural vocals • Melody • Full arrangement
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN INPUT
# ============================================================

left, right = st.columns([1.35, 1], gap="large")


with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🎤 Lyrics</div>',
        unsafe_allow_html=True,
    )

    lyrics = st.text_area(
        "Lyrics",
        height=300,
        placeholder=(
            "[Verse 1]\n"
            "నీ నవ్వే నా లోకం...\n"
            "నీ చూపే నా గానం...\n\n"
            "[Chorus]\n"
            "మనసంతా నీకే...\n"
            "ప్రాణమంతా నీకే..."
        ),
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="hint">
        💡 <b>Better structure:</b>
        Use <b>[Intro]</b>, <b>[Verse 1]</b>,
        <b>[Pre-Chorus]</b>, <b>[Chorus]</b>,
        <b>[Bridge]</b> and <b>[Outro]</b>.
        This helps Lyria create a more coherent melody and arrangement.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">🎵 Song title</div>',
        unsafe_allow_html=True,
    )

    title = st.text_input(
        "Song title",
        placeholder="Enter your song title",
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="section-title">🎚️ Extra music direction</div>',
        unsafe_allow_html=True,
    )

    extra_direction = st.text_area(
        "Extra music direction",
        height=130,
        placeholder=(
            "Example: soft piano intro, emotional strings, "
            "Indian percussion, memorable chorus, cinematic ending..."
        ),
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)


with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🎼 Generation</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hint">
        <b>{language}</b> · <b>{vocal}</b> · <b>{style}</b><br>
        Target length: <b>{length} minute{'s' if length != 1 else ''}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Lyria 3.5 is designed for complete musical arrangements,
        including vocals, lyrics, verses, choruses and bridges.
        """
    )

    generate_clicked = st.button(
        "🎵 GENERATE SONG",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        """
        <div class="small-status">
        Your first test can stay at 1 minute to keep generation time lower.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# GENERATION
# ============================================================

if generate_clicked:
    if not lyrics.strip():
        st.error("Please enter lyrics first.")
    else:
        with st.spinner(
            "🎵 Lyria 3.5 is composing the melody, arrangement and vocals..."
        ):
            try:
                audio_bytes, generated_text, used_prompt = generate_song(
                    lyrics=lyrics,
                    title=title,
                    language=language,
                    vocal=vocal,
                    style=style,
                    duration_minutes=length,
                    extra_direction=extra_direction,
                )

                st.session_state["generated_audio"] = audio_bytes
                st.session_state["generated_text"] = generated_text
                st.session_state["generated_title"] = (
                    title.strip() or "RacharlaMusic Song"
                )

                st.success(
                    "🎉 Song generated successfully!"
                )

            except Exception as exc:
                error_text = str(exc)

                st.error("❌ Song generation failed.")

                # Useful, readable diagnostics.
                if (
                    "API key" in error_text
                    or "401" in error_text
                    or "403" in error_text
                ):
                    st.warning(
                        "Your Gemini API key is missing, invalid, "
                        "or does not have access to Lyria 3.5."
                    )

                elif (
                    "429" in error_text
                    or "quota" in error_text.lower()
                    or "resource exhausted" in error_text.lower()
                ):
                    st.warning(
                        "Gemini API quota/rate limit was reached. "
                        "This is an API account limit, not a Streamlit bug."
                    )

                else:
                    with st.expander("Technical details"):
                        st.code(error_text)


# ============================================================
# AUDIO PREVIEW
# ============================================================

if "generated_audio" in st.session_state:
    st.markdown("---")

    st.markdown(
        '<div class="preview-title">🎚️ Sound preview</div>',
        unsafe_allow_html=True,
    )

    audio_bytes = st.session_state["generated_audio"]

    # Lyria 3.5 defaults to MP3 according to Google's documentation.
    st.audio(
        audio_bytes,
        format="audio/mpeg",
    )

    song_title = st.session_state.get(
        "generated_title",
        "RacharlaMusic Song",
    )

    filename = clean_filename(song_title) + ".mp3"

    st.download_button(
        label="⬇️ DOWNLOAD MP3",
        data=audio_bytes,
        file_name=filename,
        mime="audio/mpeg",
        use_container_width=True,
    )

    generated_text = st.session_state.get(
        "generated_text",
        "",
    )

    if generated_text:
        with st.expander("🎼 Generated song information"):
            st.write(generated_text)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    Powered by <b>RacharlaGPT.in</b>
</div>
""",
    unsafe_allow_html=True,
)
