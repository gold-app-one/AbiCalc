from __future__ import annotations

from typing import Protocol, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Select, Static

from .base import BaseAbiScreen
from ..core.config import ConfigManager
from ..widgets.components import AbiCard, AbiTitle


class SettingsAppContext(Protocol):
    config_manager: ConfigManager

    def apply_theme(self, theme_name: str) -> None: ...
    def apply_language(self, language: str) -> None: ...


class SettingsScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._message = ""
        self._message_key: str | None = None

    def _build_config_summary(self) -> str:
        app_ctx = cast(SettingsAppContext, self.app_ctx)
        config = app_ctx.config_manager.config
        return (
            f"{self.t('settings.theme')}: {config.active_theme}\n"
            f"{self.t('settings.language')}: {config.language}\n"
            f"{self.t('settings.result_limit')}: {config.result_limit}"
        )

    def _set_message_key(self, key: str | None) -> None:
        self._message_key = key
        self._message = self.t(key) if key is not None else ""

    def _set_button_label(self, button_id: str, label: str) -> None:
        try:
            self.query_one(f"#{button_id}", Button).label = label
        except Exception:
            pass

    def _sync_view(self) -> None:
        self.query_one("#settings_summary", AbiCard).update(self._build_config_summary())
        self.query_one("#settings_message", Static).update(self._message)

    def refresh_labels(self) -> None:
        super().refresh_labels()
        if self._message_key is not None:
            self._message = self.t(self._message_key)

        self.query_one("#settings_title", AbiTitle).update(self.t("settings.title"))
        self.query_one("#settings_theme_title", AbiCard).update(self.t("settings.theme_section"))
        self.query_one("#settings_language_title", AbiCard).update(self.t("settings.language_section"))
        self.query_one("#settings_limit_title", AbiCard).update(self.t("settings.limit_section"))

        self._set_button_label("settings_theme_light", "Classic Light")
        self._set_button_label("settings_theme_dark", "Classic Dark")
        self._set_button_label("settings_lang_de", "Deutsch")
        self._set_button_label("settings_lang_en", "English")
        self._set_button_label("settings_apply_limit", self.t("settings.apply_limit"))

        self._set_button_label("settings_back", self.t("screen.back"))

        config = cast(SettingsAppContext, self.app_ctx).config_manager.config
        limit_select = self.query_one("#settings_limit_list", Select)
        limit_options = [
            ("Top 5", "5"),
            ("Top 10", "10"),
            ("Top 20", "20"),
        ]
        limit_select.set_options(limit_options)
        valid_limits = {value for _, value in limit_options}
        next_limit = str(config.result_limit)
        if next_limit not in valid_limits:
            next_limit = "10"
        if str(limit_select.value) != next_limit:
            limit_select.value = next_limit
        self._sync_view()

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("settings.title"), id="settings_title")

        yield AbiCard(self._build_config_summary(), id="settings_summary")

        yield AbiCard(self.t("settings.theme_section"), id="settings_theme_title", classes="abi-subtitle")
        with Horizontal(classes="abi-row"):
            yield Button("Classic Light", id="settings_theme_light", classes="abi-menu-button abi-row-button")
            yield Button("Classic Dark", id="settings_theme_dark", classes="abi-menu-button abi-row-button")

        yield AbiCard(self.t("settings.language_section"), id="settings_language_title", classes="abi-subtitle")
        with Horizontal(classes="abi-row"):
            yield Button("Deutsch", id="settings_lang_de", classes="abi-menu-button abi-row-button")
            yield Button("English", id="settings_lang_en", classes="abi-menu-button abi-row-button")

        yield AbiCard(self.t("settings.limit_section"), id="settings_limit_title", classes="abi-subtitle")
        config = cast(SettingsAppContext, self.app_ctx).config_manager.config
        yield Select[str](
            [("Top 5", "5"), ("Top 10", "10"), ("Top 20", "20")],
            value=str(config.result_limit),
            allow_blank=False,
            id="settings_limit_list",
            classes="abi-card",
        )
        yield Button(self.t("settings.apply_limit"), id="settings_apply_limit", classes="abi-menu-button")

        yield Static(self._message, id="settings_message", classes="abi-ok")

        yield self.factory.action_button("screen.back", "settings_back")

    def on_mount(self) -> None:
        self.refresh_labels()

    def _save(self) -> None:
        app_ctx = cast(SettingsAppContext, self.app_ctx)
        manager = app_ctx.config_manager
        manager.save()
        self._set_message_key("settings.saved")
        self._sync_view()

    @on(Select.Changed, "#settings_limit_list")
    def _on_limit_select_changed(self, event: Select.Changed) -> None:
        app_ctx = cast(SettingsAppContext, self.app_ctx)
        manager = app_ctx.config_manager
        selected_limit = event.value
        if selected_limit is Select.BLANK:
            return
        parsed_limit = int(str(selected_limit))
        if parsed_limit == manager.config.result_limit:
            return
        manager.set_result_limit(parsed_limit)
        self._save()

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
            app_ctx.apply_language("de")
            self.refresh_labels()
            self._save()
        elif button_id == "settings_lang_en":
            manager.set_language("en")
            app_ctx.apply_language("en")
            self.refresh_labels()
            self._save()
        elif button_id == "settings_apply_limit":
            selected_limit = self.query_one("#settings_limit_list", Select).value
            if selected_limit is not Select.BLANK:
                manager.set_result_limit(int(str(selected_limit)))
                self._save()
            else:
                self._set_message_key("settings.select_limit")
            self._sync_view()
        elif button_id == "settings_back":
            self.app_ctx.pop_screen()
