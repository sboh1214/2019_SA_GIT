import platform

import windows
import darwin

OS_Windows = 'Windows'
OS_DARWIN = 'Darwin'
OS_Linux = 'Linux'


def isWindows():
    return platform.system() == OS_Windows


def isDarwin():
    return platform.system() == OS_DARWIN


def isLinux():
    return platform.system() == OS_Linux


def print_error(msg: str = "Error"):
    if isDarwin():
        darwin.print_error(msg)


def print_warning(msg: str = "Warning"):
    if isDarwin():
        darwin.print_warning(msg)


def print_debug(msg: str = "Debug"):
    if isDarwin():
        darwin.print_debug(msg)


def print_info(msg: str = "Info"):
    if isDarwin():
        darwin.print_info(msg)


if __name__ == "__main__":
    print_error('print_error(msg: str = "Error")')
    print_warning('print_warning(msg: str = "Warning")')
    print_debug('print_debug(msg: str = "Debug")')
    print_info('print_info(msg: str = "Info")')
