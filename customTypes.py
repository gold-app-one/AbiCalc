from __future__ import annotations
from typing import TypeAlias, Literal
from enum import Enum
from functools import total_ordering


class LogType(Enum):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse LogType im RAM
    Erg.: -
    """
    LOG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class ValueRange:
    """
    Vor.: eine minimale und eine maximale Zahl als Integer
    Eff.: initiert ein Objekt der Klasse ValueRange im RAM
    Erg.: -
    """
    def __init__(self, min: int, max: int):
        self.min = min
        self.max = max

class FifthPKType(Enum):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse FifthPKType im RAM
    Erg.: -
    """
    PP = 0
    BLL = 1

Semester: TypeAlias = Literal[1, 2, 3, 4]

@total_ordering
class Points:
    """
    Vor.: ein Wert 'value' und eine mögliche Erhöhung 'possibleIncrease' als Float
    Eff.: initiert ein Objekt der Klasse Points im RAM
    Erg.: -
    """
    def __init__(self, value: float = 0, possibleIncrease: float = 0) -> None:
        self.value: float = value
        self.possibleIncrease: float = possibleIncrease
    def getNumeric(self, max: int = 15) -> float:
        """
        Vor.: eine maximale Zahl 'max' als Integer
        Eff.: -
        Erg.: eine numerische Darstellung der Punkte
        """
        return (17 - self.value*15/max)/3
    def __add__(self, other: Points | int) -> Points:
        """
        Vor.: eine andere Points oder eine Zahl als Integer
        Eff.: -
        Erg.: eine neue Points, die die Summe der Punkte darstellt
        """
        if isinstance(other, Points):
            return Points(self.value+other.value, self.possibleIncrease + other.possibleIncrease)
        else:
            if other == -1:
                return Points(self.value, self.possibleIncrease+15)
            else:
                return Points(self.value+other, self.possibleIncrease)
    def __mul__(self, other: float | int) -> Points:
        """
        Vor.: eine Zahl 'other' als Float oder Integer
        Eff.: -
        Erg.: eine neue Points, die das Produkt der Punkte darstellt
        """
        return Points(self.value*other, self.possibleIncrease*other)
    def __eq__(self, other: float | int | Points | object) -> bool:
        """
        Vor.: eine andere Points oder eine Zahl als Float/Integer
        Eff.: -
        Erg.: ein Boolean, ob die Punkte gleich sind
        """
        if isinstance(other, Points):
            return (self.value + self.possibleIncrease / 2) == (other.value + other.possibleIncrease / 2)
        if isinstance(other, (int, float)):
            return (self.value + self.possibleIncrease / 2) == float(other)
        return NotImplemented
    def __lt__(self, other: float | int | Points | object) -> bool:
        """
        Vor.: eine andere Points oder eine Zahl als Float/Integer
        Eff.: -
        Erg.: ein Boolean, ob die Punkte kleiner sind
        """
        if isinstance(other, Points):
            return (self.value + self.possibleIncrease / 2) < (other.value + other.possibleIncrease / 2)
        if isinstance(other, (int, float)):
            return (self.value + self.possibleIncrease / 2) < float(other)
        return NotImplemented
    def __str__(self) -> str:
        """
        Vor.: -
        Eff.: -
        Erg.: eine Stringdarstellung der Punkte
        """
        if self.possibleIncrease == 0:
            return f'{self.value}P'
        if self.value == 0 and self.possibleIncrease == 15:
            return '??P'
        return f'{self.value}~{self.value+self.possibleIncrease}P'

UNKNOWN = Points(0, 15)

@total_ordering
class CourseType(Enum):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse CourseType im RAM
    Erg.: -
    """
    GK = 0
    LK = 1
    def __eq__(self, other: object) -> bool:
        """
        Vor.: eine andere CourseType
        Eff.: -
        Erg.: ein Boolean, ob die Kurse gleich sind
        """
        if isinstance(other, CourseType):
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other: "CourseType") -> bool:
        """
        Vor.: eine andere CourseType
        Eff.: -
        Erg.: ein Boolean, ob die Kurse kleiner sind
        """
        return self.value < other.value

class FinalExamType(Enum):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse FinalExamType im RAM
    Erg.: -
    """
    LK1 = 0
    LK2 = 1
    WRITTEN = 2
    ORALLY = 3
    PRESENTATION = 4
    BLL = 5

class SubjectCategory(Enum):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse SubjectCategory im RAM
    Erg.: -
    """
    LangArt = 1
    Political = 2
    MathScience = 3
    Physical = 4
    Other = 5