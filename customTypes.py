from __future__ import annotations
from typing import TypeAlias, Literal
from enum import Enum
from functools import total_ordering

class LogType(Enum):
    LOG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class ValueRange:
    def __init__(self, min: int, max: int):
        self.min = min
        self.max = max

class FifthPKType(Enum):
    PP = 0
    BLL = 1

Semester: TypeAlias = Literal[1, 2, 3, 4]

@total_ordering
class Points:
    def __init__(self, value: float = 0, possibleIncrease: float = 0) -> None:
        self.value: float = value
        self.possibleIncrease: float = possibleIncrease
    def __add__(self, other: Points | int) -> Points:
        if isinstance(other, Points):
            return Points(self.value+other.value, self.possibleIncrease + other.possibleIncrease)
        else:
            if other == -1:
                return Points(self.value, self.possibleIncrease+15)
            else:
                return Points(self.value+other, self.possibleIncrease)
    def __mul__(self, other: float | int) -> Points:
        return Points(self.value*other, self.possibleIncrease*other)
    def __eq__(self, other: float | int | Points | object) -> bool:
        if isinstance(other, Points):
            return (self.value + self.possibleIncrease / 2) == (other.value + other.possibleIncrease / 2)
        if isinstance(other, (int, float)):
            return (self.value + self.possibleIncrease / 2) == float(other)
        return NotImplemented
    def __lt__(self, other: float | int | Points | object) -> bool:
        if isinstance(other, Points):
            return (self.value + self.possibleIncrease / 2) < (other.value + other.possibleIncrease / 2)
        if isinstance(other, (int, float)):
            return (self.value + self.possibleIncrease / 2) < float(other)
        return NotImplemented
    def __str__(self) -> str:
        if self.possibleIncrease == 0:
            return f'{self.value}P'
        return f'{self.value}~{self.value+self.possibleIncrease}P'

UNKNOWN = Points(0, 15)

@total_ordering
class CourseType(Enum):
    GK = 0
    LK = 1
    def __eq__(self, other: object) -> bool:
        if isinstance(other, CourseType):
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other: "CourseType") -> bool:
        return self.value < other.value

class FinalExamType(Enum):
    LK1 = 0
    LK2 = 1
    WRITTEN = 2
    ORALLY = 3
    PRESENTATION = 4
    BLL = 5

class SubjectCategory(Enum):
    LangArt = 1
    Political = 2
    MathScience = 3
    Physical = 4
    Other = 5