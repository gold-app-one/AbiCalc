from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from ..core.i18n import I18nProvider
from ..widgets.factory import WidgetFactory

if TYPE_CHECKING:
    from ..app import MainApp


class AppContext(Protocol):
    i18n: I18nProvider
    factory: WidgetFactory


class BaseAbiScreen(Screen[None]):
    SHOW_FOOTER = True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(classes="abi-topbar"):
            yield Static("", classes="abi-topbar-spacer")
            yield Button("", id="global_profile_menu", classes="abi-topbar-button")
        yield from self.compose_body()
        if self.SHOW_FOOTER:
            yield Footer()

    def on_show(self) -> None:
        self.refresh_labels()

    def compose_body(self) -> ComposeResult:
        raise NotImplementedError()

    def refresh_labels(self) -> None:
        profile_label = self.t("topbar.profile").format(profile=self.app_ctx.session.active_profile)
        try:
            self.query_one("#global_profile_menu", Button).label = profile_label
        except Exception:
            pass

    @on(Button.Pressed, "#global_profile_menu")
    def _on_profile_button_pressed(self) -> None:
        if self.__class__.__name__ == "ProfilesScreen":
            return

        from .profiles import ProfilesScreen

        self.app_ctx.push_screen(ProfilesScreen())

    @property
    def i18n(self) -> I18nProvider:
        return cast(AppContext, self.app_ctx).i18n

    @property
    def factory(self) -> WidgetFactory:
        return cast(AppContext, self.app_ctx).factory

    @property
    def app_ctx(self) -> "MainApp":
        return cast("MainApp", self.app)

    def t(self, key: str) -> str:
        return self.i18n.t(key)
