from retention_score import calculate_retention_score


def test_good_metrics_produce_high_score():
    result = calculate_retention_score(
        hook_delay=0.4,
        wpm=160,
        dead_air_count=0
    )
    assert result["score"] == 100
    assert result["grade"] == "A"


def test_zero_wpm_produces_zero_score():
    result = calculate_retention_score(
        hook_delay=0,
        wpm=0,
        dead_air_count=0
    )
    assert result["score"] == 0


def test_score_is_never_above_100():
    result = calculate_retention_score(
        hook_delay=0,
        wpm=160,
        dead_air_count=0
    )
    assert result["score"] <= 100


def test_score_is_never_negative():
    result = calculate_retention_score(
        hook_delay=100,
        wpm=300,
        dead_air_count=100
    )
    assert result["score"] >= 0