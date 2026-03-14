from typing import Protocol, cast

from ui.app import MainApp


class _Runnable(Protocol):
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klases _Runnable im RAM
    Erg.: -
    """
    def run(self) -> object: ...


def main() -> None:
    """
    Vor.: -
    Eff.: startet die GUI
    Erg.: -
    """
    cast(_Runnable, MainApp()).run()


if __name__ == "__main__":
    main()
