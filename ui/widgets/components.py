from __future__ import annotations

from textual.widgets import Button, Static


class AbiButton(Button):
    """
    Vor.: label ist die Beschriftung des Buttons als String, id ist die eindeutige ID des Buttons als String oder None, classes ist eine optionale Zeichenkette von CSS-Klassen
    Eff.: initiert ein Objekt der Klasse AbiButton im RAM
    Erg.: -
    """
    def __init__(self, label: str, *, id: str | None = None, classes: str = "") -> None:
        merged_classes = "abi-menu-button"
        if classes:
            merged_classes = f"{merged_classes} {classes}"
        super().__init__(label=label, id=id, classes=merged_classes)


class AbiTitle(Static):
    """
    Vor.: label ist die Beschriftung des Titels als String, id ist die eindeutige ID des Titels als String oder None
    Eff.: initiert ein Objekt der Klasse AbiTitle im RAM
    Erg.: -
    """
    def __init__(self, label: str, *, id: str | None = None) -> None:
        super().__init__(label, id=id, classes="abi-title")


class AbiCard(Static):
    """
    Vor.: content ist der Inhalt der Karte als String, id ist die eindeutige ID der Karte als String oder None, classes ist eine optionale Zeichenkette von CSS-Klassen
    Eff.: initiert ein Objekt der Klasse AbiCard im RAM
    Erg.: -
    """
    def __init__(self, content: str, *, id: str | None = None, classes: str = "") -> None:
        merged_classes = "abi-card"
        if classes:
            merged_classes = f"{merged_classes} {classes}"
        super().__init__(content, id=id, classes=merged_classes)
