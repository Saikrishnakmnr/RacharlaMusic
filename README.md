# RacharlaMusic — Provider-Independent Build

This build removes the external GPU/provider dependency from the app path.

## What is fixed
- **Duration bug fixed:** the selected 1–6 minute value is passed as seconds and the WAV is rendered to that exact target duration.
- **Lyrics no longer collapse to one identical tune:** each lyric line is hashed into a different melodic phrase, with section/phrase variation.
- **No external GPU:** no Hugging Face Spaces, ZeroGPU, ACE-Step, MiniMax, YuE2 or DiffRhythm2.
- **No API key / payment system:** the local provider is fully offline at runtime.
- **Provider-independent interface:** `providers/base.py` defines the contract, so a future true singing provider can be plugged into the same UI.
- **Reliable download:** generated audio is a valid WAV file.

## Important limitation
The local provider is a CPU music synthesizer. It produces a real musical backing/demo track, **not natural human-sounding AI singing of the supplied lyrics**. The browser Vocal Companion can speak the lyrics using the user's installed browser voice, but that speech is not embedded in the downloaded WAV.

This limitation is intentional rather than pretending a synthesizer is an AI singer.

## Project structure

```text
app.py
requirements.txt
README.md
.streamlit/config.toml
assets/racharlamusic_poster.png
providers/base.py
providers/local.py
providers/__init__.py
lyrics/local.py
lyrics/__init__.py
audio/wav.py
audio/__init__.py
```

## Streamlit deployment
1. Replace the repository contents with these files.
2. Keep `app.py` in the repository root.
3. Deploy/redeploy on Streamlit Community Cloud.
4. No secrets are required.
