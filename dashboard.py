import streamlit as st
from core_analyzer import analyze_retention_metrics

# Set up the UI vibe
st.set_page_config(page_title="ReelForge AI", page_icon="🎬", layout="centered")
st.title("🎬 ReelForge AI: Creator Dashboard")
st.write("Drop your draft reel below to get brutal, data-driven editing advice.")

# Create a button to run the engine on the video you already have
if st.button("Analyze Current Draft"):
    with st.spinner("Watching video and measuring retention..."):
        # Run the same engine you just built
        metrics = analyze_retention_metrics("draft_reel.mp4")
        
        # Display results in clean dashboard widgets
        st.subheader("Telemetry Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Hook Delay", f"{metrics['hook_delay_seconds']}s", delta="- Target: < 1.0s", delta_color="inverse")
        col2.metric("Speaking Pace", f"{metrics['words_per_minute']} WPM", delta="Target: 150 WPM")
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