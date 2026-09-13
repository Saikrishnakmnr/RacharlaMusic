import base64
import hashlib
import re

import streamlit as st
import streamlit.components.v1 as components

from lyrics.local import generate as generate_lyrics
from providers.local import LocalFallbackProvider


st.set_page_config(
    page_title="RacharlaMusic",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# NEON UI
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 8% 8%, rgba(255,0,220,.13), transparent 30%),
        radial-gradient(circle at 92% 10%, rgba(0,200,255,.14), transparent 32%),
        linear-gradient(135deg,#07051b 0%,#11165a 55%,#04253c 100%);
    color:#ffffff;
}

section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#12154f,#101344);
    border-right:1px solid rgba(255,255,255,.08);
}

.block-container {
    max-width:1150px;
    padding-top:1.5rem;
}

.glass {
    background:rgba(8,10,35,.50);
    border:1px solid rgba(255,255,255,.13);
    border-radius:20px;
    padding:22px;
    box-shadow:0 12px 50px rgba(0,0,0,.25);
}

.hero {
    border-radius:22px;
    padding:18px;
    background:
        linear-gradient(
            100deg,
            rgba(255,20,200,.15),
            rgba(120,70,255,.12),
            rgba(0,210,255,.15)
        );
    border:1px solid rgba(255,255,255,.13);
}

