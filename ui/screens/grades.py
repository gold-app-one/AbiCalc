from __future__ import annotations

from typing import Protocol, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Select

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class GradesAppContext(Protocol):
    session: SessionModel


class GradesScreen(BaseAbiScreen):
    SHOW_FOOTER = False

    def __init__(self) -> None:
        super().__init__()
        self._semester = 1
        self._course_index = 0
        self._syncing_controls = False
        self._last_course_option_signature: tuple[tuple[str, str], ...] = ()
        self._last_add_subject_signature: tuple[tuple[str, str], ...] = ()

    def _add_subject_options(self) -> list[tuple[str, str]]:
        pool = cast(GradesAppContext, self.app_ctx).session.get_course_subject_pool()
        return [(f"{idx + 1:02d} | {subject}", subject.name) for idx, subject in enumerate(pool)]

    def _add_subject_lookup(self):
        pool = cast(GradesAppContext, self.app_ctx).session.get_course_subject_pool()
        return {subject.name: subject for subject in pool}

    def _build_contents(self) -> tuple[str, str]:
        app_ctx = cast(GradesAppContext, self.app_ctx)
        courses = app_ctx.session.get_q(self._semester)

        if courses:
            self._course_index = max(0, min(self._course_index, len(courses) - 1))
            selected = courses[self._course_index]
            summary_lines: list[str] = []
            for idx, course in enumerate(courses):
                marker = ">" if idx == self._course_index else " "
                summary_lines.append(
                    f"{marker} {idx + 1:02d}. {course.subject} | {course.type.name} | {course.grade}"
                )
            courses_content = "\n".join(summary_lines)
            selected_content = (
                f"{self.t('grades.semester')}: Q{self._semester}\n"
                f"{self.t('grades.course')}: #{self._course_index + 1} {selected.subject}\n"
                f"Typ: {selected.type.name}\n"
                f"Note: {selected.grade}"
            )
        else:
            courses_content = "-"
            selected_content = f"{self.t('grades.semester')}: Q{self._semester}\nKeine Kurse gefunden."

        return selected_content, courses_content

    def _sync_view(self) -> None:
        selected_content, courses_content = self._build_contents()
        self.query_one("#grades_selected", AbiCard).update(selected_content)
        self.query_one("#grades_courses", AbiCard).update(courses_content)

        self._syncing_controls = True
        semester_select = self.query_one("#grades_semester_select", Select)
        semester_value = str(self._semester)
        if str(semester_select.value) != semester_value:
            semester_select.value = semester_value

        courses = cast(GradesAppContext, self.app_ctx).session.get_q(self._semester)
        options = [(f"{idx + 1:02d} | {course.subject} | {course.grade}", str(idx)) for idx, course in enumerate(courses)]
        rendered_options = options if options else [("-", "0")]
        option_signature = tuple(rendered_options)
        course_select = self.query_one("#grades_course_select", Select)

        # Compute target value and set it BEFORE set_options so Textual never
        # sees an out-of-bounds value and resets to the first item, which would
        # queue a conflicting Changed event causing an infinite ping-pong loop.
        if courses:
            self._course_index = max(0, min(self._course_index, len(courses) - 1))
            course_value = str(self._course_index)
        else:
            self._course_index = 0
            course_value = "0"
        if str(course_select.value) != course_value:
            course_select.value = course_value

        if option_signature != self._last_course_option_signature:
            course_select.set_options(rendered_options)
            self._last_course_option_signature = option_signature

        add_subject_select = self.query_one("#grades_add_subject_select", Select)
        add_subject_options = self._add_subject_options()
        add_subject_signature = tuple(add_subject_options)
        if add_subject_signature != self._last_add_subject_signature:
            add_subject_select.set_options(add_subject_options)
            self._last_add_subject_signature = add_subject_signature
            if add_subject_options:
                add_subject_select.value = add_subject_options[0][1]

        self._syncing_controls = False

    @on(Select.Changed, "#grades_semester_select")
    def _on_semester_select_changed(self, event: Select.Changed) -> None:
        if self._syncing_controls:
            return
        try:
            semester = int(str(event.value))
        except ValueError:
            return
        semester = max(1, min(4, semester))
        if semester == self._semester:
            return
        self._semester = semester
        self._course_index = 0
        self._sync_view()

    @on(Select.Changed, "#grades_course_select")
    def _on_course_select_changed(self, event: Select.Changed) -> None:
        if self._syncing_controls:
            return

        courses = cast(GradesAppContext, self.app_ctx).session.get_q(self._semester)
        if not courses:
            self._course_index = 0
            self._sync_view()
            return

        try:
            parsed_index = int(str(event.value))
        except ValueError:
            return

        idx = max(0, min(len(courses) - 1, parsed_index))
        if idx == self._course_index:
            return
        self._course_index = idx
        self._sync_view()

    def compose_body(self) -> ComposeResult:
        selected_content, courses_content = self._build_contents()
        yield AbiTitle(self.t("grades.title"), id="grades_title")

        yield AbiCard(selected_content, id="grades_selected")
        yield AbiCard(courses_content, id="grades_courses")
        yield AbiCard(self.t("grades.hint"), id="grades_hint", classes="abi-subtitle")

        with Horizontal(classes="abi-row"):
            yield Select[str](
                [("Q1", "1"), ("Q2", "2"), ("Q3", "3"), ("Q4", "4")],
                value=str(self._semester),
                allow_blank=False,
                id="grades_semester_select",
                classes="abi-row-field",
            )
            yield Select[str](
                [("-", "0")],
                value="0",
                allow_blank=False,
                id="grades_course_select",
                classes="abi-row-field",
            )

        with Horizontal(classes="abi-row"):
            yield Input(
                placeholder=self.t("grades.grade_input"),
                id="grades_grade_input",
                restrict=r"([0-9]|1[0-5])?",
                classes="abi-row-field",
            )

        with Horizontal(classes="abi-row"):
            yield Button(self.t("grades.apply_selection"), id="grades_apply_selection", classes="abi-menu-button abi-row-button")
            yield Button(self.t("grades.apply_grade"), id="grades_apply_grade", classes="abi-menu-button abi-row-button")
            yield Button(self.t("grades.toggle_unknown"), id="grades_unknown", classes="abi-menu-button abi-row-button")

        with Horizontal(classes="abi-row"):
            yield Button(self.t("grades.grade_minus"), id="grades_minus", classes="abi-menu-button abi-row-button")
            yield Button(self.t("grades.grade_plus"), id="grades_plus", classes="abi-menu-button abi-row-button")

        with Horizontal(classes="abi-row"):
            yield Select[str](
                [("-", "")],
                value="",
                allow_blank=False,
                id="grades_add_subject_select",
                classes="abi-row-field",
            )

        with Horizontal(classes="abi-row"):
            yield Button(self.t("grades.add_course"), id="grades_add_course", classes="abi-menu-button abi-row-button")
            yield Button(self.t("grades.delete_course"), id="grades_delete_course", classes="abi-menu-button abi-row-button")

        yield self.factory.action_button("screen.back", "grades_back")

    def on_mount(self) -> None:
        self.query_one("#grades_grade_input", Input).cursor_blink = False
        self._sync_view()

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#grades_title", AbiTitle).update(self.t("grades.title"))
        self.query_one("#grades_hint", AbiCard).update(self.t("grades.hint"))
        self.query_one("#grades_apply_selection", Button).label = self.t("grades.apply_selection")
        self.query_one("#grades_apply_grade", Button).label = self.t("grades.apply_grade")
        self.query_one("#grades_unknown", Button).label = self.t("grades.toggle_unknown")
        self.query_one("#grades_minus", Button).label = self.t("grades.grade_minus")
        self.query_one("#grades_plus", Button).label = self.t("grades.grade_plus")
        self.query_one("#grades_add_course", Button).label = self.t("grades.add_course")
        self.query_one("#grades_delete_course", Button).label = self.t("grades.delete_course")
        self.query_one("#grades_add_subject_select", Select).prompt = self.t("grades.add_subject")
        self.query_one("#grades_grade_input", Input).placeholder = self.t("grades.grade_input")
        self.query_one("#grades_back", Button).label = self.t("screen.back")
        self._sync_view()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(GradesAppContext, self.app_ctx)
        button_id = event.button.id

        if button_id == "grades_apply_selection":
            try:
                self._semester = int(str(self.query_one("#grades_semester_select", Select).value))
            except ValueError:
                self._semester = 1
            self._semester = max(1, min(4, self._semester))

            courses = app_ctx.session.get_q(self._semester)
            if courses:
                try:
                    selected_idx = int(str(self.query_one("#grades_course_select", Select).value))
                except ValueError:
                    selected_idx = 0
                self._course_index = max(0, min(len(courses) - 1, selected_idx))
            else:
                self._course_index = 0

            self._sync_view()
        elif button_id == "grades_apply_grade":
            raw_grade = self.query_one("#grades_grade_input", Input).value.strip()
            if raw_grade.isdigit():
                numeric_grade = max(0, min(15, int(raw_grade)))
                current_courses = app_ctx.session.get_q(self._semester)
                if current_courses:
                    current_value = int(current_courses[self._course_index].grade.value)
                    app_ctx.session.adjust_course_grade(self._semester, self._course_index, numeric_grade - current_value)
            self._sync_view()
        elif button_id == "grades_minus":
            app_ctx.session.adjust_course_grade(self._semester, self._course_index, -1)
            self._sync_view()
        elif button_id == "grades_plus":
            app_ctx.session.adjust_course_grade(self._semester, self._course_index, 1)
            self._sync_view()
        elif button_id == "grades_unknown":
            app_ctx.session.toggle_course_unknown(self._semester, self._course_index)
            self._sync_view()
        elif button_id == "grades_add_course":
            lookup = self._add_subject_lookup()
            subject_name = str(self.query_one("#grades_add_subject_select", Select).value)
            subject = lookup.get(subject_name)
            if subject is None:
                return
            self._course_index = app_ctx.session.add_course(self._semester, subject, self._course_index)
            self._sync_view()
        elif button_id == "grades_delete_course":
            if app_ctx.session.delete_course(self._semester, self._course_index):
                remaining = len(app_ctx.session.get_q(self._semester))
                if remaining == 0:
                    self._course_index = 0
                else:
                    self._course_index = max(0, min(self._course_index, remaining - 1))
                self._sync_view()
        elif button_id == "grades_back":
            self.app_ctx.pop_screen()
