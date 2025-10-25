from typing import List, Tuple
from constants import (FINAL_EXAM_FACTOR, GK_FACTOR, LK_FACTOR, MAX_GK_COURSES, MAX_LK_COURSES,
    MAX_PE_COURSES, MIN_GK_COURSES, MIN_LK_COURSES, MIN_PASSED_GK, MIN_PASSED_GRADE, MIN_PASSED_LK,
    MIN_PE_COURSES, MUST_BRING_IN_SCIENCE_COURSES, MUST_BRING_IN_SPORT_COURSES,
    MUST_BRING_POLITICS_OR_POLITICAL, NON_ELIGIBLE_GRADE, OVERALL_MIN_GRADE,
    OVERALL_MIN_GRADE_FINAL_EXAMS, OVERALL_MIN_GRADE_LK, MustBringInCourses)
from customTypes import CourseType, FifthPKType, FinalExamType, LogType, Points, Semester, SubjectCategory
from logHelper import logExit, log
from subjects import ARTS, BIOLOGY, CHEMISTRY, DS, ENGLISH, FRENCH, GEOGRAPHY, HISTORY, LATIN, MATHEMATICS, MUSIC, PHILOSOPHY, PHYSICAL_EDUCATION, PHYSICS, POLITICS, SPANISH, Subject, GERMAN
import itertools
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') # type: ignore

class FinalExam:
    def __init__(self, subject: Subject, type: FinalExamType, grade: Points) -> None:
        self.subject: Subject = subject
        self.grade: Points = grade
        self.type: FinalExamType = type

class FinalExams:
    def __init__(self, LK1: FinalExam, LK2: FinalExam, written: FinalExam, orally: FinalExam, fifth: FinalExam, fifthPKType: FifthPKType) -> None:
        self.LK1: FinalExam = LK1
        self.LK2: FinalExam = LK2
        self.written: FinalExam = written
        self.orally: FinalExam = orally
        self.fifth: FinalExam = fifth

    def checkMinRequirements(self) -> bool:
        pruefungsfaecher = [self.LK1, self.LK2, self.written, self.orally]
        passed_flags = [e.grade >= MIN_PASSED_GRADE for e in pruefungsfaecher]
        has_two_pruef = sum(passed_flags) >= 2
        has_LK_among_passed = (self.LK1.grade >= MIN_PASSED_GRADE) or (self.LK2.grade >= MIN_PASSED_GRADE)


        has_written_5 = any(e.grade >= MIN_PASSED_GRADE for e in (self.LK1, self.LK2, self.written))

        exams = [self.LK1, self.LK2, self.written, self.orally, self.fifth]
        total_exam_points: Points = sum((e.grade for e in exams), Points(0)) * FINAL_EXAM_FACTOR
        passed_total = total_exam_points >= OVERALL_MIN_GRADE_FINAL_EXAMS

        return has_two_pruef and has_LK_among_passed and has_written_5 and passed_total

class Course:
    def __init__(self, subject: Subject, grade: Points | int | float, type: CourseType, semester: Semester) -> None:
        self.subject: Subject = subject
        self.type: CourseType = type
        self.grade: Points = grade if isinstance(grade, Points) else Points(grade)
        self.semester: Semester = semester

