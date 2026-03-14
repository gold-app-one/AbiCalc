from __future__ import annotations

from textual.widgets import Button, Static


class AbiButton(Button):
    def __init__(self, label: str, *, id: str | None = None, classes: str = "") -> None:
        merged_classes = "abi-menu-button"
        if classes:
            merged_classes = f"{merged_classes} {classes}"
        super().__init__(label=label, id=id, classes=merged_classes)


class AbiTitle(Static):
    def __init__(self, label: str) -> None:
        super().__init__(label, classes="abi-title")


class AbiCard(Static):
    def __init__(self, content: str, *, id: str | None = None, classes: str = "") -> None:
        merged_classes = "abi-card"
        if classes:
            merged_classes = f"{merged_classes} {classes}"
        super().__init__(content, id=id, classes=merged_classes)
