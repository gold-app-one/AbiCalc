from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import cast


@dataclass(slots=True)
class ThemeTokens:
    background: str = "#f8f9fb"
    surface: str = "#ffffff"
    primary: str = "#0b5ed7"
    primary_muted: str = "#d9e7ff"
    text: str = "#202636"
    text_muted: str = "#4d5a78"
    ok: str = "#198754"
    warn: str = "#ff8f00"
    error: str = "#d92d20"

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ThemeTokens":
        return cls(
            background=str(data.get("background", cls.background)),
            surface=str(data.get("surface", cls.surface)),
            primary=str(data.get("primary", cls.primary)),
            primary_muted=str(data.get("primary_muted", cls.primary_muted)),
            text=str(data.get("text", cls.text)),
            text_muted=str(data.get("text_muted", cls.text_muted)),
            ok=str(data.get("ok", cls.ok)),
            warn=str(data.get("warn", cls.warn)),
            error=str(data.get("error", cls.error)),
        )


class ThemeManager:
    def __init__(self, themes_dir: Path, active_theme: str = "classic-light") -> None:
        self._themes_dir = themes_dir
        self._active_theme = active_theme
        self._tokens = ThemeTokens()

    @property
    def active_theme(self) -> str:
        return self._active_theme

    @property
    def tokens(self) -> ThemeTokens:
        return self._tokens

    def load(self, theme_name: str | None = None) -> ThemeTokens:
        if theme_name is not None:
            self._active_theme = theme_name

        theme_path = self._themes_dir / f"{self._active_theme}.json"
        if not theme_path.exists():
            self._tokens = ThemeTokens()
            return self._tokens

        try:
            raw = json.loads(theme_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                typed_raw = cast(dict[str, object], raw)
                self._tokens = ThemeTokens.from_dict(typed_raw)
            else:
                self._tokens = ThemeTokens()
        except (OSError, json.JSONDecodeError):
            self._tokens = ThemeTokens()

        return self._tokens

    def build_css(self) -> str:
        t = self._tokens
        return f"""
        Screen {{
            background: {t.background};
            color: {t.text};
        }}

        Header {{
            background: {t.primary};
            color: {t.surface};
        }}

        Footer {{
            background: {t.primary};
            color: {t.surface};
        }}

        .abi-title {{
            text-align: center;
            margin: 1 1 0 1;
            padding: 1;
            background: {t.primary};
            color: {t.surface};
            text-style: bold;
        }}

        .abi-subtitle {{
            margin: 0 2 1 2;
            color: {t.text_muted};
        }}

        .abi-card {{
            margin: 1 2;
            padding: 1 2;
            background: {t.surface};
            border: round {t.primary_muted};
        }}

        Button {{
            background: {t.primary_muted};
            color: {t.text};
            border: round {t.primary};
        }}

        Button.-active {{
            background: {t.primary};
            color: {t.surface};
        }}

        .abi-ok {{
            color: {t.ok};
        }}

        .abi-warn {{
            color: {t.warn};
        }}

        .abi-error {{
            color: {t.error};
        }}

        .abi-menu-button {{
            margin: 1 2;
            height: 3;
            text-style: bold;
        }}

        Button.abi-menu-button {{
            background: #163042;
            color: #ffffff;
            border: round #ffffff;
        }}

        Button.abi-menu-button .button--label {{
            color: #ffffff;
            text-style: bold;
        }}

        Button.abi-menu-button.-active {{
            background: #ffffff;
            color: #163042;
            border: round #163042;
        }}

        Button.abi-menu-button.-active .button--label {{
            color: #163042;
            text-style: bold;
        }}

        .abi-action-row {{
            margin: 1 2;
        }}

        Button.abi-action-row {{
            background: {t.primary_muted};
            color: {t.text};
            border: round {t.primary};
        }}

        .abi-spacer {{
            height: 1;
        }}

        .abi-topbar {{
            margin: 0 2;
            height: 3;
        }}

        .abi-topbar-spacer {{
            width: 1fr;
        }}

        Button.abi-topbar-button {{
            width: auto;
            min-width: 16;
            margin: 0;
            background: {t.primary_muted};
            color: {t.text};
            border: round {t.primary};
            text-style: bold;
        }}

        .abi-row {{
            margin: 0 2;
            height: auto;
        }}

        .abi-row-field {{
            width: 1fr;
            margin: 1 1 1 0;
        }}

        .abi-row-button {{
            width: 1fr;
            margin: 1 1 1 0;
        }}
        """
