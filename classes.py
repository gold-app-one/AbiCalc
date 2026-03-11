from typing import Callable, Iterable, List, Literal, Tuple
from constants import (FINAL_EXAM_FACTOR, GK_FACTOR, LK_FACTOR, MAX_GK_COURSES, MAX_LK_COURSES,
    MAX_PE_COURSES, MIN_GK_COURSES, MIN_LK_COURSES, MIN_PASSED_GK, MIN_PASSED_GRADE, MIN_PASSED_LK,
    MIN_PE_COURSES, MUST_BRING_IN_SCIENCE_COURSES, MUST_BRING_IN_SPORT_COURSES,
    MUST_BRING_POLITICS_OR_POLITICAL, NON_ELIGIBLE_GRADE, OVERALL_MAX_GRADE, OVERALL_MIN_GRADE,
    OVERALL_MIN_GRADE_FINAL_EXAMS, OVERALL_MIN_GRADE_LK, MustBringInCourses)
from customTypes import UNKNOWN, CourseType, FifthPKType, FinalExamType, LogType, Points, Semester, SubjectCategory
from logHelper import logExit, log
from subjects import ARTS, BIOLOGY, CHEMISTRY, DS, ENGLISH, FRENCH, GEOGRAPHY, HISTORY, LATIN, MATHEMATICS, MUSIC, PHILOSOPHY, PHYSICAL_EDUCATION, PHYSICS, POLITICS, SPANISH, Subject, GERMAN
import itertools
import sys
import heapq

from subjects import *
from customTypes import CourseType, FifthPKType, FinalExamType, UNKNOWN


if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') # type: ignore

