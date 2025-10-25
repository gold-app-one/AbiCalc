from __future__ import annotations
from typing import TypeAlias, Literal, Optional
from enum import Enum
from constants import MUST_BRING_IN_GERMAN_COUSES, MUST_BRING_IN_FOREIGN_LANGUAGE_COUSES, MUST_BRING_IN_ART_COUSES, MUST_BRING_IN_POLITICAL_COUSES, MUST_BRING_IN_MATH_COURSES, MUST_BRING_IN_SCIENCE_COUSES, MUST_BRING_IN_SPORT_COUSES
from functools import total_ordering

UNKNOWN = -1

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

Grade: TypeAlias = Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, -1]]

@total_ordering
class Points:
    def __init__(self, value: int = 0, possibleIncrease: int = 0) -> None:
        self.value = value
        self.possibleIncrease = 0
    def __add__(self, other: Points | Grade | int) -> Points:
        if isinstance(other, Points):
            return Points(self.value+other.value, self.possibleIncrease + other.possibleIncrease)
        else:
            if other == None:
                return self
            elif other == -1:
                return Points(self.value, self.possibleIncrease+15)
            else:
                return Points(self.value+other, self.possibleIncrease)
    def __asFloat(self) -> float:
        return self.value
    def __eq__(self, other: float | int | Points | object) -> bool:
        if isinstance(other, Points):
            return self.__asFloat() == other.__asFloat()
        if isinstance(other, int):
            return self.__asFloat() == other
        return self.__eq__(other)
    def __lt__(self, other: float | int | Points) -> bool:
        if isinstance(other, Points):
            return self.__asFloat() < other.__asFloat()
        if isinstance(other, int):
            return self.__asFloat() < other
        return NotImplemented
    def __str__(self) -> str:
        if self.possibleIncrease == 0:
            return f'{self.value}P'
        return f'{self.value}~{self.value+self.possibleIncrease}P'

class CourseType(Enum):
    GK = 0
    LK = 1

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

class MustBringInCourses(Enum):
    German = MUST_BRING_IN_GERMAN_COUSES
    ForeignLanguage = MUST_BRING_IN_FOREIGN_LANGUAGE_COUSES
    Art = MUST_BRING_IN_ART_COUSES
    Political = MUST_BRING_IN_POLITICAL_COUSES
    Maths = MUST_BRING_IN_MATH_COURSES
    Science = MUST_BRING_IN_SCIENCE_COUSES
    Sport = MUST_BRING_IN_SPORT_COUSES