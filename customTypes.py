from typing import TypeAlias, Literal, Optional, Tuple, Annotated
from enum import Enum
from constants import MUST_BRING_IN_GERMAN_COUSES, MUST_BRING_IN_FOREIGN_LANGUAGE_COUSES, MUST_BRING_IN_ART_COUSES, MUST_BRING_IN_POLITICAL_COUSES, MUST_BRING_IN_MATH_COURSES, MUST_BRING_IN_SCIENCE_COUSES, MUST_BRING_IN_SPORT_COUSES

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

Grade: TypeAlias = Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]

Points: TypeAlias = Annotated[int, ValueRange(0, 900)]

CourseGrades: TypeAlias = Tuple[Grade, Grade, Grade, Grade]

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

class MustBringInCourses(Enum):
    German = MUST_BRING_IN_GERMAN_COUSES
    ForeignLanguage = MUST_BRING_IN_FOREIGN_LANGUAGE_COUSES
    Art = MUST_BRING_IN_ART_COUSES
    Political = MUST_BRING_IN_POLITICAL_COUSES
    Maths = MUST_BRING_IN_MATH_COURSES
    Science = MUST_BRING_IN_SCIENCE_COUSES
    Sport = MUST_BRING_IN_SPORT_COUSES