class FinalExam:
    """
    Vor.: -
    Eff.: Ein Objekt der Klasse FinalExam wird im RAM initialisiert.
    Erg.: Ein Objekt mit den lokalen Variablen subject, grade und type wird initialisiert.
    """
    def __init__(self, subject: Subject, type: FinalExamType, grade: Points | int) -> None:
        self.subject: Subject = subject
        self.grade: Points | int = grade
        self.type: FinalExamType = type
        self.prediction: Points | int | None = self.grade if self.grade != UNKNOWN else None
    def getPredictedGrade(self, courses: list["Course"]) -> Points | int:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Gibt die voraussichtliche Note als Points-Objekt oder int zurück. Wenn bereits eine Note vorhanden ist, wird diese als Points-Objekt oder int zurückgegeben.
        """
        if self.prediction is not None:
            return self.prediction
        return self.predictGrade(courses)
    def predictGrade(self, courses: list["Course"]) -> Points:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Berechnet die voraussichtliche Note als Points-Objekt basierend auf den Noten der Kurse im selben Fach. Wenn keine Noten für das Fach vorhanden sind, wird UNKNOWN zurückgegeben.
        """
        sameSubjectCourses: list[Course] = [c for c in courses if c.subject == self.subject and c.grade != UNKNOWN]
        if not sameSubjectCourses:
            return UNKNOWN
        totalPoints: Points = Points(0)
        for course in sameSubjectCourses:
            totalPoints += course.grade
        averagePoints: Points = totalPoints * (1 / len(sameSubjectCourses))
        self.prediction = averagePoints
        return self.prediction
    def stringify(self, courses: list["Course"]) -> str:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Gibt einen String zurück, der die Prüfungsart, die vorhergesagte Note und das Fach enthält.
        """
        return f'Prüfungsfach {self.type.name}: {self.getPredictedGrade(courses)}-{self.subject}'

class FinalExams:
    """
    Vor.: -
    Eff.: Ein Objekt der Klasse FinalExams wird im RAM initialisiert.
    Erg.: Ein Objekt mit den lokalen Variablen LK1, LK2, written, orally, fifth und fifthPKType wird initialisiert.
    """
    def __init__(self, LK1: FinalExam, LK2: FinalExam, written: FinalExam, orally: FinalExam, fifth: FinalExam, fifthPKType: FifthPKType) -> None:
        self.LK1: FinalExam = LK1
        self.LK2: FinalExam = LK2
        self.written: FinalExam = written
        self.orally: FinalExam = orally
        self.fifth: FinalExam = fifth

    def checkMinRequirements(self) -> bool:
        """
        Vor.: -
        Eff.: -
        Erg.: Überprüft, ob die Mindestanforderungen für das Bestehen der Abiturprüfungen erfüllt sind. Gibt True zurück, wenn alle Anforderungen erfüllt sind, andernfalls False.
        """
        pruefungsfaecher = [self.LK1, self.LK2, self.written, self.orally]
        passed_flags = [e.grade >= MIN_PASSED_GRADE for e in pruefungsfaecher]
        has_two_pruef = sum(passed_flags) >= 2
        has_LK_among_passed = (self.LK1.grade >= MIN_PASSED_GRADE) or (self.LK2.grade >= MIN_PASSED_GRADE)


        has_written_5 = any(e.grade >= MIN_PASSED_GRADE for e in (self.LK1, self.LK2, self.written))

        exams = [self.LK1, self.LK2, self.written, self.orally, self.fifth]
        total_exam_points: Points | int = sum((e.grade for e in exams), Points(0)) * FINAL_EXAM_FACTOR
        passed_total = total_exam_points >= OVERALL_MIN_GRADE_FINAL_EXAMS

        return has_two_pruef and has_LK_among_passed and has_written_5 and passed_total

class Course:
    """
    Vor.: -
    Eff.: Ein Objekt der Klasse Course wird im RAM initialisiert.
    Erg.: Ein Objekt mit den lokalen Variablen subject, grade, type, semester und prediction wird initialisiert. "prediction" ist entweder die tatsächliche Note oder die vorhergesagte Note, falls die tatsächliche Note UNKNOWN ist.
    """
    def __init__(self, subject: Subject, grade: Points | int | float, type: CourseType, semester: Semester) -> None:
        self.subject: Subject = subject
        self.type: CourseType = type
        self.grade: Points = grade if isinstance(grade, Points) else Points(grade)
        self.semester: Semester = semester
        self.prediction: Points | None = self.grade if self.grade != UNKNOWN else None
    def getPredictedGrade(self, courses: list["Course"]) -> Points:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Gibt die voraussichtliche Note als Points-Objekt zurück. Wenn bereits eine Note vorhanden ist, wird diese als Points-Objekt zurückgegeben. Ansonsten wird die Note basierend auf den Noten der Kurse im selben Fach vorhergesagt. Wenn keine Noten für das Fach vorhanden sind, wird UNKNOWN zurückgegeben.
        """
        if self.prediction is not None:
            return self.prediction
        return self.predictGrade(courses)
    def predictGrade(self, courses: list["Course"]) -> Points:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Berechnet die voraussichtliche Note als Points-Objekt basierend auf den Noten der Kurse im selben Fach. Wenn keine Noten für das Fach vorhanden sind, wird UNKNOWN zurückgegeben.
        """
        if self.grade != UNKNOWN:
            return self.grade
        sameSubjectCourses: list[Course] = [c for c in courses if c.subject == self.subject and c.grade != UNKNOWN]
        if not sameSubjectCourses:
            return UNKNOWN
        totalPoints: Points = Points(0)
        for course in sameSubjectCourses:
            totalPoints += course.grade
        averagePoints: Points = totalPoints * (1 / len(sameSubjectCourses))
        self.prediction = averagePoints
        return self.prediction
    def stringify(self, courses: list["Course"]) -> str:
        """
        Vor.: "courses" ist eine Liste von Course-Objekten, die die Kurse repräsentieren, die der Schüler besucht hat.
        Eff.: -
        Erg.: Gibt einen String zurück, der die vorhergesagte Note, das Fach und das Semester enthält.
        """
        return f'{self.getPredictedGrade(courses)}-{self.subject}-Q{self.semester}'
    def __str__(self) -> str:
        """
        Vor.: -
        Eff.: -
        Erg.: Gibt einen String zurück, der die tatsächliche Note, das Fach und das Semester enthält. Wenn die tatsächliche Note UNKNOWN ist, wird stattdessen die vorhergesagte Note angezeigt.
        """
        return f'{self.grade}-{self.subject}-Q{self.semester}'
class CreditedCombination:
    """
    Vor.: -
    Eff.: Ein Objekt der Klasse CreditedCombination wird im RAM initialisiert.
    Erg.: Ein Objekt mit den lokalen Variablen __creditedCourses, __finals, __LKs und __courses wird initialisiert. "creditedCourses" sind die Kurse, die für die Berechnung der Abiturnote berücksichtigt werden. "finals" enthält die Informationen über die Abiturprüfungen.
    """
    def __init__(self, creditedCourses: Tuple[Course, ...], finals: FinalExams, allCourses: list[Course]) -> None:
        self.__creditedCourses = creditedCourses
        self.__finals = finals
        self.__LKs: Tuple[Subject, Subject] = (self.__finals.LK1.subject, self.__finals.LK2.subject)
        self.__courses = allCourses

    def getScore(self) -> Tuple[Points, Points]:
        """
        Vor.: -
        Eff.: -
        Erg.: Berechnet die aktuelle Punktzahl und die voraussichtliche Punktzahl basierend auf den Kursen in "creditedCourses" und den Abiturprüfungen in "finals". Gibt ein Tupel zurück, wobei das erste Element die aktuelle Punktzahl und das zweite Element die voraussichtliche Punktzahl ist.
        """
        totalPoints: Points = Points(0)
        predictedPoints: Points = Points(0)
        for course in self.__creditedCourses:
            coursePredictedGrade: Points = course.getPredictedGrade(self.__courses)
            coursePoints: Points = coursePredictedGrade * (LK_FACTOR if course.subject in self.__LKs else GK_FACTOR)
            predictedPoints += coursePoints
            totalPoints += course.grade * (LK_FACTOR if course.subject in self.__LKs else GK_FACTOR)
        for exam in (self.__finals.LK1, self.__finals.LK2, self.__finals.written, self.__finals.orally, self.__finals.fifth):
            examPredictedGrade: Points | int = exam.getPredictedGrade(self.__courses)
            predictedPoints += examPredictedGrade * FINAL_EXAM_FACTOR
            totalPoints += exam.grade * FINAL_EXAM_FACTOR
        return totalPoints, predictedPoints

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
        totalScoreCondition = lambda: self.getScore()[1] >= OVERALL_MIN_GRADE
        finalExamsCondition = self.__finalExamsPassed
        conditions = (
            totalScoreCondition,
            eligibleCondition,
            finalExamsCondition
        )
        return all(condition() for condition in conditions)

    def __str__(self) -> str:
        score: tuple[Points, Points] = self.getScore()
        string: str = f'{"✅" if self.passed() else "❌"} - ({score[1].getNumeric(OVERALL_MAX_GRADE):.2f}){score[1]}{f"[{score[0]}]" if score[0] != score[1] else ""}\n\n📝Prüfungsnoten:\n\n'
        for exam in (self.__finals.LK1, self.__finals.LK2, self.__finals.written, self.__finals.orally, self.__finals.fifth):
            string += f'{exam.stringify(self.__courses)}\n'
        string += '\n📚Kursnoten:\n'
        semester: int = 0
        for course in sorted(self.__creditedCourses, key=lambda c: (c.semester, c.type, c.subject)):
            if semester != course.semester:
                semester = course.semester
                string += f'\n--- Q{semester} ---\n'
            string += (f'({course.stringify(self.__courses)})\n')
        return string + '\n--------------------------------------------------------------------------\n'


C = Course
GK = CourseType.GK
LK = CourseType.LK

class SaveState:
    def __init__(self) -> None:

        self.Lk1: Subject = GERMAN
        self.Lk2: Subject = BIOLOGY

        self.finals: FinalExams = FinalExams(
            FinalExam(self.Lk1, FinalExamType.LK1, UNKNOWN),
            FinalExam(self.Lk2, FinalExamType.LK2, UNKNOWN),
            FinalExam(ENGLISH, FinalExamType.WRITTEN, UNKNOWN),
            FinalExam(HISTORY, FinalExamType.ORALLY, UNKNOWN),
            FinalExam(MATHEMATICS, FinalExamType.PRESENTATION, UNKNOWN),
            FifthPKType.PP
        )

        self.Q1: list[Course] = [
            C(self.Lk1, 10, LK, 1),
            C(self.Lk2, 10, LK, 1),
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

        self.Q2: list[Course] = [
            C(self.Lk1, 10, LK, 2),
            C(self.Lk2, 10, LK, 2),
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

        self.Q3: list[Course] = [
            C(self.Lk1, UNKNOWN, LK, 3),
            C(self.Lk2, UNKNOWN, LK, 3),
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

        self.Q4: list[Course] = [
            C(self.Lk1, UNKNOWN, LK, 4),
            C(self.Lk2, UNKNOWN, LK, 4),
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

    def getLK(self, n: Literal[1, 2]) -> Subject:
        return self.Lk1 if n == 1 else self.Lk2

    def setLK(self, n: Literal[1, 2], subject: Subject) -> None:
        if n == 1:
            self.Lk1 = subject
        else:
            self.Lk2 = subject

    def getQ(self, q: Literal[1, 2, 3, 4]) -> list[Course]:
        match q:
            case 1:
                return self.Q1
            case 2:
                return self.Q2
            case 3:
                return self.Q3
            case 4:
                return self.Q4
            case _:
                pass
        print("q \\in {1, 2, 3, 4} ")
        return self.Q1

    def popFromQ(self, q: Literal[1, 2, 3, 4], i: int) -> bool:
        match q:
            case 1:
                bigQ = self.Q1
            case 2:
                bigQ = self.Q1
            case 3:
                bigQ = self.Q1
            case 4:
                bigQ = self.Q1
            case _:
                return False
        if i >= len(bigQ):
            return False
        bigQ.pop(i)
        return True

    def addToQ(self, q: Literal[1, 2, 3, 4], course: Course) -> None:
        match q:
            case 1:
                self.Q1.append(course)
            case 2:
                self.Q2.append(course)
            case 3:
                self.Q3.append(course)
            case 4:
                self.Q4.append(course)
            case _:
                pass

    def getFinals(self) -> FinalExams:
        return self.finals

    def getFinal(self, f: FinalExamType) -> FinalExam:
        F = FinalExamType
        match f:
            case F.LK1:
                return self.finals.LK1
            case F.LK2:
                return self.finals.LK2
            case F.WRITTEN:
                return self.finals.written
            case F.ORALLY:
                return self.finals.orally
            case _:
                pass
        return self.finals.fifth

    def replaceFinal(self, final: FinalExam) -> None:
        F = FinalExamType
        match final.type:
            case F.LK1:
                self.finals.LK1 = final
            case F.LK2:
                self.finals.LK2 = final
            case F.WRITTEN:
                self.finals.written = final
            case F.ORALLY:
                self.finals.orally = final
            case _:
                self.finals.fifth = final


class Calculator:
    def __init__(self, courses: List[Course], finals: FinalExams) -> None:
        self.__courses: List[Course] = courses
        self.__finals = finals
        self.__lkSubjects: Tuple[Subject, Subject] = (self.__finals.LK1.subject, self.__finals.LK2.subject)
        self.__examPoints: Points = self.__calculateExamPoints()
        self.__coursePointCache: dict[Course, Points] = {
            course: self.__calculateCoursePoints(course) for course in self.__courses
        }
        self.__checkValidity()

    def getBestCombinations(self, amount: int = 5) -> None:
        topIcons: dict[int, str] = {0: '🥇', 1: '🥈', 2: '🥉'}
        combinations = self.returnBestCombinations(amount)
        for i, comb in enumerate(combinations[:amount]):
            print(f'\n==================== #{i + 1} {topIcons.get(i, "")} Combination ====================\n')
            print(comb)

    def returnBestCombinations(self, amount: int = 1) -> list[CreditedCombination]:
        def score_val(c: CreditedCombination) -> float:
            s = c.getScore()
            return s[1].value + s[1].possibleIncrease / 2

        combinations = sorted(
            self.__getCreditedCombinations(amount),
            key=lambda c: (not c.passed(), -score_val(c))
        )
        return combinations

    def __checkValidity(self) -> bool:
        return self.__enoughCoursesOfTypes()

    def __scoreValue(self, points: Points) -> float:
        return points.value + points.possibleIncrease / 2

    def __calculateExamPoints(self) -> Points:
        total = Points(0)
        for exam in (self.__finals.LK1, self.__finals.LK2, self.__finals.written, self.__finals.orally, self.__finals.fifth):
            total += exam.grade * FINAL_EXAM_FACTOR
        return total

    def __calculateCoursePoints(self, course: Course) -> Points:
        factor = LK_FACTOR if course.subject in self.__lkSubjects else GK_FACTOR
        return course.grade * factor

    def __prepareCombinations(
        self,
        combinations: Iterable[tuple[tuple[Course, ...], Points]]
    ) -> List[tuple[tuple[Course, ...], set[Course], Points]]:
        prepared: List[tuple[tuple[Course, ...], set[Course], Points]] = []
        for courses, points in combinations:
            prepared.append((courses, set(courses), points))
        return prepared

    def __enumerateCombinations(
        self,
        courses: List[Course],
        pick: int,
        filter_fn: Callable[[tuple[Course, ...]], bool] | None = None,
    ) -> List[tuple[tuple[Course, ...], Points]]:
        if pick < 0:
            return []
        combinations: List[tuple[tuple[Course, ...], Points]] = []
        for combination in itertools.combinations(courses, pick):
            if filter_fn and not filter_fn(combination):
                continue
            total = Points(0)
            for course in combination:
                total += self.__coursePointCache[course]
            combinations.append((combination, total))
        combinations.sort(key=lambda item: self.__scoreValue(item[1]), reverse=True)
        return combinations

    def __getCreditedCombinations(self, limit: int) -> List[CreditedCombination]:
        M = MustBringInCourses
        germanCourses: List[Course] = [course for course in self.__courses if course.subject == GERMAN]
        foreignLangCourses: List[Course] = [
            course for course in self.__courses if course.subject in (ENGLISH, FRENCH, SPANISH, LATIN)
        ]
        artsCourses: List[Course] = [course for course in self.__courses if course.subject in (ARTS, MUSIC, DS)]
        politicalCourses: List[Course] = [
            course for course in self.__courses if course.subject in (POLITICS, HISTORY, GEOGRAPHY, PHILOSOPHY)
        ]
        mathsCourses: List[Course] = [course for course in self.__courses if course.subject == MATHEMATICS]
        PECourses: List[Course] = [course for course in self.__courses if course.subject == PHYSICAL_EDUCATION]
        historyCourses: List[Course] = [course for course in self.__courses if course.subject == HISTORY]
        scienceCourses: List[Course] = [course for course in self.__courses if course.subject in (PHYSICS, CHEMISTRY, BIOLOGY)]

        print("\n🔍 Starting optimized combination search...")

        germanCombs = self.__prepareCombinations(
            self.__enumerateCombinations(germanCourses, M.German.value)
        )
        foreignLangCombs = self.__prepareCombinations(
            self.__enumerateCombinations(foreignLangCourses, M.ForeignLanguage.value)
        )
        artsCombs = self.__prepareCombinations(
            self.__enumerateCombinations(artsCourses, M.Art.value)
        )
        historyCombs = self.__prepareCombinations(
            self.__enumerateCombinations(historyCourses, M.History.value)
        )
        mathsCombs = self.__prepareCombinations(
            self.__enumerateCombinations(mathsCourses, M.Maths.value)
        )

        hasPEAsFinal = any(
            final.subject == PHYSICAL_EDUCATION
            for final in (
                self.__finals.fifth,
                self.__finals.orally,
                self.__finals.written,
                self.__finals.LK1,
                self.__finals.LK2,
            )
        )
        pe_required = MUST_BRING_IN_SPORT_COURSES(hasPEAsFinal)
        PECombs = self.__prepareCombinations(
            self.__enumerateCombinations(PECourses, pe_required)
        )
        scienceCombs = self.__prepareCombinations(self.__getScienceCourses(scienceCourses))

        political_requirements = MUST_BRING_POLITICS_OR_POLITICAL(self.__finals.fifth.subject)
        political_fixed_cache: dict[int, List[tuple[tuple[Course, ...], set[Course], Points]]] = {}
        for idx, amount in enumerate(political_requirements):
            if idx == 0:
                political_fixed_cache[amount] = self.__prepareCombinations(
                    self.__enumerateCombinations(politicalCourses, amount)
                )

        best_heap: List[tuple[float, int, CreditedCombination]] = []
        counter = itertools.count()
        evaluated_combinations = 0

        def record_combination(courses_tuple: tuple[Course, ...]) -> None:
            nonlocal evaluated_combinations
            if len(courses_tuple) != MIN_GK_COURSES + MIN_LK_COURSES:
                log("Combination failed (couldn't get correct Amount)", LogType.LOG)
                return
            combination = CreditedCombination(creditedCourses=courses_tuple, finals=self.__finals, allCourses=self.__courses)
            evaluated_combinations += 1
            score = combination.getScore()
            score_value = self.__scoreValue(score[1])
            entry = (score_value, next(counter), combination)
            if len(best_heap) < limit:
                heapq.heappush(best_heap, entry)
            else:
                if score_value > best_heap[0][0]:
                    heapq.heapreplace(best_heap, entry)

        for germanCoursesTuple, germanSet, germanPoints in germanCombs:
            for foreignCoursesTuple, foreignSet, foreignPoints in foreignLangCombs:
                if germanSet & foreignSet:
                    continue
                coursesAfterForeign = germanCoursesTuple + foreignCoursesTuple
                setAfterForeign = germanSet | foreignSet
                pointsAfterForeign = germanPoints + foreignPoints
                for artsCoursesTuple, artsSet, artsPoints in artsCombs:
                    if setAfterForeign & artsSet:
                        continue
                    coursesAfterArts = coursesAfterForeign + artsCoursesTuple
                    setAfterArts = setAfterForeign | artsSet
                    pointsAfterArts = pointsAfterForeign + artsPoints
                    for historyCoursesTuple, historySet, historyPoints in historyCombs:
                        if setAfterArts & historySet:
                            continue
                        coursesAfterHistory = coursesAfterArts + historyCoursesTuple
                        setAfterHistory = setAfterArts | historySet
                        pointsAfterHistory = pointsAfterArts + historyPoints
                        for optionIndex, amount in enumerate(political_requirements):
                            if optionIndex == 0:
                                politicalCombs = political_fixed_cache.setdefault(
                                    amount,
                                    self.__prepareCombinations(
                                        self.__enumerateCombinations(politicalCourses, amount)
                                    ),
                                )
                            else:
                                remaining_courses_for_political = [
                                    course for course in self.__courses if course not in historySet
                                ]
                                politicalCombs = self.__prepareCombinations(
                                    self.__getTwoSubjectsCourses(remaining_courses_for_political)
                                )
                            for politicalCoursesTuple, politicalSet, politicalPoints in politicalCombs:
                                if setAfterHistory & politicalSet:
                                    continue
                                coursesAfterPolitical = coursesAfterHistory + politicalCoursesTuple
                                setAfterPolitical = setAfterHistory | politicalSet
                                pointsAfterPolitical = pointsAfterHistory + politicalPoints
                                for mathsCoursesTuple, mathsSet, mathsPoints in mathsCombs:
                                    if setAfterPolitical & mathsSet:
                                        continue
                                    coursesAfterMaths = coursesAfterPolitical + mathsCoursesTuple
                                    setAfterMaths = setAfterPolitical | mathsSet
                                    pointsAfterMaths = pointsAfterPolitical + mathsPoints
                                    for PECoursesTuple, PESet, PEPoints in PECombs:
                                        if setAfterMaths & PESet:
                                            continue
                                        coursesAfterPE = coursesAfterMaths + PECoursesTuple
                                        setAfterPE = setAfterMaths | PESet
                                        pointsAfterPE = pointsAfterMaths + PEPoints
                                        for scienceCoursesTuple, scienceSet, sciencePoints in scienceCombs:
                                            if setAfterPE & scienceSet:
                                                continue
                                            coursesAfterScience = coursesAfterPE + scienceCoursesTuple
                                            setAfterScience = setAfterPE | scienceSet
                                            pointsAfterScience = pointsAfterPE + sciencePoints
                                            remainingAmount = self.__getRemainingCoursesAmount(
                                                list(coursesAfterScience),
                                                self.__lkSubjects,
                                            )
                                            if remainingAmount < 0:
                                                continue
                                            remainingCourses = [
                                                course for course in self.__courses if course not in setAfterScience
                                            ]
                                            remainingGKCourses = [
                                                course for course in remainingCourses if course.subject not in self.__lkSubjects
                                            ]
                                            if remainingAmount == 0:
                                                record_combination(coursesAfterScience)
                                                continue
                                            if len(remainingGKCourses) < remainingAmount:
                                                continue
                                            sortedRemaining = sorted(
                                                remainingGKCourses,
                                                key=lambda course: self.__scoreValue(self.__coursePointCache[course]),
                                                reverse=True,
                                            )
                                            optimisticExtra = self.__sumTopCoursePoints(
                                                sortedRemaining, remainingAmount
                                            )
                                            optimisticTotal = (
                                                pointsAfterScience + optimisticExtra + self.__examPoints
                                            )
                                            threshold = best_heap[0][0] if len(best_heap) >= limit else float('-inf')
                                            if self.__scoreValue(optimisticTotal) <= threshold:
                                                continue
                                            self.__searchExtraCourses(
                                                sortedRemaining,
                                                remainingAmount,
                                                coursesAfterScience,
                                                pointsAfterScience,
                                                record_combination,
                                                best_heap,
                                                limit,
                                            )

        print(f"✅ Search complete! Combinations evaluated: {evaluated_combinations:,}\n")
        sorted_best = sorted(
            best_heap,
            key=lambda entry: (not entry[2].passed(), -self.__scoreValue(entry[2].getScore()[1]))
        )
        return [entry[2] for entry in sorted_best]

    def __sumTopCoursePoints(self, sortedCourses: List[Course], count: int) -> Points:
        total = Points(0)
        for course in sortedCourses[:count]:
            total += self.__coursePointCache[course]
        return total

    def __searchExtraCourses(
        self,
        sortedCourses: List[Course],
        needed: int,
        baseCourses: tuple[Course, ...],
        basePoints: Points,
        record_fn: Callable[[tuple[Course, ...]], None],
        best_heap: List[tuple[float, int, CreditedCombination]],
        limit: int,
    ) -> None:
        if needed <= 0:
            record_fn(baseCourses)
            return

        coursePoints = [self.__coursePointCache[course] for course in sortedCourses]

        def optimistic_suffix(start_idx: int, slots: int) -> Points:
            total = Points(0)
            taken = 0
            for idx in range(start_idx, len(sortedCourses)):
                total += coursePoints[idx]
                taken += 1
                if taken == slots:
                    break
            return total

        def backtrack(start_idx: int, chosen: List[Course], chosen_points: Points) -> None:
            remaining_slots = needed - len(chosen)
            if remaining_slots == 0:
                record_fn(baseCourses + tuple(chosen))
                return
            if start_idx >= len(sortedCourses):
                return

            optimistic_total_points = (
                basePoints + chosen_points + optimistic_suffix(start_idx, remaining_slots) + self.__examPoints
            )
            threshold = best_heap[0][0] if len(best_heap) >= limit else float('-inf')
            if self.__scoreValue(optimistic_total_points) <= threshold:
                return

            max_index = len(sortedCourses) - remaining_slots + 1
            for idx in range(start_idx, max_index):
                course = sortedCourses[idx]
                chosen.append(course)
                new_points = chosen_points + coursePoints[idx]
                backtrack(idx + 1, chosen, new_points)
                chosen.pop()

        backtrack(0, [], Points(0))

    def __getScienceCourses(self, scienceCourses: list[Course]) -> List[Tuple[tuple[Course, ...], Points]]:
        bio_required = MUST_BRING_IN_SCIENCE_COURSES(isBiology=True)
        non_bio_required = MUST_BRING_IN_SCIENCE_COURSES(isBiology=False)

        bio_combinations = self.__enumerateCombinations(
            scienceCourses,
            bio_required,
            lambda comb: sum(course.subject == BIOLOGY for course in comb) == 4,
        )
        non_bio_combinations = self.__enumerateCombinations(
            scienceCourses,
            non_bio_required,
            lambda comb: sum(course.subject == BIOLOGY for course in comb) == 0,
        )

        combined = bio_combinations + non_bio_combinations
        combined.sort(key=lambda item: self.__scoreValue(item[1]), reverse=True)
        return combined

    def __getTwoSubjectsCourses(self, possibleCourses: List[Course]) -> List[Tuple[tuple[Course, ...], Points]]:
        politicalCourses: list[Course] = [
            course for course in possibleCourses if course.subject.category == SubjectCategory.Political
        ]
        uncheckedCombinations: list[tuple[Course, Course]] = list(itertools.combinations(politicalCourses, 2))
        validCombinations = [
            combination
            for combination in uncheckedCombinations
            if any(course.subject != HISTORY for course in combination)
        ]
        results: List[Tuple[tuple[Course, ...], Points]] = []
        for combination in validCombinations:
            total = Points(0)
            for course in combination:
                total += self.__coursePointCache[course]
            results.append((combination, total))
        results.sort(key=lambda item: self.__scoreValue(item[1]), reverse=True)
        return results
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