from typing import NoReturn
from customTypes import LogType
from constants import LOG_LEVEL

logTypeIcons: dict[LogType, str] = {
    LogType.LOG: '📰',
    LogType.INFO: '❕',
    LogType.WARNING: '⚠️',
    LogType.ERROR: '❌',
}

def log(message: str, type: LogType) -> None:
    """
    Vor.: eine Nachricht als String und ein LogType
    Eff.: gibt die Nachricht aus, wenn der LogType größer oder gleich dem LOG_LEVEL ist
    Erg.: -
    """
    if LOG_LEVEL <= type.value:
        print(f'{logTypeIcons[type]}|{message}')

def logExit(message: str) -> NoReturn:
    """
    Vor.: eine Fehlermeldung als String
    Eff.: gibt die Fehlermeldung aus
    Erg.: -
    """
    raise Exception(f'🚫|{message}')