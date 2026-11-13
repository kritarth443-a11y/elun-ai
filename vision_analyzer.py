import cv2


def analyze_visual_pacing(video_path, sample_interval=0.4, cut_threshold=0.35, max_static_seconds=5.0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0.0
    frame_step = max(1, int(round(fps * sample_interval)))

    prev_hist = None
    jump_cuts = 0
    cut_timestamps = []
    stale_visual_zones = []
    last_cut_time = 0.0
    frame_idx = 0

    try:
        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_idx / fps

            # Convert to HSV and compute 2D Hue-Saturation histogram (resistant to lighting flicker)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

            if prev_hist is not None:
                diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
                if diff > cut_threshold:
                    jump_cuts += 1
                    cut_timestamps.append(round(current_time, 2))

                    # Check if the shot stayed static too long before this cut
                    static_duration = current_time - last_cut_time
                    if static_duration > max_static_seconds:
                        stale_visual_zones.append({
                            "start_time": round(last_cut_time, 2),
                            "end_time": round(current_time, 2),
                            "duration": round(static_duration, 2),
                        })
                    last_cut_time = current_time

            prev_hist = hist
            frame_idx += frame_step

        # Check trailing static stretch at the end of the video
        if duration - last_cut_time > max_static_seconds:
            stale_visual_zones.append({
                "start_time": round(last_cut_time, 2),
                "end_time": round(duration, 2),
                "duration": round(duration - last_cut_time, 2),
            })
    finally:
        cap.release()

    avg_cut_interval = round(duration / (jump_cuts + 1), 2) if duration > 0 else 0.0

    return {
        "jump_cuts": jump_cuts,
        "cut_timestamps": cut_timestamps,
        "avg_cut_interval_seconds": avg_cut_interval,
        "stale_visual_zones": stale_visual_zones,
    }


if __name__ == "__main__":
    vision = analyze_visual_pacing("draft_reel.mp4")
    print("\n--- VISUAL PACING RESULTS ---")
    print(f"Total Jump Cuts: {vision['jump_cuts']}")
    print(f"Avg Shot Length: {vision['avg_cut_interval_seconds']}s (Aim for < 3.5s)")
    for zone in vision["stale_visual_zones"]:
        print(f" 🎥 Static shot for {zone['duration']}s ({zone['start_time']}s - {zone['end_time']}s) -> Add zoom or B-roll")