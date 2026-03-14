from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from classes import Calculator, Course, CreditedCombination, FinalExam, FinalExams, SaveState
from customTypes import CourseType, FifthPKType, FinalExamType, Points, UNKNOWN
import subjects
from subjects import Subject


class SessionModel:
    def __init__(
        self,
        save_state: SaveState | None = None,
        data_dir: Path | None = None,
        active_profile: int = 1,
    ) -> None:
        self._save_state = save_state if save_state is not None else SaveState()
        self._data_dir = data_dir if data_dir is not None else Path(".abicalc")
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._active_profile = max(1, min(3, int(active_profile)))
        self._cached_lk_subject_pool: list[Subject] | None = None
        self._cached_course_subject_pool: list[Subject] | None = None

    @property
    def save_state(self) -> SaveState:
        return self._save_state

    def get_q(self, semester: int) -> list[Course]:
        return self._save_state.getQ(semester)

    def get_lk(self, n: int) -> Subject:
        lk_index = 1 if n == 1 else 2
        return self._save_state.getLK(lk_index)

    def get_lk_subject_pool(self) -> list[Subject]:
        if self._cached_lk_subject_pool is not None:
            return self._cached_lk_subject_pool

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

        self._cached_lk_subject_pool = sorted(by_name.values(), key=lambda s: s.name)
        return self._cached_lk_subject_pool

    def get_course_subject_pool(self) -> list[Subject]:
        if self._cached_course_subject_pool is not None:
            return self._cached_course_subject_pool

        all_subjects: list[Subject] = []
        for value in vars(subjects).values():
            if isinstance(value, Subject):
                all_subjects.append(value)

        blocked_names = {
            subjects.SUB.name,
            subjects.ENGLISH_Z.name,
        }

        by_name: dict[str, Subject] = {}
        for item in all_subjects:
            if item.name not in blocked_names:
                by_name[item.name] = item

        self._cached_course_subject_pool = sorted(by_name.values(), key=lambda s: s.name)
        return self._cached_course_subject_pool

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

    def add_course(self, semester: int, subject: Subject, reference_index: int | None = None) -> int:
        sem = max(1, min(4, int(semester)))
        courses = self.get_q(sem)
        new_grade = Points(10) if sem in (1, 2) else UNKNOWN

        if courses:
            ref_idx = 0 if reference_index is None else max(0, min(len(courses) - 1, int(reference_index)))
            ref_course = courses[ref_idx]
            new_course = Course(subject, new_grade, ref_course.type, sem)
        else:
            new_course = Course(subject, new_grade, CourseType.GK, sem)

        courses.append(new_course)
        return len(courses) - 1

    def delete_course(self, semester: int, index: int) -> bool:
        sem = max(1, min(4, int(semester)))
        courses = self.get_q(sem)
        if index < 0 or index >= len(courses):
            return False

        courses.pop(index)
        return True

    def calculate_best_combinations(self, amount: int) -> list[CreditedCombination]:
        calculator = Calculator(self.get_all_courses(), self.get_finals())
        return calculator.returnBestCombinations(amount)

    @property
    def active_profile(self) -> int:
        return self._active_profile

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    def reset_for_profile(self, profile: int) -> None:
        self._save_state = SaveState()
        self._active_profile = max(1, min(3, int(profile)))

    def _profile_path(self, profile: int) -> Path:
        slot = max(1, min(3, int(profile)))
        return self._data_dir / f"profile_{slot}.json"

    def _subjects_by_name(self) -> dict[str, Subject]:
        lookup: dict[str, Subject] = {}
        for value in vars(subjects).values():
            if isinstance(value, Subject):
                lookup[value.name] = value
        return lookup

    def _serialize_points(self, points: Points | int | float) -> dict[str, float]:
        if isinstance(points, Points):
            value = float(points.value)
            possible_increase = float(points.possibleIncrease)
        else:
            value = float(points)
            possible_increase = 0.0

        return {
            "value": value,
            "possible_increase": possible_increase,
        }

    def _deserialize_points(self, raw: object) -> Points:
        if not isinstance(raw, dict):
            return UNKNOWN

        typed_raw = cast(dict[str, object], raw)
        try:
            value = float(typed_raw.get("value", 0.0))
            possible_increase = float(typed_raw.get("possible_increase", 15.0))
        except (TypeError, ValueError):
            return UNKNOWN

        return Points(value, possible_increase)

    def _serialize_course(self, course: Course) -> dict[str, object]:
        return {
            "subject": course.subject.name,
            "type": course.type.name,
            "semester": int(course.semester),
            "grade": self._serialize_points(course.grade),
        }

    def _deserialize_course(self, raw: object, semester: int, subject_map: dict[str, Subject]) -> Course | None:
        if not isinstance(raw, dict):
            return None

        typed_raw = cast(dict[str, object], raw)
        subject_name = str(typed_raw.get("subject", ""))
        subject = subject_map.get(subject_name)
        if subject is None:
            return None

        course_type_name = str(typed_raw.get("type", "GK"))
        try:
            course_type = CourseType[course_type_name]
        except KeyError:
            course_type = CourseType.GK

        grade = self._deserialize_points(typed_raw.get("grade"))

        try:
            sem = int(typed_raw.get("semester", semester))
        except (TypeError, ValueError):
            sem = semester

        if sem not in (1, 2, 3, 4):
            sem = semester

        return Course(subject, grade, course_type, sem)

    def _serialize_final_exam(self, exam: FinalExam) -> dict[str, object]:
        return {
            "subject": exam.subject.name,
            "type": exam.type.name,
            "grade": self._serialize_points(exam.grade),
        }

    def _deserialize_final_exam(
        self,
        raw: object,
        expected_type: FinalExamType,
        fallback_subject: Subject,
        subject_map: dict[str, Subject],
    ) -> FinalExam:
        if not isinstance(raw, dict):
            return FinalExam(fallback_subject, expected_type, UNKNOWN)

        typed_raw = cast(dict[str, object], raw)
        subject_name = str(typed_raw.get("subject", fallback_subject.name))
        subject = subject_map.get(subject_name, fallback_subject)
        grade = self._deserialize_points(typed_raw.get("grade"))
        return FinalExam(subject, expected_type, grade)

    def save_profile(self, profile: int | None = None) -> Path:
        slot = self._active_profile if profile is None else max(1, min(3, int(profile)))
        self._active_profile = slot

        payload = {
            "profile": slot,
            "lk": {
                "lk1": self.get_lk(1).name,
                "lk2": self.get_lk(2).name,
            },
            "courses": {
                "q1": [self._serialize_course(c) for c in self.get_q(1)],
                "q2": [self._serialize_course(c) for c in self.get_q(2)],
                "q3": [self._serialize_course(c) for c in self.get_q(3)],
                "q4": [self._serialize_course(c) for c in self.get_q(4)],
            },
            "finals": {
                "lk1": self._serialize_final_exam(self.get_finals().LK1),
                "lk2": self._serialize_final_exam(self.get_finals().LK2),
                "written": self._serialize_final_exam(self.get_finals().written),
                "orally": self._serialize_final_exam(self.get_finals().orally),
                "fifth": self._serialize_final_exam(self.get_finals().fifth),
                "fifth_pk_type": FifthPKType.PP.name,
            },
        }

        path = self._profile_path(slot)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load_profile(self, profile: int | None = None) -> bool:
        slot = self._active_profile if profile is None else max(1, min(3, int(profile)))
        path = self._profile_path(slot)
        if not path.exists():
            self._active_profile = slot
            return False

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return False
            typed_raw = cast(dict[str, object], raw)
        except (OSError, json.JSONDecodeError):
            return False

        subject_map = self._subjects_by_name()
        new_state = SaveState()

        lk_raw = typed_raw.get("lk")
        if isinstance(lk_raw, dict):
            typed_lk = cast(dict[str, object], lk_raw)
            lk1 = subject_map.get(str(typed_lk.get("lk1", "")))
            lk2 = subject_map.get(str(typed_lk.get("lk2", "")))
            if lk1 is not None:
                new_state.setLK(1, lk1)
            if lk2 is not None and lk2 != new_state.getLK(1):
                new_state.setLK(2, lk2)

        finals_raw = typed_raw.get("finals")
        if isinstance(finals_raw, dict):
            typed_finals = cast(dict[str, object], finals_raw)
            new_state.finals = FinalExams(
                self._deserialize_final_exam(
                    typed_finals.get("lk1"),
                    FinalExamType.LK1,
                    new_state.getLK(1),
                    subject_map,
                ),
                self._deserialize_final_exam(
                    typed_finals.get("lk2"),
                    FinalExamType.LK2,
                    new_state.getLK(2),
                    subject_map,
                ),
                self._deserialize_final_exam(
                    typed_finals.get("written"),
                    FinalExamType.WRITTEN,
                    new_state.getFinals().written.subject,
                    subject_map,
                ),
                self._deserialize_final_exam(
                    typed_finals.get("orally"),
                    FinalExamType.ORALLY,
                    new_state.getFinals().orally.subject,
                    subject_map,
                ),
                self._deserialize_final_exam(
                    typed_finals.get("fifth"),
                    FinalExamType.PRESENTATION,
                    new_state.getFinals().fifth.subject,
                    subject_map,
                ),
                FifthPKType.PP,
            )

        courses_raw = typed_raw.get("courses")
        if isinstance(courses_raw, dict):
            typed_courses = cast(dict[str, object], courses_raw)
            for semester, key in ((1, "q1"), (2, "q2"), (3, "q3"), (4, "q4")):
                semester_courses_raw = typed_courses.get(key)
                parsed_courses: list[Course] = []
                if isinstance(semester_courses_raw, list):
                    for item in semester_courses_raw:
                        parsed = self._deserialize_course(item, semester, subject_map)
                        if parsed is not None:
                            parsed_courses.append(parsed)

                if parsed_courses:
                    if semester == 1:
                        new_state.Q1 = parsed_courses
                    elif semester == 2:
                        new_state.Q2 = parsed_courses
                    elif semester == 3:
                        new_state.Q3 = parsed_courses
                    else:
                        new_state.Q4 = parsed_courses

        self._save_state = new_state
        self._active_profile = slot
        return True
