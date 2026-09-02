from enum import StrEnum


class F1SessionType(StrEnum):
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
