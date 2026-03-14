from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Iterable

from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen

from .core.config import ConfigManager
from .core.i18n import I18nProvider
from .core.theme import ThemeManager
from .screens.splash import SplashScreen
from .state.session import SessionModel
from .widgets.factory import WidgetFactory


class MainApp(App[None]):
    TITLE = "AbiCalc 2026"
    CSS_PATH = "styles/generated.tcss"
    BINDINGS = [("ctrl+p", "command_palette", "Befehls-Palette")]

    def __init__(self) -> None:
        super().__init__()
        base_dir = Path(__file__).resolve().parent.parent
        storage_root = self._resolve_storage_root(base_dir)
        storage_root.mkdir(parents=True, exist_ok=True)

        legacy_config_path = base_dir / "ui_config.json"
        legacy_profiles_dir = base_dir / ".abicalc"
        config_path = storage_root / "ui_config.json"
        profiles_dir = storage_root / "profiles"

        if not config_path.exists() and legacy_config_path.exists():
            try:
                shutil.copy2(legacy_config_path, config_path)
            except OSError:
                pass

        if not profiles_dir.exists() and legacy_profiles_dir.exists():
            try:
                shutil.copytree(legacy_profiles_dir, profiles_dir)
            except OSError:
                pass

        profiles_dir.mkdir(parents=True, exist_ok=True)
        if not any(profiles_dir.glob("profile_*.json")):
            default_profile_path = legacy_profiles_dir / "profile_1.json"
            if default_profile_path.exists():
                try:
                    shutil.copy2(default_profile_path, profiles_dir / "profile_1.json")
                except OSError:
                    pass

        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()

        themes_dir = base_dir / "ui" / "styles" / "themes"
        self.theme_manager = ThemeManager(themes_dir, active_theme=self.config.active_theme)
        self.theme_manager.load(self.config.active_theme)

        self.i18n = I18nProvider(self.config.language)
        self.factory = WidgetFactory(self.i18n)
        self.session = SessionModel(data_dir=profiles_dir)
        self.session.load_profile(1)

        self._generated_css_path = base_dir / "ui" / "styles" / "generated.tcss"
        self._write_generated_css()

    def _resolve_storage_root(self, base_dir: Path) -> Path:
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "AbiCalc"
        return base_dir / ".abicalc-runtime"

    def compose(self) -> ComposeResult:
        yield SplashScreen()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        for command in super().get_system_commands(screen):
            if command.title in {"Theme", "Keys"}:
                continue
            yield command

    def apply_theme(self, theme_name: str) -> None:
        self.theme_manager.load(theme_name)
        self._write_generated_css()
        self._refresh_runtime_styles()

    def apply_language(self, language: str) -> None:
        self.i18n.set_language(language)
        self.sub_title = ""
        self._refresh_translated_views()

    def save_profile(self, profile: int) -> Path:
        return self.session.save_profile(profile)

    def load_profile(self, profile: int) -> bool:
        loaded = self.session.load_profile(profile)
        self._refresh_translated_views()
        return loaded

    def switch_profile(self, profile: int) -> bool:
        current = self.session.active_profile
        self.session.save_profile(current)

        loaded = self.session.load_profile(profile)
        if not loaded:
            self.session.reset_for_profile(profile)

        self._refresh_translated_views()
        return loaded

    def _write_generated_css(self) -> None:
        self._generated_css_path.parent.mkdir(parents=True, exist_ok=True)
        self._generated_css_path.write_text(self.theme_manager.build_css(), encoding="utf-8")

    def _refresh_runtime_styles(self) -> None:
        refresh_css = getattr(self, "refresh_css", None)
        if callable(refresh_css):
            try:
                refresh_css()
            except Exception:
                pass

        try:
            self.screen.refresh(layout=True, repaint=True)
        except Exception:
            pass

    def _refresh_translated_views(self) -> None:
        screen = self.screen
        refresh_labels = getattr(screen, "refresh_labels", None)
        if callable(refresh_labels):
            try:
                refresh_labels()
            except Exception:
                pass

        self._refresh_runtime_styles()

    def on_mount(self) -> None:
        self.sub_title = ""

    def quit_with_save(self) -> None:
        self.session.save_profile(self.session.active_profile)
        self.config_manager.save()
        self.exit()

    def on_exit(self) -> None:
        self.session.save_profile(self.session.active_profile)
        self.config_manager.save()
