from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class SplashScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Static("AbiCalc wird gestartet...", classes="abi-title")
        yield Static("Bitte einen Moment warten.", classes="abi-subtitle")

    def on_mount(self) -> None:
        self.set_timer(0.35, self._open_main_menu)

    def _open_main_menu(self) -> None:
        from .main import MainMenuScreen

        self.app.push_screen(MainMenuScreen())
