from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Button

from .base import BaseAbiScreen
from ..widgets.components import AbiCard, AbiTitle


class ExamsScreen(BaseAbiScreen):
    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("exams.title"))
        yield AbiCard(self.t("screen.not_implemented"))
        yield self.factory.action_button("screen.back", "exams_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exams_back":
            self.app_ctx.pop_screen()
