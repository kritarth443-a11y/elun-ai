from moviepy import VideoFileClip
from faster_whisper import WhisperModel
from growth_tracker import log_video_stats

def analyze_retention_metrics(video_path):
    print(f"Processing {video_path}...")
    
    # 1. Extract audio from the video draft
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path, logger=None)
    
    # 2. Load the local transcription model
    print("Loading local speech model...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    
    # 3. Get word-by-word timestamps
    print("Analyzing speech pacing...")
    segments, info = model.transcribe(audio_path, word_timestamps=True)
    
    words_data = []
    dead_air_spots = []
    last_word_end = 0.0
    
    for segment in segments:
        for word in segment.words:
            words_data.append({"word": word.word, "start": word.start, "end": word.end})
            
            # Detect dead air: any pause longer than 0.8 seconds kills retention on short-form
            if last_word_end > 0 and (word.start - last_word_end) > 0.8:
                dead_air_spots.append({
                    "start_time": round(last_word_end, 2),
                    "end_time": round(word.start, 2),
                    "silence_duration": round(word.start - last_word_end, 2)
                })
            last_word_end = word.end

    # 4. Calculate core metrics for the influencer
    total_duration = video.duration
    word_count = len(words_data)
    wpm = round((word_count / total_duration) * 60) if total_duration > 0 else 0
    hook_delay = words_data[0]["start"] if words_data else None

    return {
        "video_duration_seconds": round(total_duration, 2),
        "hook_delay_seconds": round(hook_delay, 2) if hook_delay else 0,
        "words_per_minute": wpm,
        "awkward_pauses": dead_air_spots
    }

# Run the test
if __name__ == "__main__":
    video_name = "draft_reel.mp4"
    metrics = analyze_retention_metrics(video_name)
    
    print("\n--- AI ANALYSIS RESULTS ---")
    print(f"Hook Delay: {metrics['hook_delay_seconds']}s (Aim for < 1.0s)")
    print(f"Speaking Pace: {metrics['words_per_minute']} WPM (Aim for 150-170 for Reels)")
    print(f"Dead Air Spots to Cut: {len(metrics['awkward_pauses'])}")
    for pause in metrics['awkward_pauses']:
        print(f" ✂️ Cut {pause['silence_duration']}s of silence at {pause['start_time']}s")
        
    # Automatically log the real numbers to the database
    print("\nSaving to creator dashboard...")
    log_video_stats(
        video_name, 
        metrics['hook_delay_seconds'], 
        metrics['words_per_minute'], 
        len(metrics['awkward_pauses'])
    )