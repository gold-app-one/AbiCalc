from app import MainApp


class GUI:
    """
    Vor.: -
    Eff.: initiert ein Objekt der Klases GUI im RAM
    Erg.: -
    """
    def __init__(self) -> None:
        self.__app = MainApp()


    def start(self) -> None:
        """
        Vor.: -
        Eff.: startet die GUI
        Erg.: -
        """
        self.__app.run()


def main() -> None:
    """
    Vor.: -
    Eff.: startet die GUI
    Erg.: -
    """
    gui = GUI()
    gui.start()


if __name__ == "__main__":
    main()