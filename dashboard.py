import streamlit as st
import os
from core_analyzer import analyze_retention_metrics

# Set up the UI vibe
st.set_page_config(page_title="ReelForge AI", page_icon="🎬", layout="centered")
st.title("🎬 ReelForge AI: Creator Dashboard")
st.write("Upload your draft reel below to get brutal, data-driven editing advice.")

# 1. Add a drag-and-drop upload box
uploaded_file = st.file_uploader("Upload your MP4 draft", type=["mp4"])

if uploaded_file is not None:
    # 2. Save the uploaded video temporarily so our engine can read it
    temp_video_path = "temp_ui_draft.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Show the video player directly in the web app
    st.video(temp_video_path)

    if st.button("Analyze Video"):
        with st.spinner("Watching video and measuring retention..."):
            # Run the engine on the uploaded file
            metrics = analyze_retention_metrics(temp_video_path)
            
            # Display results in clean dashboard widgets
            st.subheader("Telemetry Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Hook Delay", f"{metrics['hook_delay_seconds']}s", delta="- Target: < 1.0s", delta_color="inverse")
            col2.metric("Speaking Pace", f"{metrics['words_per_minute']} WPM", delta="Target: 150-170 WPM")
            col3.metric("Dead Air Spots", len(metrics['awkward_pauses']), delta="- Target: 0", delta_color="inverse")
            
            # Apply the AI Brain logic directly to the UI
            st.subheader("AI Action Plan")
            
            if metrics['hook_delay_seconds'] > 1.5:
                st.error(f"✂️ **Chop the hook:** Cut the first {metrics['hook_delay_seconds']} seconds. Viewers already swiped away.")
            else:
                st.success("🔥 **Great Hook:** You started speaking instantly.")
                
            if metrics['words_per_minute'] > 190:
                st.warning("🐌 **Slow Down:** You are talking way too fast. Breathe.")
            elif metrics['words_per_minute'] < 120:
                st.error("⚡ **Speed Up:** Your delivery is dragging. Script your words and speak faster.")
            else:
                st.success("🗣️ **Perfect Pacing:** Conversational and energetic.")
                
            for pause in metrics['awkward_pauses']:
                st.warning(f"🔇 **Cut dead air:** Trim {pause['silence_duration']}s of silence at the {pause['start_time']}s mark.")
            
            # Clean up the temporary file to save your C: drive storage
            os.remove(temp_video_path)