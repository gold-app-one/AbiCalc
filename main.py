from classes import Calculator, Course, FinalExam, FinalExams
from subjects import *
from customTypes import CourseType, FifthPKType, FinalExamType, UNKNOWN

def main():
    C = Course
    GK = CourseType.GK
    LK = CourseType.LK

    YOUR_LK_1: Subject = GERMAN
    YOUR_LK_2: Subject = BIOLOGY

    finals: FinalExams = FinalExams(
    FinalExam(YOUR_LK_1, FinalExamType.LK1, UNKNOWN),
    FinalExam(YOUR_LK_2, FinalExamType.LK2, UNKNOWN),
    FinalExam(ENGLISH, FinalExamType.WRITTEN, UNKNOWN),
    FinalExam(HISTORY, FinalExamType.ORALLY, UNKNOWN),
    FinalExam(MATHEMATICS, FinalExamType.PRESENTATION, UNKNOWN),
    FifthPKType.PP
    )

    Q1: list[Course] = [
        C(YOUR_LK_1, 10, LK, 1),
        C(YOUR_LK_2, 10, LK, 1),
        C(GEOGRAPHY, 10, GK, 1),
        C(ENGLISH, 10, GK, 1),
        C(MUSIC, 10, GK, 1),
        C(HISTORY, 10, GK, 1),
        C(PHILOSOPHY, 10, GK, 1),
        C(PHYSICS, 10, GK, 1),
        C(MATHEMATICS, 10, GK, 1),
        C(POLITICS, 10, GK, 1),
        C(PHYSICAL_EDUCATION, 10, GK, 1),
    ]

    Q2: list[Course] = [
        C(YOUR_LK_1, 10, LK, 2),
        C(YOUR_LK_2, 10, LK, 2),
        C(GEOGRAPHY, 10, GK, 2),
        C(ENGLISH, 10, GK, 2),
        C(MUSIC, 10, GK, 2),
        C(HISTORY, 10, GK, 2),
        C(PHILOSOPHY, 10, GK, 2),
        C(PHYSICS, 10, GK, 2),
        C(MATHEMATICS, 10, GK, 2),
        C(POLITICS, 10, GK, 2),
        C(PHYSICAL_EDUCATION, 10, GK, 2),
    ]

    Q3: list[Course] = [
        C(YOUR_LK_1, UNKNOWN, LK, 3),
        C(YOUR_LK_2, UNKNOWN, LK, 3),
        C(GEOGRAPHY, UNKNOWN, GK, 3),
        C(ENGLISH, UNKNOWN, GK, 3),
        C(MUSIC, UNKNOWN, GK, 3),
        C(HISTORY, UNKNOWN, GK, 3),
        C(PHILOSOPHY, UNKNOWN, GK, 3),
        C(PHYSICS, UNKNOWN, GK, 3),
        C(COMPUTER_SCIENCE, UNKNOWN, GK, 3),
        C(MATHEMATICS, UNKNOWN, GK, 3),
        C(PHYSICAL_EDUCATION, UNKNOWN, GK, 3),
    ]

    Q4: list[Course] = [
        C(YOUR_LK_1, UNKNOWN, LK, 4),
        C(YOUR_LK_2, UNKNOWN, LK, 4),
        C(GEOGRAPHY, UNKNOWN, GK, 4),
        C(ENGLISH, UNKNOWN, GK, 4),
        C(MUSIC, UNKNOWN, GK, 4),
        C(HISTORY, UNKNOWN, GK, 4),
        C(PHILOSOPHY, UNKNOWN, GK, 4),
        C(PHYSICS, UNKNOWN, GK, 4),
        C(COMPUTER_SCIENCE, UNKNOWN, GK, 4),
        C(MATHEMATICS, UNKNOWN, GK, 4),
        C(PHYSICAL_EDUCATION, UNKNOWN, GK, 4),
    ]

    courses: list[Course] = Q1 + Q2 + Q3 + Q4

    calculator = Calculator(courses, finals)

    calculator.getBestCombinations(1)

if __name__ == "__main__":
    main()