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


def calculate_speech_metrics(words, pause_threshold=0.8):
    """
    Calculate speech start, estimated speaking rate,
    and long pauses from timestamped Whisper words.
    """
    words = sorted(
        (word for word in words if word is not None),
        key=lambda word: word.start
    )

    if not words:
        return {
            "hook_delay_seconds": 0.0,
            "words_per_minute": 0,
            "awkward_pauses": []
        }

    first_start = float(words[0].start)
    previous_end = float(words[0].end)

    pauses = []
    total_long_pause = 0.0

    for word in words[1:]:
        word_start = float(word.start)
        word_end = float(word.end)

        gap = max(0.0, word_start - previous_end)

        if gap > pause_threshold:
            pauses.append({
                "start_time": round(previous_end, 2),
                "silence_duration": round(gap, 2)
            })
            total_long_pause += gap

        previous_end = max(previous_end, word_end)

    speech_window = max(0.0, previous_end - first_start)
    active_speech_seconds = max(0.0, speech_window - total_long_pause)

    wpm = (
        round(len(words) / active_speech_seconds * 60)
        if active_speech_seconds > 0
        else 0
    )

    return {
        "hook_delay_seconds": round(first_start, 2),
        "words_per_minute": wpm,
        "awkward_pauses": pauses
    }


def analyze_retention_metrics(video_path):
    print(f"Processing {video_path}...")

    video = VideoFileClip(video_path)
    if video.audio is None:
        video.close()
        raise ValueError("This video has no audio track.")

    fd, audio_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    try:
        video.audio.write_audiofile(audio_path, logger=None)
        model = load_model()

        print("Analyzing speech pacing...")
        segments, _ = model.transcribe(audio_path, word_timestamps=True)

        all_words = []
        for segment in segments:
            if segment.words:
                all_words.extend(segment.words)

        metrics = calculate_speech_metrics(all_words)

    finally:
        video.close()
        os.remove(audio_path)

    return metrics


if __name__ == "__main__":
    video_name = "draft_reel.mp4"
    if not os.path.exists(video_name):
        print(f"Place {video_name} in this folder to test analysis.")
    else:
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