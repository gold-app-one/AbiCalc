from __future__ import annotations

from .components import AbiButton
from ..core.i18n import I18nProvider


class WidgetFactory:
    def __init__(self, i18n: I18nProvider) -> None:
        self._i18n = i18n

    def menu_button(self, label_key: str, button_id: str) -> AbiButton:
        return AbiButton(self._i18n.t(label_key), id=button_id)

    def action_button(self, label_key: str, button_id: str) -> AbiButton:
        return AbiButton(self._i18n.t(label_key), id=button_id, classes="abi-action-row")
