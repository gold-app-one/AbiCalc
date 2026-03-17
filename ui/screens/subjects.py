from __future__ import annotations

from typing import Protocol, cast

from textual import on
from textual.app import ComposeResult
from textual.widgets import Button, Select, Static

from subjects import Subject

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class SubjectsAppContext(Protocol):
    session: SessionModel


class SubjectsScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message = ""
        self._syncing_controls = False
        self._last_subject_option_signature: tuple[tuple[str, str], ...] = ()

    def _build_state_text(self) -> str:
        app_ctx = cast(SubjectsAppContext, self.app_ctx)
        lk1 = app_ctx.session.get_lk(1)
        lk2 = app_ctx.session.get_lk(2)
        return (
            f"{self.t('subjects.current')}\n"
            f"LK1: {lk1}\n"
            f"LK2: {lk2}"
        )

    def _subject_options(self) -> list[tuple[str, str]]:
        pool = cast(SubjectsAppContext, self.app_ctx).session.get_lk_subject_pool()
        return [(f"{idx + 1:02d} | {subject}", subject.name) for idx, subject in enumerate(pool)]

    def _subject_lookup(self) -> dict[str, Subject]:
        pool = cast(SubjectsAppContext, self.app_ctx).session.get_lk_subject_pool()
        return {subject.name: subject for subject in pool}

    def _sync_view(self) -> None:
        self.query_one("#subjects_state", AbiCard).update(self._build_state_text())
        self.query_one("#subjects_message", Static).update(self._message)

        self._syncing_controls = True
        lk1_name = cast(SubjectsAppContext, self.app_ctx).session.get_lk(1).name
        lk2_name = cast(SubjectsAppContext, self.app_ctx).session.get_lk(2).name

        lk1_select = self.query_one("#subjects_lk1_select", Select)
        lk2_select = self.query_one("#subjects_lk2_select", Select)
        subject_options = self._subject_options()
        option_signature = tuple(subject_options)
        if option_signature != self._last_subject_option_signature:
            lk1_select.set_options(subject_options)
            lk2_select.set_options(subject_options)
            self._last_subject_option_signature = option_signature
        if str(lk1_select.value) != lk1_name:
            lk1_select.value = lk1_name
        if str(lk2_select.value) != lk2_name:
            lk2_select.value = lk2_name
        self._syncing_controls = False

    def compose_body(self) -> ComposeResult:
        app_ctx = cast(SubjectsAppContext, self.app_ctx)
        options = self._subject_options()
        lk1_name = app_ctx.session.get_lk(1).name
        lk2_name = app_ctx.session.get_lk(2).name

        yield AbiTitle(self.t("subjects.title"), id="subjects_title")

        yield AbiCard(self._build_state_text(), id="subjects_state")

        yield AbiCard(self.t("subjects.hint"), id="subjects_hint", classes="abi-subtitle")

        yield Select[str](options, value=lk1_name, allow_blank=False, id="subjects_lk1_select", classes="abi-row-field")
        yield Select[str](options, value=lk2_name, allow_blank=False, id="subjects_lk2_select", classes="abi-row-field")

        yield Button(self.t("subjects.apply"), id="subjects_apply", classes="abi-menu-button")

        yield Static(self._message, id="subjects_message", classes="abi-warn")

        yield self.factory.action_button("screen.back", "subjects_back")

    def on_mount(self) -> None:
        self._sync_view()

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#subjects_title", AbiTitle).update(self.t("subjects.title"))
        self.query_one("#subjects_hint", AbiCard).update(self.t("subjects.hint"))
        self.query_one("#subjects_apply", Button).label = self.t("subjects.apply")
        self.query_one("#subjects_back", Button).label = self.t("screen.back")

        self._sync_view()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(SubjectsAppContext, self.app_ctx)
        button_id = event.button.id

        if button_id == "subjects_apply":
            lookup = self._subject_lookup()
            lk1_name = str(self.query_one("#subjects_lk1_select", Select).value)
            lk2_name = str(self.query_one("#subjects_lk2_select", Select).value)
            lk1 = lookup.get(lk1_name)
            lk2 = lookup.get(lk2_name)

            if lk1 is None or lk2 is None or lk1 == lk2:
                self._message = self.t("subjects.invalid_duplicate")
                self._sync_view()
                return

            if not app_ctx.session.set_lk(1, lk1):
                self._message = self.t("subjects.invalid_duplicate")
                self._sync_view()
                return
            if not app_ctx.session.set_lk(2, lk2):
                self._message = self.t("subjects.invalid_duplicate")
                self._sync_view()
                return

            self._message = ""
            self.refresh_labels()
        elif button_id == "subjects_back":
            self.app_ctx.pop_screen()
