from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from classes import Calculator, Course, CreditedCombination, FinalExam, FinalExams, SaveState
from customTypes import CourseType, FifthPKType, FinalExamType, Points, UNKNOWN
import subjects
from subjects import Subject


class SessionModel:
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse SessionModel im RAM
    Erg.: -
    """
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
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, die das aktuelle Semester repräsentiert
        Eff.: -
        Erg.: eine Liste von Course-Objekten, die die Kurse und deren Noten für das angegebene Semester repräsentieren
        """
        return self._save_state.getQ(semester)

    def get_lk(self, n: int) -> Subject:
        """
        Vor.: n ist entweder 1 oder 2 und repräsentiert die Nummer des Leistung
        Eff.: -
        Erg.: das Subject-Objekt, das den Leistungskurs repräsentiert, der mit der Nummer n verknüpft ist
        """
        lk_index = 1 if n == 1 else 2
        return self._save_state.getLK(lk_index)

    def get_lk_subject_pool(self) -> list[Subject]:
        """
        Vor.: -
        Eff.: -
        Erg.: eine Liste von Subject-Objekten, die die verfügbaren Fächer repräsentieren, die als Leistungskurse gewählt werden können. Diese Liste wird aus den definierten Subject-Objekten generiert, wobei bestimmte Fächer ausgeschlossen werden, und ist alphabetisch nach dem Namen der Fächer sortiert
        """
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
        """
        Vor.: -
        Eff.: -
        Erg.: eine Liste von Subject-Objekten, die die verfügbaren Fächer repräsentieren, die als Grundkurse gewählt werden können. Diese Liste wird aus den definierten Subject-Objekten generiert, wobei bestimmte Fächer ausgeschlossen werden, und ist alphabetisch nach dem Namen der Fächer sortiert
        """
        if self._cached_course_subject_pool is not None:
            return self._cached_course_subject_pool

        all_subjects: list[Subject] = []
        for value in vars(subjects).values():
            if isinstance(value, Subject):
                all_subjects.append(value)

        blocked_names = {
        }

        by_name: dict[str, Subject] = {}
        for item in all_subjects:
            if item.name not in blocked_names:
                by_name[item.name] = item

        self._cached_course_subject_pool = sorted(by_name.values(), key=lambda s: s.name)
        return self._cached_course_subject_pool

    def set_lk(self, n: int, subject: Subject) -> bool:
        """
        Vor.: n ist entweder 1 oder 2 und repräsentiert die Nummer des Leistungskurses, subject ist ein Subject-Objekt, das den neuen Leistungskurs repräsentiert
        Eff.: -
        Erg.: True, wenn der Leistungskurs erfolgreich geändert wurde, False wenn der neue Leistungskurs bereits als Leistungskurs gewählt ist
        """
        lk_index = 1 if n == 1 else 2
        other_index = 2 if lk_index == 1 else 1

        if subject == self._save_state.getLK(other_index):
            return False

        self._save_state.setLK(lk_index, subject)

        # LK/GK types are derived from the two configured LK subjects.
        # If LK1/LK2 change, all existing courses must be reclassified.
        self._sync_course_types_with_lks()

        finals = self._save_state.getFinals()
        if lk_index == 1:
            finals.LK1.subject = subject
        else:
            finals.LK2.subject = subject

        return True

    def _course_type_for_subject(self, subject: Subject) -> CourseType:
        lk1 = self._save_state.getLK(1)
        lk2 = self._save_state.getLK(2)
        return CourseType.LK if subject == lk1 or subject == lk2 else CourseType.GK

    def _sync_course_types_with_lks(self) -> None:
        for semester in (1, 2, 3, 4):
            for course in self._save_state.getQ(semester):
                target_type = self._course_type_for_subject(course.subject)
                if course.type != target_type:
                    course.type = target_type

    def cycle_lk(self, n: int, direction: int) -> bool:
        """
        Vor.: n ist entweder 1 oder 2 und repräsentiert die Nummer des Leistung
        Eff.: direction ist entweder 1 oder -1 und repräsentiert die Richtung, in die der Leistungskurs gewechselt werden soll (1 für vorwärts, -1 für rückwärts)
        Erg.: True, wenn der Leistungskurs erfolgreich geändert wurde, False wenn es keinen anderen Leistungskurs gibt, zu dem gewechselt werden könnte (z.B. wenn nur ein Leistungskurs verfügbar ist oder wenn der einzige andere Leistungskurs bereits als Leistungskurs gewählt ist)
        """
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
        """
        Vor.: -
        Eff.: -
        Erg.: ein FinalExams-Objekt, das die Informationen über die fünf Prüfungsfächer und deren Noten repräsentiert
        """
        return self._save_state.getFinals()

    def get_all_courses(self) -> list[Course]:
        """
        Vor.: -
        Eff.: -
        Erg.: eine Liste von Course-Objekten, die alle Kurse und deren Noten repräsentieren, die in den vier Semestern belegt wurden
        """
        return (
            self._save_state.getQ(1)
            + self._save_state.getQ(2)
            + self._save_state.getQ(3)
            + self._save_state.getQ(4)
        )

    def _set_course_grade(self, semester: int, index: int, points: Points) -> None:
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, index ist eine gültige Zahl, die einen Kurs im angegebenen Semester repräsentiert, points ist ein Points-Objekt, das die neue Note repräsentiert
        Eff.: -
        Erg.: aktualisiert die Note des Kurses, der durch semester und index repräsentiert wird, auf die neuen Punkte. Wenn points gleich UNKNOWN ist, wird die Note auf unbekannt gesetzt, andernfalls wird die Note auf die angegebenen Punkte gesetzt
        """
        courses = self.get_q(semester)
        if index < 0 or index >= len(courses):
            return
        course = courses[index]
        course.grade = points
        course.prediction = None if points == UNKNOWN else points

    def adjust_course_grade(self, semester: int, index: int, delta: int) -> None:
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, index ist eine gültige Zahl, die einen Kurs im angegebenen Semester repräsentiert, delta ist eine Zahl zwischen -15 und 15, die angibt, um wie viele Punkte die Note des Kurses angepasst werden soll (positive Werte erhöhen die Note, negative Werte verringern die Note)
        Eff.: -
        Erg.: aktualisiert die Note des Kurses, der durch semester und index repräsentiert wird, um die angegebene Anzahl von Punkten. Wenn die aktuelle Note unbekannt ist, wird sie auf 10 gesetzt, bevor die Anpassung vorgenommen wird. Die neue Note wird auf mindestens 0 und höchstens 15 begrenzt
        """
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
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, index ist eine gültige Zahl, die einen Kurs im angegebenen Semester repräsentiert
        Eff.: -
        Erg.: wenn die Note des Kurses, der durch semester und index repräsentiert wird, unbekannt ist, wird sie auf 10 gesetzt, andernfalls wird sie auf unbekannt gesetzt
        """
        courses = self.get_q(semester)
        if index < 0 or index >= len(courses):
            return

        current = courses[index].grade
        if current == UNKNOWN:
            self._set_course_grade(semester, index, Points(10))
        else:
            self._set_course_grade(semester, index, UNKNOWN)

    def add_course(self, semester: int, subject: Subject, reference_index: int | None = None) -> int:
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, subject ist ein Subject-Objekt, das das Fach des neuen Kurses repräsentiert, reference_index ist eine optionale Zahl, die einen Kurs im angegebenen Semester repräsentiert und als Referenz für die Art des neuen Kurses verwendet wird (wenn reference_index None ist, wird der neue Kurs als Grundkurs hinzugefügt, andernfalls wird der neue Kurs als derselbe Kurstyp wie der Referenzkurs hinzugefügt)
        Eff.: -
        Erg.: die Position des neu hinzugefügten Kurses in der Liste der Kurse des angegebenen Semesters. Der neue Kurs wird mit unbekannter Note und demselben Kurstyp wie der Referenzkurs (oder als Grundkurs, wenn keine Referenz angegeben ist) hinzugefügt
        """
        sem = max(1, min(4, int(semester)))
        courses = self.get_q(sem)
        new_grade = Points(10) if sem in (1, 2) else UNKNOWN
        new_type = self._course_type_for_subject(subject)

        if courses:
            new_course = Course(subject, new_grade, new_type, sem)
        else:
            new_course = Course(subject, new_grade, new_type, sem)

        courses.append(new_course)
        return len(courses) - 1

    def delete_course(self, semester: int, index: int) -> bool:
        """
        Vor.: semester ist eine gültige Zahl zwischen 1 und 4, index ist eine gültige Zahl, die einen Kurs im angegebenen Semester repräsentiert
        Eff.: -
        Erg.: True, wenn der Kurs erfolgreich gelöscht wurde, False wenn index keine gültige Position in der Liste der Kurse des angegebenen Semesters repräsentiert. Der Kurs, der durch semester und index repräsentiert wird, wird aus der Liste der Kurse des angegebenen Semesters gelöscht
        """
        sem = max(1, min(4, int(semester)))
        courses = self.get_q(sem)
        if index < 0 or index >= len(courses):
            return False

        courses.pop(index)
        return True

    def calculate_best_combinations(self, amount: int) -> list[CreditedCombination]:
        """
        Vor.: amount ist eine Zahl zwischen 1 und 10, die angibt, wie viele der besten Kombinationen von Kursen und Prüfungsfächern zurückgegeben werden sollen
        Eff.: -
        Erg.: eine Liste von CreditedCombination-Objekten, die die besten Kombinationen von Kursen und Prüfungsfächern repräsentieren, basierend auf den aktuellen Kursen und Prüfungsfächern, die in der Session gespeichert sind. Die Anzahl der zurückgegebenen Kombinationen entspricht dem angegebenen amount, wobei die Kombinationen nach ihrer Gesamtpunktzahl sortiert sind (die Kombination mit der höchsten Punktzahl steht an erster Stelle) und nur Kombinationen zurückgegeben werden, die eine gültige Zusammenstellung von Kursen und Prüfungsfächern darstellen
        """
        calculator = Calculator(self.get_all_courses(), self.get_finals())
        return calculator.returnBestCombinations(amount)

    @property
    def active_profile(self) -> int:
        """
        Vor.: -
        Eff.: -
        Erg.: die Nummer des aktuell aktiven Profils als Integer
        """
        return self._active_profile

    @property
    def data_dir(self) -> Path:
        """
        Vor.: -
        Eff.: -
        Erg.: der Pfad, der als Speicherort für die Konfigurationsdateien und Profildaten der Anwendung verwendet wird. Bevorzugt wird der APPDATA-Ordner unter Windows, andernfalls wird ein verstecktes Verzeichnis im Installationsverzeichnis der Anwendung verwendet
        """
        return self._data_dir

    def reset_for_profile(self, profile: int) -> None:
        """
        Vor.: profile ist die Nummer eines Profils als Integer
        Eff.: -
        Erg.: setzt den Zustand der Session zurück, um die Daten des angegebenen Profils zu laden. Wenn das Profil erfolgreich geladen wird, werden die Daten des Profils in den Zustand der Session übernommen, andernfalls wird der Zustand der Session auf die Standardeinstellungen zurückgesetzt. Die Nummer des aktiven Profils wird auf die angegebene Nummer aktualisiert
        """
        self._save_state = SaveState()
        self._active_profile = max(1, min(3, int(profile)))

    def _profile_path(self, profile: int) -> Path:
        """
        Vor.: profile ist die Nummer eines Profils als Integer
        Eff.: -
        Erg.: der Pfad, unter dem die Profildaten des angegebenen Profils gespeichert werden. Die Nummer des Profils wird auf eine gültige Zahl zwischen 1 und 3 begrenzt, um sicherzustellen, dass die Profildaten in einem der drei vorgesehenen Slots gespeichert werden
        """
        slot = max(1, min(3, int(profile)))
        return self._data_dir / f"profile_{slot}.json"

    def _subjects_by_name(self) -> dict[str, Subject]:
        """
        Vor.: -
        Eff.: -
        Erg.: ein Dictionary, das die verfügbaren Subject-Objekte nach ihrem Namen indiziert. Die Schlüssel des Dictionaries sind die Namen der Fächer als Strings, und die Werte sind die entsprechenden Subject-Objekte. Dieses Dictionary wird aus den definierten Subject-Objekten generiert, um eine schnelle Suche nach Subject-Objekten basierend auf ihrem Namen zu ermöglichen
        """
        lookup: dict[str, Subject] = {}
        for value in vars(subjects).values():
            if isinstance(value, Subject):
                lookup[value.name] = value
        return lookup

    def _serialize_points(self, points: Points | int | float) -> dict[str, float]:
        """
        Vor.: points ist entweder ein Points-Objekt oder eine Zahl als Integer oder Float, die die Note repräsentiert
        Eff.: -
        Erg.: ein Dictionary mit zwei Schlüsseln: "value", der den Wert der Punkte als Float repräsentiert, und "possible_increase", der die mögliche Erhöhung der Punkte als Float repräsentiert. Wenn points ein Points-Objekt ist, werden die entsprechenden Werte aus dem Objekt extrahiert, andernfalls wird der Wert auf die angegebene Zahl gesetzt und die mögliche Erhöhung auf 0 gesetzt
        """
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
        """
        Vor.: raw ist ein Objekt, das die Punkte repräsentiert, entweder als Dictionary mit den Schlüsseln "value" und "possible_increase" oder als andere Form, die nicht den erwarteten Format entspricht
        Eff.: -
        Erg.: ein Points-Objekt, das die Punkte repräsentiert, basierend auf den Informationen im raw-Objekt. Wenn raw ein gültiges Dictionary mit den erwarteten Schlüsseln und entsprechenden Werten ist, werden diese Werte verwendet, um ein Points-Objekt zu erstellen. Wenn raw nicht den erwarteten Format entspricht oder ungültige Werte enthält, wird das UNKNOWN-Objekt zurückgegeben, um anzuzeigen, dass die Punkte unbekannt sind
        """
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
        """
        Vor.: course ist ein Course-Objekt, das die Informationen über einen Kurs repräsentiert
        Eff.: -
        Erg.: ein Dictionary mit den Schlüsseln "subject", "type", "semester" und "grade", die die entsprechenden Informationen über den Kurs repräsentieren. "subject" ist der Name des Fachs als String, "type" ist der Name des Kurstyps als String, "semester" ist die Nummer des Semesters als Integer, und "grade" ist ein Dictionary, das die Punkte des Kurses repräsentiert, wie sie von der _serialize_points-Methode zurückgegeben werden
        """
        return {
            "subject": course.subject.name,
            "type": course.type.name,
            "semester": int(course.semester),
            "grade": self._serialize_points(course.grade),
        }

    def _deserialize_course(self, raw: object, semester: int, subject_map: dict[str, Subject]) -> Course | None:
        """
        Vor.: raw ist ein Objekt, das die Informationen über einen Kurs repräsentiert, semester ist die Nummer des Semesters als Integer, subject_map ist ein Dictionary, das die verfügbaren Subject-Objekte nach ihrem Namen indiziert
        Eff.: -
        Erg.: ein Course-Objekt, das die Informationen über einen Kurs repräsentiert, basierend auf den Informationen im raw-Objekt. Wenn raw ein gültiges Dictionary mit den erwarteten Schlüsseln und entsprechenden Werten ist, werden diese Werte verwendet, um ein Course-Objekt zu erstellen. Wenn raw nicht den erwarteten Format entspricht oder ungültige Werte enthält (z.B. wenn das Fach nicht in subject_map gefunden wird), wird None zurückgegeben, um anzuzeigen, dass der Kurs nicht erfolgreich deserialisiert werden konnte
        """
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
        """
        Vor.: exam ist ein FinalExam-Objekt, das die Informationen über eine Abschlussprüfung
        Eff.: -
        Erg.: ein Dictionary mit den Schlüsseln "subject", "type" und "grade", die die entsprechenden Informationen über die Abschlussprüfung repräsentieren. "subject" ist der Name des Fachs als String, "type" ist der Name des Prüfungstyps als String, und "grade" ist ein Dictionary, das die Punkte der Abschlussprüfung repräsentiert, wie sie von der _serialize_points-Methode zurückgegeben werden
        """
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
        """
        Vor.: raw ist ein Objekt, das die Informationen über eine Abschlussprüfung repräsentiert, expected_type ist der erwartete Typ der Abschlussprüfung als FinalExamType, fallback_subject ist ein Subject-Objekt, das als Fallback verwendet wird, wenn das Fach in raw nicht gefunden wird oder raw nicht den erwarteten Format entspricht, subject_map ist ein Dictionary, das die verfügbaren Subject-Objekte nach ihrem Namen indiziert
        Eff.: -
        Erg.: ein FinalExam-Objekt, das die Informationen über eine Abschlussprüfung repräsentiert, basierend auf den Informationen im raw-Objekt. Wenn raw ein gültiges Dictionary mit den erwarteten Schlüsseln und entsprechenden Werten ist, werden diese Werte verwendet, um ein FinalExam-Objekt zu erstellen. Wenn raw nicht den erwarteten Format entspricht oder ungültige Werte enthält (z.B. wenn das Fach nicht in subject_map gefunden wird), wird ein FinalExam-Objekt mit dem fallback_subject und UNKNOWN als Note zurückgegeben, um anzuzeigen, dass die Abschlussprüfung nicht erfolgreich deserialisiert werden konnte
        """
        if not isinstance(raw, dict):
            return FinalExam(fallback_subject, expected_type, UNKNOWN)

        typed_raw = cast(dict[str, object], raw)
        subject_name = str(typed_raw.get("subject", fallback_subject.name))
        subject = subject_map.get(subject_name, fallback_subject)
        grade = self._deserialize_points(typed_raw.get("grade"))
        return FinalExam(subject, expected_type, grade)

    def save_profile(self, profile: int | None = None) -> Path:
        """
        Vor.: profile ist die Nummer eines Profils als Integer oder None, wenn das aktuell aktive Profil gespeichert
        Eff.: -
        Erg.: der Pfad, unter dem die Profildaten des angegebenen Profils gespeichert wurden. Die Nummer des Profils wird auf eine gültige Zahl zwischen 1 und 3 begrenzt, um sicherzustellen, dass die Profildaten in einem der drei vorgesehenen Slots gespeichert werden. Die aktuellen Daten der Session werden in einem JSON-Format serialisiert und in einer Datei gespeichert, die durch den zurückgegebenen Pfad repräsentiert wird
        """
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
        """
        Vor.: profile ist die Nummer eines Profils als Integer oder None, wenn das aktuell aktive Profil geladen werden soll
        Eff.: -
        Erg.: True, wenn die Profildaten erfolgreich geladen und in den Zustand der Session übernommen wurden, False wenn das Profil nicht gefunden wurde oder ungültige Daten enthält. Die Nummer des Profils wird auf eine gültige Zahl zwischen 1 und 3 begrenzt, um sicherzustellen, dass die Profildaten aus einem der drei vorgesehenen Slots geladen werden. Wenn die Profildaten erfolgreich geladen werden, werden sie in den Zustand der Session übernommen und die Nummer des aktiven Profils wird aktualisiert
        """
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
        self._sync_course_types_with_lks()
        self._active_profile = slot
        return True
