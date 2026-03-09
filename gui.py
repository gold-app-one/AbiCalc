from app import MainApp


class GUI:
    def __init__(self) -> None:
        self.__app = MainApp()
        

    def start(self) -> None:
        self.__app.run()


def main() -> None:
    gui = GUI()
    gui.start()


if __name__ == "__main__":
    main()