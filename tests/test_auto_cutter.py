import pytest

from auto_cutter import build_keep_segments


def test_full_video_is_kept_without_pauses():
    result = build_keep_segments(
        duration=10,
        hook_delay=0,
        awkward_pauses=[]
    )
    assert result == [(0.0, 10.0)]


def test_long_pause_is_removed():
    result = build_keep_segments(
        duration=10,
        hook_delay=0,
        awkward_pauses=[
            {
                "start_time": 3,
                "silence_duration": 2
            }
        ]
    )
    assert len(result) == 2
    assert result[0] == pytest.approx((0.0, 3.15))
    assert result[1] == pytest.approx((4.85, 10.0))


def test_initial_silence_is_removed():
    result = build_keep_segments(
        duration=10,
        hook_delay=1,
        awkward_pauses=[]
    )
    assert result == [(0.85, 10.0)]


def test_short_pause_is_preserved():
    result = build_keep_segments(
        duration=10,
        hook_delay=0,
        awkward_pauses=[
            {
                "start_time": 3,
                "silence_duration": 0.2
            }
        ]
    )
    assert result == [(0.0, 10.0)]