.title {
    font-size:2.8rem;
    font-weight:800;
    background:linear-gradient(90deg,#ff2ccf,#9a62ff,#00dfff);
    -webkit-background-clip:text;
    color:transparent;
    margin:0;
}

.hint {
    border-left:3px solid #00e5ff;
    padding:11px 14px;
    background:rgba(0,220,255,.06);
    border-radius:10px;
}

.small {
    color:#aaaecb;
    font-size:.88rem;
}

div.stButton > button {
    border-radius:14px;
    min-height:48px;
    font-weight:800;
    background:linear-gradient(90deg,#ff19c8,#8050ff,#00cfe9);
    color:white;
    border:0;
}

div[data-testid="stDownloadButton"] button {
    border-radius:14px;
    font-weight:800;
}

.successbox {
    background:rgba(0,220,160,.10);
    border:1px solid rgba(0,255,200,.20);
    border-radius:14px;
    padding:14px;
}

.warningbox {
    background:rgba(255,180,0,.08);
    border:1px solid rgba(255,190,0,.20);
    border-radius:14px;
    padding:14px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")

    language = st.selectbox(
        "🌐 Lyrics",
        ["Telugu", "English", "Telugu + English"],
    )

    vocal = st.selectbox(
        "🎤 Vocal",
        ["Natural lead", "Female", "Male", "Duet"],
    )

    styles = [
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
    ]

    style = st.selectbox("🎼 Style", styles)

    length_min = st.slider(
        "⏱️ Length",
        min_value=1,
        max_value=6,
        value=2,
        step=1,
        format="%d min",
    )

    st.markdown("---")

    st.info(
        "🆓 **Independent local mode**\n\n"
        "No Hugging Face Spaces.\n"
        "No ZeroGPU.\n"
        "No API key.\n"
        "No payment system.\n\n"
        "The local engine creates a musical backing track. "
        "Natural AI singing requires a separate singing model/service."
    )


# ============================================================
# SESSION STATE
# ============================================================

if "draft_lyrics" not in st.session_state:
    st.session_state["draft_lyrics"] = ""

if "title_input" not in st.session_state:
    st.session_state["title_input"] = "My Racharla Song"

if "direction_input" not in st.session_state:
    st.session_state["direction_input"] = (
        "warm piano, soft pads, clear melody, dynamic chorus"
    )

if "last_settings" not in st.session_state:
    st.session_state["last_settings"] = None


current_settings = (language, style, length_min, vocal)

if st.session_state["last_settings"] is not None:
    previous = st.session_state["last_settings"]

    if previous != current_settings:
        # Keep lyrics but remove old audio when generation settings change.
        st.session_state.pop("audio", None)

st.session_state["last_settings"] = current_settings


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="title">RacharlaMusic</div>'
    '<div class="small">Free Telugu • English • Mixed music maker</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# MAIN INPUT AREA
# ============================================================

col1, col2 = st.columns([1, 1])


with col1:
    st.markdown("### ✍️ Lyrics")

    lyrics = st.text_area(
        "Lyrics",
        value=st.session_state["draft_lyrics"],
        height=310,
        label_visibility="collapsed",
        placeholder=(
            "Paste your Telugu / English / mixed lyrics here..."
        ),
    )

    if st.button(
        "✨ GENERATE FREE LYRICS",
        use_container_width=True,
    ):
        generated = generate_lyrics(
            title=st.session_state["title_input"],
            language=language,
            style=style,
        )

        st.session_state["draft_lyrics"] = generated
        st.rerun()


with col2:
    st.markdown("### 🎧 Song details")

    title = st.text_input(
        "🎧 Song title",
        value=st.session_state["title_input"],
    )

    direction = st.text_input(
        "🎹 Extra music direction",
        value=st.session_state["direction_input"],
    )

    st.session_state["title_input"] = title
    st.session_state["direction_input"] = direction

    st.markdown(
        """
<div class="hint">
💡 <b>Better structure:</b><br>
Use sections such as
<b>[Verse]</b>,
<b>[Pre-Chorus]</b>,
<b>[Chorus]</b>,
<b>[Bridge]</b>.
<br><br>
The local music engine uses the actual lyric lines and their
content to create different melodic patterns.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 🎚️ Sound preview")

    exact_seconds = length_min * 60

    st.caption(
        f"{style} • {vocal} • {length_min} minute(s) • "
        f"exact target: {exact_seconds} seconds"
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# GENERATE
# ============================================================

generate = st.button(
    "✨ GENERATE MY SONG 🎵",
    use_container_width=True,
)


if generate:

    if not lyrics.strip():
        st.warning(
            "Please paste lyrics or click GENERATE FREE LYRICS first."
        )
        st.stop()

    st.session_state["draft_lyrics"] = lyrics
    st.session_state["title_input"] = title

    seed_text = (
        f"{title}|{lyrics}|{style}|{vocal}|"
        f"{direction}|{language}"
    )

    seed = int(
        hashlib.sha256(
            seed_text.encode("utf-8")
        ).hexdigest()[:12],
        16,
    )

    # IMPORTANT:
    # Slider is minutes.
    # Generator receives seconds.
    duration_seconds = int(length_min * 60)

    status = st.empty()

    status.info(
        f"🎼 Generating exact {duration_seconds}-second "
        f"{style} music..."
    )

    provider = LocalFallbackProvider()

    result = provider.generate(
        lyrics=lyrics,
        style_prompt=style,
        seed=seed,
        duration_sec=duration_seconds,
        vocal=vocal,
        title=title.strip() or "RacharlaMusic Song",
        language=language,
        direction=direction,
    )

    if result.ok:

        st.session_state["audio"] = result.audio_bytes
        st.session_state["duration_seconds"] = duration_seconds
        st.session_state["provider"] = result.provider
        st.session_state["generated_title"] = (
            title.strip() or "RacharlaMusic Song"
        )
        st.session_state["lyrics_to_sing"] = lyrics
        st.session_state["generated_language"] = language
        st.session_state["generated_vocal"] = vocal

        status.success(
            f"🎉 Generated successfully — "
            f"{duration_seconds} seconds."
        )

    else:
        status.error(result.message)


# ============================================================
# AUDIO RESULT
# ============================================================

if "audio" in st.session_state:

    st.markdown('<div class="glass">', unsafe_allow_html=True)

    st.markdown("## 🎉 Your music is ready")

    duration_seconds = st.session_state.get(
        "duration_seconds",
        0,
    )

    provider_name = st.session_state.get(
        "provider",
        "Local Music Engine",
    )

    st.caption(
        f"Generated by **{provider_name}** • "
        f"exact duration: **{duration_seconds} seconds**"
    )

    st.audio(
        st.session_state["audio"],
        format="audio/wav",
    )

    st.markdown(
        """
<div class="successbox">
🎼 <b>What this track contains:</b>
chords + bass + rhythm + melody + section changes,
generated from your lyrics and selected style.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        st.session_state.get(
            "generated_title",
            "RacharlaMusic_Song",
        ),
    ).strip("_")

    if not safe_name:
        safe_name = "RacharlaMusic_Song"

    st.download_button(
        "⬇️ DOWNLOAD AUDIO (WAV)",
        data=st.session_state["audio"],
        file_name=f"{safe_name}.wav",
        mime="audio/wav",
        use_container_width=True,
    )

    # --------------------------------------------------------
    # VOCAL COMPANION
    # --------------------------------------------------------

    st.markdown("### 🎤 Vocal Companion")

    st.caption(
        "This browser feature speaks the actual lyric lines. "
        "Section labels such as Verse and Chorus are removed "
        "so they are not spoken aloud. "
        "It is a vocal companion, not embedded AI singing."
    )

    raw_lyrics = st.session_state.get(
        "lyrics_to_sing",
        "",
    )

    # Remove section labels before browser speech.
    clean_lines = []

    for line in raw_lyrics.splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove [Verse], [Verse 1], [Chorus], etc.
        if re.match(
            r"^\s*\[[^\]]+\]\s*$",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        # Remove common labels even without brackets.
        if re.match(
            r"^\s*(verse|chorus|hook|bridge|"
            r"pre-chorus|pre chorus|outro|intro)"
            r"(\s*[0-9]+)?\s*:?\s*$",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        clean_lines.append(line)

    clean_lyrics = "\n".join(clean_lines)

    encoded_lyrics = base64.b64encode(
        clean_lyrics.encode("utf-8")
    ).decode("ascii")

    generated_language = st.session_state.get(
        "generated_language",
        language,
    )

    generated_vocal = st.session_state.get(
        "generated_vocal",
        vocal,
    )

    if generated_language == "English":
        lang_code = "en-US"
    elif generated_language == "Telugu":
        lang_code = "te-IN"
    else:
        lang_code = "te-IN"

    # Voice preference passed to JS.
    voice_preference = generated_vocal

    vocal_html = f"""
<div style="
    padding:16px;
    border:1px solid rgba(255,255,255,.12);
    border-radius:15px;
    background:rgba(255,255,255,.04);
">

    <button
        onclick="startVocal()"
        style="
            padding:12px 20px;
            border:0;
            border-radius:11px;
            background:linear-gradient(
                90deg,#ff18c9,#824eff,#00cef4
            );
            color:white;
            font-weight:800;
            cursor:pointer;
        "
    >
        ▶️ Start Vocal Companion
    </button>

    <button
        onclick="stopVocal()"
        style="
            padding:12px 20px;
            border:0;
            border-radius:11px;
            margin-left:8px;
            background:rgba(255,255,255,.12);
            color:white;
            font-weight:800;
            cursor:pointer;
        "
    >
        ⏹️ Stop
    </button>

    <span
        id="vocal-status"
        style="
            margin-left:12px;
            color:#00dfff;
            font-weight:600;
        "
    ></span>

</div>

<script>

let utterance = null;

function decodeLyrics() {{
    const binary = atob("{encoded_lyrics}");
    const bytes = new Uint8Array(binary.length);

    for (let i = 0; i < binary.length; i++) {{
        bytes[i] = binary.charCodeAt(i);
    }}

    return new TextDecoder("utf-8").decode(bytes);
}}


function chooseVoice(languageCode, preference) {{

    const voices = window.speechSynthesis.getVoices();

    const matching = voices.filter(
        v => v.lang &&
        v.lang.toLowerCase().startsWith(
            languageCode.toLowerCase().split("-")[0]
        )
    );

    if (matching.length === 0) {{
        return null;
    }}

    // Browser voices do not reliably expose gender.
    // Use names as a best-effort preference only.
    if (preference === "Female") {{

        const female = matching.find(v =>
            /female|woman|zira|samantha|susan|karen|google uk english female/i
                .test(v.name)
        );

        if (female) return female;
    }}

    if (preference === "Male") {{

        const male = matching.find(v =>
            /male|man|david|daniel|alex|ravi|google uk english male/i
                .test(v.name)
        );

        if (male) return male;
    }}

    return matching[0];
}}


function startVocal() {{

    window.speechSynthesis.cancel();

    const text = decodeLyrics();

    if (!text.trim()) {{
        document.getElementById("vocal-status").textContent =
            "No lyrics available.";
        return;
    }}

    utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "{lang_code}";

    utterance.rate = 0.78;

    utterance.pitch = 1.0;

    const selectedVoice = chooseVoice(
        "{lang_code}",
        "{voice_preference}"
    );

    if (selectedVoice) {{
        utterance.voice = selectedVoice;
    }}

    utterance.onstart = function() {{
        document.getElementById("vocal-status").textContent =
            "🎤 Vocal companion active...";
    }};

    utterance.onend = function() {{
        document.getElementById("vocal-status").textContent =
            "✓ Vocal companion finished.";
    }};

    utterance.onerror = function() {{
        document.getElementById("vocal-status").textContent =
            "⚠️ Browser voice is unavailable.";
    }};

    window.speechSynthesis.speak(utterance);
}}


function stopVocal() {{

    window.speechSynthesis.cancel();

    document.getElementById("vocal-status").textContent =
        "Vocals stopped.";
}}


window.speechSynthesis.onvoiceschanged = function() {{
    window.speechSynthesis.getVoices();
}};

</script>
"""

    components.html(
        vocal_html,
        height=105,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div style="
    text-align:center;
    padding:28px;
    color:#a6a2e8;
">
🎵 RacharlaMusic • 100% Independent • No External GPU Bottlenecks
<br>
<small>Powered by RacharlaGPT.in</small>
</div>
""",
    unsafe_allow_html=True,
)
