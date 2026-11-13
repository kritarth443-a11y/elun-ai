import os
from moviepy import VideoFileClip, concatenate_videoclips

from core_analyzer import analyze_retention_metrics


def _seconds_to_timecode(seconds, fps=30):
    total_frames = int(round(seconds * fps))
    frames = total_frames % fps
    total_secs = total_frames // fps
    secs = total_secs % 60
    mins = (total_secs // 60) % 60
    hours = total_secs // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"


def build_keep_segments(duration, hook_delay, awkward_pauses, speech_pad=0.15):
    cursor = max(0.0, hook_delay - speech_pad) if hook_delay > 0.3 else 0.0
    keep_segments = []

    for pause in sorted(awkward_pauses, key=lambda x: x["start_time"]):
        pause_start = pause["start_time"]
        pause_end = pause_start + pause["silence_duration"]

        cut_start = pause_start + speech_pad
        cut_end = pause_end - speech_pad

        # Only slice if at least 0.25s of genuine silence remains after padding
        if cut_end - cut_start > 0.25 and cut_start > cursor:
            keep_segments.append((round(cursor, 3), round(cut_start, 3)))
            cursor = cut_end

    if duration - cursor > 0.2:
        keep_segments.append((round(cursor, 3), round(duration, 3)))

    return keep_segments


def export_edl(keep_segments, edl_path="edit_timeline.edl", title="REELFORGE_AUTO_CUT", fps=30):
    lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
    record_cursor = 0.0

    for idx, (src_in, src_out) in enumerate(keep_segments, start=1):
        clip_len = src_out - src_in
        rec_in = record_cursor
        rec_out = record_cursor + clip_len

        lines.append(
            f"{idx:03d}  AX       V     C        "
            f"{_seconds_to_timecode(src_in, fps)} {_seconds_to_timecode(src_out, fps)} "
            f"{_seconds_to_timecode(rec_in, fps)} {_seconds_to_timecode(rec_out, fps)}"
        )
        record_cursor = rec_out

    with open(edl_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return edl_path


def auto_edit_reel(video_path, metrics, output_video="clean_draft.mp4", output_edl="edit_timeline.edl"):
    video = VideoFileClip(video_path)
    final_clip = None

    try:
        duration = video.duration
        keep_segments = build_keep_segments(
            duration=duration,
            hook_delay=metrics["hook_delay_seconds"],
            awkward_pauses=metrics["awkward_pauses"],
        )

        if not keep_segments:
            raise ValueError("No spoken segments found to keep.")

        export_edl(keep_segments, edl_path=output_edl)

        subclips = [video.subclipped(start, end) for start, end in keep_segments]
        final_clip = concatenate_videoclips(subclips, method="chain")
        final_clip.write_videofile(
            output_video,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        saved_seconds = round(duration - final_clip.duration, 2)
        return {
            "output_video": output_video,
            "output_edl": output_edl,
            "segments_kept": len(keep_segments),
            "seconds_trimmed": saved_seconds,
        }
    finally:
        if final_clip is not None:
            final_clip.close()
        video.close()


if __name__ == "__main__":
    source = "draft_reel.mp4"
    if not os.path.exists(source):
        print(f"Place {source} in this folder to test auto-cutting.")
    else:
        audio_metrics = analyze_retention_metrics(source)
        result = auto_edit_reel(source, audio_metrics)
        print("\n--- AUTO-CUT COMPLETE ---")
        print(f"Trimmed {result['seconds_trimmed']}s of dead air across {result['segments_kept']} cuts.")
        print(f"Saved video: {result['output_video']}")
        print(f"Saved timeline: {result['output_edl']}")