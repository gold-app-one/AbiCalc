from constants import FINAL_EXAM_FACTOR, MIN_LK_COURSES, MAX_LK_COURSES, MIN_GK_COURSES, MAX_GK_COURSES, MIN_PASSED_GRADE, OVERALL_MIN_GRADE_FINAL_EXAMS
from customTypes import FinalExamType, CourseGrades, CourseType, FifthPKType, MustBringInCourses, Semester, Grade
from logHelper import logExit
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
    def __init__(self, subject: Subject, grades: CourseGrades, type: CourseType) -> None:
        self.subject = subject
        self.type = type
        self.grades = grades

class CreditedCombination:
    def __init__(self, creditedCourses: tuple[Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course, Course], finals: FinalExams, courses: list[Course]) -> None:
        self.__creditedCourses = creditedCourses
        self.__finals = finals
        self.__courses = courses
    
    def checkMinRequiremnets(self) -> bool:
        lk1sub = self.__finals.LK1.subject  # type: ignore
        grades = next((course.grades for course in self.__courses if course.subject == lk1sub), None)
        if not grades:
            logExit('No LK grades found')
            
        return True

class Calculator:
    def __init__(self, courses: list[Course], finals: FinalExams) -> None:
        self.__courses: list[Course] = courses
        self.__finals = finals
        self.__checkValidity()
    def __checkValidity(self) -> bool:
        return self.__enoughCoursesOfTypes()
    def __getCreditedCombinations(self) -> CreditedCombination:
        M = MustBringInCourses
        combinations: list[CreditedCombination] = []
        germanCourses: list[Course] = [course for course in self.__courses if course.subject == GERMAN]
        foreignLangCourses: list[Course] = [course for course in self.__courses if course.subject in (ENGLISH, FRENCH, SPANISH, LATIN)]
        artsCourses: list[Course] = [course for course in self.__courses if course.subject in (ARTS, MUSIC, DS)]
        politicalCourses: list[Course] = [course for course in self.__courses if course.subject in (POLITICS, HISTORY, GEOGRAPHY, PHILOSOPHY)]
        mathsCourses: list[Course] = [course for course in self.__courses if course.subject == MATHEMATICS]
        PECourses: list[Course] = [course for course in self.__courses if course.subject == PHYSICAL_EDUCATION]
        scienceCourses: list[Course] = [course for course in self.__courses if course.subject in (PHYSICS, CHEMISTRY, BIOLOGY)]
        for germanComb in list(itertools.combinations(germanCourses, M.German.value)):
            for foreignLangComb in list(itertools.combinations(foreignLangCourses, M.ForeignLanguage.value)):
                for artsComb in list(itertools.combinations(artsCourses, M.Art.value)):
                    for politicalComb in list(itertools.combinations(politicalCourses, M.Political.value)):
                        for mathsComb in list(itertools.combinations(mathsCourses, M.Maths.value)):
                            for PEComb in list(itertools.combinations(PECourses, M.Sport.value)):
                                for ScienceComb in list(itertools.combinations(scienceCourses, M.Science.value)):
                                    courses = germanComb + foreignLangComb + artsComb + politicalComb + mathsComb + PEComb + ScienceComb
                                    if len(courses) < MIN_GK_COURSES: # FIXME: wrong because LK could and couldn't be in the list of must haves already
                                        pass # TODO: add more possible courses
                                    combination = CreditedCombination()
                                    combinations.append(combination)
                    
        
    def __enoughCoursesOfTypes(self) -> bool:
        LKs: list[Subject] = []
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
        self.__finals.LK1 = FinalExam(LKs[0], FinalExamType.LK1)
        self.__finals.LK2 = FinalExam(LKs[1], FinalExamType.LK1)
        return True