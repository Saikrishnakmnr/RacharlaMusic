import streamlit as str
import random

# App title and configuration
str.set_page_config(page_title="తెలుగు లిరిక్స్ జనరేటర్", page_icon="🎵")
str.title("🎵 తెలుగు సాంగ్ లిరిక్స్ జనరేటర్")
str.write("మీకు నచ్చిన శైలిని ఎంచుకుని క్షణాల్లో తెలుగు పాటను సృష్టించండి!")

# Pure Telugu Lyrics Database (No Sanskrit)
lyrics_db = {
    "భక్తి పాటలు (Devotional)": [
        "వినాయకా విఘ్నరాజా వేగమే రావయ్యా |\nమమ్మేలుకొని నీ దీవెనలు ఇయ్యవయ్యా ||",
        "కొండలెక్కి కొలిచేటి కోనేటి రాయుడా |\nకనులార నిన్ను చూసి కరిగిపోవాలి మా గుండె ||",
        "అమ్మలగన్న అమ్మ ముగ్గురమ్మల మూలపుటమ్మ |\nమమ్మేలి కాపాడే మంగళ గౌరమ్మ ||"
    ],
    "ప్రేమ పాటలు (Romantic)": [
        "నువ్వు నాతో ఉంటే చాలు గుండెల్లో ఏదో అలజడి |\nనీ నీడగా సాగడమే నా ప్రాణానికి ఊపిరి ||",
        "మనసున ఉన్న మాట చెప్పలేక ఆగిపోయా |\nనీ నవ్వు చూసి మళ్ళీ నిన్నే ప్రేమిస్తూ ఉండిపోయా ||",
        "వాన చినుకులు నీ పైన పడుతుంటే |\nనా కళ్ళు నీ వైపే చూస్తూ ఆగిపోయాయే ||"
    ],
    "ఉత్సాహ భరిత పాటలు (Mass/Energetic)": [
        "దరువే బద్దలయ్యేలా అడుగులేయరా తమ్ముడా |\nమన దెబ్బకి లోకమంతా అదిరిపోవాలిరా ||",
        "ఈ రోజు మనదేరా ఎదురే లేదురా |\nగుండెల్లో ధైర్యముంటే తిరుగే లేదురా ||"
    ]
}

# User Selection
genre = str.selectbox("పాట శైలిని ఎంచుకోండి (Select Genre):", list(lyrics_db.keys()))

# Generation Button
if str.button("పాటను సృష్టించు (Generate Song)"):
    lines = lyrics_db[genre]
    selected_song = random.choice(lines)
    
    str.success("✨ మీ కోసం సృష్టించిన తెలుగు లైన్లు:")
    str.subheader(selected_song)
  
