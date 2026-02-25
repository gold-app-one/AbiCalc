import graphy as g
from customTypes import MenuKey


class GUI:
    MENU_ELEMENTS: dict[MenuKey, list[g.RenderObject]] = {
        MenuKey.START: [],
        MenuKey.SETTINGS: [],
        MenuKey.SUBJECTS: [],
        MenuKey.GRADES: [],
        MenuKey.RESULT: []
    }
    def __init__(self) -> None:
        self.__darkMode: bool = True
        self.__currentMenu: MenuKey = MenuKey.START

    def start(self) -> None:
        pass