class CreditedCombination:
    def __init__(self, creditedCourses: tuple[Course, ...], finals: FinalExams) -> None:
        self.__creditedCourses = creditedCourses
        self.__finals = finals
        self.__LKs: Tuple[Subject, Subject] = (self.__finals.LK1.subject, self.__finals.LK2.subject)

    def getScore(self) -> Points:
        totalPoints: Points = Points(0)
        for course in self.__creditedCourses:
            coursePoints: Points = course.grade * (LK_FACTOR if course.subject in self.__LKs else GK_FACTOR)
            totalPoints += coursePoints
        for exam in (self.__finals.LK1, self.__finals.LK2, self.__finals.written, self.__finals.orally, self.__finals.fifth):
            totalPoints += exam.grade * FINAL_EXAM_FACTOR
        return totalPoints

    def getSummedLKGrade(self) -> Points:
        total: Points = Points(0)
        lkCourses: List[Course] = [course for course in self.__creditedCourses if course.subject in self.__LKs]
        for lk in lkCourses:
            lkPoints = lk.grade * LK_FACTOR
            total += lkPoints
        return total

    def __eligibleForExams(self) -> bool:
        if any(c.grade == NON_ELIGIBLE_GRADE for c in self.__creditedCourses):
            return False

        lk_courses: List[Course] = [c for c in self.__creditedCourses if c.subject in self.__LKs]
        gk_courses: List[Course] = [c for c in self.__creditedCourses if c.subject not in self.__LKs]

        if len(lk_courses) != MIN_LK_COURSES:
            return False
        if len(gk_courses) != MIN_GK_COURSES:
            return False

        if self.getSummedLKGrade() < OVERALL_MIN_GRADE_LK:
            return False
        if sum(1 for c in lk_courses if c.grade >= MIN_PASSED_GRADE) < MIN_PASSED_LK:
            return False

        min_gk_points: Points = Points(MIN_PASSED_GRADE * MIN_GK_COURSES * GK_FACTOR)
        gk_points: Points = Points(0)
        for c in gk_courses:
            gk_points += c.grade * GK_FACTOR
        if gk_points < min_gk_points:
            return False
        if sum(1 for c in gk_courses if c.grade >= MIN_PASSED_GRADE) < MIN_PASSED_GK:
            return False
        ref_subj = self.__finals.fifth.subject
        if not any(c.subject == ref_subj for c in self.__creditedCourses):
            return False
        return True


    def __finalExamsPassed(self) -> bool:
        return self.__finals.checkMinRequirements()

    def passed(self) -> bool:
        eligibleCondition = self.__eligibleForExams
        totalScoreCondition = lambda: self.getScore() >= OVERALL_MIN_GRADE
        finalExamsCondition = self.__finalExamsPassed
        conditions = (
            totalScoreCondition,
            eligibleCondition,
            finalExamsCondition
        )
        return all(condition() for condition in conditions)

    def __str__(self) -> str:
        string: str = f'{"✅" if self.passed() else "❌"} - {self.getScore()}'
        for course in sorted(self.__creditedCourses, key=lambda c: (c.semester, c.type, c.subject)):
            string += (f'({course.grade}-{course.subject}-Q{course.semester})')
        return string + '\n\n'

