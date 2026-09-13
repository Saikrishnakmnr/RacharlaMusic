# 🎵 RacharlaMusic

A beautiful Streamlit front end for Telugu, English, and mixed-lyrics AI song generation.

## Deploy on Streamlit Community Cloud

1. Upload these files to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Select the repository.
4. Set the main file to `streamlit_app.py`.
5. Deploy.

No API key is required by this project. It calls the public ACE-Step 1.5 hosted Space directly.

### Important

The ACE-Step API documents `audio_duration` from 10 to 600 seconds, so a 6-minute target is within the model API's documented range. The public free hosted service can still have queues, cold starts, availability limits, or changes outside this app's control.

This project does not install ACE-Step on your computer.

## Files

- `streamlit_app.py` — complete application
- `requirements.txt` — Python dependencies
- `assets/racharlamusic_poster.png` — RacharlaMusic artwork
- `.streamlit/config.toml` — Streamlit theme
