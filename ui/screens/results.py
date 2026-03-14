from __future__ import annotations

from typing import Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button, Static

from constants import OVERALL_MAX_GRADE

from .base import BaseAbiScreen
from ..core.config import ConfigManager
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle


class ResultsAppContext(Protocol):
    session: SessionModel
    config_manager: ConfigManager


class ResultsScreen(BaseAbiScreen):
    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("results.title"))

        app_ctx = cast(ResultsAppContext, self.app_ctx)
        try:
            limit = int(app_ctx.config_manager.config.result_limit)
        except (TypeError, ValueError):
            limit = 10

        combinations = app_ctx.session.calculate_best_combinations(limit)

        if not combinations:
            yield AbiCard(self.t("results.empty"), classes="abi-warn")
        else:
            for index, combination in enumerate(combinations, start=1):
                score_now, score_pred = combination.getScore()
                status = "OK" if combination.passed() else "NICHT BESTANDEN"
                grade_num = score_pred.getNumeric(OVERALL_MAX_GRADE)
                content = (
                    f"#{index} | {status}\n"
                    f"Prognose: {score_pred} ({grade_num:.2f})\n"
                    f"Ist-Stand: {score_now}"
                )
                style_class = "abi-ok" if combination.passed() else "abi-error"
                yield AbiCard(content, classes=style_class)

        yield Static(self.t("results.hint"), classes="abi-subtitle")
        yield self.factory.action_button("screen.back", "results_back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "results_back":
            self.app_ctx.pop_screen()
