import threading
from colorama import just_fix_windows_console
from colorama.ansi import Fore, Back, Style

# Enable colorama
just_fix_windows_console()

_stdout_lock = threading.RLock()
modified_stdout : bool = True

def _cc2ansi(code : str) -> str:
    match code:
        case "0":
            return Back.RESET + Fore.BLACK + Back.WHITE
        case "1":
            return Back.RESET + Fore.BLUE
        case "2":
            return Back.RESET + Fore.GREEN
        case "3":
            return Back.RESET + Fore.CYAN
        case "4":
            return Back.RESET + Fore.RED
        case "5":
            return Back.RESET + Fore.MAGENTA
        case "6":
            return Back.RESET + Fore.YELLOW
        case "7":
            return Back.RESET + Fore.BLACK + Back.WHITE
        case "8":
            return Back.RESET + Fore.BLACK + Back.WHITE
        case "9":
            return Back.RESET + Fore.BLUE
        case "a":
            return Back.RESET + Fore.LIGHTGREEN_EX
        case "b":
            return Back.RESET + Fore.LIGHTCYAN_EX
        case "c":
            return Back.RESET + Fore.LIGHTRED_EX
        case "d":
            return Back.RESET + Fore.LIGHTMAGENTA_EX
        case "e":
            return Back.RESET + Fore.LIGHTYELLOW_EX
        case "f":
            return Back.RESET + Fore.WHITE + Back.BLACK
        case _:
            return None

def write_cc(str : str) -> None:
    global _stdout_lock
    with _stdout_lock:
        global modified_stdout
        modified_stdout = True
        
        final_str = ""
        str_len = len(str)
        len_range = range(str_len)
        len_range_iter = iter(len_range)

        for i in len_range_iter:
            if str[i] == "&" and i + 2 < str_len:
                final_str += _cc2ansi(str[i + 1])
                next(len_range_iter)
            else:
                final_str += str[i]
        final_str += Style.RESET_ALL
        print(final_str)

def write(str : str) -> None:
    global _stdout_lock
    with _stdout_lock:
        global modified_stdout
        modified_stdout = True
        print(str)

def write_info(str : str) -> None:
    global _stdout_lock
    with _stdout_lock:
        global modified_stdout
        modified_stdout = True

        print(Fore.BLUE, end="")
        print("(INFO) ", end="")
        print(str, end="")
        print(Style.RESET_ALL)

def write_err(str : str) -> None:
    global _stdout_lock
    with _stdout_lock:
        global modified_stdout
        modified_stdout = True

        print(Fore.RED, end="")
        print("(ERROR) ", end="")
        print(str, end="")
        print(Style.RESET_ALL)