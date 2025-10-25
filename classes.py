from typing import List, Tuple, Optional
from constants import MIN_LK_COURSES, MAX_LK_COURSES, MIN_GK_COURSES, MAX_GK_COURSES, MIN_PASSED_GRADE, OVERALL_MIN_GRADE_FINAL_EXAMS, LK_FACTOR, GK_FACTOR
from customTypes import CourseType, FifthPKType, FinalExamType, Grade, LogType, MustBringInCourses, Points, Semester
from logHelper import logExit, log
from subjects import ARTS, BIOLOGY, CHEMISTRY, DS, ENGLISH, FRENCH, GEOGRAPHY, HISTORY, LATIN, MATHEMATICS, MUSIC, PHILOSOPHY, PHYSICAL_EDUCATION, PHYSICS, POLITICS, SPANISH, Subject, GERMAN
import itertools

class FinalExam:
    def __init__(self, subject: Subject, type: FinalExamType, grade: Grade) -> None:
        self.subject: Subject = subject
        self.grade: Grade = grade
        self.type: FinalExamType = type

class FinalExams:
    def __init__(self, LK1: FinalExam, LK2: FinalExam, written: FinalExam, orally: FinalExam, fifth: FinalExam, fithPKType: FifthPKType) -> None:
        self.LK1: FinalExam = LK1
        self.LK2: FinalExam = LK2
        self.written: FinalExam = written
        self.orally: FinalExam = orally
        self.fifth: FinalExam = fifth

    def checkMinRequirements(self) -> bool:
        if not (self.LK1.grade and self.LK2.grade and self.written.grade and self.orally.grade and self.fifth.grade):
            logExit('')
        lk1_passed: bool= self.LK1.grade >= MIN_PASSED_GRADE
        lk2_passed = self.LK2.grade >= MIN_PASSED_GRADE
        written_passed = self.written.grade >= MIN_PASSED_GRADE
        orally_passed = self.orally.grade >= MIN_PASSED_GRADE

        total_passed = sum([lk1_passed, lk2_passed, written_passed, orally_passed])

        has_passed_two = total_passed >= 2
        has_passed_LK = lk1_passed or lk2_passed

        totalGrade: int = self.LK1.grade + self.LK2.grade + self.orally.grade + self.fifth.grade
        passedTotalGrade: bool = totalGrade >= OVERALL_MIN_GRADE_FINAL_EXAMS

        return has_passed_two and has_passed_LK and passedTotalGrade

class Course:
    def __init__(self, subject: Subject, grade: Grade, type: CourseType, semester: Semester) -> None:
        self.subject: Subject = subject
        self.type: CourseType = type
        self.grade: Grade = grade
        self.semester: Semester = semester

class CreditedCombination:
    def __init__(self, creditedCourses: tuple[Course, ...], finals: FinalExams) -> None:
        self.__creditedCourses = creditedCourses
        self.__finals = finals
        self.__LKs: Tuple[Subject, Subject] = (self.__finals.LK1.subject, self.__finals.LK2.subject)

    def getScore(self) -> Points:
        totalPoints: Points = Points(0)
        for course in self.__creditedCourses:
            coursePoints = (course.grade if course.grade else 0) * (LK_FACTOR if course.subject in self.__LKs else GK_FACTOR)
            totalPoints += coursePoints
        return totalPoints

    def __eligibleForExams(self) -> bool:
        return True # TODO: implement this

    def passed(self) -> bool:
        eligibleCondition = self.__eligibleForExams
        totalScoreCondition = lambda: self.getScore() >= 300
        conditions = (
            totalScoreCondition,
            eligibleCondition
        )
        return all(condition() for condition in conditions)

    def checkMinRequiremnets(self) -> bool:
        lk1sub = self.__finals.LK1.subject  # type: ignore
        grades: List[Optional[Grade]] = list(course.grade for course in self.__creditedCourses if course.subject == lk1sub)
        if not grades:
            logExit('No LK grades found')
        return True

    def __str__(self) -> str:
        string: str = f'{"✅" if self.passed() else "❌"} - {self.getScore()}'
        for course in self.__creditedCourses:
            string += (f'({course.grade}P-{course.subject}-Q{course.semester})')
        return string + '\n\n'

