from __future__ import annotations

from typing import Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button, Static

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class SubjectsAppContext(Protocol):
    session: SessionModel


class SubjectsScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message = ""

    def compose_body(self) -> ComposeResult:
        app_ctx = cast(SubjectsAppContext, self.app_ctx)
        lk1 = app_ctx.session.get_lk(1)
        lk2 = app_ctx.session.get_lk(2)

        yield AbiTitle(self.t("subjects.title"))

        yield AbiCard(
            f"{self.t('subjects.current')}\n"
            f"LK1: {lk1}\n"
            f"LK2: {lk2}"
        )

        yield AbiCard(self.t("subjects.hint"), classes="abi-subtitle")
        yield Button(self.t("subjects.lk1_prev"), id="subjects_lk1_prev", classes="abi-menu-button")
        yield Button(self.t("subjects.lk1_next"), id="subjects_lk1_next", classes="abi-menu-button")
        yield Button(self.t("subjects.lk2_prev"), id="subjects_lk2_prev", classes="abi-menu-button")
        yield Button(self.t("subjects.lk2_next"), id="subjects_lk2_next", classes="abi-menu-button")

        if self._message:
            yield Static(self._message, classes="abi-warn")

        yield self.factory.action_button("screen.back", "subjects_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(SubjectsAppContext, self.app_ctx)
        button_id = event.button.id

        if button_id == "subjects_lk1_prev":
            if not app_ctx.session.cycle_lk(1, -1):
                self._message = self.t("subjects.invalid_duplicate")
            else:
                self._message = ""
            self.refresh(layout=True)
        elif button_id == "subjects_lk1_next":
            if not app_ctx.session.cycle_lk(1, 1):
                self._message = self.t("subjects.invalid_duplicate")
            else:
                self._message = ""
            self.refresh(layout=True)
        elif button_id == "subjects_lk2_prev":
            if not app_ctx.session.cycle_lk(2, -1):
                self._message = self.t("subjects.invalid_duplicate")
            else:
                self._message = ""
            self.refresh(layout=True)
        elif button_id == "subjects_lk2_next":
            if not app_ctx.session.cycle_lk(2, 1):
                self._message = self.t("subjects.invalid_duplicate")
            else:
                self._message = ""
            self.refresh(layout=True)
        elif button_id == "subjects_back":
            self.app_ctx.pop_screen()
