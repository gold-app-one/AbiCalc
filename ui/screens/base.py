from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header

from ..core.i18n import I18nProvider
from ..widgets.factory import WidgetFactory

if TYPE_CHECKING:
    from ..app import MainApp


class AppContext(Protocol):
    i18n: I18nProvider
    factory: WidgetFactory


class BaseAbiScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield from self.compose_body()
        yield Footer()

    def compose_body(self) -> ComposeResult:
        raise NotImplementedError()

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
