from __future__ import annotations

from typing import Protocol, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Select, Static

from customTypes import FinalExamType, Points, UNKNOWN
import subjects

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class ExamsAppContext(Protocol):
    session: SessionModel


class ExamsScreen(BaseAbiScreen):
    _EXAM_ORDER = [
        FinalExamType.LK1,
        FinalExamType.LK2,
        FinalExamType.WRITTEN,
        FinalExamType.ORALLY,
        FinalExamType.PRESENTATION,
    ]

    _EXAM_LABEL_KEYS = {
        FinalExamType.LK1: "LK1",
        FinalExamType.LK2: "LK2",
        FinalExamType.WRITTEN: "Schriftlich",
        FinalExamType.ORALLY: "Mündlich",
        FinalExamType.PRESENTATION: "5. PK",
    }

    def __init__(self) -> None:
        super().__init__()
        self._selected_exam_index = 0
        self._message_key: str | None = None
        self._syncing_controls = False
        self._cached_exam_subjects: list[subjects.Subject] | None = None
        self._cached_subject_options: list[tuple[str, str]] | None = None
        self._last_subject_option_signature: tuple[tuple[str, str], ...] = ()

    def _all_exam_subjects(self) -> list[subjects.Subject]:
        if self._cached_exam_subjects is not None:
            return self._cached_exam_subjects

        all_subjects: list[subjects.Subject] = []
        for value in vars(subjects).values():
            if isinstance(value, subjects.Subject):
                all_subjects.append(value)

        blocked_names = {subjects.SUB.name, subjects.ENGLISH_Z.name}
        filtered = [item for item in all_subjects if item.name not in blocked_names]

        by_name: dict[str, subjects.Subject] = {}
        for item in filtered:
            by_name[item.name] = item

        self._cached_exam_subjects = sorted(by_name.values(), key=lambda s: s.name)
        return self._cached_exam_subjects

    def _get_exam(self, exam_type: FinalExamType):
        finals = cast(ExamsAppContext, self.app_ctx).session.get_finals()
        if exam_type == FinalExamType.LK1:
            return finals.LK1
        if exam_type == FinalExamType.LK2:
            return finals.LK2
        if exam_type == FinalExamType.WRITTEN:
            return finals.written
        if exam_type == FinalExamType.ORALLY:
            return finals.orally
        return finals.fifth

    def _message(self) -> str:
        if self._message_key is None:
            return ""
        return self.t(self._message_key)

    def _build_overview(self) -> str:
        lines = [self.t("exams.current")]
        for idx, exam_type in enumerate(self._EXAM_ORDER):
            exam = self._get_exam(exam_type)
            marker = ">" if idx == self._selected_exam_index else " "
            slot = self._EXAM_LABEL_KEYS[exam_type]
            lines.append(f"{marker} {slot}: {exam.subject} | {exam.grade}")
        return "\n".join(lines)

    def _build_selection(self) -> str:
        exam_type = self._EXAM_ORDER[self._selected_exam_index]
        exam = self._get_exam(exam_type)
        slot = self._EXAM_LABEL_KEYS[exam_type]
        return (
            f"{self.t('exams.selection')}: {slot}\n"
            f"Fach: {exam.subject}\n"
            f"Note: {exam.grade}"
        )

    def _slot_options(self) -> list[tuple[str, str]]:
        return [(self._EXAM_LABEL_KEYS[exam_type], str(index)) for index, exam_type in enumerate(self._EXAM_ORDER)]

    def _subject_options(self) -> list[tuple[str, str]]:
        if self._cached_subject_options is not None:
            return self._cached_subject_options
        pool = self._all_exam_subjects()
        self._cached_subject_options = [(f"{idx + 1:02d} | {subject}", subject.name) for idx, subject in enumerate(pool)]
        return self._cached_subject_options

    def _subject_lookup(self) -> dict[str, subjects.Subject]:
        pool = self._all_exam_subjects()
        return {subject.name: subject for subject in pool}

    def _subject_from_number(self, raw_number: str) -> subjects.Subject | None:
        text = raw_number.strip()
        if not text:
            return None
        try:
            idx = int(text) - 1
        except ValueError:
            return None

        pool = self._all_exam_subjects()
        if idx < 0 or idx >= len(pool):
            return None
        return pool[idx]

    def _sync_view(self) -> None:
        self.query_one("#exams_overview", AbiCard).update(self._build_overview())
        self.query_one("#exams_selection", AbiCard).update(self._build_selection())
        self.query_one("#exams_message", Static).update(self._message())

        self._syncing_controls = True
        slot_select = self.query_one("#exams_slot_select", Select)
        slot_value = str(self._selected_exam_index)
        if str(slot_select.value) != slot_value:
            slot_select.value = slot_value

        selected_exam = self._get_exam(self._selected_exam_type())
        subject_select = self.query_one("#exams_subject_select", Select)
        subject_options = self._subject_options()
        option_signature = tuple(subject_options)
        old_subject_values = {value for _, value in self._last_subject_option_signature}
        valid_subject_values = {value for _, value in subject_options}
        if valid_subject_values:
            next_subject_name = selected_exam.subject.name
            subject_target = next_subject_name if next_subject_name in valid_subject_values else subject_options[0][1]
        else:
            subject_target = ""

        if option_signature != self._last_subject_option_signature:
            if subject_target and subject_target in old_subject_values and str(subject_select.value) != subject_target:
                subject_select.value = subject_target
            subject_select.set_options(subject_options)
            self._last_subject_option_signature = option_signature
        if subject_target and str(subject_select.value) != subject_target:
            subject_select.value = subject_target

        slot_input = self.query_one("#exams_slot_input", Input)
        subject_input = self.query_one("#exams_subject_input", Input)
        grade_input = self.query_one("#exams_grade_input", Input)
        slot_text = str(self._selected_exam_index + 1)
        if slot_input.value != slot_text:
            slot_input.value = slot_text
        if subject_input.value != "":
            subject_input.value = ""
        next_grade_text = "" if selected_exam.grade == UNKNOWN else str(int(selected_exam.grade.value))
        if grade_input.value != next_grade_text:
            grade_input.value = next_grade_text
        self._syncing_controls = False

    @on(Select.Changed, "#exams_slot_select")
    def _on_slot_select_changed(self, event: Select.Changed) -> None:
        if self._syncing_controls:
            return
        try:
            parsed = int(str(event.value))
        except ValueError:
            parsed = 0
        parsed = max(0, min(len(self._EXAM_ORDER) - 1, parsed))
        if parsed == self._selected_exam_index:
            return
        self._selected_exam_index = parsed
        self._message_key = None
        self._sync_view()

    @on(Input.Changed, "#exams_slot_input")
    def _on_slot_input_changed(self, event: Input.Changed) -> None:
        if self._syncing_controls:
            return
        text = event.value.strip()
        if not text:
            return
        try:
            parsed = int(text) - 1
        except ValueError:
            return
        parsed = max(0, min(len(self._EXAM_ORDER) - 1, parsed))
        if parsed == self._selected_exam_index:
            return
        self._selected_exam_index = parsed
        self._message_key = None
        self._sync_view()

    @on(Input.Changed, "#exams_grade_input")
    def _on_grade_input_changed(self, event: Input.Changed) -> None:
        if self._syncing_controls:
            return
        value = event.value.strip()
        if not value:
            return
        self._set_grade_direct(value)

    def compose_body(self) -> ComposeResult:
        selected_exam = self._get_exam(self._selected_exam_type())

        yield AbiTitle(self.t("exams.title"), id="exams_title")
        yield AbiCard(self._build_overview(), id="exams_overview")
        yield AbiCard(self._build_selection(), id="exams_selection")

        with Horizontal(classes="abi-row"):
            yield Select[str](
                self._slot_options(),
                value=str(self._selected_exam_index),
                allow_blank=False,
                id="exams_slot_select",
                classes="abi-row-field",
            )
            yield Select[str](
                self._subject_options(),
                value=selected_exam.subject.name,
                allow_blank=False,
                id="exams_subject_select",
                classes="abi-row-field",
            )

        with Horizontal(classes="abi-row"):
            yield Input(
                value=str(self._selected_exam_index + 1),
                placeholder=self.t("exams.slot_input"),
                id="exams_slot_input",
                restrict=r"[1-5]*",
                classes="abi-row-field",
            )
            yield Input(
                placeholder=self.t("exams.subject_input"),
                id="exams_subject_input",
                restrict=r"[0-9]*",
                classes="abi-row-field",
            )
            yield Input(
                placeholder=self.t("exams.grade_input"),
                id="exams_grade_input",
                restrict=r"([0-9]|1[0-5])?",
                classes="abi-row-field",
            )

        with Horizontal(classes="abi-row"):
            yield Button(self.t("exams.apply_selection"), id="exams_apply_selection", classes="abi-menu-button abi-row-button")
            yield Button(self.t("exams.apply_grade"), id="exams_apply_grade", classes="abi-menu-button abi-row-button")
            yield Button(self.t("exams.toggle_unknown"), id="exams_toggle_unknown", classes="abi-menu-button abi-row-button")

        with Horizontal(classes="abi-row"):
            yield Button(self.t("exams.slot_prev"), id="exams_slot_prev", classes="abi-menu-button abi-row-button")
            yield Button(self.t("exams.slot_next",), id="exams_slot_next", classes="abi-menu-button abi-row-button")

        with Horizontal(classes="abi-row"):
            yield Button(self.t("exams.subject_prev"), id="exams_subject_prev", classes="abi-menu-button abi-row-button")
            yield Button(self.t("exams.subject_next"), id="exams_subject_next", classes="abi-menu-button abi-row-button")

        with Horizontal(classes="abi-row"):
            yield Button(self.t("exams.grade_minus"), id="exams_grade_minus", classes="abi-menu-button abi-row-button")
            yield Button(self.t("exams.grade_plus"), id="exams_grade_plus", classes="abi-menu-button abi-row-button")

        yield Static("", id="exams_message", classes="abi-warn")
        yield self.factory.action_button("screen.back", "exams_back")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#exams_title", AbiTitle).update(self.t("exams.title"))
        self.query_one("#exams_apply_selection", Button).label = self.t("exams.apply_selection")
        self.query_one("#exams_apply_grade", Button).label = self.t("exams.apply_grade")
        self.query_one("#exams_slot_prev", Button).label = self.t("exams.slot_prev")
        self.query_one("#exams_slot_next", Button).label = self.t("exams.slot_next")
        self.query_one("#exams_subject_prev", Button).label = self.t("exams.subject_prev")
        self.query_one("#exams_subject_next", Button).label = self.t("exams.subject_next")
        self.query_one("#exams_grade_minus", Button).label = self.t("exams.grade_minus")
        self.query_one("#exams_grade_plus", Button).label = self.t("exams.grade_plus")
        self.query_one("#exams_toggle_unknown", Button).label = self.t("exams.toggle_unknown")
        self.query_one("#exams_slot_input", Input).placeholder = self.t("exams.slot_input")
        self.query_one("#exams_subject_input", Input).placeholder = self.t("exams.subject_input")
        self.query_one("#exams_grade_input", Input).placeholder = self.t("exams.grade_input")
        self.query_one("#exams_back", Button).label = self.t("screen.back")
        self._sync_view()

    def on_mount(self) -> None:
        self._sync_view()

    def _cycle_slot(self, direction: int) -> None:
        self._selected_exam_index = (self._selected_exam_index + direction) % len(self._EXAM_ORDER)
        self._message_key = None
        self._sync_view()

    def _selected_exam_type(self) -> FinalExamType:
        return self._EXAM_ORDER[self._selected_exam_index]

    def _set_subject(self, direction: int) -> None:
        exam_type = self._selected_exam_type()
        if exam_type in (FinalExamType.LK1, FinalExamType.LK2):
            self._message_key = "exams.lk_locked"
            self._sync_view()
            return

        exam = self._get_exam(exam_type)
        pool = self._all_exam_subjects()
        if not pool:
            return

        current_index = 0
        for idx, subject in enumerate(pool):
            if subject == exam.subject:
                current_index = idx
                break

        target = pool[(current_index + direction) % len(pool)]
        finals = cast(ExamsAppContext, self.app_ctx).session.get_finals()
        used_subjects = {
            finals.LK1.subject,
            finals.LK2.subject,
            finals.written.subject,
            finals.orally.subject,
            finals.fifth.subject,
        }
        used_subjects.discard(exam.subject)
        if target in used_subjects:
            self._message_key = "exams.subject_duplicate"
            self._sync_view()
            return

        exam.subject = target
        self._message_key = None
        self._sync_view()

    def _set_subject_direct(self, subject: subjects.Subject) -> None:
        exam_type = self._selected_exam_type()
        if exam_type in (FinalExamType.LK1, FinalExamType.LK2):
            self._message_key = "exams.lk_locked"
            self._sync_view()
            return

        exam = self._get_exam(exam_type)
        if exam.subject == subject:
            return

        finals = cast(ExamsAppContext, self.app_ctx).session.get_finals()
        used_subjects = {
            finals.LK1.subject,
            finals.LK2.subject,
            finals.written.subject,
            finals.orally.subject,
            finals.fifth.subject,
        }
        used_subjects.discard(exam.subject)
        if subject in used_subjects:
            self._message_key = "exams.subject_duplicate"
            self._sync_view()
            return

        exam.subject = subject
        self._message_key = None
        self._sync_view()

    def _set_grade_direct(self, raw_value: str) -> None:
        value = raw_value.strip()
        if not value.isdigit():
            return

        exam = self._get_exam(self._selected_exam_type())
        new_grade = Points(max(0, min(15, int(value))))
        if exam.grade == new_grade:
            return

        exam.grade = new_grade
        exam.prediction = exam.grade
        self._message_key = None
        self._sync_view()

    def _adjust_grade(self, delta: int) -> None:
        exam = self._get_exam(self._selected_exam_type())
        if exam.grade == UNKNOWN:
            base_value = 10
        else:
            base_value = int(exam.grade.value)

        next_value = max(0, min(15, base_value + delta))
        new_grade = Points(next_value)
        if exam.grade == new_grade:
            return

        exam.grade = new_grade
        exam.prediction = None if exam.grade == UNKNOWN else exam.grade
        self._message_key = None
        self._sync_view()

    def _toggle_unknown(self) -> None:
        exam = self._get_exam(self._selected_exam_type())
        if exam.grade == UNKNOWN:
            exam.grade = Points(10)
            exam.prediction = exam.grade
        else:
            exam.grade = UNKNOWN
            exam.prediction = None
        self._message_key = None
        self._sync_view()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "exams_apply_selection":
            slot_value = self.query_one("#exams_slot_select", Select).value
            slot_input = self.query_one("#exams_slot_input", Input).value.strip()

            if slot_input:
                try:
                    slot_idx = int(slot_input) - 1
                except ValueError:
                    slot_idx = 0
            else:
                slot_idx = int(str(slot_value))
            self._selected_exam_index = max(0, min(len(self._EXAM_ORDER) - 1, slot_idx))

            subject_lookup = self._subject_lookup()
            subject_value = self.query_one("#exams_subject_select", Select).value
            selected_subject = subject_lookup.get(str(subject_value))

            subject_input = self.query_one("#exams_subject_input", Input).value
            by_number = self._subject_from_number(subject_input)
            if by_number is not None:
                selected_subject = by_number

            if selected_subject is not None:
                self._set_subject_direct(selected_subject)
            else:
                self._sync_view()
        elif button_id == "exams_apply_grade":
            self._set_grade_direct(self.query_one("#exams_grade_input", Input).value)
        elif button_id == "exams_slot_prev":
            self._cycle_slot(-1)
        elif button_id == "exams_slot_next":
            self._cycle_slot(1)
        elif button_id == "exams_subject_prev":
            self._set_subject(-1)
        elif button_id == "exams_subject_next":
            self._set_subject(1)
        elif button_id == "exams_grade_minus":
            self._adjust_grade(-1)
        elif button_id == "exams_grade_plus":
            self._adjust_grade(1)
        elif button_id == "exams_toggle_unknown":
            self._toggle_unknown()
        elif button_id == "exams_back":
            self.app_ctx.pop_screen()
