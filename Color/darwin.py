class Back:
    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN = '\033[46m'
    WHITE = '\033[47m'
    RESET = '\033[49m'


class Fore:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[39m'


class Bright:
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    NORMAL = '\033[22m'


class Reset:
    RESET = '\033[0m'


def print_error(msg: str = "Error"):
    print(Fore.RED + msg + Fore.RESET)


def print_warning(msg: str = "Warning"):
    print(Fore.YELLOW + msg + Fore.RESET)


def print_debug(msg: str = "Debug"):
    print(Fore.GREEN + msg + Fore.GREEN)


def print_info(msg: str = "Info"):
    print(Fore.BLUE + msg + Fore.RESET)


if __name__ == "__main__":
    print(f"{Back.BLACK}Background Black{Back.RESET}")
    print(f"{Back.RED}Background RED{Back.RESET}")
