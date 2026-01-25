SCORE_DICT = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
}


def score_prediction(actual_position: int, predicted_position: int) -> int:
    diff = abs(actual_position - predicted_position)
    return SCORE_DICT.get(diff, 0)
