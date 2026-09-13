# Map slider options to exact seconds
duration_map = {"30 sec": 30.0, "1 min": 60.0, "2 min": 120.0, "3 min": 180.0}
selected_duration_sec = duration_map.get(duration_label, 30.0)

if generate:
    if not lyrics.strip():
        st.warning("Please paste lyrics or generate free lyrics first.")
        st.stop()

    status = st.empty()
    status.info(f"🎼 Generating full {duration_label} song...")
    
    provider = LocalFallbackProvider()
    # Ensure duration_sec is passed here!
    audio, label = provider.generate(lyrics, style_prompt=STYLES[style], seed=random.randint(1, 100000), duration_sec=selected_duration_sec)
    
    if validate_audio(audio):
        st.session_state["audio"] = bytes(audio)
        st.session_state["title"] = title.strip() or "RacharlaMusic Song"
        st.session_state["provider"] = label
        status.success(f"🎉 Song generated successfully ({duration_label} length)! Listen below.")
    else:
        status.error("Generation failed.")
