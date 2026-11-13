HOOK_WEIGHT = 40
PACE_WEIGHT = 30
DEAD_AIR_WEIGHT = 30

HOOK_TARGET = 1.0       # seconds, full marks at or below this
HOOK_CUTOFF = 5.0       # seconds, zero marks at or above this
PACE_RANGE = (150, 170)  # WPM, full marks inside this window
PACE_TOLERANCE = 60     # WPM outside the window before pace scores zero
DEAD_AIR_PENALTY = 10   # points lost per pause


def _linear_falloff(distance, limit):
    return max(0.0, 1 - distance / limit)


def calculate_retention_score(hook_delay, wpm, dead_air_count):
    if wpm == 0:
        return {"score": 0, "grade": "F", "breakdown": {"hook": 0, "pace": 0, "dead_air": 0}}

    hook = HOOK_WEIGHT * _linear_falloff(max(0, hook_delay - HOOK_TARGET), HOOK_CUTOFF - HOOK_TARGET)

    low, high = PACE_RANGE
    pace_distance = max(low - wpm, wpm - high, 0)
    pace = PACE_WEIGHT * _linear_falloff(pace_distance, PACE_TOLERANCE)

    dead_air = max(0, DEAD_AIR_WEIGHT - dead_air_count * DEAD_AIR_PENALTY)

    score = round(hook + pace + dead_air)
    return {
        "score": score,
        "grade": _grade(score),
        "breakdown": {"hook": round(hook), "pace": round(pace), "dead_air": round(dead_air)},
    }


def _grade(score):
    for cutoff, letter in ((90, "A"), (75, "B"), (60, "C"), (40, "D")):
        if score >= cutoff:
            return letter
    return "F"


if __name__ == "__main__":
    for hook, wpm, pauses in [(23.6, 60, 0), (1.2, 145, 1), (0.4, 160, 0), (2.5, 200, 3), (0, 0, 0)]:
        print(f"hook={hook}s wpm={wpm} pauses={pauses} -> {calculate_retention_score(hook, wpm, pauses)}")
