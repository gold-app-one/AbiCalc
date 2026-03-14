from __future__ import annotations

from .components import AbiButton
from ..core.i18n import I18nProvider


class WidgetFactory:
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klasse WidgetFactory im RAM
    Erg.: -
    """
    def __init__(self, i18n: I18nProvider) -> None:
        self._i18n = i18n

    def menu_button(self, label_key: str, button_id: str) -> AbiButton:
        """
        Vor.: label_key ist der Schlüssel für die Beschriftung des Buttons in der Übersetzungsdatei, button_id ist die eindeutige ID des Buttons
        Eff.: -
        Erg.: ein AbiButton-Objekt mit der entsprechenden Beschriftung und ID
        """
        return AbiButton(self._i18n.t(label_key), id=button_id)

    def action_button(self, label_key: str, button_id: str) -> AbiButton:
        """
        Vor.: label_key ist der Schlüssel für die Beschriftung des Buttons in der Übersetzungsdatei, button_id ist die eindeutige ID des Buttons
        Eff.: -
        Erg.: ein AbiButton-Objekt mit der entsprechenden Beschriftung, ID und der CSS-Klasse "abi-action-row" für die spezifische Gestaltung von Aktionsbuttons
        """
        return AbiButton(self._i18n.t(label_key), id=button_id, classes="abi-action-row")
