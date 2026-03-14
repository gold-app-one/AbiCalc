from classes import Calculator, Course, FinalExam, FinalExams
from subjects import *
from customTypes import CourseType, FifthPKType, FinalExamType, UNKNOWN

def main():
    C = Course
    GK = CourseType.GK
    LK = CourseType.LK

    # Set your chosen Leistungskurse (LK) subjects here:
    # Example: YOUR_LK_1 = GERMAN, YOUR_LK_2 = BIOLOGY
    # Change these to your actual LK subjects
    YOUR_LK_1: Subject = GERMAN
    YOUR_LK_2: Subject = BIOLOGY

    # Set your chosen final exam subjects and types here:
    # Replace subjects and types as needed. UNKNOWN means the grade is not yet known.
    finals: FinalExams = FinalExams(
        FinalExam(YOUR_LK_1, FinalExamType.LK1, UNKNOWN),
        FinalExam(YOUR_LK_2, FinalExamType.LK2, UNKNOWN),
        FinalExam(ENGLISH, FinalExamType.WRITTEN, UNKNOWN),
        FinalExam(HISTORY, FinalExamType.ORALLY, UNKNOWN),
        FinalExam(MATHEMATICS, FinalExamType.PRESENTATION, UNKNOWN),
        FifthPKType.PP
    )

    # Enter your grades for each course in each semester below.
    # Replace 10 with your actual grade, or use UNKNOWN if you don't know the grade yet.
    # Add/remove courses as needed to match your curriculum.
    Q1: list[Course] = [
        C(YOUR_LK_1, 10, LK, 1),  # Example: 10 is the grade for YOUR_LK_1 in Q1
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

    # Repeat for Q2 (second semester)
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

    # Repeat for Q3 (third semester)
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

    # Repeat for Q4 (fourth semester)
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

    # Combine all your courses for all semesters
    courses: list[Course] = Q1 + Q2 + Q3 + Q4

    # Create the calculator and get your best Abitur grade combinations
    calculator = Calculator(courses, finals)

    calculator.getBestCombinations(1)  # You can change the number to see more combinations

if __name__ == "__main__":
    main()