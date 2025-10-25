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
    if LOG_LEVEL <= type.value:
        print(f'{logTypeIcons[type]}|{message}')

def logExit(message: str) -> NoReturn:
    raise Exception(f'🚫|{message}')