from enum import Enum


class F1SessionType(str, Enum):
    QUALIFYING = "Qualifying"
    RACE = "Race"
    SPRINT = "Sprint"

    @property
    def api_results_key(self) -> str:
        return {
            F1SessionType.RACE: "Results",
            F1SessionType.QUALIFYING: "QualifyingResults",
            F1SessionType.SPRINT: "SprintResults",
        }[self]
