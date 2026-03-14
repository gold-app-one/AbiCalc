from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import cast


@dataclass(slots=True)
class AppConfig:
    language: str = "de"
    active_theme: str = "classic-light"
    result_limit: int = 10

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> "AppConfig":
        language = str(raw.get("language", "de"))
        active_theme = str(raw.get("theme", "classic-light"))

        result_limit_raw = raw.get("result_limit", 10)
        try:
            result_limit = int(cast(int | float | str, result_limit_raw))
        except (TypeError, ValueError):
            result_limit = 10

        result_limit = max(1, min(result_limit, 50))

        return cls(
            language=language,
            active_theme=active_theme,
            result_limit=result_limit,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "language": self.language,
            "theme": self.active_theme,
            "result_limit": self.result_limit,
        }


class ConfigManager:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._config = AppConfig()

    @property
    def config(self) -> AppConfig:
        return self._config

    def load(self) -> AppConfig:
        if not self._config_path.exists():
            self.save()
            return self._config

        try:
            raw = json.loads(self._config_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                typed_raw = cast(dict[str, object], raw)
                self._config = AppConfig.from_dict(typed_raw)
            else:
                self._config = AppConfig()
        except (OSError, json.JSONDecodeError):
            self._config = AppConfig()

        return self._config

    def save(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(
            json.dumps(self._config.to_dict(), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def set_theme(self, theme_name: str) -> None:
        self._config.active_theme = theme_name

    def set_language(self, language: str) -> None:
        self._config.language = language

    def set_result_limit(self, result_limit: int) -> None:
        self._config.result_limit = max(1, min(result_limit, 50))
