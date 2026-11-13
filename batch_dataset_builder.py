import csv
import os
from pathlib import Path

from core_analyzer import analyze_retention_metrics
from vision_analyzer import analyze_visual_pacing

INPUT_DIR = "dataset_videos"
OUTPUT_CSV = "training_batch.csv"
HEADERS = [
    "Video Link",
    "Niche",
    "Hook Delay (Seconds)",
    "Speaking Pace (WPM)",
    "Dead Air Spots",
    "Jump Cuts",
    "Total Views",
]


def build_training_csv(input_folder=INPUT_DIR, output_csv=OUTPUT_CSV, default_niche="General"):
    os.makedirs(input_folder, exist_ok=True)
    videos = sorted(
        p for p in Path(input_folder).iterdir()
        if p.suffix.lower() in {".mp4", ".mov", ".mkv"}
    )

    if not videos:
        print(f"Put downloaded reels inside '{input_folder}/' and run this script again.")
        return

    file_exists = os.path.exists(output_csv)
    processed = 0

    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(HEADERS)

        for vid in videos:
            print(f"\nAnalyzing [{processed + 1}/{len(videos)}]: {vid.name}")
            try:
                audio = analyze_retention_metrics(str(vid))
                vision = analyze_visual_pacing(str(vid))

                writer.writerow([
                    vid.name,
                    default_niche,
                    audio["hook_delay_seconds"],
                    audio["words_per_minute"],
                    len(audio["awkward_pauses"]),
                    vision["jump_cuts"],
                    "",  # Fill Total Views manually after importing to Google Sheets
                ])
                processed += 1
                print(
                    f" -> Hook: {audio['hook_delay_seconds']}s | "
                    f"WPM: {audio['words_per_minute']} | "
                    f"Pauses: {len(audio['awkward_pauses'])} | "
                    f"Cuts: {vision['jump_cuts']}"
                )
            except Exception as e:
                print(f" -> Skipped {vid.name}: {e}")

    print(f"\nDone. Appended {processed} rows to {output_csv}. Open it and paste directly into your Google Sheet.")


if __name__ == "__main__":
    niche = input("Enter niche for this batch (e.g., Tech, Finance, Fitness): ").strip() or "General"
    build_training_csv(default_niche=niche) 