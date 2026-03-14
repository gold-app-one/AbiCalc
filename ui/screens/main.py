from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button

from .base import BaseAbiScreen
from ..widgets.components import AbiTitle


class MainMenuScreen(BaseAbiScreen):
    def _styled_menu_button(self, label_key: str, button_id: str) -> Button:
        button = self.factory.menu_button(label_key, button_id)
        # Hard fallback: direct widget styles avoid CSS selector/theme mismatches.
        button.styles.background = "#163042"
        button.styles.color = "#ffffff"
        button.styles.border = ("round", "#ffffff")
        button.styles.text_style = "bold"
        return button

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("main.title"), id="main_title")
        yield self._styled_menu_button("main.subjects", "main_subjects")
        yield self._styled_menu_button("main.grades", "main_grades")
        yield self._styled_menu_button("main.exams", "main_exams")
        yield self._styled_menu_button("main.results", "main_results")
        yield self._styled_menu_button("main.settings", "main_settings")
        yield self._styled_menu_button("main.quit", "main_quit")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#main_title", AbiTitle).update(self.t("main.title"))

        labels = {
            "main_subjects": self.t("main.subjects"),
            "main_grades": self.t("main.grades"),
            "main_exams": self.t("main.exams"),
            "main_results": self.t("main.results"),
            "main_settings": self.t("main.settings"),
            "main_quit": self.t("main.quit"),
        }

        for button_id, label in labels.items():
            self.query_one(f"#{button_id}", Button).label = label

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "main_subjects":
            from .subjects import SubjectsScreen

            self.app_ctx.push_screen(SubjectsScreen())
        elif button_id == "main_grades":
            from .grades import GradesScreen

            self.app_ctx.push_screen(GradesScreen())
        elif button_id == "main_exams":
            from .exams import ExamsScreen

            self.app_ctx.push_screen(ExamsScreen())
        elif button_id == "main_results":
            from .results import ResultsScreen

            self.app_ctx.push_screen(ResultsScreen())
        elif button_id == "main_settings":
            from .settings import SettingsScreen

            self.app_ctx.push_screen(SettingsScreen())
        elif button_id == "main_quit":
            self.app_ctx.quit_with_save()