class Calculator:
    def __init__(self, courses: List[Course], finals: FinalExams) -> None:
        self.__courses: List[Course] = courses
        self.__finals = finals
        self.__checkValidity()
    def getBestCombinations(self, amount: int = 5) -> None:
        def score_val(c: CreditedCombination) -> float:
            s = c.getScore()
            return s.value + s.possibleIncrease / 2
        combinations = sorted(self.__getCreditedCombinations(),
                            key=lambda c: (not c.passed(), -score_val(c)))
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
        historyCourses: List[Course] = [course for course in self.__courses if course.subject == HISTORY]
        scienceCourses: List[Course] = [course for course in self.__courses if course.subject in (PHYSICS, CHEMISTRY, BIOLOGY)]

        germanCombs = list(itertools.combinations(germanCourses, M.German.value))
        foreignLangCombs = list(itertools.combinations(foreignLangCourses, M.ForeignLanguage.value))
        artsCombs = list(itertools.combinations(artsCourses, M.Art.value))
        historyCombs = list(itertools.combinations(historyCourses, M.History.value))

        total_outer_loops = len(germanCombs) * len(foreignLangCombs) * len(artsCombs) * len(historyCombs)
        print(f"\n🔍 Starting combination search...")
        print(f"📊 Total outer iterations: {total_outer_loops:,}")
        print(f"   German combinations: {len(germanCombs)}")
        print(f"   Foreign language combinations: {len(foreignLangCombs)}")
        print(f"   Arts combinations: {len(artsCombs)}")
        print(f"   History combinations: {len(historyCombs)}")

        outer_iteration = 0

        for germanComb in germanCombs:
            for foreignLangComb in foreignLangCombs:
                for artsComb in artsCombs:
                    for historyComb in historyCombs:
                        outer_iteration += 1
                        if outer_iteration % 10 == 0 or outer_iteration == 1:
                            progress = (outer_iteration / total_outer_loops) * 100
                            print(f"🔄 Progress: {outer_iteration}/{total_outer_loops} ({progress:.1f}%) | Combinations found: {len(combinations):,}")
                        for _any, amount in enumerate(MUST_BRING_POLITICS_OR_POLITICAL(self.__finals.fifth.subject)):
                            combs: list[tuple[Course, ...]] = []
                            if _any:
                                combs = self.__getTwoSubjectsCourses([course for course in self.__courses if course not in historyComb])
                            else:
                                combs = list(itertools.combinations(politicalCourses, amount))
                            for politicalComb in combs:
                                for mathsComb in list(itertools.combinations(mathsCourses, M.Maths.value)):
                                    hasPEAsFinal: bool = any(final.subject == PHYSICAL_EDUCATION for final in (self.__finals.fifth, self.__finals.orally, self.__finals.written, self.__finals.LK1, self.__finals.LK2))
                                    for PEComb in list(itertools.combinations(PECourses, MUST_BRING_IN_SPORT_COURSES(hasPEAsFinal))):
                                        scienceCombs = self.__getScienceCourses(scienceCourses)
                                        for scienceIdx, ScienceComb in enumerate(scienceCombs):
                                            baseCourses: List[Course] = list(germanComb + foreignLangComb + artsComb + historyComb + politicalComb + mathsComb + PEComb + ScienceComb)
                                            remainingAmount: int = self.__getRemainingCoursesAmount(baseCourses, (self.__finals.LK1.subject, self.__finals.LK2.subject))
                                            remainingCourses: list[Course] = [course for course in self.__courses if course not in baseCourses]
                                            extraCombs = self.__getPossibleExtraCoursesCombinations(remainingCourses, remainingAmount)

                                            if scienceIdx == 0 and len(extraCombs) > 100:
                                                print(f"   ⚠️ Inner loop: Processing {len(extraCombs):,} extra combinations (remaining: {len(remainingCourses)} courses, need: {remainingAmount})")

                                            for extraComb in extraCombs:
                                                courses = baseCourses + list(extraComb)
                                                coursesCombination = tuple(courses)
                                                if len(coursesCombination) != MIN_GK_COURSES + 8:
                                                    log('Combination failed (couldn\'t get correct Amount)', LogType.LOG)
                                                combination = CreditedCombination(creditedCourses=coursesCombination, finals=self.__finals)
                                                combinations.append(combination)

        print(f"\n✅ Search complete! Total combinations generated: {len(combinations):,}\n")
        return combinations

    def __getScienceCourses(self, scienceCourses: list[Course]) -> List[Tuple[Course, ...]]:
        possibleBioCombs = list(itertools.combinations(scienceCourses, MUST_BRING_IN_SCIENCE_COURSES(isBiology=True)))
        possibleNonBioCombs = list(itertools.combinations(scienceCourses, MUST_BRING_IN_SCIENCE_COURSES(isBiology=False)))
        return [comb for comb in possibleBioCombs if sum(course.subject == BIOLOGY for course in comb) == 4] + [comb for comb in possibleNonBioCombs if sum(course.subject == BIOLOGY for course in comb) == 0]

    def __getTwoSubjectsCourses(self, possibleCourses: List[Course]) -> List[Tuple[Course, Course]]:
        politicalCourses: list[Course] = [course for course in possibleCourses if course.subject.category == SubjectCategory.Political]
        uncheckedCombinations: list[tuple[Course, Course]] = list(itertools.combinations(politicalCourses, 2))
        return [combination for combination in uncheckedCombinations if any(course.subject != HISTORY for course in combination)]

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
        if not (MIN_GK_COURSES+MIN_PE_COURSES <= GKAmount <= MAX_GK_COURSES+MAX_PE_COURSES):
            logExit(f'You must have between {MIN_GK_COURSES+MIN_PE_COURSES} and {MAX_GK_COURSES+MAX_PE_COURSES} basic courses. Yours: {GKAmount}')
        # self.__finals.LK1 = FinalExam(LKs[0], FinalExamType.LK1) # What is this?
        # self.__finals.LK2 = FinalExam(LKs[1], FinalExamType.LK1)
        return True