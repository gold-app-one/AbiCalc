import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from classes import Calculator, Course, FinalExam, FinalExams
from subjects import *
from customTypes import CourseType, FifthPKType, FinalExamType, UNKNOWN

#=ME

C = Course
GK = CourseType.GK
LK = CourseType.LK

finals: FinalExams = FinalExams(
  FinalExam(CHEMISTRY, FinalExamType.LK1, UNKNOWN),
  FinalExam(MATHEMATICS, FinalExamType.LK2, UNKNOWN),
  FinalExam(PHYSICS, FinalExamType.WRITTEN, UNKNOWN),
  FinalExam(ENGLISH, FinalExamType.ORALLY, UNKNOWN),
  FinalExam(HISTORY, FinalExamType.PRESENTATION, UNKNOWN),
  FifthPKType.PP
)

Q1: list[Course] = [
  C(GERMAN, 12, GK, 1),
  C(ENGLISH, 13, GK, 1),
  C(DS, 14, GK, 1),
  C(HISTORY, 12, GK, 1),
  C(PHILOSOPHY, 14, GK, 1),
  C(MATHEMATICS, 14, LK, 1),
  C(PHYSICS, 15, GK, 1),
  C(CHEMISTRY, 12, LK, 1),
  C(COMPUTER_SCIENCE, 13, GK, 1),
  C(SUB, 15, GK, 1),
]

Q2: list[Course] = [
  C(GERMAN, 13, GK, 2),
  C(ENGLISH, 13, GK, 2),
  C(DS, 14, GK, 2),
  C(HISTORY, 14, GK, 2),
  C(PHILOSOPHY, 15, GK, 2),
  C(MATHEMATICS, 13, LK, 2),
  C(PHYSICS, 14, GK, 2),
  C(CHEMISTRY, 14, LK, 2),
  C(COMPUTER_SCIENCE, 13, GK, 2),
  C(PHYSICAL_EDUCATION, 11, GK, 1),
  C(PHYSICAL_EDUCATION, 11, GK, 2),
  C(SUB, 10, GK, 2),
]

Q3: list[Course] = [
  C(GERMAN, 13, GK, 3),
  C(ENGLISH, 13, GK, 3),
  C(DS, 14, GK, 3),
  C(HISTORY, 11, GK, 3),
  C(PHILOSOPHY, 14, GK, 3),
  C(MATHEMATICS, 14, LK, 3),
  C(PHYSICS, 14, GK, 3),
  C(CHEMISTRY, 13, LK, 3),
  C(COMPUTER_SCIENCE, 13, GK, 3),
  C(PHYSICAL_EDUCATION, 10, GK, 3),
  C(ENGLISH_Z, 14, GK, 3),
]

Q4: list[Course] = [
  C(GERMAN, UNKNOWN, GK, 4),
  C(ENGLISH, UNKNOWN, GK, 4),
  C(DS, UNKNOWN, GK, 4),
  C(HISTORY, UNKNOWN, GK, 4),
  C(PHILOSOPHY, UNKNOWN, GK, 4),
  C(MATHEMATICS, UNKNOWN, LK, 4),
  C(PHYSICS, UNKNOWN, GK, 4),
  C(CHEMISTRY, UNKNOWN, LK, 4),
  C(COMPUTER_SCIENCE, UNKNOWN, GK, 4),
  C(PHYSICAL_EDUCATION, UNKNOWN, GK, 4),
  C(ENGLISH_Z, UNKNOWN, GK, 4),
]

courses: list[Course] = Q1 + Q2 + Q3 + Q4

calculator = Calculator(courses, finals)

calculator.getBestCombinations(1)