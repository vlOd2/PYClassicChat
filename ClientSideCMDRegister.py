from typing import Callable

REGISTERED_CMDS : dict[str, tuple[Callable, str]] = {}

def CommandDeclaration(cmd : str, desc : str) -> Callable:
    def wrapper(func : Callable):
        REGISTERED_CMDS[cmd] = (func, desc)
        return func
    return wrapper