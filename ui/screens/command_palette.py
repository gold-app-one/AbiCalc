from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button, Static

from .base import BaseAbiScreen
from ..widgets.components import AbiCard, AbiTitle


class CommandPaletteScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message_key: str | None = None

    def _message(self) -> str:
        if self._message_key is None:
            return ""
        return self.t(self._message_key)

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("command_palette.title"), id="palette_title")
        yield AbiCard(self.t("command_palette.hint"), id="palette_hint", classes="abi-subtitle")

        yield Button(self.t("command_palette.open_subjects"), id="palette_subjects", classes="abi-menu-button")
        yield Button(self.t("command_palette.open_grades"), id="palette_grades", classes="abi-menu-button")
        yield Button(self.t("command_palette.open_exams"), id="palette_exams", classes="abi-menu-button")
        yield Button(self.t("command_palette.open_results"), id="palette_results", classes="abi-menu-button")
        yield Button(self.t("command_palette.open_settings"), id="palette_settings", classes="abi-menu-button")

        yield Static("", id="palette_message", classes="abi-ok")
        yield Button(self.t("command_palette.close"), id="palette_close", classes="abi-menu-button")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#palette_title", AbiTitle).update(self.t("command_palette.title"))
        self.query_one("#palette_hint", AbiCard).update(self.t("command_palette.hint"))
        self.query_one("#palette_subjects", Button).label = self.t("command_palette.open_subjects")
        self.query_one("#palette_grades", Button).label = self.t("command_palette.open_grades")
        self.query_one("#palette_exams", Button).label = self.t("command_palette.open_exams")
        self.query_one("#palette_results", Button).label = self.t("command_palette.open_results")
        self.query_one("#palette_settings", Button).label = self.t("command_palette.open_settings")

        self.query_one("#palette_close", Button).label = self.t("command_palette.close")
        self.query_one("#palette_message", Static).update(self._message())

    def on_mount(self) -> None:
        self.refresh_labels()

    def _open_screen(self, target: str) -> None:
        self.app_ctx.pop_screen()

        if target == "subjects":
            from .subjects import SubjectsScreen

            self.app_ctx.push_screen(SubjectsScreen())
        elif target == "grades":
            from .grades import GradesScreen

            self.app_ctx.push_screen(GradesScreen())
        elif target == "exams":
            from .exams import ExamsScreen

            self.app_ctx.push_screen(ExamsScreen())
        elif target == "results":
            from .results import ResultsScreen

            self.app_ctx.push_screen(ResultsScreen())
        elif target == "settings":
            from .settings import SettingsScreen

            self.app_ctx.push_screen(SettingsScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "palette_subjects":
            self._open_screen("subjects")
        elif button_id == "palette_grades":
            self._open_screen("grades")
        elif button_id == "palette_exams":
            self._open_screen("exams")
        elif button_id == "palette_results":
            self._open_screen("results")
        elif button_id == "palette_settings":
            self._open_screen("settings")
        elif button_id == "palette_close":
            self.app_ctx.pop_screen()