class Calculator:
    def __init__(self, courses: List[Course], finals: FinalExams) -> None:
        self.__courses: List[Course] = courses
        self.__finals = finals
        self.__checkValidity()
    def getBestCombinations(self, amount: int = 5) -> None:
        combinations: List[CreditedCombination] = sorted(self.__getCreditedCombinations(), key=lambda c: (c.passed(), c.getScore()))
        for comb in combinations[:amount]:
            print(comb)
    def __checkValidity(self) -> bool:
        return self.__enoughCoursesOfTypes()
    def __getCreditedCombinations(self) -> List[CreditedCombination]:
        M = MustBringInCourses
        combinations: List[CreditedCombination] = []
        germanCourses: List[Course] = [course for course in self.__courses if course.subject == GERMAN]
        foreignLangCourses: List[Course] = [course for course in self.__courses if course.subject in (ENGLISH, FRENCH, SPANISH, LATIN)]
        artsCourses: List[Course] = [course for course in self.__courses if course.subject in (ARTS, MUSIC, DS)]
        politicalCourses: List[Course] = [course for course in self.__courses if course.subject in (POLITICS, HISTORY, GEOGRAPHY, PHILOSOPHY)]
        mathsCourses: List[Course] = [course for course in self.__courses if course.subject == MATHEMATICS]
        PECourses: List[Course] = [course for course in self.__courses if course.subject == PHYSICAL_EDUCATION]
        scienceCourses: List[Course] = [course for course in self.__courses if course.subject in (PHYSICS, CHEMISTRY, BIOLOGY)]
        for germanComb in list(itertools.combinations(germanCourses, M.German.value)):
            for foreignLangComb in list(itertools.combinations(foreignLangCourses, M.ForeignLanguage.value)):
                for artsComb in list(itertools.combinations(artsCourses, M.Art.value)):
                    for politicalComb in list(itertools.combinations(politicalCourses, M.Political.value)):
                        for mathsComb in list(itertools.combinations(mathsCourses, M.Maths.value)):
                            for PEComb in list(itertools.combinations(PECourses, M.Sport.value)):
                                for ScienceComb in list(itertools.combinations(scienceCourses, M.Science.value)):
                                    courses: List[Course] = list(germanComb + foreignLangComb + artsComb + politicalComb + mathsComb + PEComb + ScienceComb)
                                    remainingAmount: int = self.__getRemainingCoursesAmount(courses, (self.__finals.LK1.subject, self.__finals.LK2.subject))
                                    remainingCourses: list[Course] = [course for course in self.__courses if course not in courses]
                                    for extraComb in self.__getPossibleExtraCoursesCombinations(remainingCourses, remainingAmount):
                                        courses += extraComb
                                    coursesCombination = tuple(courses)
                                    if len(coursesCombination) != MIN_GK_COURSES + 8:
                                        log('Combination failed (couldn\'t get correct Amount)', LogType.LOG)
                                    combination = CreditedCombination(creditedCourses=coursesCombination, finals=self.__finals)
                                    combinations.append(combination)
        return combinations

    def __getPossibleExtraCoursesCombinations(self, remainingCourses: List[Course], pickAmount: int) -> List[Tuple[Course, ...]]:
        return list(itertools.combinations(remainingCourses, pickAmount))

    def __getRemainingCoursesAmount(self, courses: List[Course], LKs: Tuple[Subject, Subject]) -> int:
        return MIN_GK_COURSES - (len(courses) - self.__countLKCourses(courses, LKs))

    def __countLKCourses(self, courses: List[Course], LKs: Tuple[Subject, Subject]) -> int:
        return sum(1 for course in courses if course.subject in LKs)

    def __enoughCoursesOfTypes(self) -> bool:
        LKs: List[Subject] = []
        LKAmount: int = 0
        GKAmount: int = 0
        for course in self.__courses:
            match course.type:
                case CourseType.LK:
                    if course.subject not in LKs:
                        LKs.append(course.subject)
                    LKAmount += 1
                case CourseType.GK:
                    GKAmount += 1
        if not (MIN_LK_COURSES <= LKAmount <= MAX_LK_COURSES):
            logExit(f'You must have between {MIN_LK_COURSES} and {MAX_LK_COURSES} advanced courses. Yours: {LKAmount}')
        if not (MIN_GK_COURSES <= LKAmount <= MAX_GK_COURSES):
            logExit(f'You must have between {MIN_GK_COURSES} and {MAX_GK_COURSES} basic courses. Yours: {GKAmount}')
        # self.__finals.LK1 = FinalExam(LKs[0], FinalExamType.LK1) # What is this?
        # self.__finals.LK2 = FinalExam(LKs[1], FinalExamType.LK1)
        return True