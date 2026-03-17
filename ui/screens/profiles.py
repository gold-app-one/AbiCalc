from __future__ import annotations

from typing import Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button, Select, Static

from .base import BaseAbiScreen
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class ProfilesAppContext(Protocol):
    session: SessionModel

    def save_profile(self, profile: int) -> object: ...
    def switch_profile(self, profile: int) -> bool: ...


class ProfilesScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message_key: str | None = None

    def _message(self) -> str:
        if self._message_key is None:
            return ""
        return self.t(self._message_key)

    def _selected_profile(self) -> int:
        profile_select = cast(Select[str], self.query_one("#profiles_selection", Select))
        selected_profile = profile_select.value
        if not isinstance(selected_profile, str):
            return cast(ProfilesAppContext, self.app_ctx).session.active_profile
        return int(selected_profile)

    def compose_body(self) -> ComposeResult:
        app_ctx = cast(ProfilesAppContext, self.app_ctx)
        active = app_ctx.session.active_profile

        yield AbiTitle(self.t("profiles.title"), id="profiles_title")
        yield AbiCard(self.t("profiles.hint"), id="profiles_hint", classes="abi-subtitle")

        yield Select[str](
            [
                (self.t("profiles.option").format(profile=1), "1"),
                (self.t("profiles.option").format(profile=2), "2"),
                (self.t("profiles.option").format(profile=3), "3"),
            ],
            value=str(active),
            allow_blank=False,
            id="profiles_selection",
            classes="abi-card",
        )

        yield Button(self.t("profiles.switch"), id="profiles_switch", classes="abi-menu-button")
        yield Button(self.t("profiles.save_current"), id="profiles_save", classes="abi-menu-button")
        yield Static("", id="profiles_message", classes="abi-ok")
        yield self.factory.action_button("screen.back", "profiles_back")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#profiles_title", AbiTitle).update(self.t("profiles.title"))
        self.query_one("#profiles_hint", AbiCard).update(self.t("profiles.hint"))

        app_ctx = cast(ProfilesAppContext, self.app_ctx)
        active = app_ctx.session.active_profile
        profile_select = cast(Select[str], self.query_one("#profiles_selection", Select))
        profile_options = [
            (self.t("profiles.option").format(profile=1), "1"),
            (self.t("profiles.option").format(profile=2), "2"),
            (self.t("profiles.option").format(profile=3), "3"),
        ]
        profile_select.set_options(profile_options)
        valid_profiles = {value for _, value in profile_options}
        selected_profile = str(active)
        if selected_profile not in valid_profiles:
            selected_profile = "1"
        if str(profile_select.value) != selected_profile:
            profile_select.value = selected_profile

        self.query_one("#profiles_switch", Button).label = self.t("profiles.switch")
        self.query_one("#profiles_save", Button).label = self.t("profiles.save_current")
        self.query_one("#profiles_back", Button).label = self.t("screen.back")
        self.query_one("#profiles_message", Static).update(self._message())

    def on_mount(self) -> None:
        self.refresh_labels()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(ProfilesAppContext, self.app_ctx)
        button_id = event.button.id

        if button_id == "profiles_switch":
            target = self._selected_profile()
            app_ctx.switch_profile(target)
            self._message_key = "profiles.switched"
            self.refresh_labels()
        elif button_id == "profiles_save":
            current = app_ctx.session.active_profile
            app_ctx.save_profile(current)
            self._message_key = "profiles.saved"
            self.refresh_labels()
        elif button_id == "profiles_back":
            self.app_ctx.pop_screen()
