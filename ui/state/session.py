from __future__ import annotations

from classes import Calculator, Course, CreditedCombination, FinalExams, SaveState
from customTypes import CourseType, Points, UNKNOWN
import subjects
from subjects import Subject


class SessionModel:
    def __init__(self, save_state: SaveState | None = None) -> None:
        self._save_state = save_state if save_state is not None else SaveState()

    @property
    def save_state(self) -> SaveState:
        return self._save_state

    def get_q(self, semester: int) -> list[Course]:
        return self._save_state.getQ(semester)

    def get_lk(self, n: int) -> Subject:
        lk_index = 1 if n == 1 else 2
        return self._save_state.getLK(lk_index)

    def get_lk_subject_pool(self) -> list[Subject]:
        all_subjects: list[Subject] = []
        for value in vars(subjects).values():
            if isinstance(value, Subject):
                all_subjects.append(value)

        blocked_names = {
            subjects.SUB.name,
            subjects.PHYSICAL_EDUCATION.name,
            subjects.ENGLISH_Z.name,
        }

        by_name: dict[str, Subject] = {}
        for item in all_subjects:
            if item.name not in blocked_names:
                by_name[item.name] = item

        return sorted(by_name.values(), key=lambda s: s.name)

    def set_lk(self, n: int, subject: Subject) -> bool:
        lk_index = 1 if n == 1 else 2
        other_index = 2 if lk_index == 1 else 1

        if subject == self._save_state.getLK(other_index):
            return False

        old_subject = self._save_state.getLK(lk_index)
        self._save_state.setLK(lk_index, subject)

        for semester in (1, 2, 3, 4):
            for course in self._save_state.getQ(semester):
                if course.type == CourseType.LK and course.subject == old_subject:
                    course.subject = subject

        finals = self._save_state.getFinals()
        if lk_index == 1:
            finals.LK1.subject = subject
        else:
            finals.LK2.subject = subject

        return True

    def cycle_lk(self, n: int, direction: int) -> bool:
        pool = self.get_lk_subject_pool()
        if not pool:
            return False

        current = self.get_lk(n)
        idx = 0
        for i, candidate in enumerate(pool):
            if candidate == current:
                idx = i
                break

        new_idx = (idx + direction) % len(pool)
        return self.set_lk(n, pool[new_idx])

    def get_finals(self) -> FinalExams:
        return self._save_state.getFinals()

    def get_all_courses(self) -> list[Course]:
        return (
            self._save_state.getQ(1)
            + self._save_state.getQ(2)
            + self._save_state.getQ(3)
            + self._save_state.getQ(4)
        )

    def _set_course_grade(self, semester: int, index: int, points: Points) -> None:
        courses = self.get_q(semester)
        if index < 0 or index >= len(courses):
            return
        course = courses[index]
        course.grade = points
        course.prediction = None if points == UNKNOWN else points

    def adjust_course_grade(self, semester: int, index: int, delta: int) -> None:
        courses = self.get_q(semester)
        if index < 0 or index >= len(courses):
            return

        course = courses[index]
        if course.grade == UNKNOWN:
            base_value = 10
        else:
            base_value = int(course.grade.value)

        new_value = max(0, min(15, base_value + delta))
        self._set_course_grade(semester, index, Points(new_value))

    def toggle_course_unknown(self, semester: int, index: int) -> None:
        courses = self.get_q(semester)
        if index < 0 or index >= len(courses):
            return

        current = courses[index].grade
        if current == UNKNOWN:
            self._set_course_grade(semester, index, Points(10))
        else:
            self._set_course_grade(semester, index, UNKNOWN)

    def calculate_best_combinations(self, amount: int) -> list[CreditedCombination]:
        calculator = Calculator(self.get_all_courses(), self.get_finals())
        return calculator.returnBestCombinations(amount)
