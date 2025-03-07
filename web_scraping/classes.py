from dataclasses import dataclass
from datetime import time, timedelta


@dataclass
class PersonData:
    name: str
    first_name: str
    start_number: int
    nationality: str




@dataclass
class Scoring:
    race: str
    division: str


@dataclass
class WorkoutResult:
    Running1: timedelta
    SkiErg: timedelta
    Running2: timedelta
    SledPush: timedelta
    Running3: timedelta
    SledPull: timedelta
    Running4: timedelta
    BurpeeBroadJumps: timedelta
    Running5: timedelta
    RowErg: timedelta
    Running6: timedelta
    FarmersCarry: timedelta
    Running7: timedelta
    SandbagLunges: timedelta
    Running8: timedelta
    WallBalls: timedelta


@dataclass
class JudgingDecision:
    bonus: timedelta
    penalty: timedelta
    disqualification_reason: str
    info: str


@dataclass
class Totals:
    rank_gender: int
    rank_age_group: int
    finish_time: timedelta



@dataclass
class Split:
    split_name: str
    time_of_day: time
    time: time
    time_diff: timedelta

    def __str__(self):
        return f"{self.split_name}: {self.time_of_day} {self.time} {self.time_diff}"

@dataclass
class SplitSummary:
    # Run 1
    RoxIn_1: Split
    SkiErgIn: Split
    SkiErgOut: Split
    RoxOut1: Split
    # Run 2
    RoxIn_2: Split
    SledPushIn: Split
    SledPushOut: Split
    RoxOut2: Split
    # Run 3
    RoxIn_3: Split
    SledPullIn: Split
    SledPullOut: Split
    RoxOut3: Split
    # Run 4
    RoxIn_4: Split
    BurpeesIn: Split
    BurpeesOut: Split
    RoxOut4: Split
    # Run 5
    RoxIn_5: Split
    RowErgIn: Split
    RowErgOut: Split
    RoxOut5: Split
    # Run 6
    RoxIn_6: Split
    FarmersCarryIn: Split
    FarmersCarryOut: Split
    RoxOut6: Split
    # Run 7
    RoxIn_7: Split
    LungesIn: Split
    LungesOut: Split
    RoxOut7: Split
    # Run 8
    RoxIn_8: Split  # frequently missing
    WallBallsIn: Split

    Total: Split


@dataclass
class RaceResult:
    person: PersonData
    scoring: Scoring
    workout_result: WorkoutResult
    judging_decision: JudgingDecision
    totals: Totals
    splits: SplitSummary
