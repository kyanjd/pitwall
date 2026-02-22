import uuid


class Scorer:
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

    def score_position(self, actual_position: int, predicted_position: int) -> int:
        diff = abs(actual_position - predicted_position)
        return self.SCORE_DICT.get(diff, 0)

    def score_dnf(self, actual_driver: uuid.UUID | None, predicted_driver: uuid.UUID) -> int:
        if actual_driver is None:
            return 0
        if actual_driver == predicted_driver:
            return 10
        return 0

    def set_score_dict(self, score_dict: dict):
        self.SCORE_DICT = score_dict
