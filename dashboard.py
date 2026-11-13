import os
import tempfile

import streamlit as st

from core_analyzer import analyze_retention_metrics

st.set_page_config(page_title="ReelForge AI", page_icon="🎬", layout="centered")
st.title("🎬 ReelForge AI: Creator Dashboard")
st.write("Upload your draft reel below to get brutal, data-driven editing advice.")

uploaded_file = st.file_uploader("Upload your MP4 draft", type=["mp4"])

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Analyze Video"):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(uploaded_file.getbuffer())

        try:
            with st.spinner("Watching video and measuring retention..."):
                metrics = analyze_retention_metrics(tmp.name)
        except Exception as e:
            st.error(f"Could not analyze this video: {e}")
            st.stop()
        finally:
            os.remove(tmp.name)

        hook = metrics["hook_delay_seconds"]
        wpm = metrics["words_per_minute"]
        pauses = metrics["awkward_pauses"]

        st.subheader("Telemetry Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Hook Delay", f"{hook}s", delta="- Target: < 1.0s", delta_color="inverse")
        col2.metric("Speaking Pace", f"{wpm} WPM", delta="Target: 150-170 WPM")
        col3.metric("Dead Air Spots", len(pauses), delta="- Target: 0", delta_color="inverse")

        st.subheader("AI Action Plan")

        if hook > 1.5:
            st.error(f"✂️ **Chop the hook:** Cut the first {hook} seconds. Viewers already swiped away.")
        else:
            st.success("🔥 **Great Hook:** You started speaking instantly.")

        if wpm > 190:
            st.warning("🐌 **Slow Down:** You are talking way too fast. Breathe.")
        elif wpm < 120:
            st.error("⚡ **Speed Up:** Your delivery is dragging. Script your words and speak faster.")
        else:
            st.success("🗣️ **Perfect Pacing:** Conversational and energetic.")

        for pause in pauses:
            st.warning(f"🔇 **Cut dead air:** Trim {pause['silence_duration']}s of silence at the {pause['start_time']}s mark.")
