from types import SimpleNamespace

from core_analyzer import calculate_speech_metrics


def make_word(start, end):
    return SimpleNamespace(start=start, end=end)


def test_calculates_speech_start_and_long_pauses():
    words = [
        make_word(0.0, 0.2),
        make_word(0.3, 0.5),
        make_word(2.0, 2.2),
        make_word(2.3, 2.5)
    ]
    result = calculate_speech_metrics(words)

    assert result["hook_delay_seconds"] == 0.0
    assert result["awkward_pauses"] == [
        {
            "start_time": 0.5,
            "silence_duration": 1.5
        }
    ]
    assert result["words_per_minute"] == 240


def test_handles_empty_transcript():
    result = calculate_speech_metrics([])

    assert result["hook_delay_seconds"] == 0.0
    assert result["words_per_minute"] == 0
    assert result["awkward_pauses"] == []