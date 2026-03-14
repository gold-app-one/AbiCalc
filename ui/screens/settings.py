from __future__ import annotations

from typing import Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button, Static

from .base import BaseAbiScreen
from ..core.config import ConfigManager
from ..widgets.components import AbiCard, AbiTitle


class SettingsAppContext(Protocol):
    config_manager: ConfigManager

    def apply_theme(self, theme_name: str) -> None: ...


class SettingsScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message = ""

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("settings.title"))

        app_ctx = cast(SettingsAppContext, self.app_ctx)
        config = app_ctx.config_manager.config

        theme_name = config.active_theme
        language = config.language
        result_limit = config.result_limit

        yield AbiCard(
            f"{self.t('settings.theme')}: {theme_name}\n"
            f"{self.t('settings.language')}: {language}\n"
            f"{self.t('settings.result_limit')}: {result_limit}"
        )

        yield AbiCard("Theme wechseln", classes="abi-subtitle")
        yield Button("Classic Light", id="settings_theme_light", classes="abi-menu-button")
        yield Button("Classic Dark", id="settings_theme_dark", classes="abi-menu-button")

        yield AbiCard("Sprache wechseln", classes="abi-subtitle")
        yield Button("Deutsch", id="settings_lang_de", classes="abi-menu-button")
        yield Button("English", id="settings_lang_en", classes="abi-menu-button")

        yield AbiCard("Top-N Ergebnisse", classes="abi-subtitle")
        yield Button("Top 5", id="settings_limit_5", classes="abi-menu-button")
        yield Button("Top 10", id="settings_limit_10", classes="abi-menu-button")
        yield Button("Top 20", id="settings_limit_20", classes="abi-menu-button")

        if self._message:
            yield Static(self._message, classes="abi-ok")

        yield self.factory.action_button("screen.back", "settings_back")

    def _save(self) -> None:
        app_ctx = cast(SettingsAppContext, self.app_ctx)
        manager = app_ctx.config_manager
        manager.save()
        self._message = self.t("settings.saved")
        self.app_ctx.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app_ctx = cast(SettingsAppContext, self.app_ctx)
        manager = app_ctx.config_manager

        button_id = event.button.id
        if button_id == "settings_theme_light":
            manager.set_theme("classic-light")
            app_ctx.apply_theme("classic-light")
            self._save()
        elif button_id == "settings_theme_dark":
            manager.set_theme("classic-dark")
            app_ctx.apply_theme("classic-dark")
            self._save()
        elif button_id == "settings_lang_de":
            manager.set_language("de")
            self.i18n.set_language("de")
            self._save()
        elif button_id == "settings_lang_en":
            manager.set_language("en")
            self.i18n.set_language("en")
            self._save()
        elif button_id == "settings_limit_5":
            manager.set_result_limit(5)
            self._save()
        elif button_id == "settings_limit_10":
            manager.set_result_limit(10)
            self._save()
        elif button_id == "settings_limit_20":
            manager.set_result_limit(20)
            self._save()
        elif button_id == "settings_back":
            self.app_ctx.pop_screen()
