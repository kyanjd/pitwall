SCORE_DICT = {
    0: 25,
    1: 18,
    2: 15,
    3: 12,
    4: 10,
    5: 8,
    6: 6,
    7: 4,
    8: 2,
    9: 1,
}


def score_position(actual_position: int, predicted_position: int) -> int:
    diff = abs(actual_position - predicted_position)
    return SCORE_DICT.get(diff, 0)


def score_dnf(predicted_driver):
    pass
