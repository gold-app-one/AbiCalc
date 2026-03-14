from __future__ import annotations

from typing import Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class GradesAppContext(Protocol):
    session: SessionModel


class GradesScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._semester = 1
        self._course_index = 0

    def compose_body(self) -> ComposeResult:
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

        yield AbiTitle(self.t("grades.title"))

        yield AbiCard(selected_content)
        yield AbiCard(courses_content)
        yield AbiCard(self.t("grades.hint"), classes="abi-subtitle")

        yield Button(f"{self.t('grades.prev')} Q", id="grades_sem_prev", classes="abi-menu-button")
        yield Button(f"{self.t('grades.next')} Q", id="grades_sem_next", classes="abi-menu-button")

        yield Button(f"{self.t('grades.prev')} {self.t('grades.course')}", id="grades_course_prev", classes="abi-menu-button")
        yield Button(f"{self.t('grades.next')} {self.t('grades.course')}", id="grades_course_next", classes="abi-menu-button")

        yield Button(self.t("grades.grade_minus"), id="grades_minus", classes="abi-menu-button")
        yield Button(self.t("grades.grade_plus"), id="grades_plus", classes="abi-menu-button")
        yield Button(self.t("grades.toggle_unknown"), id="grades_unknown", classes="abi-menu-button")

        yield self.factory.action_button("screen.back", "grades_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(GradesAppContext, self.app_ctx)
        button_id = event.button.id

        if button_id == "grades_sem_prev":
            self._semester = 4 if self._semester <= 1 else self._semester - 1
            self._course_index = 0
            self.refresh(layout=True)
        elif button_id == "grades_sem_next":
            self._semester = 1 if self._semester >= 4 else self._semester + 1
            self._course_index = 0
            self.refresh(layout=True)
        elif button_id == "grades_course_prev":
            courses = app_ctx.session.get_q(self._semester)
            if courses:
                self._course_index = max(0, self._course_index - 1)
            self.refresh(layout=True)
        elif button_id == "grades_course_next":
            courses = app_ctx.session.get_q(self._semester)
            if courses:
                self._course_index = min(len(courses) - 1, self._course_index + 1)
            self.refresh(layout=True)
        elif button_id == "grades_minus":
            app_ctx.session.adjust_course_grade(self._semester, self._course_index, -1)
            self.refresh(layout=True)
        elif button_id == "grades_plus":
            app_ctx.session.adjust_course_grade(self._semester, self._course_index, 1)
            self.refresh(layout=True)
        elif button_id == "grades_unknown":
            app_ctx.session.toggle_course_unknown(self._semester, self._course_index)
            self.refresh(layout=True)
        elif button_id == "grades_back":
            self.app_ctx.pop_screen()
