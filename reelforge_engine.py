import json
import os

from ai_brain import generate_edit_plan
from auto_cutter import auto_edit_reel
from core_analyzer import analyze_retention_metrics
from growth_tracker import log_video_stats
from vision_analyzer import analyze_visual_pacing


def run_full_pipeline(video_path, run_auto_cut=True, use_ai_brain=True):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # 1. Audio & speech pacing telemetry
    audio = analyze_retention_metrics(video_path)
    pause_count = len(audio["awkward_pauses"])

    # 2. Computer-vision jump-cut & static-frame telemetry
    vision = analyze_visual_pacing(video_path)

    # 3. Log telemetry to local SQLite tracker
    log_video_stats(
        os.path.basename(video_path),
        audio["hook_delay_seconds"],
        audio["words_per_minute"],
        pause_count,
    )

    # 4. Auto-trim dead air + export pro .edl timeline
    edit_outputs = None
    if run_auto_cut:
        edit_outputs = auto_edit_reel(video_path, audio)

    # 5. Generate AI editing plan (requires GEMINI_API_KEY set in terminal)
    ai_advice = None
    if use_ai_brain and os.environ.get("GEMINI_API_KEY"):
        ai_advice = generate_edit_plan(
            audio["hook_delay_seconds"],
            audio["words_per_minute"],
            pause_count,
        )

    return {
        "video": os.path.basename(video_path),
        "audio_telemetry": audio,
        "visual_telemetry": vision,
        "auto_edit": edit_outputs,
        "ai_action_plan": ai_advice,
    }


if __name__ == "__main__":
    report = run_full_pipeline("draft_reel.mp4", run_auto_cut=True, use_ai_brain=True)
    print("\n--- FULL REELFORGE ENGINE REPORT ---")
    print(json.dumps(report, indent=2))