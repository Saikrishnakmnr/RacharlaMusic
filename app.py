
import io
import os
import re
import time
from pathlib import Path

import streamlit as st

APP_NAME = "RacharlaMusic"
SPACE_ID = "ACE-Step/Ace-Step-v1.5"
ROOT = Path(__file__).parent
POSTER = ROOT / "assets" / "racharlamusic_poster.png"

st.set_page_config(page_title="RacharlaMusic", page_icon="🎵", layout="wide")

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
</style>
""", unsafe_allow_html=True)

if POSTER.exists():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.image(str(POSTER), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass"><div class="title">🎵 RacharlaMusic</div>'
            '<div class="muted">Your lyrics • AI melody • Natural singing • Your song</div>'
            '<div><span class="badge">🇮🇳 Telugu</span><span class="badge">🇬🇧 English</span>'
            '<span class="badge">🔀 Mixed</span><span class="badge">🎤 Vocals</span>'
            '<span class="badge">⬇️ MP3</span></div></div><br>', unsafe_allow_html=True)

STYLES = {
"Melody":"beautiful Indian melodic film song, memorable hook, warm piano, acoustic guitar, lush strings, soft percussion, expressive natural singing, polished studio mix",
"Romantic":"romantic Indian film song, intimate natural vocals, piano, acoustic guitar, lush strings, emotional melody, polished studio production",
"Folk":"Telugu folk-inspired song, organic percussion, acoustic instruments, catchy traditional melody, energetic natural singing",
"Mass":"high-energy Telugu commercial song, powerful natural vocals, punchy drums, bass, rhythmic hooks, cinematic production",
"Sad":"emotional Indian ballad, expressive natural vocals, piano, strings, restrained drums, haunting memorable melody",
"Cinematic":"grand Indian cinematic soundtrack, expressive natural vocals, orchestral strings, piano, percussion, dramatic build",
"Lo-fi":"dreamy lo-fi Indian pop, intimate natural vocals, soft drums, warm keys, mellow bass",
"Devotional":"devotional Indian melody, respectful natural vocals, flute, gentle percussion, uplifting arrangement",
"Hip-hop":"Indian melodic hip-hop, natural sung hook, rhythmic vocal delivery, deep bass, crisp drums, modern production",
"Rock":"Indian pop rock, natural expressive vocals, electric guitars, live drums, bass, strong melodic chorus",
"Pop":"modern Indian pop, natural lead vocals, catchy melody, polished drums, bass, bright synths"
}
LANG={"Telugu":"te","English":"en","Telugu + English":"te"}

@st.cache_resource(show_spinner=False)
def get_client():
    try:
        from gradio_client import Client
        return Client(SPACE_ID)
    except Exception as e:
        raise RuntimeError(f"Could not connect to the free music service: {e}")

def safe_view_api(client):
    try:
        info=client.view_api(return_format="dict")
        return info
    except TypeError:
        return client.view_api()
    except Exception as e:
        raise RuntimeError(f"Could not read the music service API: {e}")

def endpoint_candidates(info):
    out=[]
    if isinstance(info,dict):
        named=info.get("named_endpoints",{})
        if isinstance(named,dict):
            for name,spec in named.items():
                text=(str(name)+" "+str(spec)).lower()
                if any(x in text for x in ("generate","music","audio")):
                    out.append((name,spec))
        unnamed=info.get("unnamed_endpoints",{})
        if isinstance(unnamed,dict):
            for name,spec in unnamed.items():
                out.append((name,spec))
    return out

def choose_endpoint(info):
    eps=endpoint_candidates(info)
    if not eps:
        raise RuntimeError("The hosted music Space did not expose a callable generation endpoint.")
    # Prefer an endpoint that explicitly looks like generation/music.
    for name,spec in eps:
        n=str(name).lower()
        if "generate" in n and "music" in n: return name,spec
    for name,spec in eps:
        if "generate" in str(name).lower(): return name,spec
    return eps[0]

def spec_params(spec):
    if not isinstance(spec,dict): return []
    for key in ("parameters","inputs"):
        val=spec.get(key)
        if isinstance(val,list): return val
    return []

def make_value(p, lyrics, caption, language, duration, audio_format):
    name=str(p.get("parameter_name",p.get("name",p.get("label","")))).lower()
    default=p.get("default",None)
    if default is not None:
        # Replace duration/language/text defaults below when relevant.
        pass
    if any(x in name for x in ("lyric","lyrics")): return lyrics
    if any(x in name for x in ("caption","prompt","description","desc","sample_query","query")): return caption
    if "duration" in name:
        return float(duration)
    if "language" in name or "vocal_language" in name: return language
    if "audio_format" in name or name=="format": return audio_format
    if name in ("thinking","think"): return True
    if "instrumental" in name: return False
    if "inference_steps" in name or name=="steps": return 8
    if "seed" in name: return -1
    if "batch_size" in name: return 1
    if "bpm" in name: return None
    if "key_scale" in name or "keyscale" in name: return ""
    if "time_signature" in name or "timesignature" in name: return ""
    if "model" in name and "path" not in name: return "acestep-v15-turbo"
    if "task_type" in name: return "text2music"
    if "use_format" in name or "format" in name and "audio" not in name: return True
    if "lm_temperature" in name: return 0.85
    if "lm_cfg_scale" in name: return 2.0
    if "lm_top_k" in name: return 0
    if "lm_top_p" in name: return 0.9
    if "lm_repetition_penalty" in name: return 1.0
    if "lm_negative_prompt" in name: return "NO USER INPUT"
    if "use_cot" in name or "constrained_decoding" in name: return True
    if "guidance_scale" in name: return 7.0
    if "shift" in name: return 3.0
    if "infer_method" in name: return "ode"
    if "random_seed" in name: return True
    if "timesteps" in name: return ""
    if "audio_cover_strength" in name: return 1.0
    if "repainting_start" in name: return 0.0
    if "repainting_end" in name: return -1.0
    if "track_name" in name: return None
    if "complete_track" in name: return []
    if default is not None: return default
    # conservative fallbacks
    typ=p.get("type",{})
    if isinstance(typ,dict):
        t=str(typ.get("type","")).lower()
        if "bool" in t: return False
        if "number" in t or "integer" in t: return 0
    return ""

def call_generation(client, lyrics, caption, language, duration):
    info=safe_view_api(client)
    endpoint,spec=choose_endpoint(info)
    params=spec_params(spec)

    values=[make_value(p,lyrics,caption,language,duration,"mp3") for p in params]
    try:
        result=client.predict(*values,api_name=endpoint)
    except Exception as first:
        # Try keyword arguments if the API exposes parameter names.
        kwargs={}
        for p,v in zip(params,values):
            name=p.get("parameter_name") or p.get("name")
            if name: kwargs[name]=v
        if not kwargs:
            raise first
        result=client.predict(api_name=endpoint,**kwargs)
    return result

def extract_file(result):
    if isinstance(result,dict):
        for k in ("path","url","name","audio","audio_url","value"):
            v=result.get(k)
            if isinstance(v,str) and (v.startswith("http") or os.path.exists(v) or "." in os.path.basename(v)):
                return v
        for v in result.values():
            x=extract_file(v)
            if x:return x
    if isinstance(result,(list,tuple)):
        for v in result:
            x=extract_file(v)
            if x:return x
    if isinstance(result,str):
        return result
    return None

with st.sidebar:
    st.markdown("## 🎵 RacharlaMusic")
    language=st.selectbox("🌐 Lyrics",list(LANG),index=0)
    vocal=st.selectbox("🎤 Vocal",["Natural lead","Female","Male","Duet"])
    style=st.selectbox("🎼 Style",list(STYLES),index=0)
    duration_label=st.select_slider("⏱️ Length",["1 min","2 min","3 min","4 min","5 min","6 min"],value="4 min")
    duration=int(duration_label.split()[0])*60
    st.markdown("---")
    st.info("No API key is required by this version. Generation uses the public ACE-Step Hugging Face Space. Free ZeroGPU availability can vary.")

c1,c2=st.columns([1.35,.75],gap="large")
with c1:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("### ✍️ Create your song")
    lyrics=st.text_area("Lyrics",height=330,max_chars=8000,placeholder="[Verse 1]\nనీ కోసం నా గుండెలో...\n\n[Chorus]\nYou are my light...")
    title=st.text_input("🎧 Song title",placeholder="My Racharla Song")
    extra=st.text_input("🎹 Extra music direction",placeholder="flute intro, warm piano, big cinematic chorus")
    st.markdown('<div class="tip">💡 Better structure: use [Verse], [Pre-Chorus], [Chorus], [Bridge], [Outro].</div>',unsafe_allow_html=True)
    generate=st.button("✨  GENERATE MY SONG  🎵",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("### 🎚️ Sound preview")
    st.markdown(f"**Language:** {language}<br>**Vocal:** {vocal}<br>**Style:** {style}<br>**Length:** {duration_label}",unsafe_allow_html=True)
    st.markdown(f'<p class="muted">{STYLES[style]}</p>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

if generate:
    if not lyrics.strip():
        st.warning("Please paste your lyrics first.")
        st.stop()

    vocal_text={
        "Natural lead":"natural human-like lead singing, expressive phrasing, clear diction",
        "Female":"natural human-like female lead singing, expressive phrasing, clear diction",
        "Male":"natural human-like male lead singing, expressive phrasing, clear diction",
        "Duet":"natural human-like male and female duet singing, expressive harmonies"
    }[vocal]
    caption=f"{STYLES[style]}, {vocal_text}, {extra}, professional studio mix, strong melodic chorus, no spoken narration"
    status=st.empty()
    try:
        status.info("🔌 Connecting to the free AI music Space...")
        client=get_client()
        status.info("🎼 Sending your lyrics to ACE-Step 1.5...")
        with st.spinner("🎵 Generating your song... this can take time on a free GPU queue."):
            result=call_generation(client,lyrics,caption,LANG[language],duration)
        status.success("🎉 Generation finished!")

        audio_path=extract_file(result)
        if audio_path and os.path.exists(audio_path):
            data=Path(audio_path).read_bytes()
        elif audio_path and audio_path.startswith("http"):
            import requests
            rr=requests.get(audio_path,timeout=180)
            rr.raise_for_status()
            data=rr.content
        else:
            st.write(result)
            st.error("The music service returned a result, but no downloadable audio file could be identified.")
            st.stop()

        st.session_state["audio"]=data
        st.session_state["title"]=title.strip() or "RacharlaMusic Song"
    except Exception as e:
        st.error("❌ The free music service could not generate the song.")
        st.code(str(e))
        st.info("This is usually a temporary Hugging Face/ZeroGPU queue or API availability problem—not a problem with your lyrics.")

if "audio" in st.session_state:
    st.markdown('<div class="glass">',unsafe_allow_html=True)
    st.markdown("## 🎉 Your song is ready")
    st.audio(st.session_state["audio"],format="audio/mpeg")
    fname=re.sub(r"[^A-Za-z0-9_-]+","_",st.session_state["title"]).strip("_") or "RacharlaMusic_Song"
    st.download_button("⬇️ DOWNLOAD MP3",st.session_state["audio"],file_name=f"{fname}.mp3",mime="audio/mpeg",use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown('<div class="footer">🎵 <b>RacharlaMusic</b> • Create • Sing • Share • Anytime<br>Powered by <b>RacharlaGPT.in</b></div>',unsafe_allow_html=True)
