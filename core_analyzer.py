import os
import tempfile
from functools import lru_cache

from faster_whisper import WhisperModel
from moviepy import VideoFileClip

from growth_tracker import log_video_stats


@lru_cache(maxsize=1)
def load_model():
    print("Loading local speech model...")
    return WhisperModel("base", device="cpu", compute_type="int8")


def analyze_retention_metrics(video_path):
    print(f"Processing {video_path}...")

    video = VideoFileClip(video_path)
    if video.audio is None:
        video.close()
        raise ValueError("This video has no audio track.")

    duration = video.duration
    fd, audio_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    word_count = 0
    hook_delay = None
    dead_air = []
    last_end = 0.0

    try:
        video.audio.write_audiofile(audio_path, logger=None)
        model = load_model()

        print("Analyzing speech pacing...")
        segments, _ = model.transcribe(audio_path, word_timestamps=True)

        for segment in segments:
            for word in segment.words:
                if hook_delay is None:
                    hook_delay = word.start
                word_count += 1
                gap = word.start - last_end
                if last_end > 0 and gap > 0.8:
                    dead_air.append({
                        "start_time": round(last_end, 2),
                        "silence_duration": round(gap, 2),
                    })
                last_end = word.end
    finally:
        video.close()
        os.remove(audio_path)

    return {
        "hook_delay_seconds": round(hook_delay, 2) if hook_delay else 0,
        "words_per_minute": round(word_count / duration * 60) if duration > 0 else 0,
        "awkward_pauses": dead_air,
    }


if __name__ == "__main__":
    video_name = "draft_reel.mp4"
    metrics = analyze_retention_metrics(video_name)
    pauses = metrics["awkward_pauses"]

    print("\n--- AI ANALYSIS RESULTS ---")
    print(f"Hook Delay: {metrics['hook_delay_seconds']}s (Aim for < 1.0s)")
    print(f"Speaking Pace: {metrics['words_per_minute']} WPM (Aim for 150-170 for Reels)")
    print(f"Dead Air Spots to Cut: {len(pauses)}")
    for pause in pauses:
        print(f" ✂️ Cut {pause['silence_duration']}s of silence at {pause['start_time']}s")

    print("\nSaving to creator dashboard...")
    log_video_stats(
        video_name,
        metrics["hook_delay_seconds"],
        metrics["words_per_minute"],
        len(pauses),
    )
