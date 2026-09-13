import os
import re
import random
from pathlib import Path

import requests
import streamlit as st

APP_NAME = "RacharlaMusic"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

# IMPORTANT: These are NEW backends. ACE-Step, MiniMax Music 3 and Gemini/Lyria
# are intentionally NOT used in this build because their earlier integrations
# exhausted quota or required paid API access during our testing.
YUE2_SPACE = "mrfakename/yue2-3b"
DIFFRHYTHM2_SPACE = "ASLP-lab/DiffRhythm2"

st.set_page_config(page_title=APP_NAME, page_icon="🎵", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp{font-family:Poppins,sans-serif;color:#fff;background:
radial-gradient(circle at 8% 4%,rgba(255,30,205,.22),transparent 27%),
radial-gradient(circle at 94% 8%,rgba(0,220,255,.18),transparent 28%),
radial-gradient(circle at 55% 90%,rgba(105,62,255,.22),transparent 34%),
linear-gradient(135deg,#06051a,#10134a 50%,#061c39);}
.block-container{max-width:1280px;padding-top:1rem}
.hero{border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.16);
box-shadow:0 25px 75px rgba(0,0,0,.48),0 0 45px rgba(255,35,205,.13);margin-bottom:22px}
.hero img{display:block;width:100%}
.glass{border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:22px;
background:linear-gradient(145deg,rgba(25,28,88,.86),rgba(6,20,57,.78));
box-shadow:0 20px 55px rgba(0,0,0,.34),inset 0 1px rgba(255,255,255,.06)}
.title{font-size:2.5rem;font-weight:800;background:linear-gradient(90deg,#fff,#ff4ed4,#7c62ff,#20e5ff);
-webkit-background-clip:text;color:transparent}
.muted{color:#bdbcdc}
.badge{display:inline-block;margin:4px;padding:6px 11px;border-radius:99px;background:rgba(255,255,255,.07);
border:1px solid rgba(255,255,255,.1);font-size:.78rem}
.tip{border-left:4px solid #ff35cf;border-radius:0 14px 14px 0;background:rgba(255,53,207,.07);padding:12px 15px}
.stButton>button{border:0!important;border-radius:16px!important;color:#fff!important;font-weight:800!important;
background:linear-gradient(90deg,#ff18c9,#824eff,#00cef4)!important;
box-shadow:0 12px 35px rgba(255,24,201,.3)!important;min-height:52px!important}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 18px 45px rgba(255,24,201,.42)!important}
div[data-testid="stTextArea"] textarea{background:rgba(4,8,35,.88)!important;color:white!important;
border-radius:18px!important;border:1px solid rgba(160,110,255,.45)!important}
div[data-baseweb="select"]>div{background:rgba(6,11,44,.9)!important;border-radius:14px!important}
.footer{text-align:center;color:#aaa9c9;padding:30px 0 8px}
.free-note{border:1px solid rgba(0,220,255,.20);background:rgba(0,220,255,.06);padding:10px 14px;border-radius:14px;color:#c9f8ff}
</style>
""", unsafe_allow_html=True)

if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
    '<div class="muted">Your lyrics • AI melody • Natural singing • Your song</div>'
    '<div><span class="badge">🇮🇳 Telugu</span><span class="badge">🇬🇧 English</span>'
    '<span class="badge">🔀 Mixed</span><span class="badge">🎤 Vocals</span>'
    '<span class="badge">⬇️ MP3</span><span class="badge">🆓 Free</span></div></div><br>',
    unsafe_allow_html=True,
)

STYLES = {
    "Melody": "beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar, lush strings, soft percussion, expressive lead vocal, polished studio mix",
    "Romantic": "romantic Indian film song, intimate lead vocal, piano, acoustic guitar, lush strings, emotional melody, polished studio production",
    "Folk": "Telugu folk-inspired song, organic percussion, acoustic instruments, catchy traditional melody, energetic lead vocal",
    "Mass": "high-energy Telugu commercial song, powerful lead vocal, punchy drums, bass, rhythmic hooks, cinematic production",
    "Sad": "emotional Indian ballad, expressive lead vocal, piano, strings, restrained drums, haunting memorable melody",
    "Cinematic": "grand Indian cinematic soundtrack, expressive lead vocal, orchestral strings, piano, percussion, dramatic build",
    "Lo-fi": "dreamy lo-fi Indian pop, intimate lead vocal, soft drums, warm keys, mellow bass",
    "Devotional": "devotional Indian melody, respectful lead vocal, flute, gentle percussion, uplifting arrangement",
    "Hip-hop": "Indian melodic hip-hop, sung hook, rhythmic vocal delivery, deep bass, crisp drums, modern production",
    "Rock": "Indian pop rock, expressive lead vocal, electric guitars, live drums, bass, strong melodic chorus",
    "Pop": "modern Indian pop, natural lead vocal, catchy melody, polished drums, bass, bright synths",
}
LANG = {"Telugu": "Telugu", "English": "English", "Telugu + English": "English"}

# ----------------------------- helpers -----------------------------
@st.cache_resource(show_spinner=False)
def get_gradio_client(space_id):
    from gradio_client import Client
    return Client(space_id)


def safe_text(value):
    return value if isinstance(value, str) else str(value or "")


def extract_path(value):
    """Extract a downloaded/local audio path from nested Gradio output."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        for item in value:
            found = extract_path(item)
            if found:
                return found
        return None
    if isinstance(value, dict):
        for key in ("path", "name", "file", "url"):
            item = value.get(key)
            if isinstance(item, str):
                if item.startswith(("http://", "https://")):
                    return download_audio(item)
                if os.path.isfile(item):
                    return Path(item).read_bytes()
        for item in value.values():
            found = extract_path(item)
            if found:
                return found
        return None
    if isinstance(value, str):
        if os.path.isfile(value):
            return Path(value).read_bytes()
        if value.startswith(("http://", "https://")):
            return download_audio(value)
    return None


def download_audio(url):
    try:
        response = requests.get(url, timeout=180)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "audio" in content_type or any(x in url.lower() for x in (".mp3", ".wav", ".flac", ".ogg", ".m4a")):
            return response.content
    except Exception:
        return None
    return None


def validate_audio(data):
    if not data:
        return False
    if not isinstance(data, (bytes, bytearray)):
        return False
    if len(data) < 10000:
        return False
    # MP3/ID3, WAV/RIFF, FLAC/fLaC, OGG/OggS, M4A/ftyp.
    head = bytes(data[:16])
    return (
        head.startswith(b"ID3")
        or head.startswith(b"RIFF")
        or head.startswith(b"fLaC")
        or head.startswith(b"OggS")
        or b"ftyp" in head
        or head[:2] == b"\xff\xfb"
        or head[:2] == b"\xff\xf3"
        or head[:2] == b"\xff\xf2"
    )


def make_tags(style, vocal, extra):
    base = {
        "Melody": "piano,acoustic guitar,strings,pop,warm,emotional",
        "Romantic": "piano,acoustic guitar,strings,pop,Romantic,warm",
        "Folk": "acoustic guitar,drums,folk,energetic,uplifting,warm",
        "Mass": "drums,bass,powerful,pop,energetic,driving",
        "Sad": "piano,strings,Ballad,Sad,Longing,emotional",
        "Cinematic": "piano,strings,drums,epic,emotional,powerful",
        "Lo-fi": "piano,soft,acoustic,drum machine,dreamy,warm",
        "Devotional": "piano,acoustic,Strings,peaceful,faith,uplifting",
        "Hip-hop": "drum machine,bass,hip-hop,driving,energetic,powerful",
        "Rock": "electric guitar,drums,bass,rock,powerful,driving",
        "Pop": "piano,drums,bass,pop,happy,uplifting",
    }.get(style, "piano,pop,warm,uplifting")
    if vocal == "Female":
        base += ",female vocal"
    elif vocal == "Male":
        base += ",male vocal"
    elif vocal == "Duet":
        base += ",duet vocal,harmony"
    if extra:
        cleaned = re.sub(r"[^A-Za-z0-9, _-]", "", extra).replace(" ", ",")
        if cleaned:
            base += "," + cleaned
    return base[:900]


def normalize_sections(lyrics):
    lyrics = lyrics.strip()
    lyrics = re.sub(r"\[Pre[- ]?Chorus\]", "[Prechorus]", lyrics, flags=re.I)
    if not re.search(r"\[(?:Verse|Chorus|Intro|Bridge|Outro|Prechorus)\]", lyrics, re.I):
        lyrics = "[Verse]\n" + lyrics + "\n\n[Chorus]\n" + lyrics[:220]
    return lyrics


def transliterate_telugu(text):
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate
        return transliterate(text, sanscript.TELUGU, sanscript.ITRANS)
    except Exception:
        # Keep original Telugu if optional transliteration package is unavailable.
        return text


def local_free_lyrics(theme, language, style):
    """No-API lyric helper. It always works and never consumes a provider quota."""
    theme = (theme or "my story").strip()
    if language == "Telugu":
        return f"""[Intro]\n{theme} నా పాటగా మారే వేళ\nమనసు పలికే మాటే మధుర గీతం\n\n[Verse]\nఈ రోజు నా హృదయం కొత్తగా పాడుతోంది\nనీ జ్ఞాపకం ప్రతి అడుగులో నడుస్తోంది\nచిన్న ఆశ ఒక దీపంలా వెలుగుతోంది\nనా కథలో కొత్త రంగు చేరుతోంది\n\n[Prechorus]\nనిశ్శబ్దం దాటి స్వరం లేస్తోంది\nమనసంతా ఒక రాగం అవుతోంది\n\n[Chorus]\n{theme} తోనే నా లోకం నవ్వుతోంది\nఈ క్షణం నా గుండెలో పాటై నిలుస్తోంది\nఎంత దూరమైనా కలలే తోడుంటాయి\nనా అడుగులు కొత్త ఆకాశం చేరుతాయి\n\n[Verse]\nనిన్నటి నీడలు మెల్లగా కరిగిపోతాయి\nరేపటి వెలుగులు దారిని చూపుతాయి\nనమ్మకం ఉంటే ప్రతి కల నిజమవుతుంది\nమనసు పాడితే ప్రతి రోజు పండుగవుతుంది\n\n[Bridge]\nఒక చిన్న స్వరం ఒక పెద్ద ప్రయాణం\nఒక చిన్న కల ఒక కొత్త ప్రపంచం\n\n[Chorus]\n{theme} తోనే నా లోకం నవ్వుతోంది\nఈ క్షణం నా గుండెలో పాటై నిలుస్తోంది\n\n[Outro]\nఈ పాట మనసులో ఎప్పటికీ మిగులుతుంది\n"""
    return f"""[Intro]\nA new story starts tonight\n{theme} in the neon light\n\n[Verse]\nI carry every dream inside\nI let the rhythm be my guide\nEvery little step becomes a sign\nTurning ordinary moments into mine\n\n[Prechorus]\nThe silence turns to melody\nA brighter world is calling me\n\n[Chorus]\n{theme} is the song inside my heart\nA brand new rhythm, a brand new start\nEven when the road is long and wild\nI keep the fire like a fearless child\n\n[Verse]\nYesterday can fade away\nTomorrow waits for me today\nI hear a beat beneath the rain\nAnd turn the memory into a refrain\n\n[Bridge]\nOne small dream can light the sky\nOne true voice can learn to fly\n\n[Chorus]\n{theme} is the song inside my heart\nA brand new rhythm, a brand new start\n\n[Outro]\nKeep the music close tonight\n"""


def generate_lyrics_free(theme, language, style):
    # Try the new YuE2 lyric writer first for its supported languages.
    if language in ("English", "Chinese", "Japanese", "Korean", "Spanish", "Cantonese"):
        try:
            client = get_gradio_client(YUE2_SPACE)
            result = client.predict(
                theme,
                STYLES.get(style, style),
                language,
                "Verse – Pre-Chorus – Chorus – Verse – Pre-Chorus – Chorus – Bridge – Chorus – Outro",
                random.randint(1, 2_000_000_000),
                api_name="/write_lyrics",
            )
            text = normalize_sections(safe_text(result))
            if len(text) > 80:
                return text, "YuE2 free lyric writer"
        except Exception:
            pass
    return normalize_sections(local_free_lyrics(theme, language, style)), "RacharlaMusic free lyric assistant"


def generate_yue2(lyrics, style_prompt, seed):
    client = get_gradio_client(YUE2_SPACE)
    # YuE2's current public Space exposes this exact endpoint and five inputs.
    result = client.predict(
        style_prompt,
        normalize_sections(lyrics),
        "full",
        16,
        int(seed),
        api_name="/generate_song",
    )
    data = extract_path(result)
    if not validate_audio(data):
        raise RuntimeError("YuE2 returned no valid downloadable audio.")
    return data, "YuE2-3B"


def generate_diffrhythm2(lyrics, style_prompt, seed):
    client = get_gradio_client(DIFFRHYTHM2_SPACE)
    # DiffRhythm2 is a different backend from the previously tested ACE/MiniMax/Gemini stack.
    # It accepts lyrics + text style and currently renders a fixed ~240s song.
    result = client.predict(
        normalize_sections(lyrics),
        "text",
        None,
        style_prompt,
        int(seed),
        True,
        16,
        1.3,
        "mp3",
        "euler",
        api_name="/infer_music",
    )
    data = extract_path(result)
    if not validate_audio(data):
        raise RuntimeError("DiffRhythm2 returned no valid downloadable audio.")
    return data, "DiffRhythm2"

# ----------------------------- sidebar -----------------------------
with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language = st.selectbox("🌐 Lyrics", ["Telugu", "English", "Telugu + English"], index=0)
    vocal = st.selectbox("🎤 Vocal", ["Natural lead", "Female", "Male", "Duet"])
    style = st.selectbox("🎼 Style", list(STYLES), index=0)
    duration_label = st.select_slider(
        "⏱️ Length", ["1 min", "2 min", "3 min", "4 min", "5 min", "6 min"], value="1 min"
    )
    duration_minutes = int(duration_label.split()[0])
    st.markdown("---")
    st.markdown('<div class="free-note">🆓 <b>Free mode</b><br>No Razorpay. No Gemini billing. No paid API key.</div>', unsafe_allow_html=True)
    st.caption("The music backends are public open-model demos. Their availability can change; the app will never show a fake successful download.")

# ----------------------------- main UI -----------------------------
c1, c2 = st.columns([1.35, 0.75], gap="large")

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ✍️ Create your song")

    theme_for_lyrics = st.text_input("🧠 Free lyrics idea (optional)", placeholder="A love story under Hyderabad night lights")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        make_lyrics = st.button("📝 GENERATE FREE LYRICS", use_container_width=True)
    with col_b:
        clear_lyrics = st.button("↺ Clear lyrics", use_container_width=True)

    if clear_lyrics:
        st.session_state["lyrics_text"] = ""
        st.rerun()

    if make_lyrics:
        if not theme_for_lyrics.strip():
            st.warning("Enter a song idea first, for example: 'A mother and son reunion'.")
        else:
            with st.spinner("Writing free lyrics..."):
                generated_lyrics, lyric_source = generate_lyrics_free(theme_for_lyrics, language, style)
            st.session_state["lyrics_text"] = generated_lyrics
            st.session_state["lyric_source"] = lyric_source
            st.success(f"Lyrics ready — {lyric_source}")

    lyrics = st.text_area(
        "Lyrics",
        value=st.session_state.get("lyrics_text", ""),
        height=330,
        max_chars=12000,
        placeholder="[Verse 1]\nనీ కోసం నా గుండెలో...\n\n[Prechorus]\n...\n\n[Chorus]\nYou are my light...",
        key="lyrics_text",
    )
    title = st.text_input("🎧 Song title", placeholder="My Racharla Song")
    extra = st.text_input("🎹 Extra music direction", value="flute intro, warm piano, big cinematic chorus")

    st.markdown(
        '<div class="tip">💡 Better structure: use [Verse], [Prechorus], [Chorus], [Bridge], [Outro].</div>',
        unsafe_allow_html=True,
    )
    generate = st.button("✨  GENERATE MY SONG  🎵", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.markdown(
        f"**Language:** {language}<br>**Vocal:** {vocal}<br>**Style:** {style}<br>**Length:** {duration_label}",
        unsafe_allow_html=True,
    )
    st.markdown(f'<p class="muted">{STYLES[style]}</p>', unsafe_allow_html=True)
    st.markdown("**Free backends:** YuE2-3B → DiffRhythm2", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------- generation -----------------------------
if generate:
    if not lyrics.strip():
        st.warning("Please paste lyrics or use GENERATE FREE LYRICS first.")
        st.stop()

    # New providers have different language support. For Telugu, give YuE2 a
    # readable romanized form so the English-trained lyric tokenizer can still
    # attempt a sung result. The original Telugu remains in the editor.
    provider_lyrics = lyrics
    if language == "Telugu":
        provider_lyrics = transliterate_telugu(lyrics)
    elif language == "Telugu + English":
        provider_lyrics = transliterate_telugu(lyrics)

    vocal_text = {
        "Natural lead": "natural expressive lead vocal",
        "Female": "warm expressive female lead vocal",
        "Male": "strong expressive male lead vocal",
        "Duet": "male and female duet vocals with harmonies",
    }[vocal]
    style_prompt = f"{STYLES[style]}, {vocal_text}, {extra}, professional studio mix, strong melodic chorus"
    seed = random.randint(1, 2_000_000_000)

    # The free public providers currently expose songs around 2–5 minutes rather
    # than a guaranteed exact duration. Keep the user's selector intact and state
    # the actual backend behavior instead of fabricating duration.
    status = st.empty()
    progress = st.progress(0)
    errors = []
    final_audio = None
    used_provider = None

    providers = [
        ("YuE2-3B", generate_yue2),
        ("DiffRhythm2", generate_diffrhythm2),
    ]

    for index, (provider_name, generator_fn) in enumerate(providers):
        status.info(f"🎼 Free provider {index + 1}/{len(providers)}: trying **{provider_name}**...")
        try:
            with st.spinner(f"Generating with {provider_name}. This can take a few minutes on public free GPU..."):
                audio, provider_label = generator_fn(provider_lyrics, style_prompt, seed)
            if validate_audio(audio):
                final_audio = audio
                used_provider = provider_label
                progress.progress(100)
                status.success(f"🎉 Song generated with {provider_label}!")
                break
            raise RuntimeError("Provider returned data that failed audio validation.")
        except Exception as exc:
            message = str(exc)
            errors.append((provider_name, message))
            status.warning(f"⚠️ {provider_name} could not complete the song. Trying the next new free backend...")
            progress.progress(int(((index + 1) / len(providers)) * 100))

    if final_audio:
        st.session_state["audio"] = bytes(final_audio)
        st.session_state["title"] = title.strip() or "RacharlaMusic Song"
        st.session_state["provider"] = used_provider
        st.session_state["requested_length"] = duration_label
    else:
        status.error("❌ No free music backend completed this request.")
        with st.expander("Technical details", expanded=False):
            for name, message in errors:
                st.write(f"**{name}:**")
                st.code(message[:1800])
        st.info("Nothing was charged because this build has no payment system. No download button is shown unless real audio was received and validated.")

# ----------------------------- player/download -----------------------------
if "audio" in st.session_state and validate_audio(st.session_state["audio"]):
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.caption(
        f"Generated by **{st.session_state.get('provider', 'free music provider')}** • "
        f"Requested length: {st.session_state.get('requested_length', 'free provider output')}"
    )
    st.audio(st.session_state["audio"], format="audio/mpeg")
    fname = (
        re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.get("title", "RacharlaMusic Song")).strip("_")
        or "RacharlaMusic_Song"
    )
    st.download_button(
        "⬇️ DOWNLOAD MP3",
        data=st.session_state["audio"],
        file_name=f"{fname}.mp3",
        mime="audio/mpeg",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer">🎵 <b>RacharlaMusic</b> • Create • Sing • Share • Anytime'
    '<br>Powered by <b>RacharlaGPT.in</b></div>',
    unsafe_allow_html=True,
)
