from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult

from .core.config import ConfigManager
from .core.i18n import I18nProvider
from .core.theme import ThemeManager
from .screens.splash import SplashScreen
from .state.session import SessionModel
from .widgets.factory import WidgetFactory


class MainApp(App[None]):
    TITLE = "AbiCalc"
    CSS_PATH = "styles/generated.tcss"

    def __init__(self) -> None:
        super().__init__()
        base_dir = Path(__file__).resolve().parent.parent

        self.config_manager = ConfigManager(base_dir / "ui_config.json")
        self.config = self.config_manager.load()

        themes_dir = base_dir / "ui" / "styles" / "themes"
        self.theme_manager = ThemeManager(themes_dir, active_theme=self.config.active_theme)
        self.theme_manager.load(self.config.active_theme)

        self.i18n = I18nProvider(self.config.language)
        self.factory = WidgetFactory(self.i18n)
        self.session = SessionModel()

        self._generated_css_path = base_dir / "ui" / "styles" / "generated.tcss"
        self._write_generated_css()

    def compose(self) -> ComposeResult:
        yield SplashScreen()

    def apply_theme(self, theme_name: str) -> None:
        self.theme_manager.load(theme_name)
        self._write_generated_css()

    def _write_generated_css(self) -> None:
        self._generated_css_path.write_text(self.theme_manager.build_css(), encoding="utf-8")

    def on_mount(self) -> None:
        self.sub_title = self.i18n.t("app.title")
