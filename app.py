from typing import Protocol, cast

from ui.app import MainApp


class _Runnable(Protocol):
    def run(self) -> object: ...


def main() -> None:
    cast(_Runnable, MainApp()).run()


if __name__ == "__main__":
    main()