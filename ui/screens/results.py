from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from textual.app import ComposeResult
from textual.widgets import Button, Static

from constants import OVERALL_MAX_GRADE

from .base import BaseAbiScreen
from ..core.config import ConfigManager
from ..state.session import SessionModel
from ..widgets.components import AbiCard, AbiTitle

if TYPE_CHECKING:
    from classes import CreditedCombination


def _rank_emoji(index: int) -> str:
    if index == 1:
        return "🥇"
    if index == 2:
        return "🥈"
    if index == 3:
        return "🥉"
    return "📌"


def _status_emoji(passed: bool) -> str:
    return "✅" if passed else "❌"


def _grade_emoji(numeric_grade: float) -> str:
    if numeric_grade <= 1.5:
        return "🌟"
    if numeric_grade <= 2.5:
        return "😄"
    if numeric_grade <= 3.5:
        return "🙂"
    if numeric_grade <= 4.0:
        return "😐"
    return "😬"


def _delta_emoji(delta_points: float) -> str:
    if delta_points > 0:
        return "📈"
    if delta_points < 0:
        return "📉"
    return "➖"


class ResultsAppContext(Protocol):
    session: SessionModel
    config_manager: ConfigManager


class ResultDetailScreen(BaseAbiScreen):
    def __init__(self, index: int, total: int, combination: "CreditedCombination") -> None:
        super().__init__()
        self._index = index
        self._total = total
        self._combination = combination

    def _build_summary(self) -> str:
        score_now, score_pred = self._combination.getScore()
        passed = self._combination.passed()
        status = self.t("results.status_ok") if passed else self.t("results.status_failed")
        status_icon = _status_emoji(passed)
        rank_icon = _rank_emoji(self._index)
        grade_now = score_now.getNumeric(OVERALL_MAX_GRADE)
        grade_pred = score_pred.getNumeric(OVERALL_MAX_GRADE)
        grade_now_icon = _grade_emoji(grade_now)
        grade_pred_icon = _grade_emoji(grade_pred)
        delta = score_pred.value - score_now.value
        delta_icon = _delta_emoji(delta)
        return (
            f"{self.t('results.detail_rank')}: {rank_icon} {self._index}/{self._total}\n"
            f"{self.t('results.detail_status')}: {status_icon} {status}\n"
            f"{self.t('results.detail_current')}: {grade_now_icon} {score_now} ({grade_now:.2f})\n"
            f"{self.t('results.detail_predicted')}: {grade_pred_icon} {score_pred} ({grade_pred:.2f})\n"
            f"{self.t('results.detail_delta')}: {delta_icon} {delta:+.2f}P"
        )

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("results.detail_title").format(index=self._index, total=self._total), id="results_detail_title")
        yield AbiCard(self._build_summary(), id="results_detail_summary", classes="abi-subtitle")
        yield AbiCard(str(self._combination), id="results_detail_content")
        yield Static(self.t("results.detail_hint"), id="results_detail_hint", classes="abi-subtitle")
        yield self.factory.action_button("screen.back", "results_detail_back")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#results_detail_title", AbiTitle).update(
            self.t("results.detail_title").format(index=self._index, total=self._total)
        )
        self.query_one("#results_detail_summary", AbiCard).update(self._build_summary())
        self.query_one("#results_detail_hint", Static).update(self.t("results.detail_hint"))
        self.query_one("#results_detail_back", Button).label = self.t("screen.back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "results_detail_back":
            self.app_ctx.pop_screen()


class ResultsScreen(BaseAbiScreen):
    def __init__(self) -> None:
        super().__init__()
        self._combinations: list["CreditedCombination"] = []

    def _load_combinations(self) -> list["CreditedCombination"]:
        app_ctx = cast(ResultsAppContext, self.app_ctx)
        try:
            limit = int(app_ctx.config_manager.config.result_limit)
        except (TypeError, ValueError):
            limit = 10
        return app_ctx.session.calculate_best_combinations(limit)

    def _build_preview(self, index: int, combination: "CreditedCombination") -> str:
        score_now, score_pred = combination.getScore()
        passed = combination.passed()
        status = self.t("results.status_ok") if passed else self.t("results.status_failed")
        status_icon = _status_emoji(passed)
        rank_icon = _rank_emoji(index)
        grade_now = score_now.getNumeric(OVERALL_MAX_GRADE)
        grade_pred = score_pred.getNumeric(OVERALL_MAX_GRADE)
        grade_now_icon = _grade_emoji(grade_now)
        grade_pred_icon = _grade_emoji(grade_pred)
        delta = score_pred.value - score_now.value
        delta_icon = _delta_emoji(delta)
        return (
            f"{rank_icon} #{index} | {status_icon} {status}\n"
            f"{self.t('results.preview_predicted')}: {grade_pred_icon} {score_pred} ({grade_pred:.2f})\n"
            f"{self.t('results.preview_current')}: {grade_now_icon} {score_now} ({grade_now:.2f})\n"
            f"{self.t('results.preview_delta')}: {delta_icon} {delta:+.2f}P"
        )

    def compose_body(self) -> ComposeResult:
        yield AbiTitle(self.t("results.title"), id="results_title")

        self._combinations = self._load_combinations()

        if not self._combinations:
            yield AbiCard(self.t("results.empty"), classes="abi-warn")
        else:
            total = len(self._combinations)
            for index, combination in enumerate(self._combinations, start=1):
                content = self._build_preview(index, combination)
                style_class = "abi-ok" if combination.passed() else "abi-error"
                yield AbiCard(content, id=f"results_preview_{index}", classes=style_class)
                yield Button(
                    self.t("results.open_detail").format(index=index, total=total),
                    id=f"results_open_{index}",
                    classes="abi-menu-button",
                )

        yield Static(self.t("results.hint"), id="results_hint", classes="abi-subtitle")
        yield self.factory.action_button("screen.back", "results_back")

    def refresh_labels(self) -> None:
        super().refresh_labels()
        self.query_one("#results_title", AbiTitle).update(self.t("results.title"))
        self.query_one("#results_hint", Static).update(self.t("results.hint"))
        self.query_one("#results_back", Button).label = self.t("screen.back")

        if not self._combinations:
            return

        total = len(self._combinations)
        for index, combination in enumerate(self._combinations, start=1):
            self.query_one(f"#results_preview_{index}", AbiCard).update(self._build_preview(index, combination))
            self.query_one(f"#results_open_{index}", Button).label = self.t("results.open_detail").format(
                index=index,
                total=total,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "results_back":
            self.app_ctx.pop_screen()
            return

        if button_id is None:
            return

        if button_id.startswith("results_open_"):
            try:
                index = int(button_id.rsplit("_", maxsplit=1)[1])
            except ValueError:
                return

            if 1 <= index <= len(self._combinations):
                self.app_ctx.push_screen(
                    ResultDetailScreen(index=index, total=len(self._combinations), combination=self._combinations[index - 1])
                )
